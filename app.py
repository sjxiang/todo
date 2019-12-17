from flask import Flask, render_template
app = Flask(__name__)



name = "xsj"

todos = [
    {
        "title": "The Litter Scheme",
        "type": "PL",
     },
    {
        "title": "OSTEP",
        "type": "OS",
    },
    {
        "title": "计算机程序的构造和解释",
        "type": "PL",
    },
    {
        "title": "算法设计与分析",
        "type": "Algorithm",
    },
]

@app.route("/")
def hello():
    return render_template("index.html", name=name, todos=todos)