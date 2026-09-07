from flask import Flask
from waitress import serve
from routesModule import register_routes

# Crea una instancia de la aplicación Flask
app = Flask(__name__)

# Registra todas las rutas
register_routes(app)

# Ejecuta la aplicación si el script es el principal
if __name__ == '__main__':
    app.run(debug=True,host='0.0.0.0',port=5000)