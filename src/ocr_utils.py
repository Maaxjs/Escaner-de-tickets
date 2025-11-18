"""
ocr_utils.py - Utilidades para procesamiento OCR
"""

import base64
import tempfile
import os


def process_ocr_from_base64(image_base64):
    """
    Decodifica imagen base64, la guarda en archivo temporal,
    y la procesa con ocr_api.process_uploaded_file
    """
    try:
        # Decodificar base64 a bytes
        image_bytes = base64.b64decode(image_base64)
        
        # Crear archivo temporal
        with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as tmp:
            tmp.write(image_bytes)
            temp_file_path = tmp.name
        
        # Importar y usar ocr_api
        from ocr_api import process_uploaded_file
        
        # Procesar el archivo
        result = process_uploaded_file(temp_file_path)
        
        # Limpiar archivo temporal
        try:
            os.remove(temp_file_path)
        except:
            pass
        
        return result
        
    except Exception as e:
        return {
            'error': str(e),
            'nombre_lugar': 'Error',
            'items': [],
            'precio_total_compra': 0
        }
