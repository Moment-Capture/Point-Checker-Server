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
    # id 생성 규칙 - 클라이언트 ip + 접속시간
    id = getId()
    return f'Hello World! <br><br> id : {id}'

@app.route("/id/<id>", methods=["GET"])
def get_json(client_id):
    id_path = UPLOAD_FOLDER + "/" + client_id
    json_path = id_path + "/" + "data.json"

    with open(json_path) as f:
        json_data = load(f)

    return json_data, 200


@app.route("/upload", methods=["POST"])
def upload_files():
    ## upload 폴더 생성 ##
    try:
        if not os.path.exists(UPLOAD_FOLDER):
            os.mkdir(UPLOAD_FOLDER)
    except:
        pass
    ## upload 폴더 생성 ##

    if request.method == "POST":
        files = request.files
        datas = request.form
        data = datas.get("data")
        data = json.loads(data)

        client_id = data["client_id"]
        id_path = UPLOAD_FOLDER + "/" + client_id

        print(client_id)
        print(id_path)

        ## id 폴더 생성 ##
        try:
            if not os.path.exists(id_path):
                os.mkdir(id_path)
        except:
            pass
        ## id 폴더 생성 ##

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
        
        print("파일 업로드 성공")

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
    print(df.set_index(keys=["testee_id", "file"], drop=True))
    print()
    print("point_eta: " + f"{point_eta:.2f} sec")
    
    if len(df) == 0:
        return "Error Occured", 200
    
    json_data = df.to_json(orient="records")
    json_path = id_path + "/" + "data.json"

    with open(json_path, 'w') as f:
        json.dump(json_data, f)
    
    return json_data, 200


# 1인용
@app.route("/single")
def single_check():
    id = request.args.get("id", type=str)
    id_path = UPLOAD_FOLDER + "/" + id
    mul_path = id_path + "/mul"
    sub_path = id_path + "/sub"

    ## 결과 저장 폴더 생성 ##
    makeFolder(id_path)
    makeFolder(mul_path)
    makeFolder(sub_path)
    ## 결과 저장 폴더 생성 ##

    print_intro()

    original_pdf_file_path_list = []
    original_pdf_file_path_list = os_sorted(Path(id_path).glob('*.pdf'))
    convertPdfToJpg(original_pdf_file_path_list, id_path)
    
    df = pd.DataFrame()
    mul_df = pd.DataFrame()
    sub_df = pd.DataFrame()

    final_df = pd.DataFrame(columns=["testee_id", "file", "num", "testee_answer", "correct_answer"])

    start = time.time()
    categorize_qna(id_path)
    end = time.time()
    qna_eta = end - start
    
    start = time.time()
    mul_df = detect_multiple(id_path)
    mul_df.sort_values(by=["num"], inplace=True)
    end = time.time()
    mul_eta = end - start
    print()
    print_full(mul_df)
    
    start = time.time()
    sub_df = detect_subjective(id_path)
    sub_df.sort_values(by=["num"], inplace=True)
    end = time.time()
    sub_eta = end - start
    print()
    print_full(sub_df)

    df = pd.concat([mul_df, sub_df], axis=0, ignore_index=True)
    df.sort_values(by=["num"], inplace=True)
    final_df = dfToFinalDf(df)
    print()
    print_full(final_df)

    final_df.to_excel(excel_writer=id_path+"/df.xlsx")

    print("qna_eta: " + f"{qna_eta:.2f} sec")
    print("mul_eta: " + f"{mul_eta:.2f} sec")
    print("sub_eta: " + f"{sub_eta:.2f} sec")

    print_outro()

    json_data = final_df.to_json(orient="records")
    return json_data, 200


# mul_test
@app.route("/mul_test")
def mul_check():
    id = request.args.get("id", type=str)
    id_path = UPLOAD_FOLDER + "/" + id
    mul_path = id_path + "/mul"

    ## 결과 저장 폴더 생성 ##
    makeFolder(id_path)
    makeFolder(mul_path)
    ## 결과 저장 폴더 생성 ##

    print_intro()

    original_pdf_file_path_list = []
    original_pdf_file_path_list = os_sorted(Path(id_path).glob('*.pdf'))
    convertPdfToJpg(original_pdf_file_path_list, id_path)
    
    df = pd.DataFrame()
    mul_df = pd.DataFrame()

    final_df = pd.DataFrame(columns=["testee_id", "file", "num", "testee_answer", "correct_answer"])

    start = time.time()
    categorize_qna(id_path)
    end = time.time()
    
    print("\ncategorize_qna eta: " + f"{end - start:.2f} sec")
    
    mul_df = detect_multiple(id_path)
    mul_df.sort_values(by=["num"], inplace=True)
    print()
    print_full(mul_df)

    df = mul_df
    df.sort_values(by=["num"], inplace=True)
    print()
    print_full(df)

    final_df = dfToFinalDf(df)
    print()
    print_full(df)

    final_df.to_excel(excel_writer=id_path+"/df.xlsx")

    print_outro()

    json_data = final_df.to_json(orient="records")
    return json_data, 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)