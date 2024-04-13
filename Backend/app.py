from flask import Flask

import os
import pandas as pd

from main import getFinalDf

app = Flask(__name__)

@app.route("/")
def hello():
    return "Hello, World!"

@app.route("/demo")
def view_demo():
    # os.chdir("D:\michelle\PointCheckerProject\Flask")
    df = pd.DataFrame()
    df = main()
    json_data = df.to_json(orient="records")
    return json_data

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)