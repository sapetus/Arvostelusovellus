from db import db


def create(name, publication_date, category, description):
    try:
        sql = "INSERT INTO review_item (name, publication_date, category, description) \
            VALUES (:name, :publication_date, :category, :description)"
        db.session.execute(sql,
                           {"name": name, "publication_date": publication_date,
                            "category": category, "description": description})
        db.session.commit()
    except:
        return False
    return True
