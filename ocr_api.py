import requests
import os

print("--- Importaciones listas ---")

# 
# FUNCIONES DE PROCESAMIENTO
# 

def extract_text_via_api(file_path, api_key):
    """
    Usa la API de ocr.space pidiendo ESTRUCTURA DE TABLA.
    """
    print("--- Enviando imagen a ocr.space API ---")
    try:
        with open(file_path, 'rb') as f:
            payload = {
                'apikey': api_key,
                'language': 'spa',
                'isOverlayRequired': False,
                'isTable': True,
                'scale': True,
                'OCREngine': 2,
            }
            files_data = {'file': (os.path.basename(file_path), f)}
            response = requests.post(
                'https://api.ocr.space/parse/image',
                files=files_data,
                data=payload,
                timeout=10
            )
        response.raise_for_status()
        result = response.json()

        if result.get('IsErroredOnProcessing'):
            print(f"Error de la API: {result.get('ErrorMessage')}")
            return None

        return result

    except requests.exceptions.RequestException as e:
        print(f"Error de conexión con la API: {e}")
        return None
    except Exception as e:
        print(f"Error inesperado: {e}")
        return None

def extract_text_via_optiic(file_path, api_key):
    """Usa Optiic.dev como alternativa."""
    print("--- Enviando imagen a Optiic.dev ---")
    try:
        with open(file_path, 'rb') as f:
            files = {'image': (os.path.basename(file_path), f)}
            data = {'apiKey': api_key}
            response = requests.post(
                'https://api.optiic.dev/process',
                files=files,
                data=data,
                timeout=30
            )
        response.raise_for_status()
        result = response.json()
        return result.get('text', '') or result

    except Exception as e:
        print(f"Error en Optiic.dev: {e}")
        return None

# 
# FUNCIÓN PRINCIPAL DE EJECUCIÓN
# 
from config import OCR_API_KEY, OPTIIC_API_KEY
def process_uploaded_file(original_file_path):
    """
    Orquesta todo el proceso y devuelve el JSON parseado del ticket.
    """

    api_key = OCR_API_KEY
    if not api_key:
        return {'error': 'API Key no válida'}

    file_name, file_ext = os.path.splitext(original_file_path)
    file_ext = file_ext.lower()

    file_to_send_path = original_file_path
    is_temp_file = False

    if file_ext not in [".jpg", ".jpeg", ".png", ".bmp", ".tiff"]:
        return {'error': f'Formato de archivo no soportado: {file_ext}'}

    # --- 1. Extraer Texto Y ESTRUCTURA DE TABLA ---
    api_response_data = extract_text_via_api(file_to_send_path, api_key)

    if not api_response_data and OPTIIC_API_KEY:
        print("--- Intentando con API de respaldo (Optiic.dev) ---")
        api_response_data = extract_text_via_optiic(original_file_path, OPTIIC_API_KEY)

    if not api_response_data:
        return {'error': 'No se pudo extraer texto con ninguna API.'}


    # --- 2. Obtener LA CADENA DE TEXTO PARSEADA ---
    try:
        parsed_text_string = api_response_data['ParsedResults'][0]['ParsedText']
    except (KeyError, IndexError, TypeError) as e:
        return {'error': f'No se pudo encontrar la ParsedText en la respuesta JSON: {str(e)}'}

    # --- 3. Procesar con OCR API ---
    from ticket_parser import process_ticket

    ocr_json = process_ticket(parsed_text_string)

    # Limpiar solo el archivo temporal si se crea uno
    if is_temp_file:
        try:
            os.remove(file_to_send_path)
        except:
            pass

    return ocr_json

