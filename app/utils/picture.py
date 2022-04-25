from db import db


def get_profile_picture(id):
    sql = "SELECT picture FROM picture WHERE user_account_id=:user_account_id"
    result = db.session.execute(sql, {"user_account_id": id})
    picture = result.fetchone()

    if picture:
        return picture[0]

    return False


def save_profile_picture(id, picture):
    try:
        sql = "INSERT INTO picture (user_account_id, picture) VALUES (:user_account_id, :picture)"
        db.session.execute(sql, {"user_account_id": id, "picture": picture})
        db.session.commit()
        return True
    except:
        return False


def update_profile_picture(id, picture):
    try:
        sql = "UPDATE picture SET picture=:picture WHERE user_account_id=:id"
        db.session.execute(sql, {"picture": picture, "id": id})
        db.session.commit()
        return True
    except:
        return False


def get_item_picture(id):
    sql = "SELECT picture FROM picture WHERE review_item_id=:review_item_id"
    result = db.session.execute(sql, {"review_item_id": id})
    picture = result.fetchone()

    if picture:
        return picture[0]

    return False


def save_item_picture(id, picture):
    try:
        sql = "INSERT INTO picture (review_item_id, picture) VALUES (:review_item_id, :picture)"
        db.session.execute(sql, {"review_item_id": id, "picture": picture})
        db.session.commit()
        return True
    except:
        return False


def update_item_picture(id, picture):
    try:
        sql = "UPDATE picture SET picture=:picture WHERE review_item_id=:id"
        db.session.execute(sql, {"picture": picture, "id": id})
        db.session.commit()
        return True
    except:
        return False
