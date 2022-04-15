from db import db


def create(name, publication_date, category, description):
    try:
        sql = "INSERT INTO review_item (name, publication_date, category, description) \
               VALUES (:name, :publication_date, :category, :description) RETURNING id"
        result = db.session.execute(sql,
                           {"name": name, "publication_date": publication_date,
                            "category": category, "description": description})
        db.session.commit()
        return result.fetchone().id
    except:
        return False


def delete(id):
    try:
        sql = "DELETE FROM review_item WHERE id=:id"
        db.session.execute(sql, {"id": id})
        db.session.commit()
        return True
    except:
        return False


def update(name, description, publication_date, id):
    try:
        sql = "UPDATE review_item SET name=:name, description=:description, publication_date=:publication_date WHERE id=:id"
        db.session.execute(sql, {"name": name, "description": description, "publication_date": publication_date, "id": id})
        db.session.commit()
        return True
    except:
        return False


def get_review_items_by_category(category):
    sql = "SELECT name, id FROM review_item WHERE category=:category"
    result = db.session.execute(sql, {"category": category.upper()})
    review_items = result.fetchall()

    return review_items


def get_review_item(id):
    sql = "SELECT * FROM review_item WHERE id=:id"
    result = db.session.execute(sql, {"id": id})
    review_item = result.fetchone()

    if review_item:
        return review_item
    else:
        return None


def average_rating(id):
    sql = "SELECT AVG(rating)::numeric(10,1) FROM review WHERE review_item_id=:id"
    result = db.session.execute(sql, {"id": id})
    average_rating = result.fetchone()[0]
    return average_rating
