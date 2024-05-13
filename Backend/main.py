import os
import shutil
import pandas as pd

from pathlib import Path
from natsort import os_sorted

from qna import categorize_qna
from mul import detect_multiple
from sub import detect_subjective
from utils import *


def pointchecker(upload_path, test_name, copy_num, total_qna_num, testee_num, test_category):
    # 경로 정의
    path = str(Path(upload_path))
    jpg_path = path + "/jpg"
    temp_path = path + "/temp"

    # 파일 생성
    makeIdFolder(path)

    # pdf 파일 탐지
    original_pdf_file_path_list = []
    original_pdf_file_path_list = os_sorted(Path(path).glob('*.pdf'))
    
    # pdf 파일 있는지 검사
    if len(original_pdf_file_path_list) == 0:
        print("original pdf file path list is empty")
        return None
    
    # pdf 파일 jpg로 변환
    convertPdfToJpg(original_pdf_file_path_list, jpg_path)

    # jpg 파일 개수 검사
    jpg_file_path_list = []
    jpg_file_path_list = os_sorted(Path(jpg_path).glob('*.jpg'))

    if len(jpg_file_path_list) == 0:
        print("jpg file path list is empty")
        return None
    
    if len(jpg_file_path_list) != copy_num * testee_num:
        print("some jpg files are missing")
        return None

    # jpg에 적힌 코드 인식해서 testee 구분
    ## 구현 해야 함 ##
    testee_jpg_df = pd.DataFrame(columns=["file", "num_id", "page", "id"])
    testeeCodeRecognition(jpg_path, jpg_file_path_list, testee_jpg_df)
    ## 구현 해야 함 ##


    # xlsx 파일 탐지
    answer_file_path_list = []
    answer_file_path_list = os_sorted(Path(path).glob('*.xlsx'))
    
    # xlsx 파일 있는지 검사
    if len(answer_file_path_list) == 0:
        print("answer file path list is empty")
        return None
    
    # xlsx 파일 df로 변환
    answer_df = convertExcelToDf(answer_file_path_list, path)

    # answer df에 값이 존재하는지 검사
    if len(answer_df) == 0:
        print("answer df is empty")
        return None

    # 데이터프레임 생성
    df = pd.DataFrame(columns=["testee", "file", "num", "testee_answer", "correct_answer"])

    # 응시자 수만큼 해당 과정 반복
    for i in range(testee_num):
        # 응시자별 폴더 생성
        testee_id = "testee" + str(i)
        testee_path = temp_path + "/" + testee_id
        makeTesteeFolder(testee_path, testee_num)

        # 응시자별 폴더로 jpg 나누기
        ## 구현 해야 함 ##
        
        ## 구현 해야 함 ##

        # 응시자별 df 생성
        testee_df = getTesteeDf(testee_path)

        # 정답 df와 합치기
        testee_df = concatAnswer(testee_df, answer_df)

        # 전체 df와 합치기
        concatTesteeDf(df, testee_id, testee_df)

        # 응시자별 폴더 삭제
        deleteFolder(testee_path)


def getTesteeDf(testee_path):
    # 경로 정의
    path = testee_path

    # 문제 인식 및 채점 진행
    categorize_qna(path)
    mul_df = detect_multiple(path)
    sub_df = detect_subjective(path)

    # mul과 sub 통합을 위한 df 생성
    df = pd.concat([mul_df, sub_df], axis=0)
    print_full(df)

    # df 정리해서 testee_df로 반환
    df = dfToFinalDf(df)
    print_full(df)

    return df