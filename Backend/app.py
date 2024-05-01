from flask import Flask, request

import os
import pandas as pd

from main import getFinalDf

app = Flask(__name__)

UPLOAD_FOLDER = os.getcwd() + "\\upload"
ALLOWED_EXTENSIONS = set(['pdf', 'png', 'jpg', 'jpeg'])

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS


@app.route("/")
def hello():
    return "Hello, World!"


@app.route("/upload", methods=["POST"])
def upload_pdf():
    if request.method == "POST":
        file = request.files["file"]
        file_name = file.filename
        file_path = os.path.join(UPLOAD_FOLDER, file_name)
        if file and allowed_file(file_name):
            file.save(file_path)

        df = pd.DataFrame()
        df = getFinalDf(UPLOAD_FOLDER)
        json_data = df.to_json(orient="records")
        return json_data
        

@app.route("/demo")
def view_demo():
    df = pd.DataFrame()
    df = getFinalDf()
    json_data = df.to_json(orient="records")
    return json_data


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)