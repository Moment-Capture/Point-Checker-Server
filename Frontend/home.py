if __name__ == "__main__":
    from multiprocessing import freeze_support
    freeze_support()


import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter import ttk
from tkinter import *

import os
import fitz
import json

import pandas as pd
from threading import Thread
from pandastable import Table

from path import *
from server import *



##########################################################
##########################################################
### 함수 및 변수 ###

## 전역변수 ##
widgets = []
entry_columns = []
file_path_var = None
answer_path_var = None
json_data = None
file_name = ""
is_scoring_finished = 1


## 공통  ##

## 공통 버튼 스타일 ##
button_style = {
    "bg": "#FCB6A8",     # 배경색
    "fg": "white",       # 텍스트 색상
    "font": (FONT_PATH, 12),  # 폰트 및 크기
    "relief": RIDGE      # 외곽선 스타일
}


### 위젯 숨기는 함수 ###
def hide_widgets(widget_list):
    for widget in widget_list:
        widget.place_forget()


### test_category 숫자 변환 ###
def int_to_string(test_category):
    for cate in test_category:
        if cate == 0:
            cate = "0"
        else:
            cate = "1"


##1. 시험지 양식 적용 화면 함수##
def browse_file():
    file_path = filedialog.askopenfilename(filetypes=(("pdf files","*.pdf*"),))  # 파일 선택 다이얼로그 열기
    file_path_var.set(file_path)  # 파일 경로를 보여주는 필드에 경로 설정

def insert_page_number(num_students, file_path):
    # Open the PDF
    pdf_document = fitz.open(file_path)
    num_pages = len(pdf_document)

    first_page = pdf_document[0]
    # first_page = pdf_document.newPage()

    # Get page width and height
    page_width = first_page.rect.width
    page_height = first_page.rect.height

    # Convert start and end points to coordinates relative to top-right corner
    start_point = (page_width - 180, 65)
    end_point = (page_width - 60, 65)

    for i in range(0, num_students):
        output_pdf_path = os.path.splitext(file_path)[0] + "_new" + f"_{i+1}.pdf"

        #첫 장에 이름 적는 칸
        page = pdf_document[0]
        rotation = page.rotation
        # page.clean_contents()
        # page = pdf_document.newPage()
        page.wrap_contents()
        text = "ID : "
        point = fitz.Point(page_width-220, 60)
        page.insert_text(point*page.derotation_matrix, text, fontsize=16, fontname="courier", rotate=rotation)
        page.draw_line(start_point, end_point)

        for j in range(0, num_pages):
            # 삽입할 숫자 (예: "1-1", "1-2", ...)
            text = f"{i+1}-{j+1}"

            # 삽입할 위치 (x, y 좌표)
            insert_position = fitz.Point(60, 60)  # 적절한 위치로 수정 필요

            # Select the first page
            page = pdf_document[j]

            # Start editing the page
            page.insert_text(insert_position*page.derotation_matrix, text, fontsize=18, fontname="courier", rotate=rotation)

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
        text="2. 변환할 시험지 파일을 업로드 하세요. (파일 확장자: .pdf)\n   (선택한 시험지 파일과 같은 위치에 양식이 적용된 새 파일이 생성됩니다.)",
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

    # 1-2. 응시자수
    canvas_r.create_text(
        40,
        90,
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
        y=85,
        width=140,
        height=23
    )

    # 1-3. 시험지 1부당 매수
    canvas_r.create_text(
        40,
        125,
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
        y=120,
        width=140,
        height=23
    )
    
    # 1-4. 총 문항 수  
    canvas_r.create_text(
        40,
        160,
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

    # 1-5-1. 객관식 체크박스 생성
    test_category_mul = tk.IntVar(value=0)
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
 
    # 1-5-2. 단답식 체크박스 생성
    test_category_sub = tk.IntVar(value=0)
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
    file_path_var = tk.StringVar()   
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
    
    # 응시자수, 한부당 매수 확인 후 서버 전달
    def check_entries_and_start_grading():
        global is_scoring_finished

        if not is_scoring_finished:
            print()
            print("채점 진행 중")
            print()
        
            tk.messagebox.showinfo("안내", "채점이 진행 중입니다.")

            return 
        
        # 텍스트 필드가 모두 채워졌는지 확인
        if testee_num.get() and copy_num.get() and total_qna_num.get() and file_path_var.get() and answer_path_var.get() and test_name.get():
            global file_name
            file_name = str(test_name.get())

            progress_bar.start(20)

            is_scoring_finished = 0

            tThread = Thread(target=start_connect, args=(file_path_var.get(), test_name.get(), copy_num.get(), total_qna_num.get(),
                        testee_num.get(), [str(test_category_mul.get()), str(test_category_sub.get())], progress_bar))
            tThread.setDaemon(True)
            tThread.start()

        else:
            # 시험 정보가 모두 입력되지 않은 경우 안내창 표시
            print("시험 정보가 다 안 채워짐")
            tk.messagebox.showinfo("안내", "시험 정보를 다 입력하세요.")


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
        command=lambda: check_entries_and_start_grading(),
        relief="flat"
    )
    StartGradingBtn.place(
        x=200,
        y=560,
        width=125,
        height=30
    )

    # 4-2. 진행 막대 생성
    progress_bar = ttk.Progressbar(root, orient="horizontal", length=260, mode="determinate")
    progress_bar.place(x=350, y=565)

    # 4-3. 채점 결과 확인하기 버튼
    ViewGradingResultsBtn = tk.Button(
        text="채점 결과 확인하기",
        borderwidth=0,
        highlightthickness=0,
        command=lambda:show_result(),
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

#pandastable 띄우기
class PandasViewer(tk.Frame):
    def __init__(self, parent=None, dataframe=None):
        super().__init__(parent)
        self.parent = parent
        self.dataframe = dataframe
        self.table = None
        self.initialize()

    def initialize(self):
        self.parent.title("채점 결과 확인")
        
        # PandasTable 프레임 생성
        frame = tk.Frame(self.parent)
        frame.pack(fill='both', expand=True)

        # PandasTable table 생성
        self.table = Table(frame, dataframe=self.dataframe, showtoolbar=False, showstatusbar=True, showindex=True, width=1000, height=700)
        self.table.show()

        #excel로 저장하는 버튼 생성
        export_button = tk.Button(self.parent, text="Export to Excel", command=self.export_to_excel)
        export_button.pack(side = tk.RIGHT, padx=10, pady=10)

    def export_to_excel(self):
        global file_name
        ftypes = [('excel file', '.xlsx'), ('csv file', '.csv'), ('All files', '*')]
        init_file = file_name + ".xlsx"
        file_path = filedialog.asksaveasfilename(filetypes=ftypes, initialfile=init_file, defaultextension=".xlsx")
        if file_path:
            self.dataframe.to_excel(file_path, index=True)


# 답 파일을 딕셔너리로 바꾸는 함수
def answer_to_dict(answer_path_var):
    # 파라미터로 입력 받을 예정
    file_path = answer_path_var

    # 엑셀 파일 읽기
    df_answer = pd.read_excel(file_path, names=["문항번호", "정답"], engine='openpyxl')
    data_dict = {'answer': {str(key): str(value) for key, value in df_answer.set_index('문항번호')['정답'].to_dict().items()}}

    return data_dict


# 서버에서 json data를 받아서 채점 결과 df 만드는 함수
def json_to_df_for_tables(data):
    data = json.loads(data)

    # 답 딕셔너리 가져오기
    question_answer = answer_to_dict(answer_path_var.get())

    # 필요한 정보 testee_id별 'num':'testee_answer'를 딕셔너리로 저장하는 함수 
    testee_answers = {}
    total_num = len(question_answer["answer"])
    count_o = 0

    for entry in data:
        testee_id = entry.get('testee_id')
        num = str(entry.get('num'))
        testee_answer = entry.get('testee_answer')

        if testee_id not in testee_answers:
            count_o = 0
            testee_answers[testee_id] = {}
            testee_answers[testee_id+" O/X"] = {}
            testee_answers[testee_id+" O/X"]['정답'] = ""
            testee_answers[testee_id+" O/X"]['오답'] = ""
            testee_answers[testee_id+" O/X"]['총 문항수'] = str(total_num)

            for ans_num in question_answer['answer']:
                if ans_num not in testee_answers[testee_id]:
                    testee_answers[testee_id][ans_num] = ""
                if ans_num not in testee_answers[testee_id+" O/X"]:
                    testee_answers[testee_id+" O/X"][ans_num] = 'X'

        if not num in question_answer["answer"]:
            continue

        # 다중 정답일 경우 대괄호를 제외하고 문자열로 저장
        if isinstance(testee_answer, list):
            testee_answer = ','.join(map(str, testee_answer))
        else:
            testee_answer = str(testee_answer)

        testee_answers[testee_id][num] = testee_answer

        if testee_answer == question_answer['answer'][num].replace(" ", ""):
            count_o += 1
            testee_answers[testee_id+" O/X"][num] = 'O'
        
        testee_answers[testee_id+" O/X"]['정답'] = str(count_o)

        testee_answers[testee_id+" O/X"]['오답'] = str(total_num-count_o)


    # 답 딕셔너리와 응시자 답안 딕셔너리를 합쳐서 data로 삽입
    df = pd.DataFrame.from_dict(data={**question_answer, **testee_answers}, orient='index', dtype='str')

    return df


def show_result():
    global json_data
    data = json_data

    global is_scoring_finished

    if not is_scoring_finished:
        print()
        print("채점 진행 중")
        print()
        
        tk.messagebox.showinfo("안내", "채점이 진행 중입니다.")

        return 

    if not json_data:
        print()
        print("채점 진행 중")
        print()
        
        tk.messagebox.showinfo("안내", "채점이 진행 중입니다.")
        
        return    
    
    # Initialize Tkinter
    root2 = tk.Toplevel()

    # Create the PandasViewer instance
    viewer = PandasViewer(root2, dataframe=json_to_df_for_tables(data))

    # Run the Tkinter event loop
    root2.mainloop()

# 메인 창 생성
root = tk.Tk()
root.title("POINT-CHECKER")
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
photo = PhotoImage(file = TOOL1_PATH)
transfer_button = tk.Button(root, image=photo, command=show_transfer, bg="#FFDED7", borderwidth=-1)
transfer_button.pack(padx=10, pady=10)

photo2 = PhotoImage(file = TOOL2_PATH)
home_button = tk.Button(root, image=photo2, command=show_grade, bg="#FFDED7", borderwidth=-1) 
home_button.pack( padx=10, pady=10) 

# 메인 화면 설정
show_transfer()

# 메인 루프 실행
root.mainloop()
