import os
import numpy as np
import pandas as pd

from pdf2image import convert_from_path


def print_intro():
    print()
    print("========================")
    print("환영합니다.")
    print()
    print("해당 프로그램은 포인트체커의 프로토 타입으로, 데모를 위해 설계되었습니다.")
    print("========================")
    print()


def print_outro():
    print()
    print("========================")
    print("감사합니다.")
    print("========================")
    print()

# 모든 df cmd로 출력
def print_full(df):
    pd.set_option('display.max_rows', len(df))
    print(df)
    pd.reset_option('display.max_rows')
    return


# 이미지와 박스 영역을 주면 박스 영역 추출
def cropBox(box, img):
    obj = img[int(box[1]):int(box[3]), int(box[0]):int(box[2])]
    return obj


# 겹치는 영역 계산
# bb_intersection_over_union(boxA, boxB)
# https://gist.github.com/meyerjo/dd3533edc97c81258898f60d8978eddc
def compute_intersect_size(boxA, boxB):
    if len(boxA) == 0 or len(boxB) == 0:
        return 0
    
    xA = max(boxA[0], boxB[0])
    yA = max(boxA[1], boxB[1])
    xB = min(boxA[2], boxB[2])
    yB = min(boxA[3], boxB[3])

    # compute the area of intersection rectangle
    interArea = abs(max((xB - xA, 0)) * max((yB - yA), 0))
    if interArea == 0:
        return 0
    # compute the area of both the prediction and ground-truth
    # rectangles
    boxAArea = abs((boxA[2] - boxA[0]) * (boxA[3] - boxA[1]))
    boxBArea = abs((boxB[2] - boxB[0]) * (boxB[3] - boxB[1]))

    # compute the intersection over union by taking the intersection
    # area and dividing it by the sum of prediction + ground-truth
    # areas - the interesection area
    iou = interArea / float(boxAArea + boxBArea - interArea)

    # return the intersection over union value
    return iou


# 두 이미지를 이어 붙임
def concatImage(crop_obj, searching_obj):
    max_width = 0
    total_height = crop_obj.shape[0] + searching_obj.shape[0]
    if (crop_obj.shape[1] > searching_obj.shape[1]):
        max_width = crop_obj.shape[1]
    else:
        max_width = searching_obj.shape[1]

    final_obj = np.zeros((total_height, max_width, 3), dtype=np.uint8)
    final_obj.fill(255)
    current_y = 0

    final_obj[current_y:crop_obj.shape[0]+current_y,:crop_obj.shape[1],:] = crop_obj
    current_y += crop_obj.shape[0]

    final_obj[current_y:searching_obj.shape[0]+current_y,:searching_obj.shape[1],:] = searching_obj
    current_y += searching_obj.shape[0]

    return final_obj


# jpg로 변환
def convertToJpg(file_path_list, path):
    file_path = ""

    if file_path_list is None:
        print("pdf is not found")
        return None
    else:
        for file in file_path_list:
            file_path = file
            break
    
    file_name = os.path.basename(file_path)
    pages = convert_from_path(file_path)

    for i, page in enumerate(pages):
        page.save(path + "/" + file_name + "_" + str(i) + ".jpg", "JPEG")


# df으로 변환
def convertToDf(file_path_list, path):
    file_path = ""
    df = pd.DataFrame()

    if len(file_path_list) == 0:
        print("excel not found")
        return None
    else:
        for file in file_path_list:
            file_path = file
            break
    
    df = pd.read_excel(file_path, engine='openpyxl')
    return df


#df를 최종 출력 형태로 변환
def dfToFinalDf(df):
    final_df = pd.DataFrame()
    final_df = df[df.check != 0]
    final_df = final_df.drop(["file"], axis=1)
    final_df = final_df[final_df.ans != 0]
    final_df = final_df.set_index(keys=["num"], drop=True)
    final_df = final_df.sort_index(ascending=True)
    final_df = final_df.reset_index(drop=False)
    return final_df


# 입력 받은 label을 int로 변환
def label_to_int(label):
    if label == "a1":
        return 1
    elif label == "a2":
        return 2
    elif label == "a3":
        return 3
    elif label == "a4":
        return 4
    elif label == "a5":
        return 5
    else:
        return 0
    