from app import app
from flask import render_template, redirect, request
from db import db
import user


@app.route("/")
def index():
    sql = "SELECT * FROM user_account"
    result = db.session.execute(sql)
    users = result.fetchall()
    return render_template("index.html", users=users)


@app.route("/login", methods=["POST", "GET"])
def login():
    if request.method == "GET":
        return render_template("login.html")
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        if user.login(username, password):
            return redirect("/")
        else:
            return render_template("error.html", message="Wrong credentials")


@app.route("/register", methods=["POST", "GET"])
def register():
    if request.method == "GET":
        return render_template("register.html")
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        password_confirmation = request.form["password_confirmation"]
        if password != password_confirmation:
            return render_template("error.html", message="Passwords need to match!")
        if user.register(username, password):
            return redirect("/")
        else:
            return render_template("error.html", message="Registration failed, please try again.")
