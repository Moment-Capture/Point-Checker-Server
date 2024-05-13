from pathlib import Path
import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter import ttk
from tkinter import *
# from reportlab.pdfgen import canvas

# import gc, time
import os
import requests
import fitz


FILE_PATH = Path(__file__)
OUTPUT_PATH = FILE_PATH.parent
ASSETS_PATH = OUTPUT_PATH / "assets"
FONT_PATH = "Malgun Gothic"
ICON_PATH = ASSETS_PATH / "pointchecker.ico"



##########################################################
##########################################################



### assets의 상대 경로 ###
def relative_to_assets(path: str) -> Path:
    return ASSETS_PATH / Path(path)



##########################################################
##########################################################
### 함수 및 변수 ###

## 공통  ##

## 공통 버튼 스타일 ##
button_style = {
    "bg": "#FCB6A8",     # 배경색
    "fg": "white",       # 텍스트 색상
    "font": (FONT_PATH, 12),  # 폰트 및 크기
    "relief": RIDGE      # 외곽선 스타일
}

## 전역변수 ##
widgets = []
entry_columns = []
file_path_var = None
answer_path_var = None

### 위젯 숨기는 함수 ###
def hide_widgets(widget_list):
    for widget in widget_list:
        widget.place_forget()


### 서버 연결하는 함수 ###
def server_connect(file_path, answer_path, test_name, copy_num, total_qna_num, testee_num, test_category):
    url = "http://107.23.189.114:8080/upload"
    files = {"file":open(file_path, "rb"),
             "answer":open(answer_path, "rb"),
             "test_name":test_name,
             "copy_num":copy_num,
             "total_qna_num":total_qna_num,
             "testee_num":testee_num,
             "test_category":test_category}
    r = requests.post(url, files=files)



##1. 시험지 양식 적용 화면 함수##
def browse_file():
    file_path = filedialog.askopenfilename(filetypes=(("pdf files","*.pdf*"),))  # 파일 선택 다이얼로그 열기
    file_path_var.set(file_path)  # 파일 경로를 보여주는 필드에 경로 설정

def insert_page_number(num_students, file_path):
    # Open the PDF
    pdf_document = fitz.open(file_path)
    num_pages = len(pdf_document)

    # Get page width and height
    page_width = pdf_document[0].rect.width
    page_height = pdf_document[0].rect.height
    print(page_width)
    print(page_height)
    # Convert start and end points to coordinates relative to top-right corner
    start_point = (page_width - 180, 65)
    end_point = (page_width - 60, 65)

    for i in range(0, num_students):
        output_pdf_path = os.path.splitext(file_path)[0] + f"_{i+1}.pdf"
        pdf_document = fitz.open(file_path)

        #첫 장에 이름 적는 칸
        page = pdf_document[0]
        text = "ID : "
        page.insert_text((page_width-220, 60), text, fontsize=16,fontname="courier")
        page.draw_line(start_point, end_point)

        for j in range(0, num_pages):
            # 삽입할 숫자 (예: "1-1", "1-2", ...)
            text = f"{i+1}-{j+1}"

            # 삽입할 위치 (x, y 좌표)
            insert_position = (60, 60)  # 적절한 위치로 수정 필요

            # Select the first page
            page = pdf_document[j]

            # Start editing the page
            page.insert_text(insert_position, text, fontsize=18,fontname="courier")

        # Save the changes to a new PDF
        pdf_document.save(output_pdf_path)
        
        # Close the PDF
        pdf_document.close()
    show_popup()

#종료 팝업 띄우기
def show_popup():
    root = tk.Tk()
    root.withdraw()  # 메인 윈도우 숨기기

    messagebox.showinfo("완료", "시험지 양식 적용이 완료되었습니다.")  # 팝업 메시지 보이기
    root.destroy()  # Tkinter 종료
    show_transfer()  # 메인 함수 다시 실행


##2. 채점하기 화면 함수##
#답안지 파일용
def browse_file2():
    file_path = filedialog.askopenfilename(filetypes=(("Excel files","*.xls*"),))  # 파일 선택 다이얼로그 열기
    answer_path_var.set(file_path)  # 파일 경로를 보여주는 필드에 경로 설정



##########################################################
##########################################################
### 화면 ###



############################
### 시험지 양식 적용 화면 ###
############################
def show_transfer():
    global widgets, file_path_var
    hide_widgets(widgets)
    canvas_r.delete("all")  # 캔버스 초기화
    
    canvas_r.create_text(
        35.0,
        25.0,
        anchor="nw",
        text="1. 시험 정보를 입력 하세요.",
        fill="#000000",
        font=(FONT_PATH, 14 * -1) 
    )
    canvas_r.create_text(
        35,
        70,
        anchor="nw",
        text="응시자수",
        fill="#000000",
        font=(FONT_PATH, 14 * -1)
    )

    #응시자수 입력하는 텍스트필트
    testee_num = tk.StringVar()  
    testee_num_field = tk.Entry(
        bd=0,
        bg="white",  # 배경색 (흰색)
        fg="#000716",  # 텍스트 색상
        highlightbackground="#d9d9d9",  # 테두리 색상
        highlightthickness=1,
        font=(FONT_PATH, 16 * -1),
        textvariable=testee_num
    )
    testee_num_field.place(
        x=330,
        y=65,
        width=170,
        height=25
    )

    canvas_r.create_text(
        35.0,
        130.0,
        anchor="nw",
        text="2. 변환할 시험지 파일을 업로드 하세요. (파일 확장자: .pdf)\n   (선택한 시험지 파일과 같은 위치에 양식이 적용된 새파일이 생성됩니다.)",
        fill="#000000",
        font=(FONT_PATH, 14 * -1)
    )

     
   #시험지 파일 업로드 버튼
    UploadExamSheetsBtn = tk.Button(
        text="시험지 파일 업로드",
        borderwidth=0,
        highlightthickness=0,
        command=browse_file
    )
    UploadExamSheetsBtn.place(
        x=195,
        y=180,
        width=155,
        height=30.0
    )

    #시험지 파일 경로를 전역변수로 사용
    file_path_var = tk.StringVar()

    file_path_label=tk.Label(
        bd=0,
        bg="#dddddd",
        fg="#000716",
        highlightthickness=0,
        textvariable=file_path_var
        )
    file_path_label.place(
        x=360,
        y=180,
        width=390, 
        height=30
    )
    
    #인쇄용 파일 저장 버튼
    SaveNewSheetsBtn = tk.Button(
        text="인쇄용 파일 저장",
        borderwidth=0,
        highlightthickness=0,
        command=lambda: insert_page_number(int(testee_num.get()), file_path_var.get())
    )
    SaveNewSheetsBtn.place(
        x=620,
        y=230,
        width=135,
        height=30.0
    )

    widgets = [testee_num_field, UploadExamSheetsBtn, file_path_label, SaveNewSheetsBtn]



#############################
####### 채점하기 화면 #######
#############################
def show_grade():
    global widgets, file_path_var, answer_path_var
    hide_widgets(widgets)
    canvas_r.delete("all")  # 캔버스 초기화

    # 1. 시험정보를 입력하세요
    canvas_r.create_text(
        40.0,
        20.0,
        anchor="nw",
        text="1. 시험 정보를 입력 하세요.",
        fill="#000000",
        font=(FONT_PATH, 14 * -1)
    )

    # 1-1. 시험명
    canvas_r.create_text(
        40,
        55,
        anchor="nw",
        text="시험명",
        fill="#000000",
        font=(FONT_PATH, 14 * -1)
    )
    
    test_name = tk.StringVar()
    test_name_field = tk.Entry(
        bd=0,
        bg="white",  # 배경색 (흰색)
        fg="#000716",  # 텍스트 색상
        highlightbackground="#d9d9d9",  # 테두리 색상
        highlightthickness=1,
        font=(FONT_PATH, 16 * -1),
        textvariable=test_name
    )
    test_name_field.place(
        x=340, 
        y=50,
        width=140,
        height=23
    )

    # 1-2. 시험지1부당매수
    canvas_r.create_text(
        40,
        90,
        anchor="nw",
        text="시험지 1부당 매수",
        fill="#000000",
        font=(FONT_PATH, 14 * -1)
    )

    copy_num = tk.StringVar()
    copy_num_field = tk.Entry(
        bd=0,
        bg="white",  # 배경색 (흰색)
        fg="#000716",  # 텍스트 색상
        highlightbackground="#d9d9d9",  # 테두리 색상
        highlightthickness=1,
        font=(FONT_PATH, 16 * -1),
        textvariable=copy_num
    )
    copy_num_field.place(
        x=340, 
        y=85,
        width=140,
        height=23
    )
    
    # 1-3. 총문항수  
    canvas_r.create_text(
        40,
        125,
        anchor="nw",
        text="총 문항 수",
        fill="#000000",
        font=(FONT_PATH, 14 * -1)
    )

    total_qna_num = tk.StringVar()
    total_qna_num_field = tk.Entry(
        bd=0,
        bg="white",  # 배경색 (흰색)
        fg="#000716",  # 텍스트 색상
        highlightbackground="#d9d9d9",  # 테두리 색상
        highlightthickness=1,
        font=(FONT_PATH, 16 * -1),
        textvariable=total_qna_num
    )
    total_qna_num_field.place(
        x=340, 
        y=120,
        width=140,
        height=23
    )

    # 1-4. 응시자수
    canvas_r.create_text(
        40,
        160,
        anchor="nw",
        text="응시자수",
        fill="#000000",
        font=(FONT_PATH, 14 * -1)
    )
    
    testee_num = tk.StringVar()
    testee_num_field = tk.Entry(
        bd=0,
        bg="white",  # 배경색 (흰색)
        fg="#000716",  # 텍스트 색상
        highlightbackground="#d9d9d9",  # 테두리 색상
        highlightthickness=1,
        font=(FONT_PATH, 16 * -1),
        textvariable=testee_num
    )
    testee_num_field.place(
        x=340, 
        y=155,
        width=140,
        height=23
    )

    # 1-5. 문제유형
    canvas_r.create_text(
        40,
        195,
        anchor="nw",
        text="문제유형",
        fill="#000000",
        font=(FONT_PATH, 14 * -1)
    )

    # 1-6. 객관식 체크박스 생성
    test_category_mul = tk.IntVar()
    test_category_mul_checkbox = tk.Checkbutton(
        root,
        text="객관식",
        variable=test_category_mul,
        onvalue=1,
        offvalue=0,
        bg="white",  # 체크박스 텍스트 영역의 배경색을 변경
        activebackground="white",  # 마우스가 올려졌을 때 배경색을 변경하지 않음
    ) 
    test_category_mul_checkbox.place(
        x=340, 
        y=190
    )
 
    # 1-7. 단답식 체크박스 생성
    test_category_sub = tk.IntVar()
    test_category_sub_checkbox = tk.Checkbutton(
        root,
        text="단답식",
        variable=test_category_sub,
        onvalue=1,
        offvalue=0,
        bg="white",  # 체크박스 텍스트 영역의 배경색을 변경
        activebackground="white",  # 마우스가 올려졌을 때 배경색을 변경하지 않음
    )
    test_category_sub_checkbox.place(
        x=420,
        y=190
    )

    # 2. 채점할 시험지 파일 업로드하세요
    canvas_r.create_text(
        40,
        250,
        anchor="nw",
        text="2. 채점할 시험지 파일을 업로드 하세요. (파일 확장자: .pdf)",
        fill="#000000",
        font=(FONT_PATH, 14 * -1)
    )

    # 2-1. 시험지 파일 업로드 버튼
    file_path = tk.StringVar()   
    file_path_label=tk.Label(
        bd=0,
        bg="#dddddd",
        fg="#000716",
        highlightthickness=0,
        textvariable=file_path_var
        )
    file_path_label.place(
        x=370,
        y=280.0, 
        width=390,
        height=30
    )
   
    UploadExamSheetsBtn = tk.Button(
        text="시험지 파일 업로드",
        borderwidth=0,
        highlightthickness=0,
        command=browse_file,
        relief="flat"
    )
    UploadExamSheetsBtn.place(
        x=200,
        y=280.0,
        width=150,
        height=30.0
    )

    # 3. 시험지 답을 입력해주세요
    canvas_r.create_text(
        40,
        360,
        anchor="nw",
        text="3. 시험지의 답 파일을 양식에 맞추어 업로드 해주세요.(파일확장자: .xlsx)",
        fill="#000000",
        font=(FONT_PATH, 14 * -1)
    )

    UploadAnswerSheetsBtn = tk.Button(
        text="답 파일 업로드",
        borderwidth=0,
        highlightthickness=0,
        command=browse_file2,
        relief="flat"
    )
    UploadAnswerSheetsBtn.place(
        x=200,
        y=400.0,
        width=150,
        height=30.0
    )

    answer_path_var = tk.StringVar()  
    answer_path_label=tk.Label(
        bd=0,
        bg="#dddddd",
        fg="#000716",
        highlightthickness=0,
        textvariable=answer_path_var
        )
    answer_path_label.place(
        x=370,
        y=400.0, 
        width=390,
        height=30
    )
    
    # 4. 채점 버튼을 클릭하세요
    canvas_r.create_text( 
        40.0,
        490.0,
        anchor="nw",
        text="4. 채점하기 버튼을 클릭하세요. \n\n   채점이 완료되면 ‘결과 다운로드’ 버튼을 클릭하여 채점 결과를 다운로드 하세요.",
        fill="#000000",
        font=(FONT_PATH, 14 * -1)
    )

    # 4-1. 채점하기 버튼
    ### 채점하기 누르면 서버에 연결됨 ###
    StartGradingBtn = tk.Button(
        text="채점하기",
        borderwidth=0,
        highlightthickness=0,
        ### 서버 연결 함수 ###
        command=lambda: server_connect(file_path_var.get(),
                                       answer_path_var.get(),
                                       test_name.get(),
                                       copy_num.get(),
                                       total_qna_num.get(),
                                       testee_num.get(),
                                       [test_category_mul.get(), test_category_sub.get()]),
        relief="flat"
    )
    StartGradingBtn.place(
        x=200,
        y=560,
        width=125,
        height=30
    )

    # 4-2. 진행 막대 생성
    progress_bar = ttk.Progressbar(root, orient="horizontal", length=260, mode="indeterminate")
    progress_bar.place(x=350, y=565)

    # 4-3. 채점 결과 확인하기 버튼
    ViewGradingResultsBtn = tk.Button(
        text="채점 결과 확인하기",
        borderwidth=0,
        highlightthickness=0,
        command=show_result,
        relief="flat"
    ) 
    ViewGradingResultsBtn.place(
        x=630,
        y=560,
        width=125,
        height=30
    )

    ## home_widgets 리스트 정의 ##
    widgets = [testee_num_field, total_qna_num_field, copy_num_field, test_name_field, test_category_mul_checkbox, test_category_sub_checkbox, UploadExamSheetsBtn, file_path_label, UploadAnswerSheetsBtn, answer_path_label, StartGradingBtn, progress_bar, ViewGradingResultsBtn]


#####################################
####### 채점 결과 확인하기 화면 #######
#####################################
def show_result():
    global widgets
    hide_widgets(widgets)
    canvas_r.delete("all")  # 캔버스 초기화

    # 1. 채점 결과 확인
    canvas_r.create_text(
        40.0,
        20.0,
        anchor="nw",
        text="1. 채점 결과를 확인하세요.",
        fill="#000000",
        font=(FONT_PATH, 14 * -1)
    )
    button_1 = tk.Button(
        text="채점 결과 다운로드",
        borderwidth=0,
        highlightthickness=0,
        command=lambda: print("clicked 채점 결과 다운로드"),
        relief="flat"
    )
    button_1.place(
        x=600,
        y=20,
        width=125,
        height=30
    )
    
    #결과 확인용 임시 textarea
    T = tk.Text(root, height=40, width=80)
    T.place(
        x=200,
        y=60
    )

    #텍스트 삽입문 아래 큰따옴표 안에 원하는 텍스트 넣으면 됨
    T.insert(tk.END, "HELLO")
    
    ## widgets 리스트 정의 ##
    widgets = [button_1]


# 메인 창 생성
root = tk.Tk()
root.title("POINTCHECKER")
root.geometry("800x660")
root.resizable(False, False)
root.configure(bg = "#FFDED7")#"#FFFFFF")
root.iconbitmap(ICON_PATH)

# 창을 화면 중앙에 배치
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()
window_width = 800
window_height = 660
x = (screen_width - window_width) // 2
y = (screen_height - window_height) // 2
root.geometry("{}x{}+{}+{}".format(window_width, window_height, x, y))

# 오른쪽에 캔버스 생성
canvas_r = tk.Canvas(
    root,
    bg = "#FFFFFF",
    height = 660,
    width = 650,
    bd = 0,
    highlightthickness = 0,
    relief = "ridge"
) 
canvas_r.pack(side=tk.RIGHT, padx=0, pady=0)

# 툴바 버튼 생성 
photo = PhotoImage(file = ASSETS_PATH / "btn_img/tool1.png")
transfer_button = tk.Button(root, image=photo, command=show_transfer, bg="#FFDED7", borderwidth=-1)
transfer_button.pack(padx=10, pady=10)

photo2 = PhotoImage(file = ASSETS_PATH / "btn_img/tool2.png")
home_button = tk.Button(root, image=photo2, command=show_grade, bg="#FFDED7", borderwidth=-1) 
home_button.pack( padx=10, pady=10) 

# 메인 화면 설정
show_transfer()

# 메인 루프 실행
root.mainloop()
