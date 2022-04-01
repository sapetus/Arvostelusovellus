from flask import session
from werkzeug.security import check_password_hash, generate_password_hash
from db import db


def register(username, password):
    password_hash = generate_password_hash(password)
    try:
        sql = "INSERT INTO user_account (username, password_hash, is_admin) VALUES (:username, :password_hash, false)"
        db.session.execute(
            sql, {"username": username, "password_hash": password_hash})
        db.session.commit()
    except:
        return False
    return login(username, password)


def login(username, password):
    sql = "SELECT id, password_hash FROM user_account WHERE username=:username"
    result = db.session.execute(sql, {"username": username})
    user = result.fetchone()

    if not user:
        return False
    else:
        if check_password_hash(user.password_hash, password):
            session["username"] = username
            return True
        else:
            return False


def user_id(username):
    sql = "SELECT id FROM user_account WHERE username=:username"
    result = db.session.execute(sql, {"username": username})
    id = result.fetchone()

    return id.id


# this is probably not safe, because, if a malicious user finds out the username of an admin account,
# they can set the cookie them selves, and gain access to admin status
def is_admin(username):
    if not username:
        return False

    sql = "SELECT is_admin FROM user_account WHERE username=:username"
    result = db.session.execute(sql, {"username": username})
    user = result.fetchone()

    return user.is_admin


def get_user_information(username):
    sql = "SELECT key, value FROM user_information JOIN user_account \
           ON user_account_id = user_account.id WHERE user_account.username=:username;"
    result = db.session.execute(sql, {"username": username})
    user_information = result.fetchall()

    return user_information


def add_user_information(key, value, id):
    try:
        sql = "INSERT INTO user_information (user_account_id, key, value) \
               VALUES (:user_account_id, :key, :value)"
        db.session.execute(
            sql, {"user_account_id": id, "key": key, "value": value})
        db.session.commit()
        return True
    except:
        return False
