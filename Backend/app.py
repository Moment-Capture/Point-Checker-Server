from flask import Flask, request

import os
import pandas as pd

from main import getFinalDf

from mul import detect_multiple
from sub import detect_subjective
from utils import print_full, print_intro, print_outro

app = Flask(__name__)

CWD_PATH = os.getcwd()

BE_PATH = "/home/ubuntu/Point-Checker/Backend"
UPLOAD_FOLDER = BE_PATH + "/upload"

ALLOWED_FILE_EXTENSIONS = set(['pdf', 'png', 'jpg', 'jpeg'])
ALLOWED_ANSWER_EXTENSIONS = set(['xlsx'])

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_FILE_EXTENSIONS


def allowed_answer(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_ANSWER_EXTENSIONS


@app.route("/")
def hello():
    return "Hello, World!"


@app.route("/upload", methods=["POST"])
def upload_pdf():
    ## upload 폴더 생성 ##
    try:
        if not os.path.exists(UPLOAD_FOLDER):
            os.mkdir(UPLOAD_FOLDER)
    except:
        pass
    ## upload 폴더 생성 ##

    if request.method == "POST":
        files = request.files

        file = files["file"]
        file_name = file.filename
        file_path = os.path.join(UPLOAD_FOLDER, file_name)
        print(file_name)
        print(file_path)
        if file and allowed_file(file_name):
            file.save(file_path)
        
        answer = files["answer"]
        answer_name = answer.filename
        answer_path = os.path.join(UPLOAD_FOLDER, answer_name)
        if answer and allowed_answer(answer_name):
            answer.save(answer_path)
        
        print("파일 업로드 성공")

        df = pd.DataFrame()
        df = getFinalDf(UPLOAD_FOLDER)
        json_data = df.to_json(orient="records")
        return json_data
    
    # return 200
        

@app.route("/demo")
def view_demo():
    df = pd.DataFrame()
    df = getFinalDf(UPLOAD_FOLDER)
    json_data = df.to_json(orient="records")
    return json_data


@app.route("/test")
def view_test():
    print_intro()
    
    mul_df = pd.DataFrame()
    sub_df = pd.DataFrame()

    path = UPLOAD_FOLDER
    
    mul_df = detect_multiple(path)
    print()
    print_full(mul_df)
    
    sub_df = detect_subjective(path)
    print()
    print_full(sub_df)

    df = pd.concat([mul_df, sub_df], axis=0)
    print()
    print_full(df)

    print_outro()

    json_data = df.to_json(orient="records")
    return json_data


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)