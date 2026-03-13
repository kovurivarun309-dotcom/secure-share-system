from flask import Flask, render_template, request
import uuid
import os
from crypto_utils import hash_password

app = Flask(__name__)

# Temporary memory storage
data_store = {}

# Home Page
@app.route("/")
def home():
    return render_template("index.html")


# Process message + password
@app.route("/process", methods=["POST"])
def process():

    message = request.form.get("message")
    password = request.form.get("password")

    # If fields are empty reload page
    if not message or not password:
        return render_template("index.html")

    # Hash the password
    hashed = hash_password(password)

    # Generate unique token
    token = str(uuid.uuid4())[:8]

    # Store encrypted data
    data_store[token] = {
        "message": message,
        "password": hashed
    }

    # Generate secure link
    link = f"/access/{token}"

    return render_template("processing.html", link=link)


# Access secure message
@app.route("/access/<token>", methods=["GET", "POST"])
def access(token):

    # If token doesn't exist
    if token not in data_store:
        return render_template("expired.html")

    # When user submits password
    if request.method == "POST":

        password = request.form.get("password")
        hashed = hash_password(password)

        # Check password
        if hashed == data_store[token]["password"]:

            message = data_store[token]["message"]

            # Delete after viewing (one-time view)
            del data_store[token]

            return render_template("view.html", message=message)

    return render_template("access.html")


# Run server
if __name__ == "__main__":

    # Render or hosting platforms provide PORT
    port = int(os.environ.get("PORT", 5000))

    app.run(host="0.0.0.0", port=port, debug=True)