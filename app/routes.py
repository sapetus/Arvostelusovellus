from app import app
from flask import render_template, redirect, request, session
from db import db
import user
import review
import review_item


@app.route("/")
def index():
    sql = "SELECT enum_range(NULL::CATEGORY)"
    result = db.session.execute(sql)
    data = result.fetchone()[0]
    data = data[1:-1]
    categories = data.split(",")
    admin = user.is_admin(session.setdefault("username", None))

    return render_template("index.html", categories=categories, admin=admin)


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


@app.route("/logout")
def logout():
    del session["username"]
    return redirect("/")


@app.route("/register", methods=["POST", "GET"])
def register():
    if request.method == "GET":
        return render_template("register.html")
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        password_confirmation = request.form["password_confirmation"]
        if not password or not username:
            return render_template("error.html", message="Username and password are required!")
        if password != password_confirmation:
            return render_template("error.html", message="Passwords need to match!")
        if user.register(username, password):
            return redirect("/")
        else:
            return render_template("error.html", message="Registration failed, please try again.")


@app.route("/category/<category>", methods=["POST", "GET"])
def category(category):
    if request.method == "GET":
        sql = "SELECT name, id FROM review_item WHERE category=:category"
        result = db.session.execute(sql, {"category": category})
        review_items = result.fetchall()

        admin = user.is_admin(session.setdefault("username", None))

        return render_template("category.html", category=category, review_items=review_items, admin=admin)
    if request.method == "POST":
        name = request.form["name"]
        publication_date = request.form["publication_date"]
        description = request.form["description"]
        item_category = request.form["category"]

        if len(description) > 1000:
            return render_template("error.html", message="Description has a maximum length of 1000 characters.")
        if len(name) > 500:
            return render_template("error.html", message="Name has a maximum length of 500 characters.")
        if review_item.create(name, publication_date, item_category, description):
            return redirect(request.url)

        return render_template("error.html", message="Something went wrong when trying to create a new review item.")


@app.route("/category/<category>/<int:id>", methods=["POST", "GET"])
def item(id, category):
    if request.method == "GET":
        # Possible to merge these queries?
        item_query = "SELECT * FROM review_item WHERE id=:id"
        item_result = db.session.execute(item_query, {"id": id})
        review_item = item_result.fetchone()

        rating_query = "SELECT AVG(rating)::numeric(10,1) FROM review WHERE review_item_id=:id"
        rating_result = db.session.execute(rating_query, {"id": id})
        rating = rating_result.fetchone()[0]

        reviews_query = "SELECT id, user_account_id, rating, text FROM review WHERE review_item_id=:id"
        reviews_result = db.session.execute(reviews_query, {"id": id})
        reviews = reviews_result.fetchall()

        admin = user.is_admin(session.setdefault("username", None))

        return render_template("review_item.html", review_item=review_item, rating=rating, reviews=reviews, admin=admin)
    if request.method == "POST":
        rating = int(request.form["rating"])
        text = request.form["review"]
        review_item_id = request.form["review_item_id"]
        user_id = user.user_id(session["username"])

        if rating > 10 or rating < 1:
            return render_template("error.html", message="Rating needs to be between 1 and 10.")
        if len(text) > 1000:
            return render_template("error.html", message="Review has a maximum length of 1000 characters.")
        if review.create(rating, text, review_item_id, user_id):
            return redirect(request.url)

        return render_template("error.html", message="Something went wrong when trying to create a review.")


@app.route("/delete_review/<int:id>")
def delete_review(id):
    admin = user.is_admin(session.setdefault("username", None))

    if admin:
        if review.delete(id):
            return redirect("/")

    return render_template("error.html", message="Something went wront when trying to delete a review.")


@app.route("/user/<username>")
def user_page(username):
    user_information = user.get_user_information(username)

    return render_template("user.html", user_information=user_information, username=username)