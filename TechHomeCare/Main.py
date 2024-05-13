from MondayAPI import fetch_and_format_items
from flask import Flask, render_template
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

@app.route('/')
def index():
    # Obtener los datos de los usuarios
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

if __name__ == '__main__':
    print(fetch_and_format_items(1496686926))
    app.run(debug=True)

#board_id = 1496686926  # Replace with your actual board ID
