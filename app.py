import hashlib
import random
import uuid

from flask import Flask, render_template, request, make_response, redirect, url_for
from model import User, db

app = Flask(__name__)
db.create_all()


@app.route ("/")
def home():
    return render_template("index.html")


@app.route ("/chat")
def chat():
    username = request.args.get("username")
    room = request.args.get("room")

    if username and room:
        return render_template("chat.html" , username=username, room=room)
    else:
        return redirect (url_for("home"))

@app.route("/profile", methods=["GET"])
def profile():

@app.route("/profile/sent", methods=["GET", "POST"])
def profile_sent():

@app.route("/profile/recieved", methods=["GET", "POST"])
def profile_recieved():

@app.route("/prognoza", methods=["GET"])
def prognoza():
        query = "Rovinj"
        unit = "metric"
        api_key = "de47075e358a7ac9b08b976edc874b8e"
        lang = "hr"

        url = "https://api.openweathermap.org/data/2.5/weather?q={0}&lang={3}&units={1}&appid={2}".format(query, unit,
                                                                                                          api_key, lang)
        data = requests.get(url=url)
        return render_template("index.html", data=data.json())



if __name__ == '__main__':
    app.run()

    # glavni ili main
