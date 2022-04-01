import base64
from re import I
from app import app
from flask import make_response, render_template, redirect, request, session
from db import db
from utils import user, review, review_item, categories, picture


@app.route("/")
def index():
    cats = categories.get_categories()
    admin = user.is_admin(session.setdefault("username", None))

    return render_template("index.html", categories=cats, admin=admin)


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
        result = db.session.execute(sql, {"category": category.upper()})
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
        if review_item.create(name, publication_date, item_category.upper(), description):
            return redirect(request.url)

        return render_template("error.html", message="Something went wrong when trying to create a new review item.")


@app.route("/category/<category>/<int:id>", methods=["POST", "GET"])
def item(id, category):
    if request.method == "GET":
        item = review_item.get_review_item(id)
        rating = review_item.average_rating(id)
        reviews = review.get_reviews_for_review_item(id)

        admin = user.is_admin(session.setdefault("username", None))

        return render_template("review_item.html", review_item=item, rating=rating, reviews=reviews, admin=admin)
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
    # checks if the user trying to delete the review is the same as the one who created it
    sql = "SELECT 1 FROM review \
           JOIN user_account ON review.user_account_id = user_account.id \
           WHERE user_account.username=:username AND review.id=:id"
    result = db.session.execute(
        sql, {"username": session.get("username", None), "id": id})
    same_user = result.fetchone()[0]

    # if the user trying to delete the review is admin or is the same user who created it, delete review
    if admin or same_user == 1:
        if review.delete(id):
            return redirect("/")

    return render_template("error.html", message="Something went wront when trying to delete a review.")


@app.route("/user/<username>")
def user_page(username):
    user_information = user.get_user_information(username)
    reviews = review.get_reviews_for_user(username)
    profile_picture = picture.get_profile_picture(user.user_id(username))

    allowed_to_modify = False
    if session.get("username", None) == username:
        allowed_to_modify = True

    if profile_picture: 
        encoded_picture = base64.b64encode(bytes(profile_picture)).decode('utf-8')
        response = make_response(bytes(profile_picture))
        response.headers.set("Content-Type", "image/jpg")
        return render_template("user.html", user_information=user_information,
                            username=username, reviews=reviews, allowed_to_modify=allowed_to_modify,
                            profile_picture=encoded_picture)
    else:
        return render_template("user.html", user_information=user_information,
                            username=username, reviews=reviews, allowed_to_modify=allowed_to_modify)


@app.route("/user/<username>/modify", methods=["POST", "GET"])
def user_page_modify(username):
    if not username == session.get("username", None):
        return redirect("/")

    if request.method == "GET":
        cats = categories.get_categories()
        return render_template("user_modify.html", username=username, categories=cats)

    if request.method == "POST":
        profile_picture = request.files["profile_picture"]
        picture_data = profile_picture.read()
        favourite_category = request.form["category"]

        # change query to overwrite users old information (currently duplicates)
        if not user.add_user_information("favourite_category", favourite_category, user.user_id(username)):
            return render_template("error.html", message="Something went wrong when trying to save user information")

        # implement some logic here to remove users old picture 
        if profile_picture.filename:
            # if larger than 1MB
            if len(picture_data) > 1000*1024:
                return render_template("error.html", message="File has maximum size of 1MB")
            # if file is of allowed type
            content_type = profile_picture.content_type
            if content_type.endswith('jpeg') or content_type.endswith('png') or content_type.endswith('jpg'):
                # try to save picture, if failed, return error page
                if not picture.save_profile_picture(user.user_id(username), picture_data):
                    return render_template("error.html", message="Something went wrong when trying to save profile picture")
                else:
                    return redirect("/")
            else:
                return render_template("error.html", message="File needs to be either JPG/JPEG or PNG")

        return redirect("/")
