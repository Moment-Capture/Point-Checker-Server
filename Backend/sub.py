import os
import sys
import easyocr
import pandas as pd

from pathlib import Path
from natsort import os_sorted
from ultralytics import YOLO

sys.path.append(os.path.dirname(os.getcwd() + "/models/tamil_ocr"))

from models import tamil_ocr as tamil_ocr
from models.tamil_ocr import ocr_tamil as ocr_tamil
from models.tamil_ocr.ocr_tamil import ocr

from utils import cropBox, deleteDuplicateFiles


BE_PATH = "/home/ubuntu/Point-Checker/Backend"


def detect_subjective(path):
    # 경로 정의
    sub_path = path + "/sub"

    model_path = BE_PATH + "/models"
    subjective_path = model_path + "/subjective/weights/best.pt"

    # 결과 저장을 위한 df 선언
    df = pd.DataFrame(columns=["file", "num", "testee_answer", "correct_answer"])

    # 입력 파일 정렬
    images = os_sorted(Path(sub_path).glob('*.jpg'))
    deleteDuplicateFiles(sub_path, images)

    if len(images) == 0:
        return df

    # Yolov8 사용
    model_sub = YOLO(subjective_path)
    results = model_sub(source=images, save=False, save_crop=False, name='sub_test')
    names = model_sub.names

    # easyocr 사용
    reader = easyocr.Reader(['ko', 'en'])

    # 파일 리스트 생성
    files = []

    for result in results:
        boxes = result.boxes.xyxy.tolist()
        clss = result.boxes.cls.cpu().tolist()

        image = result.orig_img
        file = result.path

        if boxes is not None:
            # 변수 초기화
            qna_num = 0
            answer = ""

            # 문항 번호 감지 & checked 영역 감지
            for box, cls in zip(boxes, clss):                
                # 일단 객관식 답안이 숫자로 적힐 경우만 상정
                img = cropBox(box, image)
                
                ocr_text = ocr.OCR().predict(img)
                text = ""
                
                for txt in ocr_text:
                    for t in txt:
                        if (t.isdigit()):
                            text += t
                        elif (t == 'l' or t == 'i' or t == 'I' or t == '|' or t == '/'):
                            text += '1'
                
                if (len(text) == 0):
                    continue
                
                # 문항 번호 num 감지
                if (names[int(cls)] == "num"):
                    qna_num = int(text)
                
                # 적힌 단답 answer 감지
                else:
                    # 이미 있는 파일의 경우 건너뛰기
                    if file in files:
                        continue
                    files.append(file)
                    answer = int(text)
            
            new_row = {"file" : file, "num" : qna_num, "testee_answer" : answer, "correct_answer" : 0}
            df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
    
    return df