from flask import Flask, render_template, request, redirect, url_for, make_response
from datetime import datetime
import requests
import uuid
import hashlib
from model import db, User, Message


app = Flask(__name__)
db.create_all()


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("login.html")
    elif request.method == "POST":
        session_token = request.cookies.get("session_token")
        if not session_token:
            session_token = str(uuid.uuid4())
        name = request.form.get("user-name")
        email = request.form.get("user-email")
        location = request.form.get("user-location")
        password = request.form.get("user-password")
        # hash the password - to smo koristili za sakriti pass kad dizemo app.
        hashed_password = hashlib.sha256(password.encode()).hexdigest()

        # see if user already exists
        user = db.query(User).filter_by(email=email).first()

        if not user:
            # create a User object
            user = User(name=name, email=email, password=hashed_password, location=location,
                        session_token=session_token)
            db.add(user)
            db.commit()
        else:
            # check if password is incorrect, but only if it exists in database
            if user.password:
                if hashed_password != user.password:
                    return render_template("wrong_password.html")
                elif hashed_password == user.password:
                    # save the session token in a database
                    user.session_token = session_token
                    db.add(user)
                    db.commit()

        # save user's session token into a cookie
        response = make_response(redirect(url_for("profile")))
        response.set_cookie("session_token", session_token, httponly=True, samesite='Strict')
        return response


@app.route("/profile")
def profile():
    session_token = request.cookies.get("session_token")
    user = db.query(User).filter_by(session_token=session_token).first()
    if not user:  # if no user is logged in
        return render_template("login.html")
    else:
        sent_no = len(db.query(Message).filter_by(sender=user.name).all())
        rec_no = len(db.query(Message).filter_by(receiver=user.name).all())
        return render_template("profile.html", user=user, brpo=sent_no, brpr=rec_no)


@app.route("/logout")
def logout():
    response = make_response(redirect(url_for('index')))  # redirect to the index page
    response.set_cookie("oauth_token", expires=0)  # delete the oauth_cookie to logout
    response.set_cookie("session_token", expires=0)
    response.set_cookie("oauth_state", expires=0)
    return response


@app.route("/weather", methods=["GET", "POST"])
def weather():
    session_token = request.cookies.get("session_token")
    user = db.query(User).filter_by(session_token=session_token).first()
    if user:
        if request.method == "GET":
            city = user.location
        elif request.method == "POST":
            city = request.form.get("city")
    else:
        city = request.form.get("city")
    unit = "metric"  # use "imperial" for Fahrenheit
    lang = "en"
    api_key = "5272dc9425b14ee904edf1ff01498fc2"
    url = "https://api.openweathermap.org/data/2.5/weather?q={0}&lang={3}&units={1}&appid={2}".format(city, unit,
                                                                                                      api_key, lang)
    data = requests.get(url=url)  # GET request to the OpenWeatherMap API
    ts = int(data.json()["dt"]) + data.json()["timezone"]
    time = datetime.utcfromtimestamp(ts).strftime('%H:%M')

    print(time)
    return render_template("prognoza.html", data=data.json(), city=city, time=time)


@app.route("/message_edit", methods=["GET", "POST"])
def message_edit():
    session_token = request.cookies.get("session_token")
    user = db.query(User).filter_by(session_token=session_token).first()
    users = db.query(User).filter(User.name != user.name)
    if request.method == "POST":
        sender = user.name
        receiver = request.form.get("receiver")
        title = request.form.get("title")
        if title == "":
            title = "°"
        message_text = request.form.get("poruka")
        new_message = Message(sender=sender, receiver=receiver, title=title, message=message_text)
        db.add(new_message)
        db.commit()
        response = make_response(redirect(url_for("profile")))
        return response
    elif request.method == "GET":
        return render_template("message_edit.html", users=users)


@app.route("/message_reply/<message_id>", methods=["GET", "POST"])
def message_reply(message_id):
    message = db.query(Message).get(int(message_id))
    if request.method == "POST":
        sender = message.receiver
        receiver = message.sender
        title = "Re:"+message.title
        message_text = request.form.get("poruka")
        print(message_text)
        new_message = Message(sender=sender, receiver=receiver, title=title, message=message_text)
        db.add(new_message)
        db.commit()
        response = make_response(redirect(url_for("profile")))
        return response
    elif request.method == "GET":
        return render_template("message_reply.html", message=message)


@app.route("/sent")
def sent():
    session_token = request.cookies.get("session_token")
    user = db.query(User).filter_by(session_token=session_token).first()
    sent_m = db.query(Message).filter_by(sender=user.name).all()
    return render_template("profile_sent.html", sent=sent_m)


@app.route("/received")
def received():
    session_token = request.cookies.get("session_token")
    user = db.query(User).filter_by(session_token=session_token).first()
    rec_m = db.query(Message).filter_by(receiver=user.name).all()
    return render_template("profile_received.html", rec=rec_m)


@app.route("/message/<message_id>")
def message(message_id):
    message = db.query(Message).get(int(message_id))
    return render_template("message.html", message=message)


if __name__ == '__main__':
    app.run()
