import easyocr
import pandas as pd

from pathlib import Path
from natsort import os_sorted
from ultralytics import YOLO

from utils import cropBox, compute_intersect_size, label_to_int


def detect_multiple(path):
    # 경로 정의
    ultralytics_path = path + "\\ultralytics"
    save_path = path + "\\temp"
    mul_save_path = save_path + "\\mul"

    multiple_path = ultralytics_path + "\\runs\\detect\\multiple_train2_epoch50\\weights\\best.pt"

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

            # 문항 번호 감지 & checked 영역 감지
            for box, cls in zip(boxes, clss):
                # 문항 번호 감지
                if (names[int(cls)] == "num"):
                    img = cropBox(box, image)
                    text = reader.readtext(img, detail = 0, allowlist="0123456789")
                    if len(text) != 0:
                        qna_num = int(text[0])
                        continue
                
                # checked 영역 감지
                elif (names[int(cls)] == "checked"):
                    checked_box = box
            
            max_size = 0
            max_choice = ""

            # checked 영역과 a1~a5 영역 비교해서 가장 큰 값 도출
            for box, cls in zip(boxes, clss):
                if names[int(cls)] != "num" and names[int(cls)] != "checked":
                    size = compute_intersect_size(checked_box, box)
                    if (size > max_size):
                        max_choice = label_to_int(names[int(cls)])
                        max_size = size

            if max_size > 0:
                check = max_choice
            else:
                check = 0
            
            
            new_row = {"file" : file, "num" : qna_num, "check" : check, "ans" : 0}
            df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
    
    return df

   