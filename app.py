from flask import Flask, render_template, request
import uuid
from crypto_utils import hash_password

app = Flask(__name__)

data_store = {}

@app.route("/")
def home():
    return render_template("index.html")


@app.route("/process", methods=["POST"])
def process():

    message = request.form.get("message")
    password = request.form.get("password")

    if not message or not password:
        return render_template("index.html")

    hashed = hash_password(password)

    token = str(uuid.uuid4())[:8]

    data_store[token] = {
        "message": message,
        "password": hashed
    }

    link = f"/access/{token}"

    return render_template("processing.html", link=link)


@app.route("/access/<token>", methods=["GET", "POST"])
def access(token):

    if token not in data_store:
        return render_template("expired.html")

    if request.method == "POST":

        password = request.form.get("password")
        hashed = hash_password(password)

        if hashed == data_store[token]["password"]:

            message = data_store[token]["message"]

            del data_store[token]

            return render_template("view.html", message=message)

    return render_template("access.html")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)