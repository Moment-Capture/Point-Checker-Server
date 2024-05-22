import json
import requests

import pandas as pd

import global_vars

from path import *

url = "http://13.125.91.116:8080"

def set_global(data):
    global_vars.json_data = data


### 서버 연결하는 함수 ###
def start_connect(pdf_path, test_name, copy_num, total_qna_num, testee_num, test_category):
    response = post_server(pdf_path, test_name, copy_num, total_qna_num, testee_num, test_category)
    json_data = json.loads(response.text)
    json_path = OUTPUT_PATH / "data.json"

    with open(json_path, 'w') as f:
        json.dump(json_data, f)
    
    df = pd.json_normalize(json_data)
    df.drop(columns=["file"], inplace=True)
    df.set_index(["testee_id", "num"], inplace=True)

    set_global(json_data)

    return True


### 서버에 post하는 함수 ###
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