from db import db


def check_if_user_has_reviewed(user_id, review_item_id):
    sql = "SELECT 1 FROM review WHERE review_item_id=:review_item_id AND\
         user_account_id=:user_account_id"
    result = db.session.execute(
        sql, {"review_item_id": review_item_id, "user_account_id": user_id})
    has_reviewed = result.fetchone()
    if has_reviewed and has_reviewed[0] == 1:
        print("here!")
        return True
    return False


def create(rating, text, review_item_id, user_id):
    try:
        sql = "INSERT INTO review (rating, text, review_item_id, user_account_id) \
            VALUES (:rating, :text, :review_item_id, :user_account_id)"
        db.session.execute(
            sql, {"rating": rating, "text": text,
                  "review_item_id": review_item_id, "user_account_id": user_id})
        db.session.commit()
    except:
        return False
    return True


def delete(id):
    try:
        sql = "DELETE FROM review WHERE id=:id"
        db.session.execute(sql, {"id": id})
        db.session.commit()
    except:
        return False
    return True


def get_reviews_for_review_item(id):
    sql = "SELECT r.id, u.username, r.rating, r.text \
                         FROM review as r \
                         JOIN user_account as u ON r.user_account_id = u.id \
                         WHERE r.review_item_id=:id"
    result = db.session.execute(sql, {"id": id})
    reviews = result.fetchall()

    return reviews


def get_reviews_for_user(username):
    sql = "SELECT r.rating, r.text, ri.name, ri.category, ri.id FROM review as r \
           JOIN user_account as u ON r.user_account_id = u.id \
           JOIN review_item as ri ON r.review_item_id = ri.id \
           WHERE u.username=:username"
    result = db.session.execute(sql, {"username": username})
    reviews = result.fetchall()

    return reviews
