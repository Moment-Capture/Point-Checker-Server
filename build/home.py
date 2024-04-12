from pathlib import Path
import tkinter as tk
from tkinter import filedialog
from tkinter import ttk

import os
import time
from pdf2image import convert_from_path
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from PIL import Image, ImageDraw, ImageFont

OUTPUT_PATH = Path(__file__).parent
ASSETS_PATH = OUTPUT_PATH / Path(r"assets//assets//frame0")



##########################################################
##########################################################

def relative_to_assets(path: str) -> Path:
    return ASSETS_PATH / Path(path)



##########################################################
##########################################################

transfer_widgets = []
home_widgets = []



def process_input(num_candidates, file_path):
    start_time = time.time()
    insert(num_candidates, file_path)
    end_time = time.time()  # 처리 종료 시간 기록
    print(f"전체 처리 시간: {end_time - start_time} 초")
    # show_grade()



def insert(num_candidates, file_path):

    output_pdf_path = os.path.splitext(file_path)[0] + "_pointchecker.pdf"

    # PDF를 이미지로 변환하고 번호를 삽입하여 저장
    images,num_pages = pdf_to_images(file_path)
    processed_images = []
    # 각 페이지에 대해 번호 삽입
    for page_num in range(1, int(num_candidates) + 1):
        for i in range(1, num_pages+1):
            # 삽입할 숫자 (예: "1-1", "1-2", ...)
            
            number_to_insert = f"{page_num}-{i}"
            # 삽입할 위치 (x, y 좌표)
            insert_position = (100, 100)  # 적절한 위치로 수정 필요
            
            image = images[i-1].copy()
            image = insert_number(image, number_to_insert, insert_position, i)
            processed_images.append(image)
    # 최종 PDF 파일 저장
    save_as_pdf(output_pdf_path, num_candidates, processed_images)
   


def save_as_pdf(output_pdf_path, num_candidates, images):
    # PDF 생성 및 이미지 추가
    c = canvas.Canvas(output_pdf_path, pagesize=letter)

    for image in images:

        c.drawInlineImage(image, 0, 0, width=letter[0], height=letter[1])
        c.showPage()
    # PDF 파일 저장
    c.save()



def pdf_to_images(pdf_path):#output_folder):
    images = []

    # PDF 파일 열기
    images = convert_from_path(pdf_path)
    num_pages = len(images)

    return images, num_pages



def insert_number(image, text, position, page_num):

    # 이미지에 숫자 삽입
    draw = ImageDraw.Draw(image)
    font_path = ImageFont.truetype("C:/Windows/Fonts/NanumGothic.ttf", 80)  # 폰트와 크기 설정
    position = position  # 왼쪽 상단에 출력

    # 삽입할 텍스트의 너비와 높이 초기화
    total_width = 0
    max_height = 0

    # 하이픈을 포함한 텍스트 삽입
    position_x, position_y = position
    for char in text:

      char_width = draw.textlength(char, font=font_path)
      char_height = 80
      draw.text((position_x, position_y), char, fill="black", font=font_path)
      total_width += char_width
      max_height = max(max_height, char_height)
      position_x += char_width  # 다음 문자의 x 위치 조정
    # 선 추가
    if page_num==1:
      underline_x1 = 1750 
      underline_x2 = 2100 
      underline_y = 200 
      draw.line([(underline_x1, underline_y), (underline_x2, underline_y)], fill="black", width=2)

        # 'id :' 텍스트 삽입
      id_text = 'ID :'
      id_position_x = 1600  # 박스 왼쪽에 위치하도록 조정
      id_position_y = 130
      draw.text((id_position_x, id_position_y), id_text, fill="black", font=font_path)

    return (image)



def hide_widgets(widget_list):
    for widget in widget_list:
        widget.place_forget()



##########################################################
##########################################################



##########################################################
##########################################################

### 시험지 양식 적용 화면 ###
def show_transfer():
    global home_widgets
    hide_widgets(home_widgets)
    canvas_r.delete("all")  # 캔버스 초기화
    
    canvas_r.create_text(
        35.0,
        130.0,
        anchor="nw",
        text="2. 변환할 시험지 파일을 업로드 하세요. (파일 확장자: .pdf)",
        fill="#000000",
        font=("Inter", 14 * -1)
    )

    entry_2_value = tk.StringVar()  # entry_2_value를 함수 내에서 선언합니다.
    entry_2 = tk.Entry(
        bd=0,
        bg="#D9D9D9",
        fg="#000716",
        highlightthickness=0,
        textvariable=entry_2_value
    )
    entry_2.place(
        x=330,
        y=65,
        width=170,
        height=25
    )

    
    canvas_r.create_text(
        35.0,
        25.0,
        anchor="nw",
        text="1. 시험 정보를 입력 하세요.",
        fill="#000000",
        font=("Inter", 14 * -1) 
    )
    canvas_r.create_text(
        35,
        70,
        anchor="nw",
        text="응시자수",
        fill="#000000",
        font=("Inter", 14 * -1)
    )

    file_path_var=tk.StringVar()

    file_path_label=tk.Label(
        bd=0,
        bg="#dddddd",
        fg="#000716",
        highlightthickness=0,
        textvariable=file_path_var
        )
    file_path_label.place(
        x=360,
        y=165.0,
        width=390, 
        height=30
    )

    def browse_file():
        file_path = filedialog.askopenfilename()  # 파일 선택 다이얼로그 열기
        file_path_var.set(file_path)  # 파일 경로를 보여주는 필드에 경로 설정
   
   #시험지 파일 업로드 버튼
    button_2 = tk.Button(
        text="시험지 파일 업로드",
        borderwidth=0,
        highlightthickness=0,
        command=browse_file,
        relief="flat"
    )
    button_2.place(
        x=195,
        y=165.0,
        width=155,
        height=30.0
    )
    
    #인쇄용 파일 저장 버튼
    button_1 = tk.Button(
        text="인쇄용 파일 저장",
        borderwidth=0,
        highlightthickness=0,
        command=lambda: process_input(entry_2_value.get(), file_path_var.get()), #print("button_1 clicked"),
        relief="flat"
    )
    button_1.place(
        x=620,
        y=263.0,
        width=135,
        height=30.0
    )
    # transfer_widgets 리스트 정의
    global transfer_widgets
    transfer_widgets = [entry_2, button_2, button_1, file_path_label]



### 채점하기 화면 ###
def show_grade():
    global transfer_widgets
    hide_widgets(transfer_widgets)
    canvas_r.delete("all")  # 캔버스 초기화

    # 1. 시험정보를 입력하세요
    canvas_r.create_text(
        40.0,
        20.0,
        anchor="nw",
        text="1. 시험 정보를 입력 하세요.",
        fill="#000000",
        font=("Inter", 14 * -1)
    )

    # 1-1. 시험명
    canvas_r.create_text(
        40,
        50,
        anchor="nw",
        text="시험명",
        fill="#000000",
        font=("Inter", 14 * -1)
    )
    entry_5 = tk.Text(
        bd=0,
        bg="white",  # 배경색 (흰색)
        fg="#000716",  # 텍스트 색상
        highlightbackground="#d9d9d9",  # 테두리 색상
        highlightthickness=1,
        font=("Inter", 16 * -1)
    )
    entry_5.place(
        x=340, 
        y=45,
        width=140,
        height=23
    )

    # 1-2. 시험지1부당매수
    canvas_r.create_text(
        40,
        80,
        anchor="nw",
        text="시험지 1부당 매수",
        fill="#000000",
        font=("Inter", 14 * -1)
    ) 
    entry_4 = tk.Text(
        bd=0,
        bg="white",  # 배경색 (흰색)
        fg="#000716",  # 텍스트 색상
        highlightbackground="#d9d9d9",  # 테두리 색상
        highlightthickness=1,
        font=("Inter", 16 * -1)
    )
    entry_4.place(
        x=340, 
        y=75,
        width=140,
        height=23
    )

    # 1-3. 총문항수
    canvas_r.create_text(
        40,
        110,
        anchor="nw",
        text="총 문항 수",
        fill="#000000",
        font=("Inter", 14 * -1)
    )
    entry_3 = tk.Text(
        bd=0,
        bg="white",  # 배경색 (흰색)
        fg="#000716",  # 텍스트 색상
        highlightbackground="#d9d9d9",  # 테두리 색상
        highlightthickness=1,
        font=("Inter", 16 * -1)
    )
    entry_3.place(
        x=340, 
        y=105,
        width=140,
        height=23
    )

    # 1-4. 응시자수
    canvas_r.create_text(
        40,
        140,
        anchor="nw",
        text="응시자수",
        fill="#000000",
        font=("Inter", 14 * -1)
    )
    entry_2 = tk.Text(
        bd=0,
        bg="white",  # 배경색 (흰색)
        fg="#000716",  # 텍스트 색상
        highlightbackground="#d9d9d9",  # 테두리 색상
        highlightthickness=1,
        font=("Inter", 16 * -1)
    )
    entry_2.place(
        x=340, 
        y=135,
        width=140,
        height=23
    )

    # 1-5. 문제유형
    canvas_r.create_text(
        40,
        170,
        anchor="nw",
        text="문제유형",
        fill="#000000",
        font=("Inter", 14 * -1)
    )

    # 1-6. 객관식 체크박스 생성
    choice_var = tk.IntVar()
    choice_checkbox = tk.Checkbutton(
        root,
        text="객관식",
        variable=choice_var,
        onvalue=1,
        offvalue=0,
        bg="white",  # 체크박스 텍스트 영역의 배경색을 변경
        activebackground="white",  # 마우스가 올려졌을 때 배경색을 변경하지 않음
    ) 
    choice_checkbox.place(
        x=340, 
        y=165
    )
 
    # 1-7. 단답식 체크박스 생성
    short_answer_var = tk.IntVar()
    short_answer_checkbox = tk.Checkbutton(
        root,
        text="단답식",
        variable=short_answer_var,
        onvalue=1,
        offvalue=0,
        bg="white",  # 체크박스 텍스트 영역의 배경색을 변경
        activebackground="white",  # 마우스가 올려졌을 때 배경색을 변경하지 않음
    )
    short_answer_checkbox.place(
        x=420,
        y=165
    )

    # 2. 채점할 시험지 파일 업로드하세요
    canvas_r.create_text(
        40,
        220,
        anchor="nw",
        text="2. 채점할 시험지 파일을 업로드 하세요. (파일 확장자: .pdf)",
        fill="#000000",
        font=("Inter", 14 * -1)
    )

    # 2-1. 시험지 파일 업로드 버튼
    file_path_var=tk.StringVar()
    file_path_label=tk.Label(
        bd=0,
        bg="#dddddd",
        fg="#000716",
        highlightthickness=0,
        textvariable=file_path_var
        )
    file_path_label.place(
        x=370,
        y=250.0, 
        width=300,
        height=30
    )

    def browse_file():
        file_path = filedialog.askopenfilename()  # 파일 선택 다이얼로그 열기
        file_path_var.set(file_path)  # 파일 경로를 보여주는 필드에 경로 설정
   
    button_2 = tk.Button(
        text="시험지 파일 업로드",
        borderwidth=0,
        highlightthickness=0,
        command=browse_file,
        relief="flat"
    )
    button_2.place(
        x=200,
        y=250.0,
        width=150,
        height=30.0
    )


    # 3. 시험지 답을 입력해주세요
    canvas_r.create_text(
        40,
        310,
        anchor="nw",
        text="3. 시험지의 답을 입력해주세요.",
        fill="#000000",
        font=("Inter", 14 * -1)
    )

    # 표의 행과 열 수 정의
    num_rows = 4
    num_columns = 15

    # 표의 셀 크기 설정
    cell_width = 35 
    cell_height = 30

    # 표의 시작 위치 설정
    start_x = 200
    start_y = 340 
    cell_entries = []
    
    # 표 생성
    for i in range(num_rows):
        for j in range(num_columns):
            # 각 셀의 좌표 계산
            x1 = start_x + j * cell_width
            y1 = start_y + i * cell_height
            x2 = x1 + cell_width
            y2 = y1 + cell_height
            
            # 셀 생성
            cell_entry = tk.Entry(
                bd=1,  # 테두리 굵기 설정
                bg="#FFFFFF",  # 배경색 설정
                fg="#000000",  # 텍스트 색상 설정
                highlightthickness=0
            )
            cell_entry.place(x=x1, y=y1, width=cell_width, height=cell_height)
            cell_entries.append((cell_entry, x1, y1, x2, y2))
            

 
    # 4. 채점 버튼을 클릭하세요
    canvas_r.create_text( 
        40.0,
        490.0,
        anchor="nw",
        text="4. 채점하기 버튼을 클릭하세요. \n\n   채점이 완료되면 ‘결과 다운로드’ 버튼을 클릭하여 채점 결과를 다운로드 하세요.",
        fill="#000000",
        font=("Inter", 14 * -1)
    )

    # 4-1. 채점하기 버튼
    button_1 = tk.Button(
        text="채점하기",
        borderwidth=0,
        highlightthickness=0,
        command=lambda: print("button_1 clicked"),
        relief="flat"
    )
    button_1.place(
        x=200,
        y=560,
        width=125,
        height=30
    )

    # 4-2. 진행 막대 생성
    progress_bar = ttk.Progressbar(root, orient="horizontal", length=260, mode="indeterminate")
    progress_bar.place(x=350, y=565)


    # 4-3. 채점 결과 확인하기 버튼
    button_3 = tk.Button(
        text="채점 결과 확인하기",
        borderwidth=0,
        highlightthickness=0,
        command=lambda: print("button_3 clicked"),
        relief="flat"
    ) 
    button_3.place(
        x=630,
        y=560,
        width=125,
        height=30
    )

    ## home_widgets 리스트 정의 ##
    global home_widgets
    home_widgets = [entry_2,entry_3,entry_4,entry_5,choice_checkbox, short_answer_checkbox,button_3, button_2, button_1, file_path_label,progress_bar]
    home_widgets += [entry[0] for entry in cell_entries]
    ## home_widgets 리스트 정의 ##



##########################################################
##########################################################



##########################################################
##########################################################

# 메인 창 생성
root = tk.Tk()
root.title("POINTCHECKER")
root.geometry("800x660")
root.resizable(False, False)
root.configure(bg = "#FFFFFF")
root.iconbitmap('assets\pointchecker.ico')

# 왼쪽에 툴바 생성 
toolbar_frame = tk.Frame(root)
toolbar_frame.pack(side=tk.LEFT, fill=tk.Y)

# 오른쪽에 캔버스 생성

canvas_r = tk.Canvas(
    root,
    bg = "#FFFFFF",
    height = 660,
    width = 800,
    bd = 0,
    highlightthickness = 0,
    relief = "ridge"
) 
canvas_r.pack(side=tk.RIGHT, padx=0, pady=0)
 
# 툴바 버튼 생성 
transfer_button = tk.Button(toolbar_frame, text="시험지 양식 적용", command=show_transfer, bg="#d9d9d9", font=("Inter", 14 * -1))
transfer_button.pack(fill=tk.X, padx=10, pady=20,ipadx=10, ipady=20)
home_button = tk.Button(toolbar_frame, text="채점 하기", command=show_grade, bg="#d9d9d9",font=("Inter", 14 * -1)) 
home_button.pack(fill=tk.X, padx=10, pady=10,ipadx=10, ipady=20) 

# 메인 화면 설정
show_grade()

# 메인 루프 실행
root.mainloop()

##########################################################
##########################################################