from flask import Flask, render_template, request, send_from_directory
import uuid
import os
from crypto_utils import hash_password

app = Flask(__name__)

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

data_store = {}

# Home page
@app.route("/")
def home():
    return render_template("index.html")


# Process sharing request
@app.route("/process", methods=["POST"])
def process():

    message = request.form.get("message")
    password = request.form.get("password")
    share_type = request.form.get("type")

    file = request.files.get("file")

    if not password:
        return render_template("index.html")

    hashed = hash_password(password)

    token = str(uuid.uuid4())[:8]

    filename = None

    if file and file.filename != "":
        filename = token + "_" + file.filename
        file_path = os.path.join(UPLOAD_FOLDER, filename)
        file.save(file_path)

    data_store[token] = {
        "message": message,
        "password": hashed,
        "file": filename,
        "type": share_type
    }

    link = f"/access/{token}"

    return render_template("processing.html", link=link)


# Access shared content
@app.route("/access/<token>", methods=["GET", "POST"])
def access(token):

    if token not in data_store:
        return render_template("expired.html")

    data = data_store[token]

    if request.method == "POST":

        password = request.form.get("password")
        hashed = hash_password(password)

        if hashed == data["password"]:

            message = data["message"]
            file = data["file"]
            share_type = data["type"]

            # One-time access
            del data_store[token]

            return render_template(
                "view.html",
                message=message,
                file=file,
                type=share_type
            )

    return render_template("access.html")


# View uploaded files (not download)
@app.route("/uploads/<filename>")
def uploaded_file(filename):
    return send_from_directory("uploads", filename, as_attachment=False)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)