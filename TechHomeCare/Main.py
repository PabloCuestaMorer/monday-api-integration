from flask import (
    Flask,
    jsonify,
    make_response,
    redirect,
    render_template,
    request,
    url_for,
)
from MondayAPI import fetch_items

app = Flask(__name__)

BOARD_ID = 1496686926


def verificar_credenciales(nombre_usuario, password):
    for usuario in fetch_items(BOARD_ID):
        if usuario["name"] == nombre_usuario and usuario["Contraseña"] == password:
            return True
    return False


@app.route("/login", methods=["POST"])
def login():
    nombre_usuario = request.form["nombre_usuario"]
    password = request.form["password"]

    print("el usuario recibido del form es: " + str(nombre_usuario))

    if verificar_credenciales(nombre_usuario, password):
        # Credenciales válidas, crear una cookie de usuario autenticado y redirigir a la página principal
        respuesta = make_response(redirect(url_for("index")))
        respuesta.set_cookie("usuario_autenticado", nombre_usuario)
        return respuesta
    else:
        # Credenciales inválidas, devolver un mensaje de error
        return jsonify({"error": "Nombre de usuario o contraseña incorrectos"}), 401


@app.route("/")
def index():
    if "usuario_autenticado" in request.cookies:
        # El usuario está autenticado, mostrar los datos de los usuarios
        user_data = fetch_items(BOARD_ID)

        return render_template("index.html", users=user_data)
    else:
        # El usuario no está autenticado, redirigir al formulario de inicio de sesión
        return redirect(url_for("login_form"))


@app.route("/login_form")
def login_form():
    return render_template("login.html")


if __name__ == "__main__":
    app.run(debug=True)
