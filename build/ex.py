import tkinter as tk
import requests
from flask import Flask

# 플라스크 애플리케이션 생성
app = Flask(__name__)

# 플라스크 라우트 정의
@app.route('/your_flask_route')
def your_function():
    # 버튼을 눌렀을 때 실행될 기능을 정의합니다.
    return '플라스크 서버로부터의 응답입니다.'

def button_clicked():
    # 버튼을 클릭했을 때 실행되는 함수
    response = requests.get('http://localhost:5000/your_flask_route')
    print(response.text)  # 플라스크에서 받은 응답을 출력합니다.

# Tkinter 애플리케이션 생성
tk_app = tk.Tk()
tk_app.title("GUI 버튼 예제")

button = tk.Button(tk_app, text="플라스크 서버에 요청 보내기", command=button_clicked)
button.pack()

# 플라스크 서버 실행
if __name__ == '__main__':
    app.run(debug=True, threaded=True)

tk_app.mainloop()