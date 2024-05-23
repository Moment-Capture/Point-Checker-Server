import os
import time
import shutil
import pandas as pd

from pathlib import Path
from natsort import os_sorted

from qna import categorize_qna
from mul import detect_multiple
from sub import detect_subjective

from path import *
from utils import *
from id import *


def getMulDf(testee_path):
    # 경로 정의
    path = testee_path

    # easyocr 사용
    reader = easyocr.Reader(['ko', 'en'])

    # 문제 인식 및 채점 진행
    start = time.time()
    categorize_qna(path)
    end = time.time()
    qna_eta = end - start

    start = time.time()
    mul_df = detect_multiple(path, reader)
    end = time.time()
    mul_eta = end - start

    print()
    print("qna_eta: " + f"{qna_eta:.2f} sec")
    print("mul_eta: " + f"{mul_eta:.2f} sec")

    return mul_df


def getSubDf(testee_path):
    # 경로 정의
    path = testee_path

    # easyocr 사용
    reader = easyocr.Reader(['ko', 'en'])

    # 문제 인식 및 채점 진행
    start = time.time()
    categorize_qna(path)
    end = time.time()
    qna_eta = end - start

    start = time.time()
    sub_df = detect_multiple(path, reader)
    end = time.time()
    sub_eta = end - start

    print()
    print("qna_eta: " + f"{qna_eta:.2f} sec")
    print("sub_eta: " + f"{sub_eta:.2f} sec")

    return sub_df


def getMulSubDf(testee_path):
    # 경로 정의
    path = testee_path

    # easyocr 사용
    reader = easyocr.Reader(['ko', 'en'])

    # 문제 인식 및 채점 진행
    start = time.time()
    categorize_qna(path)
    end = time.time()
    qna_eta = end - start

    start = time.time()
    mul_df = detect_multiple(path, reader)
    end = time.time()
    mul_eta = end - start

    start = time.time()
    sub_df = detect_subjective(path, reader)
    end = time.time()
    sub_eta = end - start

    print()
    print("qna_eta: " + f"{qna_eta:.2f} sec")
    print("mul_eta: " + f"{mul_eta:.2f} sec")
    print("sub_eta: " + f"{sub_eta:.2f} sec")

    # mul과 sub 통합을 위한 df 생성
    df = pd.concat([mul_df, sub_df], axis=0, ignore_index=True)

    return df


def pointchecker(upload_path, test_name, copy_num, total_qna_num, testee_num, test_category):
    # 경로 정의
    path = str(Path(upload_path))
    jpg_path = path + "/jpg"
    temp_path = path + "/temp"

    # is_mul, is_sub 정의
    is_mul = int(test_category[0])
    is_sub = int(test_category[1])

    # 파일 생성
    makeIdFolder(path)

    # df, testee_df 생성
    df = pd.DataFrame(columns=["testee_id", "file", "num", "testee_answer"])
    testee_df = pd.DataFrame(columns=["file", "num", "testee_answer"])

    # pdf 파일 탐지
    original_pdf_file_path_list = []
    original_pdf_file_path_list = os_sorted(Path(path).glob('*.pdf'))
    
    # pdf 파일 있는지 검사
    if len(original_pdf_file_path_list) == 0:
        print("original pdf file path list is empty")
        return df
    
    # pdf 파일 jpg로 변환
    convertPdfToJpg(original_pdf_file_path_list, jpg_path)

    # jpg 파일 개수 검사
    jpg_file_path_list = []
    jpg_file_path_list = os_sorted(Path(jpg_path).glob('*.jpg'))

    if len(jpg_file_path_list) == 0:
        print("jpg file path list is empty")
        return df
    
    # 사용자가 입력한 정보에 맞게 분리됐는지 확인
    # if len(jpg_file_path_list) != copy_num * testee_num:
    #     print("some jpg files are missing or entered incorrect information")
    #     return None

    # jpg에 적힌 코드 인식해서 testee 구분
    testee_jpg_df = pd.DataFrame(columns=["index_id", "file", "testee_id", "page"])
    id_match = pd.DataFrame(columns=["testee_id", "testee_name"])
    testee_jpg_df, id_match = testeeCodeRecognition(jpg_file_path_list, testee_jpg_df)
    testee_jpg_df.to_excel(jpg_path + "/testee_jpg_df.xlsx")

    testee_id_jpg_df = pd.DataFrame(columns=["index_id", "testee_id", "testee_name", "file", "page"])
    testee_id_jpg_df = testeeIdJpgDf(testee_id_jpg_df, testee_jpg_df, id_match)
    display_testeed_jpg_df = testee_id_jpg_df.set_index(keys=["index_id", "testee_id", "testee_name", "file"], drop=True)
    
    print()
    print(id_match)
    print()
    print_full(display_testeed_jpg_df)
    
    # 응시자 수만큼 해당 과정 반복
    for id_idx, id_row in id_match.iterrows():
        # 응시자별 폴더 생성
        start = time.time()
        
        index_id = id_idx
        this_id = "testee_" + str(index_id)
        testee_id = id_row["testee_id"]
        testee_name = id_row["testee_name"]

        # if str(i) in id_match:
        #     testee_id = id_match[str(i)]
        #     testee_name = id_match[str(i)][testee_id]

        testee_path = temp_path + "/" + this_id
        makeTesteeFolder(testee_path)

        print()
        print("testee_id: " + testee_id)
        print()

        # 응시자별 폴더로 jpg 나누기
        for idx, row in testee_jpg_df.iterrows():
            if row["index_id"] == index_id:
                testee_jpg_path = row["file"]
                testee_jpg_name = os.path.basename(testee_jpg_path)
                testee_jpg_copy_path = testee_path + "/" + testee_jpg_name
                shutil.move(testee_jpg_path, testee_jpg_copy_path)

        # 응시자별 df 생성
        testee_df = pd.DataFrame()

        if is_mul and is_sub:
            testee_df = getMulSubDf(testee_path)
        else:
            if is_mul:
                testee_df = getMulDf(testee_path)
            if is_sub:
                testee_df = getSubDf(testee_path)

        # 전체 df와 합치기
        testee_df.sort_values(by=["num"], inplace=True)
        if testee_name:
            df = concatTesteeDf(df, testee_name, testee_df)
        else:
            df = concatTesteeDf(df, this_id, testee_df)

        end = time.time()
        testee_eta = end - start
        print("testee_eta: " + f"{testee_eta:.2f} sec")


    # # 응시자 수만큼 해당 과정 반복
    # for i in range(1, testee_num+1):
    #     # 응시자별 폴더 생성
    #     start = time.time()

    #     if not i in id_match.index:
    #         continue
        
    #     index_id = i
    #     this_id = "testee_" + str(index_id)
    #     testee_id = id_match.loc[index_id, "testee_id"]
    #     testee_name = id_match.loc[index_id, "testee_name"]

    #     # if str(i) in id_match:
    #     #     testee_id = id_match[str(i)]
    #     #     testee_name = id_match[str(i)][testee_id]

    #     testee_path = temp_path + "/" + this_id
    #     makeTesteeFolder(testee_path)

    #     print()
    #     print("testee_id: " + testee_id)
    #     print()

    #     # 응시자별 폴더로 jpg 나누기
    #     for idx, row in testee_jpg_df.iterrows():
    #         if row["index_id"] == index_id:
    #             testee_jpg_path = row["file"]
    #             testee_jpg_name = os.path.basename(testee_jpg_path)
    #             testee_jpg_copy_path = testee_path + "/" + testee_jpg_name
    #             shutil.move(testee_jpg_path, testee_jpg_copy_path)

    #     # 응시자별 df 생성
    #     testee_df = pd.DataFrame()

    #     if is_mul and is_sub:
    #         testee_df = getMulSubDf(testee_path)
    #     else:
    #         if is_mul:
    #             testee_df = getMulDf(testee_path)
    #         if is_sub:
    #             testee_df = getSubDf(testee_path)

    #     # 전체 df와 합치기
    #     testee_df.sort_values(by=["num"], inplace=True)
    #     if testee_name:
    #         df = concatTesteeDf(df, testee_name, testee_df)
    #     else:
    #         df = concatTesteeDf(df, this_id, testee_df)

    #     end = time.time()
    #     testee_eta = end - start
    #     print("testee_eta: " + f"{testee_eta:.2f} sec")


    df.to_excel(path+"/final_df.xlsx")

    # 응시자별 폴더 삭제
    deleteFolder(testee_path)

    return df