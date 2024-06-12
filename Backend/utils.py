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
def printIntro():
    print()
    print("========================")
    print("환영합니다.")
    print()
    print("해당 프로그램은 포인트체커의 프로토 타입으로, 데모를 위해 설계되었습니다.")
    print("========================")
    print()


# 아웃트로 출력
def printOutro():
    print()
    print("========================")
    print("감사합니다.")
    print("========================")
    print()


# 모든 df cmd로 출력
def printFull(df):
    pd.set_option('display.max_rows', len(df))
    print(df)
    pd.reset_option('display.max_rows')
    return


# 값 확인
def printVal(val_name, val_data):
    print()
    print(str(val_name) + ": ")
    print(str(val_data))
    print()


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


# 만약 testee_df['num']에 빈 곳이 하나 있으면 없는 번호로 채우기
def fillOneDf(testee_df):
    if (testee_df["num"] == -1).sum() == 1:
        missing_idx = testee_df[testee_df["num"] == -1].index[0]
        existing_numbers = testee_df["num"][testee_df["num"] != -1].tolist()
        existing_numbers = list(map(int, existing_numbers))

        new_number = 1
        while new_number in existing_numbers:
            new_number += 1
            
        testee_df.at[missing_idx, "num"] = new_number
    
    return testee_df


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
    mul_path = testee_path + "/" + "mul"
    sub_path = testee_path + "/" + "sub"
        
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
    jpg_path = id_path + "/" + "jpg"
    temp_path = id_path + "/" + "temp"

    ## 결과 저장 폴더 생성 ##
    # 해당 id의 폴더 생성
    makeFolder(id_path)

    # 해당 id 밑의 jpg 폴더 생성
    makeFolder(jpg_path)

    # 해당 id 밑의 temp 폴더 생성
    makeFolder(temp_path)


# 이미지 전처리
def preprocess_image(img):
    # 대비 조정
    img = cv2.convertScaleAbs(img, alpha=0.9, beta=0)
    
    return img


# 답안 이미지 전처리
def preprocess_image_answer(img):
    # 대비 조정
    img = cv2.convertScaleAbs(img, alpha=0.9, beta=0)
    
    # upscale & blur
    scale_factor = 2
    upscaled = cv2.resize(img, None, fx=scale_factor, fy=scale_factor, interpolation=cv2.INTER_LINEAR)
    blur = cv2.blur(upscaled, (5, 5))

    img = blur
    
    return img


# ocr_text에서 숫자만 추출
def getNumText(ocr_text):
    text = ""
    for txt in ocr_text:
        for t in txt:
            if (t.isdigit()):
                text += t
            elif (t == 'l' or t == 'i' or t == 'I' or t == '|' or t == '/' or t == ')'):
                text += '1'
            elif (t == '그'):
                text += '2'
            elif (t == 'b'):
                text += '6'
            elif (t == 'o'):
                text += '8'
            elif (t == 'q'):
                text += '9'
    return text


# 문항 번호 반환 - EasyOCR
def getNumEasy(img, reader):
    num = -1
    img = preprocess_image(img)
    ocr_text = reader.readtext(img, detail=0)
    text = getNumText(ocr_text)
    
    if text:
        num = int(text)
    
    return num


# 문항 번호 반환 - OCR Tamil
def getNumTamil(img):
    num = -1
    img = preprocess_image(img)
    ocr_text = OCR().predict(img)
    text = getNumText(ocr_text)
    
    if text:
        num = int(text)
    
    return num


def checkNum(num, total_num, num_list):
    if num in num_list:
        num = -1
    if num > total_num:
        num = -1
    
    return num


# qna_num 반환
def getQnaNum(num_list, img, total_qna_num, reader):
    total_num = int(total_qna_num)
    qna_num = -1
    num = getNumTamil(img)
    num = checkNum(num, total_num, num_list)
    
    if num == -1:
        num = getNumEasy(img, reader)
        num = checkNum(num, total_num, num_list)
    
    qna_num = num

    if qna_num != -1:
        num_list.append(qna_num)
    
    return qna_num


# 문항 번호 반환 - EasyOCR
def getTextEasy(img, reader):
    text = ""
    img = preprocess_image(img)
    ocr_text = reader.readtext(img, detail=0)
    text = getNumText(ocr_text)

    # print()
    # print("easy")
    # print(ocr_text)
    
    return text


# 문항 번호 반환 - OCR Tamil
def getTextTamil(img):
    text = ""
    img = preprocess_image(img)
    ocr_text = OCR().predict(img)
    text = getNumText(ocr_text)

    # print()
    # print("tamil")
    # print(ocr_text)
    
    return text


# 문항 번호 반환 - EasyOCR
def getAnswerEasy(img, reader):
    text = ""
    img = preprocess_image_answer(img)
    ocr_text = reader.readtext(img, detail=0)
    text = getNumText(ocr_text)
    
    return text


# 문항 번호 반환 - OCR Tamil
def getAnswerTamil(img):
    text = ""
    img = preprocess_image_answer(img)
    ocr_text = OCR().predict(img)
    text = getNumText(ocr_text)
    
    return text


# 단답 답안 반환
def getAnswer(img, reader):
    text = getAnswerTamil(img)

    if not text:
        text = getAnswerEasy(img, reader)

    return text 


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
