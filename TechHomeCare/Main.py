from flask import (
    Flask,
    jsonify,
    make_response,
    redirect,
    render_template,
    request,
    url_for,
    json,
)
from MondayAPI import fetch_items, update_user_subscription, send_sms

app = Flask(__name__)

BOARD_ID = 1510653193


def verificar_credenciales(nombre_usuario, password):
    for usuario in fetch_items(BOARD_ID):
        if usuario["name"] == nombre_usuario and usuario["Contraseña"] == password:
            return usuario
    return None


@app.route("/login", methods=["POST"])
def login():
    nombre_usuario = request.form["nombre_usuario"]
    password = request.form["password"]

    print("el usuario recibido del form es: " + str(nombre_usuario))

    user_data = verificar_credenciales(nombre_usuario, password)
    if user_data:
        # Credenciales válidas, crear una cookie de usuario autenticado y redirigir a la página principal
        respuesta = make_response(redirect(url_for("index")))
        max_age = 1800 # seconds -> 30min
        respuesta.set_cookie("usuario_autenticado", nombre_usuario, max_age=max_age)
        respuesta.set_cookie("user_data", json.dumps(user_data), max_age=max_age)
        return respuesta
    else:
        # Credenciales inválidas, devolver un mensaje de error
        return jsonify({"error": "Nombre de usuario o contraseña incorrectos"}), 401


@app.route("/")
def index():
    if "usuario_autenticado" in request.cookies:
        # El usuario está autenticado, mostrar los datos del usuario autenticado
        user_data = json.loads(request.cookies.get("user_data", "{}"))

        return render_template(
            "index.html", users=[user_data]
        )  # Pass user data as a list
    else:
        # El usuario no está autenticado, redirigir al formulario de inicio de sesión
        return redirect(url_for("login_form"))


@app.route("/login_form")
def login_form():
    return render_template("login.html")


@app.route("/toggle_subscription", methods=["POST"])
def toggle_subscription():
    user_id = request.form["user_id"]
    action = request.form["action"]

    # Fetch user data from the cookie
    user_data = json.loads(request.cookies.get("user_data", "{}"))

    if user_data["id"] != user_id:
        return jsonify({"error": "User ID mismatch"}), 404

    new_status = "Alta" if action == "subscribe" else "Baja"
    phone_number = user_data["Telefono"]
    user_name = user_data["name"]
    message = (
        f"Hola, {user_name}:\n\n"
        f"El estado de tu sucripción ha sido modificado a '{new_status}'.\n\n"
        f"Gracias por elegir TechHome Care.\n"
        f"Besitos en el clito,\n"
        f"TechHome Care"
    )

    # Update subscription status in Monday.com
    update_response = update_user_subscription(BOARD_ID, user_id, new_status)

    if "errors" in update_response:
        return jsonify({"error": "Failed to update subscription status"}), 500

    # Send SMS
    send_sms(phone_number, message)

    #Fetch updated user data
    updated_user_data = next((user for user in fetch_items(BOARD_ID) if user["id"] == user_id), None)

    if not updated_user_data:
        return jsonify({"error": "Failed to fetch updated user data"}), 500

    # Update the cookie with the new data
    respuesta = make_response(jsonify({"message": "Subscription status updated and SMS sent"}))
    max_age = 1800  # seconds -> 30min
    respuesta.set_cookie("user_data", json.dumps(updated_user_data), max_age=max_age)


    return respuesta


if __name__ == "__main__":
    app.run(debug=True)
