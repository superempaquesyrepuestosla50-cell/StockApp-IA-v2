from flask import app, render_template

def register_routes(app):
    """Registra todas las rutas de la aplicación"""
    @app.route('/')
    def index():
        return render_template('index.html', name="Hola")