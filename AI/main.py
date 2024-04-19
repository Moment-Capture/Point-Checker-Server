import os
import shutil
import pandas as pd

from pathlib import Path
from natsort import os_sorted

from qna import categorize_qna
from mul import detect_multiple
from utils import convertToJpg, convertToDf, dfToFinalDf



def getFinalDf():
    # 경로 정의: yolo 이용 편의성을 위해 경로 설정을 따로 해야 할 필요성 있음
    cwd_path = os.getcwd()
    path = str(Path(cwd_path))
    input_path = path + "\\input"
    save_path = path + "\\temp"
    input_save_path = save_path + "\\jpg"
    mul_save_path = save_path + "\\mul"
    sub_save_path = save_path + "\\sub"
    os.chdir(path)

    ## input 폴더 생성 ##
    try:
        # if os.path.exists(input_path):
        #     shutil.rmtree(input_path)
        # os.mkdir(input_path)
        if not os.path.exists(input_path):
            os.mkdir(input_path)
    except:
        pass
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
    df = detect_multiple(path)

    # df와 answer_df 합치기
    for df_idx, df_row in df.iterrows():
        df_num = df_row["num"]
        if df_num == 0:
            continue
        for ans_idx, ans_row in answer_df.iterrows():
            if (int(ans_row["correct_answer"]) == int(df_num)):
                df.loc[df_idx, "correct_answer"] = ans_row["correct_answer"]
                break

    final_df = dfToFinalDf(df)

    ## 결과 저장 폴더 삭제 ##
    try:
        if (os.path.exists(save_path)):
            shutil.rmtree(save_path)
    except:
        pass
    ## 결과 저장 폴더 삭제 ##

    return final_df