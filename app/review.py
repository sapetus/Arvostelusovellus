from db import db


def create(rating, text, review_item_id):
    try:
        sql = "INSERT INTO review (rating, text, review_item_id) VALUES (:rating, :text, :review_item_id)"
        db.session.execute(
            sql, {"rating": rating, "text": text, "review_item_id": review_item_id})
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
