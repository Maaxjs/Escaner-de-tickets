"""
auth.py - Autenticación y protección de rutas
"""

from functools import wraps
from flask import session, redirect, url_for
from werkzeug.security import check_password_hash
from src.db import get_db


def login_required(f):
    """Decorador que requiere que el usuario esté autenticado."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function


def validate_credentials(username, password):
    """Valida credenciales del usuario contra la base de datos."""
    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT * FROM admin WHERE username = ?", (username,))
    user = c.fetchone()
    conn.close()
    
    if user and check_password_hash(user['password'], password):
        return True
    return False
