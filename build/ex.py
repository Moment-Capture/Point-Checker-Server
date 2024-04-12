import tkinter as tk

def show_home():
    content_label.config(text="Home Screen")

def show_about():
    content_label.config(text="About Page")

def show_contact():
    content_label.config(text="Contact Page")

# 메인 창 생성
window = tk.Tk()
window.title("POINTCHECKER")
window.geometry("800x660")
window.configure(bg = "#FFFFFF")

# 왼쪽에 툴바 생성
toolbar_frame = tk.Frame(window)
toolbar_frame.pack(side=tk.LEFT, fill=tk.Y)

# 오른쪽에 내용을 표시할 레이블
content_label = tk.Label(window, text="Welcome!", font=("Arial", 16))
content_label.pack(side=tk.RIGHT, padx=20, pady=20)

# 툴바 버튼 생성
home_button = tk.Button(toolbar_frame, text="Home", command=show_home)
home_button.pack(fill=tk.X, padx=10, pady=5)

about_button = tk.Button(toolbar_frame, text="About", command=show_about)
about_button.pack(fill=tk.X, padx=10, pady=5)

contact_button = tk.Button(toolbar_frame, text="Contact", command=show_contact)
contact_button.pack(fill=tk.X, padx=10, pady=5)

# 초기 내용 표시
show_home()

# 메인 루프 실행
window.mainloop()
