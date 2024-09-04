from flask import Flask, render_template

app = Flask(__name__)


@app.route("/")
def hello():
    return render_template("index_prac.html")


@app.route("/about")
def subham():
    name = "Subham"
    return render_template("about_prac.html", name2=name)


# app.run()
app.run(debug=True)
