import secrets
from flask import session
from werkzeug.security import check_password_hash, generate_password_hash
from db import db

# EVERY USER IS GIVEN ADMIN STATUS FOR NOW! EASIER TO TEST APP
def register(username, password):
    password_hash = generate_password_hash(password)
    try:
        sql = "INSERT INTO user_account (username, password_hash, is_admin) VALUES (:username, :password_hash, true)"
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
            session["token"] = secrets.token_hex(16)
            return True
        else:
            return False


def check_user(token):
    if session["token"] != token:
        return False
    else:
        return True


# returns true if username exists, false otherwise
def check_username(username):
    sql = "SELECT 1 FROM user_account WHERE username=:username"
    result = db.session.execute(sql, {"username": username})
    if result.fetchone():
        return True
    else:
        return False


def user_id(username):
    sql = "SELECT id FROM user_account WHERE username=:username"
    result = db.session.execute(sql, {"username": username})
    id = result.fetchone()

    if id:
        return id.id
    else:
        return None


# this is not safe, because, if a malicious user finds out the username of an admin account,
# they can set the cookie themselves, and gain access to admin status
def is_admin(username):
    if not username:
        return False

    sql = "SELECT is_admin FROM user_account WHERE username=:username"
    result = db.session.execute(sql, {"username": username})
    user = result.fetchone()
    if user:
        return user.is_admin
    else:
        return False


def get_user_information(username):
    sql = "SELECT key, value FROM user_information JOIN user_account \
           ON user_account_id = user_account.id WHERE user_account.username=:username;"
    result = db.session.execute(sql, {"username": username})
    user_information = result.fetchall()

    if user_information:
        return user_information
    else:
        return None


def get_user_information_by_key(key, id):
    sql = "SELECT value FROM user_information WHERE key=:key AND user_account_id=:id"
    result = db.session.execute(sql, {"key":key, "id":id})
    value = result.fetchone()
    if value:
        return value[0]
    else:
        return None


def add_user_information(key, value, id):
    try:
        sql = "INSERT INTO user_information (user_account_id, key, value) \
               VALUES (:user_account_id, :key, :value)"
        db.session.execute(sql, {"user_account_id": id, "key": key, "value": value})
        db.session.commit()
        return True
    except:
        return False


def update_user_information(key, value, id):
    try:
        sql = "UPDATE user_information SET value=:value WHERE key=:key AND user_account_id=:id"
        db.session.execute(sql, {"value":value, "key":key, "id":id})
        db.session.commit()
        return True
    except:
        return False


def delete_user(username):
    try:
        id = user_id(username)
        sql = "DELETE FROM user_account WHERE id=:id"
        db.session.execute(sql, {"id": id})
        db.session.commit()
        del session["username"]
        del session["token"]
        return True
    except:
        return False