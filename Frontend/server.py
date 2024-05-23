import json
import requests
import datetime

import pandas as pd
import public_ip as ip

import global_vars

from path import *

url = "http://13.125.91.116:8080"

def set_global(data):
    global_vars.json_data = data


## id 생성 ##
def getId():
    client_ip = ip.get()
    access_now = datetime.datetime.now()
    access_date = access_now.strftime("%Y-%m-%d")
    access_time = access_now.strftime("%H-%M-%S")
    client_id = client_ip + "_" + access_date + "_" + access_time
    return client_id


## 서버 연결하는 함수 ##
def start_connect(pdf_path, test_name, copy_num, total_qna_num, testee_num, test_category):
    response = post_server(pdf_path, test_name, copy_num, total_qna_num, testee_num, test_category)
    json_data = json.loads(response.text)
    
    df = pd.json_normalize(json_data)
    df.drop(columns=["file"], inplace=True)
    df.set_index(["testee_id", "num"], inplace=True)

    set_global(json_data)

    return True


## 서버에 post하는 함수 ##
def post_server(pdf_path, test_name, copy_num, total_qna_num, testee_num, test_category):
    global client_id

    post_url = url + "/upload"
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