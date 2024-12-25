import os

import sqlite3

from flask import Flask, g, render_template, request, flash, abort

from FDataBase import FDataBase

# configuration settings
DATABASE = "/tmp/flsite.db"
DEBUG = True
SECRET_KEY = "mwe2345kjnkjnkjn234!!njkjjdn"

app = Flask(__name__)

# set config values
app.config.from_object(__name__)

# update config values
app.config.update(dict(DATABASE=os.path.join(app.root_path, "flsite.db")))


@app.teardown_appcontext
def close_db(e=None):
    if hasattr(g, "link_db"):
        g.link_db.close()


# connect to db
def connect_db():
    conn = sqlite3.connect(app.config["DATABASE"])
    conn.row_factory = sqlite3.Row
    return conn


# create database
def create_db():
    conn = connect_db()
    with app.open_resource("sq_db.sql", mode="r") as fh:
        conn.cursor().executescript(fh.read())
    conn.commit()
    conn.close()


def get_db():
    if not hasattr(g, "link_db"):
        g.link_db = connect_db()

    return g.link_db


@app.route("/")
def index():
    db = get_db()
    dbase = FDataBase(db)
    return render_template(
        "index.html", items=dbase.getMenu(), posts=dbase.getPostsAnonce()
    )


@app.route("/add_post", methods=["POST", "GET"])
def add_post():
    db = get_db()
    dbase = FDataBase(db)

    if request.method == "POST":
        if len(request.form["name"]) > 4 and len(request.form["post"]) > 10:
            res = dbase.addPost(
                request.form["name"], request.form["post"], request.form["url"]
            )
            if not res:
                flash("Error adding post", category="error")
            else:
                flash("Post successfully added", category="success")
        else:
            flash("Error adding post", category="error")

    return render_template("add_post.html", items=dbase.getMenu(), title="Adding post")


@app.route("/post/<alias>")
def show_post(alias):
    db = get_db()
    dbase = FDataBase(db)
    title, post = dbase.getPost(alias)
    if not title:
        abort(404)

    return render_template("post.html", items=dbase.getMenu(), title=title, post=post)


if __name__ == "__main__":
    app.run(debug=True)
