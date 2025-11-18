"""
db.py - Gestión de base de datos y operaciones CRUD
"""

import sqlite3
from werkzeug.security import generate_password_hash
from config import DB_PATH, DEFAULT_ADMIN_USERNAME, DEFAULT_ADMIN_PASSWORD


def get_db():
    """Abre conexión a base de datos SQLite con row_factory activado."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Inicializa la base de datos y crea tablas si no existen."""
    conn = get_db()
    c = conn.cursor()

    # Crear tablas si no existen
    c.execute('''CREATE TABLE IF NOT EXISTS admin (
        id INTEGER PRIMARY KEY,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL
    )''')

    c.execute('''CREATE TABLE IF NOT EXISTS tickets (
        id INTEGER PRIMARY KEY,
        image_base64 TEXT NOT NULL,
        date_uploaded TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        nombre_negocio TEXT,
        items_json TEXT,
        precio_total_compra REAL,
        nombre_usuario TEXT,
        estado TEXT DEFAULT 'pendiente'
    )''')
    conn.commit()

    # Crear admin solo si no existe
    c.execute("SELECT COUNT(*) FROM admin WHERE username = ?", (DEFAULT_ADMIN_USERNAME,))
    if c.fetchone()[0] == 0:
        c.execute("INSERT INTO admin (username, password) VALUES (?, ?)",
                  (DEFAULT_ADMIN_USERNAME, generate_password_hash(DEFAULT_ADMIN_PASSWORD)))
        conn.commit()

    # Asegurar que las columnas nuevas existan
    columnas = [r[1] for r in c.execute("PRAGMA table_info(tickets)").fetchall()]
    columnas_necesarias = ["nombre_negocio", "items_json", "precio_total_compra", "nombre_usuario"]
    for col in columnas_necesarias:
        if col not in columnas:
            c.execute(f"ALTER TABLE tickets ADD COLUMN {col} TEXT")
    conn.commit()

    conn.close()


def allowed_file(filename):
    """Valida si la extensión del archivo es permitida."""
    from config import ALLOWED_EXTENSIONS
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
