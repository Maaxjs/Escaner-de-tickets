import os

# === CONFIGURACIÓN BÁSICA ===

# Clave secreta para sesiones
SECRET_KEY = 'um4j2byu234gij2b2g5vg23b4bg23v'

# Credenciales de admin por defecto
DEFAULT_ADMIN_USERNAME = 'admin'
DEFAULT_ADMIN_PASSWORD = 'admin123'

# === CONFIGURACIÓN DE ARCHIVOS ===

# Carpeta para guardar archivos generados
UPLOAD_FOLDER = 'uploads'

# Extensiones de archivo permitidas
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

# Tamaño máximo de archivo para la API de OCR SPACE (1MB)
MAX_FILE_SIZE = 1024 * 1024

# === CONFIGURACIÓN DE BASE DE DATOS ===
# Ruta de la base de datos SQLite
DB_PATH = 'tickets.db'

# === CONFIGURACIÓN DE FLASK ===

# Modo de despliegue
DEBUG = False
HOST = '0.0.0.0'
PORT = 5000

# === CONFIGURACIÓN MAIL

MAIL_SERVER = os.getenv('MAIL_SERVER', 'smtp.gmail.com')
MAIL_PORT = int(os.getenv('MAIL_PORT', 587))
MAIL_USERNAME = os.getenv('MAIL_USERNAME', '')
MAIL_PASSWORD = os.getenv('MAIL_PASSWORD', '')


# === CONFIGURACIÓN APIS

GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
OCR_API_KEY = os.getenv("OCR_API_KEY", "")
OPTIIC_API_KEY = os.getenv("OPTIIC_API_KEY", "")