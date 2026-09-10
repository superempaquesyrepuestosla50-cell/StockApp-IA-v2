import tempfile
from pathlib import Path

from flask import jsonify, request
from werkzeug.utils import secure_filename

from iaClass import iaClass

def register_api_routes(app):
    """Registra todas las rutas de la aplicación"""
    @app.route('/api/upload', methods=['POST'])
    def upload_invoice():
        uploaded_file = request.files.get('file')

        if uploaded_file is None or uploaded_file.filename == '':
            return jsonify(error='No se recibió ningún archivo en el campo "file".'), 400

        original_filename = secure_filename(uploaded_file.filename)
        if not original_filename:
            return jsonify(error='El nombre del archivo no es válido.'), 400

        temporary_file = tempfile.NamedTemporaryFile(
            prefix='stockapp_',
            suffix=Path(original_filename).suffix,
            delete=False,
        )
        temporary_path = Path(temporary_file.name)

        try:
            uploaded_file.save(temporary_path)
            invoice_data = iaClass().extract_invoice_data(str(temporary_path))
        except Exception as error:
            return jsonify(
                error='No se pudo procesar la factura.',
                details=str(error),
            ), 502
        finally:
            temporary_file.close()
            temporary_path.unlink(missing_ok=True)

        return jsonify(filename=original_filename, data=invoice_data), 201