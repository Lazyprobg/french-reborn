from flask import Flask, render_template, request, redirect, url_for
app = Flask(__name__)
@app.route("/")
def home():
    return "index.html"
@app.route("/menu")
def menu():
    return
render_template("menu.html")

app.run(host="0.0.0.0", port=5000)




