import os
import shutil
import pandas as pd

from pathlib import Path
from natsort import os_sorted

from qna import categorize_qna
from mul import detect_multiple
from sub import detect_subjective
from utils import print_full, convertToJpg, convertToDf, concatDfWithAnswer, dfToFinalDf


def getFinalDf(upload_path):
    # 경로 정의: yolo 이용 편의성을 위해 경로 설정을 따로 해야 할 필요성 있음
    path = str(Path(upload_path))
    input_path = path
    save_path = path + "/temp"
    input_save_path = save_path + "/jpg"
    mul_save_path = save_path + "/mul"
    sub_save_path = save_path + "/sub"
    os.chdir(path)

    ## input 폴더 생성 ##
    # try:
    #     # if os.path.exists(input_path):
    #     #     shutil.rmtree(input_path)
    #     # os.mkdir(input_path)
    #     if not os.path.exists(input_path):
    #         os.mkdir(input_path)
    # except:
    #     pass
    ## input 폴더 생성 ##

    ## 결과 저장 폴더 생성 ##
    try:
        if (os.path.exists(save_path)):
            shutil.rmtree(save_path)
        os.mkdir(save_path)
    except:
        pass

    try:
        os.mkdir(input_save_path)
        os.mkdir(mul_save_path)
        os.mkdir(sub_save_path)
    except:
        pass
    ## 결과 저장 폴더 생성 ##

    # df, answer_df, final_df
    df = pd.DataFrame()
    answer_df = pd.DataFrame()
    final_df = pd.DataFrame()

    mul_df = pd.DataFrame(columns=["file", "num", "testee_answer", "correct_answer"])
    sub_df = pd.DataFrame(columns=["file", "num", "testee_answer", "correct_answer"])

    # file path list
    original_pdf_file_path_list = []
    answer_file_path_list = []

    # file path list에 각 파일 경로 검색해 저장
    original_pdf_file_path_list = os_sorted(Path(input_path).glob('*.pdf'))
    answer_file_path_list = os_sorted(Path(input_path).glob('*.xlsx'))
    if len(original_pdf_file_path_list) == 0 or len(answer_file_path_list) == 0:
        print("file path list is empty")
        return None

    # pdf 파일 jpg로 변환
    convertToJpg(original_pdf_file_path_list, input_save_path)

    # excel 읽어 df로 변환
    answer_df = convertToDf(answer_file_path_list, input_path)
    
    if len(answer_df) == 0:
        print("answer_df empty")
        return None

    # 문제 인식 및 채점 진행
    categorize_qna(path)
    mul_df = detect_multiple(path)
    print_full(mul_df)
    sub_df = detect_subjective(path)
    print_full(sub_df)

    # mul과 sub 통합을 위한 df 생성
    df = pd.concat([mul_df, sub_df], axis=0)
    print_full(df)
    df = concatDfWithAnswer(df, answer_df)
    print_full(df)

    # df 정리해서 final_df로 반환
    final_df = dfToFinalDf(df)
    print_full(final_df)

    ## 결과 저장 폴더 삭제 ##
    try:
        if (os.path.exists(save_path)):
            shutil.rmtree(save_path)
    except:
        pass
    ## 결과 저장 폴더 삭제 ##

    return final_df