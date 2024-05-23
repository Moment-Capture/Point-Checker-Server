import os
import sys
import easyocr

import numpy as np

from PIL import Image

from utils import getNumText
from utils import *

sys.path.append(os.path.dirname(os.getcwd() + "/models/tamil_ocr/ocr_tamil"))
from ocr_tamil.ocr import OCR


### 텍스트 부분 잘라내기 함수 ###

# 각 jpg에 적힌 코드 인식해서 이름 매칭
# testee jpg df 생성
# - testee_jpg_df = pd.DataFrame(columns=["file", "testee_id", "page"])
# - name은 page가 1일 때만 인식 (학생 이름은 각 시험지 첫 장에만 적혀 있기 때문임)
# 식별코드: testee_id - page (ex. 3-2라면, testee_id=3, page=2)

### 오른쪽 상단 testee_name 인식 함수 ###
def readTesteeName(img, reader):
  x1, y1, x2, y2 = (610, 30, 750, 90)
  cropped_img = img.crop((x1, y1, x2, y2))
  image_np = np.array(cropped_img)
  
  # tamilocr 사용
  text = ""
  ocr_text = OCR().predict(image_np)
  text = getNumText(ocr_text)

  return text


### 텍스트에서 testee_id와 page를 추출하는 함수 ###
def extractTesteeId(text):
    if text:
        text_split = text[0].split('-')
        testee_id = text_split[0].strip()
        page = text_split[1].strip() if len(text_split) > 1 else None
        return testee_id, page
    else:
        return "", ""


### testee_jpg_df에 id_match 추가
def testeeIdJpgDf(df, testee_jpg_df, id_match):
    # df = pd.DataFrame(columns=["index_id", "testee_id", "testee_name", "file", "page"])
    for testee_jpg_df_idx, testee_jpg_df_row in testee_jpg_df.iterrows():
        index_id = testee_jpg_df_row["index_id"]
        testee_id = testee_jpg_df_row["testee_id"]
        testee_name = id_match.loc[index_id, "testee_name"]
        file = testee_jpg_df_row["file"]
        page = testee_jpg_df_row["page"]
        df.loc[len(df)] = [index_id, testee_id, testee_name, file, page]

    return df  


### 텍스트 부분 잘라내기 함수 (메인) ###
def testeeCodeRecognition(jpg_file_path_list, testee_jpg_df):
    # easyOCR 사용
    reader = easyocr.Reader(['ko', 'en'])
    
    # id_match 딕셔너리 초기화
    id_match = pd.DataFrame(columns=["testee_id", "testee_name"])

    # index_id
    index_id = 0

    # 폴더 내의 모든 파일에 대해 반복
    for file in jpg_file_path_list:
        # 이미지 파일 열기
        img = Image.open(file)
        img = img.resize((794,1123), Image.LANCZOS) # 인식 위치를 같게 만들기 위한 이미지 규격화.

        # 왼쪽 상단 num_id와 page 인식
        x1, y1, x2, y2 = (35, 35, 160, 90)
        cropped_img = img.crop((x1, y1, x2, y2))
        image_np = np.array(cropped_img)

        # easyOCR 사용
        text = reader.readtext(image_np, detail=0)
        testee_id, page = extractTesteeId(text)

        #오른쪽 상단 testee_name 인식
        # page가 1인 경우 testee_id와 testee_name를 id_match에 딕셔너리로 추가
        if page == "1":
            testee_name = readTesteeName(img, reader)
            id_match.loc[len(id_match)] = [testee_id, testee_name]
            index_id += 1

        testee_jpg_df.loc[len(testee_jpg_df)] = [index_id, file, testee_id, page]

    id_match.index += 1

    return testee_jpg_df, id_match
