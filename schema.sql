CREATE TYPE CATEGORY AS ENUM ('MOVIE', 'TV-SHOW', 'GAME', 'BOOK');

CREATE TABLE user_account (id SERIAL PRIMARY KEY, username TEXT UNIQUE, password_hash TEXT, is_admin BOOLEAN);

CREATE TABLE review_item (id SERIAL PRIMARY KEY, category CATEGORY, name TEXT, publication_date DATE, rating FLOAT, description TEXT);

CREATE TABLE review (id SERIAL PRIMARY KEY, user_account_id INTEGER REFERENCES user_account(id), review_item_id INTEGER REFERENCES review_item(id), rating INTEGER, text TEXT);

CREATE TABLE picture (id SERIAL PRIMARY KEY, user_account_id INTEGER REFERENCES user_account(id), review_item_id INTEGER REFERENCES review_item(id), picture BYTEA);

CREATE TABLE user_information (id SERIAL PRIMARY KEY, user_account_id INTEGER REFERENCES user_account(id), key TEXT, value TEXT);