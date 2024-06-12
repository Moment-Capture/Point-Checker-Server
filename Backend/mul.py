import os
import pandas as pd

from pathlib import Path
from natsort import os_sorted
from ultralytics import YOLO

from path import *
from utils import cropBox, labelToInt, deleteDuplicateFiles, getQnaNum


def detect_multiple(path, num_list, total_qna_num, reader):
    # 경로 정의
    mul_path = path + "/" + "mul"
    mul_result_path = path + "/" + "result_mul"
    model_path = BE_PATH + "/" + "models"
    multiple_path = model_path + "/" + "multiple" + "/" + "weights" + "/" + "best.pt"

    # 결과 저장을 위한 df 선언
    df = pd.DataFrame(columns=["file", "num", "testee_answer", "correct_answer"])

    # 입력 파일 정렬
    images = os_sorted(Path(mul_path).glob('*.jpg'))
    deleteDuplicateFiles(mul_path, images)

    if len(images) == 0:
        return df

    # Yolov8 사용
    model_mul = YOLO(multiple_path)
    # results = model_mul(source=images, save=False, save_crop=False, conf=0.5)
    # results = model_mul(source=images, save=True, save_crop=True, conf=0.5, project=mul_result_path)
    results = model_mul(source=images, save=False, save_crop=False, conf=0.5)
    names = model_mul.names

    for result in results:
        boxes = result.boxes.xyxy.tolist()
        clss = result.boxes.cls.cpu().tolist()

        image = result.orig_img
        file = result.path
        file_name = os.path.basename(file)

        if boxes is not None:
            # 변수 초기화
            qna_num = -1
            check = ""
            check_list = []

            # 문항 번호 감지 & checked 영역 감지
            for box, cls in zip(boxes, clss):
                img = cropBox(box, image)
                
                # 문항 번호 num 감지
                if (names[int(cls)] == "num"):              
                    qna_num = getQnaNum(num_list, img, total_qna_num, reader)
                
                # 체크한 선지 번호 check 감지
                else:
                    check = labelToInt(names[int(cls)])
                    if not (check in check_list):
                        check_list.append(check)           
            
            if (len(check_list) > 1):
                check_list.sort()
                new_row = {"file" : file_name, "num" : qna_num, "testee_answer" : check_list, "correct_answer" : 0}
            else:
                new_row = {"file" : file_name, "num" : qna_num, "testee_answer" : check, "correct_answer" : 0}
            
            df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
    
    return df