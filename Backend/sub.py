import os
import pandas as pd

from pathlib import Path
from natsort import os_sorted
from ultralytics import YOLO

from path import *
from utils import cropBox, deleteDuplicateFiles, getQnaNum, getAnswer


def detect_subjective(path, num_list, total_qna_num, reader):
    # 경로 정의
    sub_path = path + "/" + "sub"
    sub_result_path = path + "/" + "result_sub"
    model_path = BE_PATH + "/" + "models"
    subjective_path = model_path + "/" + "subjective" + "/" + "weights" + "/" + "best.pt"

    # 결과 저장을 위한 df 선언
    df = pd.DataFrame(columns=["file", "num", "testee_answer", "correct_answer"])

    # 입력 파일 정렬
    images = os_sorted(Path(sub_path).glob('*.jpg'))
    deleteDuplicateFiles(sub_path, images)

    if len(images) == 0:
        return df

    # Yolov8 사용
    model_sub = YOLO(subjective_path)
    # results = model_sub(source=images, save=False, save_crop=False, conf=0.3)
    # results = model_sub(source=images, save=True, save_crop=True, conf=0.3, project=sub_result_path)
    results = model_sub(source=images, save=False, save_crop=False, conf=0.3)
    names = model_sub.names

    # 파일 리스트 생성
    files = []

    for result in results:
        boxes = result.boxes.xyxy.tolist()
        clss = result.boxes.cls.cpu().tolist()

        image = result.orig_img
        file = result.path
        file_name = os.path.basename(file)

        if boxes is not None:
            # 변수 초기화
            qna_num = -1
            answer = ""

            # 문항 번호 감지 & checked 영역 감지
            for box, cls in zip(boxes, clss):                
                # 일단 객관식 답안이 숫자로 적힐 경우만 상정
                img = cropBox(box, image)

                # 문항 번호 num 감지
                if names[int(cls)] == "num":              
                    qna_num = getQnaNum(num_list, img, total_qna_num, reader)
                
                # 적힌 단답 answer 감지
                else:
                    # answer가 여러 개인 경우
                    if file in files:
                        if answer == "":
                            answer = getAnswer(img, reader)
                        else:
                            continue
                    else:
                        files.append(file)
                    
                    # ocr 사용
                    answer = getAnswer(img, reader)
            
            new_row = {"file" : file_name, "num" : qna_num, "testee_answer" : answer, "correct_answer" : 0}
            df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
    
    return df