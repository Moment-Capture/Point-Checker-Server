from flask import Flask, request, redirect, url_for

import os
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
from utils import *

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
    # id 생성 규칙 - 클라이언트 ip + 접속시간
    id = getId()
    return f'Hello World! <br><br> id : {id}'


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
        # id 생성 규칙 - 클라이언트 ip + 접속시간
        id_ = getId()
        id_path = UPLOAD_FOLDER + "/" + id_
        
        ## id 폴더 생성 ##
        try:
            if not os.path.exists(id_path):
                os.mkdir(id_path)
        except:
            pass
        ## id 폴더 생성 ##

        files = request.files

        pdf = files["pdf"]
        pdf_name = pdf.filename
        pdf_path = os.path.join(id_path, pdf_name)
        if pdf and allowed_file(pdf_name):
            pdf.save(pdf_path)
        
        answer = files["answer"]
        answer_name = answer.filename
        answer_path = os.path.join(id_path, answer_name)
        if answer and allowed_answer(answer_name):
            answer.save(answer_path)

        datas = request.form

        data = datas.get("data")
        data = json.loads(data)

        test_name_ = data["test_name"]
        copy_num_ = data["copy_num"]
        total_qna_num_ = data["total_qna_num"]
        testee_num_ = data["testee_num"]
        test_category_ = data["test_category"]
        
        print("파일 업로드 성공")
    
    # if copy_num == 1:
    #     return redirect(url_for("single_check",
    #                             id=id,
    #                             test_name=test_name,
    #                             copy_num=copy_num,
    #                             total_qna_num=total_qna_num,
    #                             testee_num=testee_num,
    #                             test_category=test_category))
    
    # else: 
    #     return redirect(url_for("plural_check",
    #                             id=id,
    #                             test_name=test_name,
    #                             copy_num=copy_num,
    #                             total_qna_num=total_qna_num,
    #                             testee_num=testee_num,
    #                             test_category=test_category))

    return redirect(url_for("plural_check",
                            id=id_,
                            test_name=test_name_,
                            copy_num=copy_num_,
                            total_qna_num=total_qna_num_,
                            testee_num=testee_num_,
                            test_category=test_category_))
        

# 다인용
@app.route("/plural")
def plural_check(id, test_name, copy_num, total_qna_num, testee_num, test_category):
    id_path = UPLOAD_FOLDER + "/" + id

    df = pd.DataFrame()
    df = pointchecker(id_path, test_name, copy_num, total_qna_num, testee_num, test_category)
    if len(df) == 0:
        return "Error Occured", 200
    json_data = df.to_json(orient="records")
    return json_data, 200


# 1인용
@app.route("/single")
def single_check(id, test_name, copy_num, total_qna_num, testee_num, test_category):
    id_path = UPLOAD_FOLDER + "/" + id
    jpg_path = id_path + "/jpg"
    temp_path = id_path + "/temp"
    mul_path = temp_path + "/mul"
    sub_path = temp_path + "/sub"

    ## 결과 저장 폴더 생성 ##
    makeFolder(id_path)
    makeFolder(jpg_path)
    
    try:
        if (os.path.exists(temp_path)):
            shutil.rmtree(temp_path)
        os.mkdir(temp_path)
    except:
        pass

    makeFolder(mul_path)
    makeFolder(sub_path)
    ## 결과 저장 폴더 생성 ##

    print_intro()

    answer_file_path_list = []
    answer_file_path_list = os_sorted(Path(id_path).glob('*.xlsx'))
    answer_df = convertExcelToDf(answer_file_path_list, id_path)

    original_pdf_file_path_list = []
    original_pdf_file_path_list = os_sorted(Path(id_path).glob('*.pdf'))
    convertPdfToJpg(original_pdf_file_path_list, jpg_path)
    
    df = pd.DataFrame()
    mul_df = pd.DataFrame()
    sub_df = pd.DataFrame()
    answer_df = pd.DataFrame()
    final_df = pd.DataFrame()

    categorize_qna(id_path)
    
    mul_df = detect_multiple(id_path)
    mul_df.sort_values(by=["num"], inplace=True)
    print()
    print_full(mul_df)
    
    sub_df = detect_subjective(id_path)
    sub_df.sort_values(by=["num"], inplace=True)
    print()
    print_full(sub_df)

    df = pd.concat([mul_df, sub_df], axis=0)
    df.sort_values(by=["num"], inplace=True)
    print()
    print_full(df)

    answer_df = convertExcelToDf(answer_file_path_list, id_path)
    final_df = concatAnswer(df, answer_df)
    print()
    print_full(final_df)

    final_df.to_excel(excel_writer=id_path+"/df.xlsx")

    print_outro()

    json_data = final_df.to_json(orient="records")
    return json_data, 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)