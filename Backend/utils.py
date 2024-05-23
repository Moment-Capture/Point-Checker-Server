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
    file_name = ""
    df = pd.DataFrame(columns=["num", "correct_answer"])

    if len(file_path_list) == 0:
        print("excel not found")
        return None
    else:
        for file in file_path_list:
            file_path = file
            file_name = os.path.basename(file_path)
            break
    
    df = pd.read_excel(file_path, names=["num", "correct_answer"], engine='openpyxl')
    # df = pd.read_excel(file_path)
    return df


# df와 answer_df 합치기
def concatAnswer(df, answer_df):
    for df_idx, df_row in df.iterrows():
        df_num = df_row["num"]
        if df_num == 0:
            continue
        for ans_idx, ans_row in answer_df.iterrows():
            ans_num = ans_row["num"]
            if (df_num != "" and int(ans_num) == int(df_num)):
                df.loc[df_idx, "correct_answer"] = ans_row["correct_answer"]
                break
    
    return df


# df에 testee df 합치기
def concatTesteeDf(df, testee_id, testee_df):
    for testee_df_idx, testee_df_row in testee_df.iterrows():
        file = testee_df_row["file"]
        num = testee_df_row["num"]
        testee_answer = testee_df_row["testee_answer"]
        df.loc[len(df)] = [testee_id, file, num, testee_answer]
  
    return df


#df를 최종 출력 형태로 변환
def dfToFinalDf(df):
    final_df = pd.DataFrame()
    final_df = df
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


# ocr_text에서 숫자만 추출
def getNumText(ocr_text):
    text = ""
    for txt in ocr_text:
        for t in txt:
            if (t.isdigit()):
                text += t
            elif (t == 'l' or t == 'i' or t == 'I' or t == '|' or t == '/'):
                text += '1'
            elif (t == 'q'):
                text += '9'
    return text


# 문항 번호 반환 - EasyOCR
def getNumEasy(num, img, reader):
    ocr_text = reader.readtext(img, detail=0)
    text = getNumText(ocr_text)
    
    if text:
        num = int(text)
    else:
        num = getNumTamil(num, img)
    
    # if num == -1:
    #     num = getNumTamil(num, img)
    
    return num


# 문항 번호 반환 - OCR Tamil
def getNumTamil(num, img):
    ocr_text = OCR().predict(img)
    text = getNumText(ocr_text)
    
    if text:
        num = int(text)
    
    return num


# 단답 답안 반환 - OCR Tamil
def getAnswerTamil(answer, img):
    ocr_text = OCR().predict(img)
    text = getNumText(ocr_text)
    
    if text:
        answer = text
    
    # else:
    #     reader = easyocr.Reader(['ko', 'en'])
    #     ocr_text = reader.readtext(img, detail=0)
    #     text = getString(ocr_text)
    #     print("문항 감지 안 됨(text): " + text)
    #     print("문항 감지 안 됨(ocr_text):")
    #     for ocr in ocr_text:
    #         print(ocr)
    
    return answer


# ocr_text에서 문자 전체 추출
def getString(ocr_text):
    text = ""
    for txt in ocr_text:
        for t in txt:
            text += t
    return text


# 감지 안 됨 - OCR Tamil
def getStringTamil(img):
    ocr_text = OCR().predict(img)
    text = getString(ocr_text)
    
    print("문항 감지 안 됨: " + text)
