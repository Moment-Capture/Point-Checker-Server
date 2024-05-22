import cv2

from pathlib import Path
from natsort import os_sorted
from ultralytics import YOLO

from path import *
from utils import cropBox, concatImage


def crop_match(cropped_qna_arr, crop_obj, match_path, mul_save_idx, mul_save_path):
    # cropped_arr에 저장된 crop_obj 매칭
    model_match = YOLO(match_path)
    results_match = model_match(source=crop_obj, conf=0.6, save=False)
    
    names = model_match.names
    result = results_match[0]

    boxes = result.boxes.xyxy.tolist()
    clss = result.boxes.cls.cpu().tolist()

    name_match = ""
    name_search = ""
    forb = ""

    # cropped_arr에 crop_obj 유형 정보 추가해서 저장
    print()
    name_crop_arr = []
    if boxes is not None:
        for cls in clss:
            name_match = names[int(cls)]
            name_crop_arr = [name_match, crop_obj]
            cropped_qna_arr.append(name_crop_arr)
    
    if name_match == "etc" or name_match == "back_5":
        return
    elif name_match == "front_5":
        # 이미지 저장
        save_name = mul_save_path + "\mul_" + str(mul_save_idx) + ".jpg"
        cv2.imwrite(save_name, crop_obj)
        mul_save_idx += 1
        cropped_qna_arr.pop()
        return
    elif name_match == "front_num":
        forb = "f"
        name_search = "back_num"
    elif name_match == "front_1":
        forb = "f"
        name_search = "back_1"
    elif name_match == "front_2":
        forb = "f"
        name_search = "back_2"
    elif name_match == "front_3":
        forb = "f"
        name_search = "back_3"
    elif name_match == "front_4":
        forb = "f"
        name_search = "back_4"
    elif name_match == "back_num":
        forb = "b"
        name_search = "front_num"
        forb = "b"
    elif name_match == "back_1":
        forb = "b"
        name_search = "front_1"
    elif name_match == "back_2":
        forb = "b"
        name_search = "front_2"
    elif name_match == "back_3":
        forb = "b"
        name_search = "front_3"
    elif name_match == "back_4":
        forb = "b"
        name_search = "front_4"

    for i in range(len(cropped_qna_arr)-1):
        searching_arr = cropped_qna_arr[i]
        searching_name = searching_arr[0]
        searching_obj = searching_arr[1]

        if (searching_name == name_search):
            # 이미지 이어붙이기
            if (forb == "f"):
                joined_image = concatImage(crop_obj, searching_obj)
            else:
                joined_image = concatImage(searching_obj, crop_obj)

            cropped_qna_arr.remove(name_crop_arr)
            cropped_qna_arr.remove(searching_arr)

            # 이미지 저장
            save_name = mul_save_path + "\\mul_" + str(mul_save_idx) + ".jpg"
            cv2.imwrite(save_name, joined_image)
            mul_save_idx += 1

        break


def categorize_qna(path):
    # 경로 정의
    mul_path = path + "/mul"
    sub_path = path + "/sub"
    save_name = ""

    model_path = BE_PATH + "/models"
    qna_path = model_path + "/qna/weights/best.pt"
    match_path = model_path + "/matching/weights/best.pt"

    # 입력 파일 정렬
    images = os_sorted(Path(path).glob('*.jpg'))

    # 잘린 예외 문항들 저장 array
    cropped_qna_arr = []

    # Yolov8 사용
    model_qna = YOLO(qna_path)
    results_qna = model_qna(source=images, conf=0.75, save=False, save_crop=False)

    names = model_qna.names

    # mul, sub 나눠서 저장
    global mul_save_idx, sub_save_idx
    mul_save_idx = 0
    sub_save_idx = 0

    for result in results_qna:
        # 한 페이지 내의 결과들
        boxes = result.boxes.xyxy.tolist()
        clss = result.boxes.cls.cpu().tolist()

        image = result.orig_img

        if boxes is not None:
            for box, cls in zip(boxes, clss):
                qna = cropBox(box, image)

                if (names[int(cls)] == "q_mark" or names[int(cls)] == "q_period" or names[int(cls)] == "s_period"):
                    continue

                elif (names[int(cls)] == "multiple"):
                    save_name = mul_path + "/mul_" + str(mul_save_idx) + ".jpg"
                    cv2.imwrite(save_name, qna)
                    mul_save_idx += 1
                    continue

                elif (names[int(cls)] == "subjective"):
                    save_name = sub_path + "/sub_" + str(sub_save_idx) + ".jpg"
                    cv2.imwrite(save_name, qna)
                    sub_save_idx += 1
                    continue

                elif (names[int(cls)] == "multiple_cropped"):
                    crop_match(cropped_qna_arr, qna, match_path, mul_save_idx, mul_path)