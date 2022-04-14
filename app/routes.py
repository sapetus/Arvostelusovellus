import base64
from app import app
from flask import make_response, render_template, redirect, request, session, abort
from db import db
from utils import user, review, review_item, categories, picture


@app.errorhandler(404)
def error_404(error):
    return render_template("error.html", message="Page you tried to reach does not exist")


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
            return render_template("login.html", error="Wrong credentials")


@app.route("/logout")
def logout():
    del session["username"]
    del session["token"]
    return redirect("/")


@app.route("/register", methods=["POST", "GET"])
def register():
    if request.method == "GET":
        return render_template("register.html")
    if request.method == "POST":
        username = request.form["username"]

        if user.check_username(username):
            return render_template("register.html", error="Username already taken")

        password = request.form["password"]
        password_confirmation = request.form["password_confirmation"]

        if (len(username) > 20 or len(username) < 2) or (len(password) > 50 or len(password) < 5):
            return render_template("register.html",
                                   error="Username needs to be between 2-20 characters and \
                                            password needs to be between 5-50 characters.")

        if not password or not username:
            return render_template("register.html", error="Username and password are required!")
        if password != password_confirmation:
            return render_template("register.html", error="Passwords need to match!")
        if user.register(username, password):
            return redirect("/")
        else:
            return render_template("register.html", error="Registration failed, please try again.")


@app.route("/category/<category>", methods=["POST", "GET"])
def category(category):
    cats = categories.get_categories()
    if not category.capitalize() in cats:
        abort(404)

    review_items = review_item.get_review_items_by_category(category)
    admin = user.is_admin(session.setdefault("username", None))

    if request.method == "GET":
        return render_template("category.html", category=category, review_items=review_items, admin=admin)
    if request.method == "POST":
        if not user.check_user(request.form["token"]):
            return render_template("category.html", error="Forbidden action",
                                   category=category, review_items=review_items, admin=admin)

        name = request.form["name"]
        publication_date = request.form["publication_date"]
        description = request.form["description"]
        item_category = request.form["category"]

        if len(description) > 1000 or len(description) < 10:
            return render_template("category.html", error="Description has a length of 10-1000 characters.",
                                   category=category, review_items=review_items, admin=admin)
        if len(name) > 500 or len(name) < 1:
            return render_template("category.html", error="Name has a length of 1-500 characters.",
                                   category=category, review_items=review_items, admin=admin)
        if review_item.create(name, publication_date, item_category.upper(), description):
            return redirect(request.url)

        return render_template("category.html", error="Something went wrong when trying to create a new review item.",
                               category=category, review_items=review_items, admin=admin)


@app.route("/category/<category>/<int:id>", methods=["POST", "GET"])
def item(id, category):
    item = review_item.get_review_item(id)

    if not item:
        abort(404)

    rating = review_item.average_rating(id)
    reviews = review.get_reviews_for_review_item(id)

    admin = user.is_admin(session.setdefault("username", None))

    if request.method == "GET":
        return render_template("review_item.html", review_item=item, rating=rating,
                               reviews=reviews, admin=admin, category=category)
    if request.method == "POST":
        if not user.check_user(request.form["token"]):
            return render_template("review_item.html", error="Forbidden action", review_item=item,
                                   rating=rating, reviews=reviews, admin=admin, category=category)

        rating = request.form["rating"]
        text = request.form["review"]
        review_item_id = request.form["review_item_id"]
        user_id = user.user_id(session["username"])

        if rating == "" or int(rating) > 10 or int(rating) < 1:
            return render_template("review_item.html", error="Rating needs to be between 1 and 10.",
                                   review_item=item, rating=rating, reviews=reviews, admin=admin, category=category)
        if len(text) > 1000 or len(text) < 10:
            return render_template("review_item.html", error="Review has a length of 10-1000 characters.",
                                   review_item=item, rating=rating, reviews=reviews, admin=admin, category=category)
        if review.check_if_user_has_reviewed(user_id, review_item_id):
            return render_template("review_item.html", error="You have already reviewd this item.",
                                   review_item=item, rating=rating, reviews=reviews, admin=admin, category=category)
        if review.create(int(rating), text, review_item_id, user_id):
            return redirect(request.url)

        return render_template("review_item.html", error="Something went wrong when trying to create a review.",
                               review_item=item, rating=rating, reviews=reviews, admin=admin, category=category)


@app.route("/category/<category>/<int:id>/modify", methods=["POST", "GET"])
def update_review_item(id, category):
    admin = user.is_admin(session.setdefault("username", None))

    if request.method == "GET":
        token = user.check_user(request.args.get("token"))
        if admin and token:
            item = review_item.get_review_item(id)
            print(item)
            return render_template("review_item_modify.html", review_item=item)
        else:
            return render_template("error.html", message="Forbidden action")
    if request.method == "POST":
        token = request.form["token"]
        if admin and token:
            name = request.form["name"]
            publication_date = request.form["publication_date"]
            description = request.form["description"]
            if review_item.update(name, description, publication_date, id):
                return redirect("/category/" + str(category) + "/" + str(id))
            else:
                return render_template("error.html", message="Something went wront when trying to update review item")
        else:
            return render_template("error.html", message="Forbidden action")


@app.route("/category/<category>/<int:id>/delete", methods=["POST"])
def delete_review_item(id, category):
    admin = user.is_admin(session.setdefault("username", None))
    token = user.check_user(request.form["token"])

    if admin and token:
        if review_item.delete(id):
            return redirect("/category/" + str(category))
        else:
            return render_template("error.html", message="Something went wrong when trying to delete review item")
    else:
        return render_template("error.html", message="Forbidden action")


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
            category = request.args.get("category")
            item = request.args.get("item")
            url = "/category/" + str(category) + "/" + str(item)
            return redirect(url)

    return render_template("error.html", message="Something went wront when trying to delete a review.")


@app.route("/user/<username>")
def user_page(username):
    if not user.check_username(username):
        abort(404)

    user_information = user.get_user_information(username)
    reviews = review.get_reviews_for_user(username)
    profile_picture = picture.get_profile_picture(user.user_id(username))

    allowed_to_modify = False
    if session.get("username", None) == username:
        allowed_to_modify = True

    if profile_picture:
        encoded_picture = base64.b64encode(
            bytes(profile_picture)).decode('utf-8')
        response = make_response(bytes(profile_picture))
        response.headers.set("Content-Type", "image/jpg")
        return render_template("user.html", user_information=user_information,
                               username=username, reviews=reviews, allowed_to_modify=allowed_to_modify,
                               profile_picture=encoded_picture)
    else:
        return render_template("user.html", user_information=user_information,
                               username=username, reviews=reviews, allowed_to_modify=allowed_to_modify)


@app.route("/user/<username>/delete", methods=["POST"])
def user_delete(username):
    if (not username == session.get("username", None)) or (not user.check_user(request.form["token"])):
        return render_template("error.html", message="Forbidden action")

    if not user.delete_user(username):
        return render_template("error.html", message="Could not delete given user")

    return redirect("/")


@app.route("/user/<username>/modify", methods=["POST", "GET"])
def user_page_modify(username):
    if not username == session.get("username", None):
        return redirect("/")

    cats = categories.get_categories()
    current_category = user.get_user_information_by_key("favourite_category",
                                                        user.user_id(username))

    if request.method == "GET":
        return render_template("user_modify.html", username=username, categories=cats, current_category=current_category)

    if request.method == "POST":
        if not user.check_user(request.form["token"]):
            return render_template("error.html", message="Forbidden action")

        profile_picture = request.files["profile_picture"]
        picture_data = profile_picture.read()
        favourite_category = request.form["category"]

        if current_category:
            if not user.update_user_information("favourite_category", favourite_category, user.user_id(username)):
                return render_template("error.html", message="Something went wrong when trying to update user information")
        else:
            if not user.add_user_information("favourite_category", favourite_category, user.user_id(username)):
                return render_template("error.html", message="Something went wrong when trying to save user information")

        # This is a mess. Try to clean it up
        if profile_picture.filename:
            # if larger than 1MB
            if len(picture_data) > 1000*1024:
                return render_template("user_modify.html", error="File has maximum size of 1MB",
                                       username=username, categories=cats, current_category=current_category)
            # if file is of allowed type
            content_type = profile_picture.content_type
            if content_type.endswith('jpeg') or content_type.endswith('png') or content_type.endswith('jpg'):
                # if this user already has a picture, replace it
                if picture.get_profile_picture(user.user_id(username)):
                    if not picture.update_profile_picture(user.user_id(username), picture_data):
                        return render_template("error.html", message="Something went wrong when trying to update profile picture")
                else:
                    # try to save picture, if failed, return error page
                    if not picture.save_profile_picture(user.user_id(username), picture_data):
                        return render_template("error.html", message="Something went wrong when trying to save profile picture")
                    else:
                        return redirect("/")
            else:
                return render_template("user_modify.html", message="File needs to be either JPG/JPEG or PNG",
                                       username=username, categories=cats, current_category=current_category)

        url = "/user/" + str(username)
        return redirect(url)
