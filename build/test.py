import tkinter as tk

def open_file():
    print("File opened")

def save_file():
    print("File saved")

def exit_app():
    root.quit()

# 메인 창 생성
root = tk.Tk()

# 파일 열기 버튼
open_button = tk.Button(root, text="Open", command=open_file)
open_button.pack(side=tk.TOP, padx=5, pady=5, fill=tk.X)

# 파일 저장 버튼
save_button = tk.Button(root, text="Save", command=save_file)
save_button.pack(side=tk.TOP, padx=5, pady=5, fill=tk.X)

# 종료 버튼
exit_button = tk.Button(root, text="Exit", command=exit_app)
exit_button.pack(side=tk.TOP, padx=5, pady=5, fill=tk.X)

# 메인 루프 실행
root.mainloop()
