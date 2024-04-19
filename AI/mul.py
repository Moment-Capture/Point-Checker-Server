import easyocr
import pandas as pd

from pathlib import Path
from natsort import os_sorted
from ultralytics import YOLO

from utils import cropBox, compute_intersect_size, label_to_int


def detect_multiple(path):
    # 경로 정의
    save_path = path + "\\temp"
    mul_save_path = save_path + "\\mul"

    model_path = path + "\\models"
    multiple_path = model_path + "\\multiple\\weights\\best.pt"

    # 입력 파일 정렬
    images = os_sorted(Path(mul_save_path).glob('*.jpg'))

    # Yolov8 사용
    model_mul = YOLO(multiple_path)
    results = model_mul(source=images, save=False, save_crop=False, name='mul_test')
    names = model_mul.names

    # easyocr 사용
    reader = easyocr.Reader(['ko', 'en'], gpu=False)

    # 결과 저장을 위한 df 선언
    df = pd.DataFrame(columns=["file", "num", "check", "ans"])

    print()

    for result in results:
        boxes = result.boxes.xyxy.tolist()
        clss = result.boxes.cls.cpu().tolist()

        image = result.orig_img
        file = result.path

        if boxes is not None:
            # 변수 초기화
            checked_box = []
            qna_num = 0
            check = 0

            # 문항 번호 감지 & checked 영역 감지
            for box, cls in zip(boxes, clss):
                # 문항 번호 num 감지
                if (names[int(cls)] == "num"):
                    img = cropBox(box, image)
                    text = reader.readtext(img, detail = 0, allowlist="0123456789")
                    if len(text) != 0:
                        qna_num = int(text[0])
                        continue
                
                # 체크한 선지 번호 check 감지
                check = label_to_int(names[int(cls)])            
            
            new_row = {"file" : file, "num" : qna_num, "check" : check, "ans" : 0}
            df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
    
    return df