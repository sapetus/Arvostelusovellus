from db import db


def get_categories():
    sql = "SELECT enum_range(NULL::CATEGORY)"
    result = db.session.execute(sql)
    data = result.fetchone()[0]
    data = data[1:-1]
    categories = data.split(",")
    capitalized_categories = []
    for category in categories:
        category = category.lower()
        category = category.capitalize()
        capitalized_categories.append(category)
    return capitalized_categories
