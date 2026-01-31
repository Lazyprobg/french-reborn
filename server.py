from flask import Flask
app = Flask(__name__)
@app.route("/")
def home():
    return "index.html"
@app.route("/menu")
def home():
    return
render_template("Menu.html")

app.run(host="0.0.0.0", port=5000)

