import os
import tempfile
import requests
from pathlib import Path
from flask import jsonify, request
from werkzeug.utils import secure_filename
from dotenv import load_dotenv
from iaClass import iaClass
load_dotenv()

def register_api_routes(app):
    """Registra todas las rutas de la aplicación"""
    @app.route('/api/demo', methods=['POST'])
    def demos():
        uploaded_file = request.files.get('file')
        data = {
                "data_invoice": {
                "factura": {
                    "fecha_emision": "2026-09-09",
                    "fecha_vencimiento": "2026-09-09",
                    "metodo_pago": "Efectivo",
                    "moneda": "COP",
                    "numero_factura": "FEAL69528",
                    "orden_compra": None,
                    },
                "proveedor": {
                    "direccion": "CARRERA 38 #44-79 BARRANQUILLA",
                    "email": "contabilidad1@alda.com.co",
                    "nit": "802015914-1",
                    "nombre": "ALDA Y CIA S.A.S.",
                    "telefono": "3799854",
                    },
                "totales": {
                    "descuento": 0,
                    "impuestos": 7983,
                    "porcentaje_descuento": 0,
                    "subtotal": 42017,
                    "total": 50000,
                    },
                    },
                "items": [
                    {
                    "cantidad": 1,
                    "codigo": "NP1147A-85",
                    "descripcion": "INSTALACION ALTA CIELO/RACER",
                    "descuento": 0,
                    "impuesto_porcentaje": 19,
                    "precio_unitario": 42017,
                    "total_linea": 42017,
                    }
                    ],
                }
        return jsonify(filename="data", data = data);
    
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
    
    @app.route('/api/svd/items',methods=['POST'])
    @app.route('/api/svd/items/<code>',methods=['POST'])
    def get_items(code):

        svd_api_id = os.getenv("_SVD_API_ID")
        svd_applicationAccessKey = os.getenv("_SVD_APPLICATIONACCESSKEY")

        url = f'https://api.appsheet.com/api/v2/apps/{svd_api_id}/tables/Referencias/Action'
        
        payload = {
                    "Action": "Find",
                    "Properties": {
                        "Locale": "en-US",
                        "Location": "47.623098, -122.330184",
                        "Selector": f"Filter(Referencias, [Codigo] = '{code}')",
                        "Timezone": "Pacific Standard Time",
                        "UserSettings": {}
                    },
                    "Rows": []
                }
        headers = {
        'applicationAccessKey': f'{svd_applicationAccessKey}',
        'Content-Type': 'application/json'
        }

        response = requests.post(url, headers=headers, json=payload)

        return jsonify(
            code = code,
            data = response.json()
        ),response.status_code