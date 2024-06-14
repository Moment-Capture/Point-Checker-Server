<p align="center"><img width="450" alt="포인트_체커_대문" src="https://github.com/Moment-Capture/Point-Checker/assets/112560299/cb64e342-fcf4-4ca5-be0a-fc6beb00c96b"></p>
</br></br>


# 프로젝트 개요
## 문제 정의
✔ 종이 기반 시험(PBT)은 수기 채점이나 광학마크인식(OMR)을 활용하여 채점합니다. </br>
✔ 수기 채점은 사람이 직접 채점하여 많은 인력과 시간이 소요되며 부정확합니다. </br>
✔ OMR을 활용한 채점은 별도의 답안지 작성이 필요하여, 답안지 구매 비용을 부담해야 하고 단답식 문항은 채점할 수 없습니다. </br>
</br></br>
 
## 솔루션
종이 시험지에 표시된 답안을 객체 인식과 OCR을 활용하여 자동으로 문항을 인식하고 채점하는 AI 채점 소프트웨어를 개발했습니다. </br>
</br></br>

# 서비스 소개
## 시험지 양식 적용
<p><img width="500" alt="시험지_양식_적용_화면" src="https://github.com/Moment-Capture/Point-Checker/assets/112560299/a462b027-2886-4835-8f5b-02fbf3045887"></br></br>
 <img width="400" alt="시험지_양식_예시_화면" src="https://github.com/Moment-Capture/Point-Checker/assets/112560299/f70b9d1a-87f5-4bd2-9f5f-76d48be52a19"> </p>
</br>

- 시험지 원본 파일을 입력받으면 시험지 양식이 적용된 파일을 반환합니다.
</br></br>
 
## 채점하기
<p><img width="500" alt="채점하기_화면" src="https://github.com/Moment-Capture/Point-Checker/assets/112560299/afb50d49-50bc-4201-9b93-59f3daa1a90a"></p>

- 사용자는 시험 정보를 입력하고 응시한 시험지를 스캔한 파일(.pdf)과 답 파일(.xlsx)을 업로드 합니다. </br>
- ‘채점하기' 버튼을 통해 시험지 채점을 수행하여 채점 결과를 반환합니다. </br>
</br></br>
 
## 채점 결과 확인하기
<p><img width="500" alt="채점_결과_확인_화면" src="https://github.com/Moment-Capture/Point-Checker/assets/112560299/c1c80708-3f88-4ef9-9b44-5d5e8c1c6680"></p>

- 채점 결과는 응시자가 시험지에 작성한 응시자 ID를 추출하여, 각 응시자의 문항별 응답과 정답 여부를 정오표 형태로 출력합니다. </br>
- 사용자는 해당 데이터를 직접 추가, 수정, 삭제할 수 있으며, 엑셀 파일로 다운로드 할 수 있습니다. </br>
</br></br>

## 채점 결과 저장하기
<p><img width="500" alt="채점_결과_저장_화면" src="https://github.com/Moment-Capture/Point-Checker/assets/112560299/18df3402-4c92-4345-aaa8-58b2a6a74012"></p>

- 채점 결과를 엑셀로 저장했을 때 화면입니다. </br>
</br></br>


# 실행 방법
## 1. 리포지토리 클론
```bash
git clone https://github.com/Moment-Capture/Point-Checker.git
```
</br>
 
## 2. 라이브러리 설치
```bash
pip install -r requirements.txt
```

- Python 3.9 이상 환경에서 구동 가능합니다.
</br></br>

## 3. main.py 실행
```bash
python main.py
```
</br>

# 기술 소개
## 시스템 구조도
<p><img width="1000" alt="시스템 아키텍쳐" src="https://github.com/Moment-Capture/Point-Checker-Server/assets/112560299/603b7058-08ca-4003-81e7-e7f81e596095"></p>
</br></br>

- Tkinter GUI를 통해 사용자와 인터렉션
- Flask를 통해 서버와 통신
- Yolov8을 통해 객체 인식
- EasyOCR, Tamil-OCR을 통해 OCR
- pandastable로 생성된 엑셀 파일을 출력물로 전달
</br></br>

## 채점 엔진
<p><img width="1000" alt="채점 플로우" src="https://github.com/Moment-Capture/Point-Checker/assets/112560299/4e786b3a-58c1-4f7e-aef3-8201087fba65"></p>
</br>
</br></br>

### 응시자 인식 모델
- 사전에 적용된 양식을 통해 응시자를 인식합니다. </br>
- EasyOCR을 통해 사용자 아이디를 추출합니다. </br>
</br></br>

### QNA 분류 모델
- Yolov8으로 각 시험지의 문항 영역을 탐지하고 종류에 맞게 분류합니다. </br>
- 사용한 라벨: multiple, multiple_cropped, subjective, subjective_cropped, q_mark, s_period, q_period </br>
</br></br>

### 잘린 QNA 문항 매칭 모델
- Yolov8으로 잘린 문항을 분류하고, 일치하는 유형을 매칭합니다. </br>
- 사용한 라벨: front_num, front_1, front_2, front_3, front_4, front_5, back_num, back_1, back_2, back_3, back_4, back_5, etc </br>
</br></br>

### 객관식 인식 모델
- Yolov8으로 문항 번호와 선지를 인식합니다. </br>
- Yolov8 라벨링 결과를 통해 선지를 분류합니다. </br>
- EasyOCR을 통해 문항 번호를 추출합니다. </br>
- 사용한 라벨: num, check1, check2, check3, check4, check5 </br>
</br></br>

### 단답식 인식 모델
- Yolov8으로 문항 번호와 답안을 인식합니다. </br>
- tamil-ocr을 통해 필기 답안을 인식합니다. </br>
- EasyOCR을 통해 문항 번호를 추출합니다. </br>
- 사용한 라벨: num, answer </br>
</br></br>


# 성능 평가
## 소요 시간
✔ 1부 30문항 기준 35초 </br>
✔ 5부 30문항 기준 207초 </br>
✔ 10부 30문항 기준 403초 </br>
</br></br>

## 채점 정확도
✔ 문항 번호 인식 : 98 % </br>
✔ 정답 인식 : 98 % </br>
✔ 최종 인식 : 96 % </br>
</br></br>

 
## 기대효과 및 의의
- 비용 절감 : 답안지 및 시험 채점을 위한 인건비, 시간, 비용을 절감할 수 있습니다. </br>
- 환경 보호 : 답안지에 사용되는 종이 사용량을 줄여 환경 보호에 기여합니다. </br>
- 다양한 사람들에게 응시 기회 제공: OMR 작성을 어려워 하는 어린이, 노인, 장애인에게 응시 기회를 제공합니다. </br>
</br></br>


# 데모 영상
[캡스톤 그로쓰 39팀 최종발표 데모 동영상](https://youtu.be/WLkjEvUcV60) </br>
</br></br>


# 기술 블로그
[<포인트 체커 - 객체 인식과 OCR를 활용한 객관·단답식 시험 채점 AI 소프트웨어> 기술 블로그](https://velog.io/@gongkeo/%EC%9D%B4%ED%99%94%EC%97%AC%EB%8C%80-%EC%BA%A1%EC%8A%A4%ED%86%A4-%EB%94%94%EC%9E%90%EC%9D%B8-%ED%8F%AC%EC%9D%B8%ED%8A%B8-%EC%B2%B4%EC%BB%A4-%EA%B0%9D%EC%B2%B4-%EC%9D%B8%EC%8B%9D%EA%B3%BC-OCR%EB%A5%BC-%ED%99%9C%EC%9A%A9%ED%95%9C-%EA%B0%9D%EA%B4%80%EB%8B%A8%EB%8B%B5%EC%8B%9D-%EC%8B%9C%ED%97%98-%EC%B1%84%EC%A0%90-AI-%EC%86%8C%ED%94%84%ED%8A%B8%EC%9B%A8%EC%96%B4-%EA%B8%B0%EC%88%A0-%EB%B8%94%EB%A1%9C%EA%B7%B8) </br>
</br></br>


# 레퍼런스
## 라이브러리
- [Yolov8](https://github.com/ultralytics/yolov8) </br>
- [EasyOCR](https://github.com/JaidedAI/EasyOCR) </br>
- [Tamil-Ocr](https://github.com/gnana70/tamil_ocr) </br>
</br></br>

## 참고 자료
- [2021CapstoneDesign](https://velog.io/@nayeon_p00/series/2021CapstoneDesign) </br>
</br></br>
