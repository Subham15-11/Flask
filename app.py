from flask import Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail, Message
from datetime import datetime
import json
import math

with open("config.json", "r") as c:
    params = json.load(c)["params"]

local_server = True

app = Flask(__name__)

mail = Mail(app)  # instantiate the mail class

# configuration of mail
app.config["MAIL_SERVER"] = "smtp.gmail.com"
app.config["MAIL_PORT"] = 465
app.config["MAIL_USERNAME"] = params["gmail-user"]
app.config["MAIL_PASSWORD"] = params["gmail-password"]
app.config["MAIL_USE_TLS"] = False
app.config["MAIL_USE_SSL"] = True

mail = Mail(app)

# app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://username:password@localhost/db_name'
if local_server:
    app.config["SQLALCHEMY_DATABASE_URI"] = params["local_uri"]
else:
    app.config["SQLALCHEMY_DATABASE_URI"] = params["prod_uri"]

db = SQLAlchemy(app)


class Contacts(db.Model):
    sno = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(50), nullable=False)
    phone = db.Column(db.String(50), nullable=False)
    message = db.Column(db.String(500), nullable=False)
    date = db.Column(db.String(20), nullable=False)


class Posts(db.Model):
    sno = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(50), nullable=False)
    slug = db.Column(db.String(50), nullable=False)
    content = db.Column(db.String(500), nullable=False)
    date = db.Column(db.String(20), nullable=True)
    img_file = db.Column(db.String(20), nullable=True)


@app.route("/")
def home():
    posts = Posts.query.filter_by().all()
    last = math.ceil(len(posts) / int(params["no_of_posts"]))
    page = request.args.get("page")

    if not str(page).isnumeric():
        page = 1
    page = int(page)
    posts = posts[
        (page - 1)
        * int(params["no_of_posts"]) : (page - 1)
        * int(params["no_of_posts"])
        + int(params["no_of_posts"])
    ]

    if page == 1:
        prev = "#"
        next = "/?page=" + str(page + 1)
    elif page == last:
        prev = "/?page=" + str(page - 1)
        next = "#"
    else:
        prev = "/?page=" + str(page - 1)
        next = "/?page=" + str(page + 1)

    return render_template(
        "index.html", params=params, posts=posts, prev=prev, next=next
    )


@app.route("/about")
def about():
    return render_template("about.html", params=params)


@app.route("/contact", methods=["GET", "POST"])
def contact():
    if request.method == "POST":
        """Add entry to the database"""
        name = request.form.get("name")
        email = request.form.get("email")
        phone = request.form.get("phone")
        message = request.form.get("message")
        entry = Contacts(
            name=name, phone=phone, message=message, date=datetime.now(), email=email
        )
        db.session.add(entry)
        db.session.commit()
        msg = Message("Hello", sender=email, recipients=[params["gmail-user"]])
        msg.body = f"Hello Flask message sent from Flask-Mail by {name},ph:{phone}"
        mail.send(msg)

    return render_template("contact.html", params=params)


@app.route("/post/<string:slug>", methods=["GET"])
def Samplepost(slug):
    post = Posts.query.filter_by(slug=slug).first()
    return render_template("post.html", params=params, post=post)


app.run(debug=True)
