from MondayAPI import fetch_and_format_items
from flask import Flask, jsonify, make_response, redirect, render_template, request, url_for
from MondayAPI import fetch_and_format_items
import json

app = Flask(__name__)

def convertir_meses(data):
    index = json.loads(data)['index']
    if index == 5:
        return '0 meses'
    elif index == 1:
        return '3 meses'
    elif index == 0:
        return '6 meses'
    elif index == 2:
        return '12 meses'
    else:
        return 'Desconocido'


def verificar_credenciales(nombre_usuario, password):
    for usuario in fetch_and_format_items(1496686926):
        if usuario['name'] == nombre_usuario and usuario['Contraseña'] == password:
            return True
    return False

@app.route('/login', methods=['POST'])
def login():
    nombre_usuario = request.form['nombre_usuario']
    password = request.form['password']

    print("el usuario recibido del form es: " + str(nombre_usuario))

    if verificar_credenciales(nombre_usuario, password):
        # Credenciales válidas, crear una cookie de usuario autenticado y redirigir a la página principal
        respuesta = make_response(redirect(url_for('index')))
        respuesta.set_cookie('usuario_autenticado', nombre_usuario)
        return respuesta
    else:
        # Credenciales inválidas, devolver un mensaje de error
        return jsonify({'error': 'Nombre de usuario o contraseña incorrectos'}), 401

@app.route('/')
def index():
    if 'usuario_autenticado' in request.cookies:
        # El usuario está autenticado, mostrar los datos de los usuarios
        board_id = 1496686926  # Reemplaza con tu ID de tabla real
        user_data = fetch_and_format_items(board_id)
        # Procesar los datos para convertir las cadenas JSON en objetos Python
        for user in user_data:
            if 'Subcripcion' in user:
                subcripcion_data = json.loads(user['Subcripcion'])
                if 'index' in subcripcion_data:
                    if subcripcion_data['index'] == 1:
                        subcripcion_data['estado'] = 'alta'
                    elif subcripcion_data['index'] == 2:
                        subcripcion_data['estado'] = 'baja'
                    user['Subcripcion'] = subcripcion_data
            if 'Telefono' in user:
                user['Telefono'] = json.loads(user['Telefono'])
            if 'meses' in user:
                user['meses'] = convertir_meses(user['meses'])

        return render_template('index.html', users=user_data)
    else:
        # El usuario no está autenticado, redirigir al formulario de inicio de sesión
        return redirect(url_for('login_form'))
    

@app.route('/login_form')
def login_form():
    return render_template('login.html')

if __name__ == '__main__':
    #print(fetch_and_format_items(1496686926))
    app.run(debug=True)

#board_id = 1496686926  # Replace with your actual board ID
