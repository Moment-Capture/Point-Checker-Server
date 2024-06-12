from flask import Flask, request, redirect, url_for

import os
import time
import json
import shutil
import datetime
import pandas as pd

from pathlib import Path
from natsort import os_sorted

from main import pointchecker
from qna import categorize_qna
from mul import detect_multiple
from sub import detect_subjective
from path import *
from utils import *

app = Flask(__name__)

ALLOWED_FILE_EXTENSIONS = set(['pdf', 'png', 'jpg', 'jpeg'])


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_FILE_EXTENSIONS


@app.route("/")
def hello():
    return f'Hello World!'


@app.route("/upload", methods=["POST"])
def upload_files():
    ## upload 폴더 생성 ##
    makeFolder(UPLOAD_FOLDER)

    if request.method == "POST":
        files = request.files
        datas = request.form
        data = datas.get("data")
        data = json.loads(data)

        client_id = data["client_id"]
        id_path = UPLOAD_FOLDER + "/" + client_id

        ## id 폴더 생성 ##
        makeIdFolder(id_path)

        pdf = files["pdf"]
        pdf_name = pdf.filename
        pdf_path = os.path.join(id_path, pdf_name)
        if pdf and allowed_file(pdf_name):
            pdf.save(pdf_path)

        test_name = data["test_name"]
        copy_num = data["copy_num"]
        total_qna_num = data["total_qna_num"]
        testee_num = data["testee_num"]
        test_category = data["test_category"]
        
        print()
        print(client_id)
        print(id_path)
        print("파일 업로드 성공")
        print()

    return redirect(url_for("plural_check",
                            client_id=client_id, 
                            test_name=test_name,
                            copy_num=copy_num,
                            total_qna_num=total_qna_num,
                            testee_num=testee_num,
                            test_category=test_category))
     

# 다인용
@app.route("/plural", methods=["GET"])
def plural_check():
    client_id = request.args.get("client_id", type=str)
    test_name = request.args.get("test_name", type=int)
    copy_num = request.args.get("copy_num", type=int)
    total_qna_num = request.args.get("total_qna_num", type=int)
    testee_num = request.args.get("testee_num", type=int)
    test_category = request.args.getlist("test_category")

    id_path = UPLOAD_FOLDER + "/" + client_id

    start = time.time()
    df = pd.DataFrame()
    df = pointchecker(id_path, test_name, copy_num, total_qna_num, testee_num, test_category)
    end = time.time()
    point_eta = end - start

    print()
    printFull(df.set_index(keys=["testee_id", "file"], drop=True))
    print()
    print("point_eta: " + f"{point_eta:.2f} sec")
    print()
    
    if len(df) == 0:
        return "Error Occured", 200
    
    json_data = df.to_json(orient="records")
    
    return json_data, 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)