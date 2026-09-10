from flask import app, render_template

def register_routes(app):
    """Registra todas las rutas de la aplicación"""
    @app.route('/')
    def index():
        return render_template('index.html', name="Hola")

    @app.route('/invoice/upload')
    def invoice_upload():
        return render_template('invoice/upload-form.html', name="Hola")