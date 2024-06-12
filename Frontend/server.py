import re
import json
import requests
import datetime

import tkinter as tk
import public_ip as ip

import global_vars

from path import *

url = "http://13.125.91.116:8080"

def set_global(data):
    global_vars.json_data = data


def getTestName(test_name):
    pattern = r'[^a-zA-Z0-9\s]'
    test_name = re.sub(pattern, '', test_name)
    return test_name


## id 생성 ##
def getId(test_name):
    client_ip = ip.get()
    access_now = datetime.datetime.now()
    access_date = access_now.strftime("%Y-%m-%d")
    access_time = access_now.strftime("%H-%M-%S")
    client_id = client_ip + "_" + access_date + "_" + access_time + "_" + test_name
    return client_id


## 서버 연결하는 함수 ##
def start_connect(pdf_path, test_name, copy_num, total_qna_num, testee_num, test_category, progress_bar):
    global is_scoring_finished
    is_scoring_finished = 0    
    response = post_server(pdf_path, test_name, copy_num, total_qna_num, testee_num, test_category)
    json_data = json.loads(response.text)
    set_global(json_data)
    is_scoring_finished = 1

    finish_connect(json_data, progress_bar)


## 서버에 post하는 함수 ##
def post_server(pdf_path, test_name, copy_num, total_qna_num, testee_num, test_category):
    post_url = url + "/upload"
    test_name = getTestName(test_name)
    client_id = getId()

    data = {
        'client_id':client_id,
        'test_name':test_name,
        'copy_num':copy_num,
        'total_qna_num':total_qna_num,
        'testee_num':testee_num,
        'test_category':test_category
    }

    files = {
        'pdf':open(pdf_path, "rb"),
        'data':(None, json.dumps(data), 'application/json')
    }

    return requests.post(post_url, files=files)


## 채점 종료 ##
def finish_connect(json_data, progress_bar):
    global is_scoring_finished

    if json_data and is_scoring_finished:
        progress_bar.stop()
        progress_bar["value"]=100
        tk.messagebox.showinfo("채점 완료", "채점이 완료되었습니다.\n채점 결과 확인 버튼을 누르세요.")
    else:
        print("채점 진행 중")
        tk.messagebox.showinfo("안내", "채점이 진행 중입니다.")