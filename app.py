from flask import Flask, render_template, request, redirect, url_for, session, jsonify
import json
import os
import base64
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import warnings
warnings.filterwarnings("ignore", message="Using the in-memory storage for tracking rate limits*")
from PIL import Image, ImageFile
import io
ImageFile.LOAD_TRUNCATED_IMAGES = True

# Importar módulos de lógica de negocio
from config import UPLOAD_FOLDER, ALLOWED_EXTENSIONS, MAX_FILE_SIZE, SECRET_KEY
from src.db import get_db, init_db, allowed_file
from src.auth import login_required, validate_credentials
from src.ocr_utils import process_ocr_from_base64
from src.export_mail import export_monthly

app = Flask(__name__)
app.secret_key = SECRET_KEY

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits=["200 per day", "50 per hour"]
)

@app.route('/')
def index():
    return redirect(url_for('upload'))

@app.route('/login', methods=['GET', 'POST'])
@limiter.limit("3 per minute")
def login():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')

        if not username or not password:
            return render_template('login.html', error='Campos incompletos', logged_in=False)

        if validate_credentials(username, password):
            session['user'] = username
            session.permanent = True 
            return redirect(url_for('dashboard'))
        else:
            return render_template('login.html', error='Credenciales inválidas', logged_in=False)

    return render_template('login.html', logged_in=('user' in session))

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/upload', methods=['GET', 'POST'])
def upload():
    if request.method == 'POST':
        # Verificar que hay archivo
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        if file and allowed_file(file.filename):
            image_data = file.read()
            
            if len(image_data) >= MAX_FILE_SIZE:
                try:
                    # Cargar la imagen en Pillow desde los bytes en memoria
                    img = Image.open(io.BytesIO(image_data))

                    if img.mode in ('RGBA', 'P'):
                        img = img.convert('RGB')
                    
                    max_width = 1920
                    if img.width > max_width:
                        ratio = max_width / float(img.width)
                        height = int(float(img.height) * ratio)
                        # Usar LANCZOS es el 'resample' de alta calidad
                        img = img.resize((max_width, height), Image.LANCZOS)

                    # Búfer en memoria para guardar la imagen comprimida
                    output_buffer = io.BytesIO()
                    
                    # Guardar con calidad inicial
                    quality = 85
                    img.save(output_buffer, format='JPEG', quality=quality, optimize=True)

                    # Bajar la calidad iterativamente si sigue siendo muy grande
                    while output_buffer.tell() > MAX_FILE_SIZE and quality > 10:
                        output_buffer.seek(0)  
                        output_buffer.truncate() 
                        quality -= 10 
                        img.save(output_buffer, format='JPEG', quality=quality, optimize=True)
                    
                    # Obtener los bytes de la imagen comprimida
                    image_data = output_buffer.getvalue()

                    # Si después de comprimir a calidad 10 sigue siendo muy grande...
                    if len(image_data) > MAX_FILE_SIZE:
                        return jsonify({'error': 'File is too large, even after compression'}), 400
                        
                except Exception as e:
                    return jsonify({'error': f'Image processing failed: {str(e)}'}), 500
            
            image_base64 = base64.b64encode(image_data).decode('utf-8')
            
            # Procesar OCR con ocr_api (esto espera las 2 APIs: ocr.space + Groq)
            ocr_data = process_ocr_from_base64(image_base64)
            
            return jsonify({
                'success': True,
                'image': image_base64,
                'ocr_data': ocr_data
            })
        
        return jsonify({'error': 'Invalid file type'}), 400
    
    return render_template('upload.html', logged_in=('user' in session), username=session.get('user'))

@app.route('/api/save-ticket', methods=['POST'])
def save_ticket():
    data = request.json
    
    image_base64 = data.get('image')
    nombre_negocio = data.get('nombre_negocio')
    items = data.get('items')  
    precio_total_compra = data.get('precio_total_compra')
    nombre_usuario = data.get('nombre_usuario')

    if not image_base64:
        return jsonify({'error': 'Image required'}), 400

    conn = get_db()
    c = conn.cursor()
    c.execute('''INSERT INTO tickets 
                (image_base64, nombre_negocio, items_json, precio_total_compra, nombre_usuario)
                VALUES (?, ?, ?, ?, ?)''',
              (image_base64, 
               nombre_negocio, 
               json.dumps(items, ensure_ascii=False) if items else None, 
               precio_total_compra,
               nombre_usuario))
    ticket_id = c.lastrowid
    conn.commit()
    conn.close()

    return jsonify({'success': True, 'message': 'Ticket saved successfully', 'id': ticket_id})

@app.route('/dashboard')
@login_required
def dashboard():
    if session.get('user') != 'admin':
        return redirect(url_for('upload'))
    
    conn = get_db()
    c = conn.cursor()
    c.execute('SELECT * FROM tickets ORDER BY date_uploaded DESC')
    tickets = c.fetchall()
    conn.close()

    tickets = [dict(row) for row in tickets]
    for ticket in tickets:
        if isinstance(ticket.get('items_json'), str):
            try:
                ticket['items'] = json.loads(ticket['items_json'])
            except json.JSONDecodeError:
                ticket['items'] = []
        else:
            ticket['items'] = []
        
 

    return render_template('dashboard.html', tickets=tickets, logged_in=('user' in session), username=session.get('user'))

@app.route('/confirm/<int:ticket_id>')
def confirm_ticket(ticket_id):
    conn = get_db()
    c = conn.cursor()
    c.execute('SELECT * FROM tickets WHERE id = ?', (ticket_id,))
    ticket = c.fetchone()
    conn.close()

    if not ticket:
        return "Ticket no encontrado", 404

    nombre_negocio = ticket['nombre_negocio']
    items = []
    try:
        if ticket['items_json']:
            items = json.loads(ticket['items_json'])
    except Exception:
        items = []
    
    precio_total_compra = ticket['precio_total_compra']

    return render_template('confirm.html', 
                         ticket=ticket, 
                         nombre_negocio=nombre_negocio,
                         items=items,
                         precio_total_compra=precio_total_compra,
                         logged_in=('user' in session), 
                         username=session.get('user'))

@app.route('/api/delete-ticket/<int:ticket_id>', methods=['DELETE'])
@login_required
def delete_ticket(ticket_id):
    if session.get('user') != 'admin':
        return jsonify({'error': 'Unauthorized'}), 403
    
    conn = get_db()
    c = conn.cursor()
    c.execute('DELETE FROM tickets WHERE id = ?', (ticket_id,))
    conn.commit()
    conn.close()
    
    return jsonify({'success': True})

@app.route('/api/export-monthly', methods=['POST'])
@login_required
def export_monthly_route():
    if session.get('user') != 'admin':
        return jsonify({'error': 'Unauthorized'}), 403
    
    email = request.json.get('email')
    if not email:
        return jsonify({'error': 'Email required'}), 400

    result = export_monthly(email)
    
    if result['success']:
        return jsonify(result)
    else:
        return jsonify(result), 500

if __name__ == '__main__':
    init_db()
    app.run(host="0.0.0.0", port=5000)

