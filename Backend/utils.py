import os
import sys
import shutil
import easyocr
import datetime

import numpy as np
import pandas as pd

from pathlib import Path
from natsort import os_sorted
from flask import request

from pdf2image import convert_from_path
from PIL import Image

sys.path.append(os.path.dirname(os.getcwd() + "/models/tamil_ocr/ocr_tamil"))
from ocr_tamil.ocr import OCR


# 인트로 출력
def print_intro():
    print()
    print("========================")
    print("환영합니다.")
    print()
    print("해당 프로그램은 포인트체커의 프로토 타입으로, 데모를 위해 설계되었습니다.")
    print("========================")
    print()


# 아웃트로 출력
def print_outro():
    print()
    print("========================")
    print("감사합니다.")
    print("========================")
    print()


# 모든 df cmd로 출력
def print_full(df):
    pd.set_option('display.max_rows', len(df))
    print(df)
    pd.reset_option('display.max_rows')
    return


# 이미지와 박스 영역을 주면 박스 영역 추출
def cropBox(box, img):
    obj = img[int(box[1]):int(box[3]), int(box[0]):int(box[2])]
    return obj


# 겹치는 영역 계산
# bb_intersection_over_union(boxA, boxB)
# https://gist.github.com/meyerjo/dd3533edc97c81258898f60d8978eddc
def compute_intersect_size(boxA, boxB):
    if len(boxA) == 0 or len(boxB) == 0:
        return 0
    
    xA = max(boxA[0], boxB[0])
    yA = max(boxA[1], boxB[1])
    xB = min(boxA[2], boxB[2])
    yB = min(boxA[3], boxB[3])

    # compute the area of intersection rectangle
    interArea = abs(max((xB - xA, 0)) * max((yB - yA), 0))
    if interArea == 0:
        return 0
    # compute the area of both the prediction and ground-truth
    # rectangles
    boxAArea = abs((boxA[2] - boxA[0]) * (boxA[3] - boxA[1]))
    boxBArea = abs((boxB[2] - boxB[0]) * (boxB[3] - boxB[1]))

    # compute the intersection over union by taking the intersection
    # area and dividing it by the sum of prediction + ground-truth
    # areas - the interesection area
    iou = interArea / float(boxAArea + boxBArea - interArea)

    # return the intersection over union value
    return iou


# 두 이미지를 이어 붙임
def concatImage(crop_obj, searching_obj):
    max_width = 0
    total_height = crop_obj.shape[0] + searching_obj.shape[0]
    if (crop_obj.shape[1] > searching_obj.shape[1]):
        max_width = crop_obj.shape[1]
    else:
        max_width = searching_obj.shape[1]

    final_obj = np.zeros((total_height, max_width, 3), dtype=np.uint8)
    final_obj.fill(255)
    current_y = 0

    final_obj[current_y:crop_obj.shape[0]+current_y,:crop_obj.shape[1],:] = crop_obj
    current_y += crop_obj.shape[0]

    final_obj[current_y:searching_obj.shape[0]+current_y,:searching_obj.shape[1],:] = searching_obj
    current_y += searching_obj.shape[0]

    return final_obj


# jpg로 변환
def convertPdfToJpg(file_path_list, path):
    file_path = ""

    if file_path_list is None:
        print("pdf is not found")
        return None
    else:
        for file in file_path_list:
            file_path = file
            break
    
    file_name = os.path.basename(file_path)
    pages = convert_from_path(file_path)

    for i, page in enumerate(pages):
        page.save(path + "/" + file_name + "_" + str(i) + ".jpg", "JPEG")


# df으로 변환
def convertExcelToDf(file_path_list, path):
    file_path = path
    df = pd.DataFrame()

    if len(file_path_list) == 0:
        print("excel not found")
        return None
    else:
        for file in file_path_list:
            file_path = file
            break
    
    df = pd.read_excel(file_path, names=["num", "correct_answer"] ,engine='openpyxl')
    return df


# df와 answer_df 합치기
def concatAnswer(df, answer_df):
    for df_idx, df_row in df.iterrows():
        df_num = df_row["num"]
        if df_num == 0:
            continue
        for ans_idx, ans_row in answer_df.iterrows():
            if (int(ans_row["correct_answer"]) == int(df_num)):
                df.loc[df_idx, "correct_answer"] = ans_row["correct_answer"]
                break
    
    return df


# df에 testee df 합치기
def concatTesteeDf(df, testee_id, testee_df):
    for testee_df_idx, testee_df_row in testee_df.iterrows():
        file = testee_df_row["file"]
        num = testee_df_row["num"]
        testee_answer = testee_df_row["testee_answer"]
        correct_answer = testee_df_row["correct_answer"]
        df.loc[len(df)] = [testee_id, file, num, testee_answer, correct_answer]
  
    return df


#df를 최종 출력 형태로 변환
def dfToFinalDf(df):
    final_df = pd.DataFrame()
    # final_df = df[df.testee_answer != 0]
    final_df = df
    # final_df = final_df.drop(["file"], axis=1)
    # final_df = final_df[final_df.correct_answer != 0]
    final_df = final_df.set_index(keys=["num"], drop=True)
    final_df = final_df.sort_index(ascending=True)
    final_df = final_df.reset_index(drop=False)
    return final_df


# 입력 받은 label을 int로 변환
def labelToInt(label):
    if label == "check1":
        return 1
    elif label == "check2":
        return 2
    elif label == "check3":
        return 3
    elif label == "check4":
        return 4
    elif label == "check5":
        return 5
    else:
        return 0


# 중복 파일들 제거
def deleteDuplicateFiles(path, images):
    for file in Path(path).glob('*).jpg'):
        images.remove(file)


# 폴더 생성
def makeFolder(path):
    ## 폴더 생성 ##
    try:
        if not (os.path.exists(path)):
            os.mkdir(path)
    except:
        pass


# 폴더 삭제
def deleteFolder(path):
    try:
        if (os.path.exists(path)):
            shutil.rmtree(path)
    except:
        pass


# 응시자 폴더 생성
def makeTesteeFolder(testee_path):
    mul_path = testee_path + "/mul"
    sub_path = testee_path + "/sub"
        
    ## temp 하위 폴더 생성 ##
    # 해당 tester의 폴더 생성
    makeFolder(testee_path)

    # 해당 tester 폴더 밑의 mul 폴더 생성
    makeFolder(mul_path)

    # 해당 tester 폴더 밑의 sub 폴더 생성
    makeFolder(sub_path)


# id 폴더 생성
def makeIdFolder(upload_path):
    id_path = str(Path(upload_path))
    jpg_path = id_path + "/jpg"
    temp_path = id_path + "/temp"

    ## 결과 저장 폴더 생성 ##
    # 해당 id의 폴더 생성
    makeFolder(id_path)

    # 해당 id 밑의 jpg 폴더 생성
    makeFolder(jpg_path)

    # 해당 id 밑의 temp 폴더 생성
    makeFolder(temp_path)


# id 생성
def getId():
    client_ip = request.environ.get('HTTP_X_REAL_IP', request.remote_addr)
    access_now = datetime.datetime.now()
    access_date = access_now.strftime("%Y-%m-%d")
    access_time = access_now.strftime("%H-%M-%S")
    id = client_ip + "_" + access_date + "_" + access_time
    return id


def getText(ocr_text):
    text = ""
    for txt in ocr_text:
        for t in txt:
            if (t.isdigit()):
                text += t
            elif (t == 'l' or t == 'i' or t == 'I' or t == '|' or t == '/'):
                text += '1'
    return text


### 텍스트 부분 잘라내기 함수 ###

# 각 jpg에 적힌 코드 인식해서 이름 매칭
# testee jpg df 생성
# - testee_jpg_df = pd.DataFrame(columns=["file", "testee_id", "page"])
# - name은 page가 1일 때만 인식 (학생 이름은 각 시험지 첫 장에만 적혀 있기 때문임)
# 식별코드: testee_id - page (ex. 3-2라면, testee_id=3, page=2)

### 오른쪽 상단 testee_name 인식 함수 ###
def readTesteeName(img, reader):
  x1, y1, x2, y2 = (620, 30, 750, 65)
  cropped_img = img.crop((x1, y1, x2, y2))
  image_np = np.array(cropped_img)
  
  # tamilocr 사용
  text = ""
  ocr_text = OCR().predict(image_np)
  text = getText(ocr_text)
  print(text)

  # id가 있다면 id 반환, 없으면 none 반환
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


### 텍스트 부분 잘라내기 함수 (메인) ###
def testeeCodeRecognition(jpg_file_path_list, testee_jpg_df):
    # easyOCR 사용
    reader = easyocr.Reader(['ko', 'en'])
    
    # id_match 딕셔너리 초기화
    id_match = dict()

    # 폴더 내의 모든 파일에 대해 반복
    for file in jpg_file_path_list:
        # 이미지 파일 열기
        img = Image.open(file)
        img = img.resize((794,1123),Image.LANCZOS) # 인식 위치를 같게 만들기 위한 이미지 규격화.

        # 왼쪽 상단 num_id와 page 인식
        x1, y1, x2, y2 = (30, 30, 165, 70)
        cropped_img = img.crop((x1, y1, x2, y2))
        image_np = np.array(cropped_img)

        # easyOCR 사용
        text = reader.readtext(image_np, detail=0)
        testee_id, page = extractTesteeId(text)

        #오른쪽 상단 testee_name 인식
        # page가 1인 경우 testee_id와 testee_name를 id_match에 딕셔너리로 추가
        if page == "1":
            testee_name = readTesteeName(img, reader)
            id_match[testee_id] = testee_name

        testee_jpg_df.loc[len(testee_jpg_df)] = [file, testee_id, page]

    return testee_jpg_df, id_match

### testee_jpg_df에 사용자 이름 추가
def testeeIdJpgDf(df, testee_jpg_df, id_match):
    # df = pd.DataFrame(columns=["testee_id", "testee_name", "file", "page"])
    for testee_jpg_df_idx, testee_jpg_df_row in testee_jpg_df.iterrows():
        testee_id = testee_jpg_df_row["testee_id"]
        testee_name = id_match[testee_id]
        file = testee_jpg_df_row["file"]
        page = testee_jpg_df_row["page"]
        df.loc[len(df)] = [testee_id, testee_name, file, page]

    return df  
