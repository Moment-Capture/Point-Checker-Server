import os
import shutil
import pandas as pd

from pathlib import Path
from natsort import os_sorted

from qna import categorize_qna
from mul import detect_multiple
from sub import detect_subjective
from utils import print_full, convertPdfToJpg, convertExcelToDf, concatAnswer, dfToFinalDf, makeFolder, makeIdFolder, makeTesteeFolder, deleteFolder, concatTesteeDf


def pointchecker(upload_path, num):
    # 경로 정의
    path = str(Path(upload_path))
    jpg_path = path + "/jpg"
    temp_path = path + "/temp"

    # 파일 생성
    makeIdFolder(path)

    # pdf 파일 jpg로 변환
    original_pdf_file_path_list = []
    original_pdf_file_path_list = os_sorted(Path(path).glob('*.pdf'))
    
    if len(original_pdf_file_path_list) == 0:
        print("original pdf file path list is empty")
        return None
    
    convertPdfToJpg(original_pdf_file_path_list, jpg_path)

    # xlsx 파일 df로 변환
    answer_file_path_list = []
    answer_file_path_list = os_sorted(Path(path).glob('*.xlsx'))
    
    if len(answer_file_path_list) == 0:
        print("answer file path list is empty")
        return None
    
    answer_df = convertExcelToDf(answer_file_path_list, path)

    if len(answer_df) == 0:
        print("answer_df empty")
        return None

    # 데이터프레임 생성
    df = pd.DataFrame(columns=["testee", "file", "num", "testee_answer", "correct_answer"])

    # 응시자 수만큼 해당 과정 반복
    for i in range(num):
        # 응시자별 폴더 생성
        testee_id = "testee" + str(i)
        testee_path = temp_path + "/" + testee_id
        makeTesteeFolder(testee_path, num)

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