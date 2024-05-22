import json
import requests

import pandas as pd

from path import *


### 서버 연결하는 함수 ###
def server_connect(pdf_path, test_name, copy_num, total_qna_num, testee_num, test_category):
    global df
    global json_data
    
    url = "http://13.125.91.116:8080/upload"

    data = {
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

    response = requests.post(url, files=files)
    json_data = json.loads(response.text)
    json_path = OUTPUT_PATH / "data.json"

    with open(json_path, 'w') as f:
        json.dump(json_data, f)
    
    df = pd.json_normalize(json_data)
    df.drop(columns=["file"], inplace=True)
    df.set_index(["testee_id", "num"], inplace=True)
    print(df)