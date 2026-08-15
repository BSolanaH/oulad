"""
wsgi.py — Entry point para Render (gunicorn wsgi:app).

Por qué existe este archivo: Python no puede importar con 'import' estándar
módulos cuyo nombre empieza por dígito (05_flask_api). Se usa importlib
para cargar el archivo por ruta, sin necesidad de renombrarlo.
"""
import importlib.util
import os

_spec = importlib.util.spec_from_file_location(
    "flask_api",
    os.path.join(os.path.dirname(__file__), "05_flask_api.py")
)
_module = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_module)

app = _module.app
