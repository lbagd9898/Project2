import os

from flask import Flask, render_template, session, request, redirect, url_for
from flask_socketio import SocketIO, emit

app = Flask(__name__)
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")
app.secret_key = 'super secret key'
app.config["SESSION_TYPE"] = "filesystem"
socketio = SocketIO(app)

channels = ["hello", "me"]
messages = {'me': ["Thisone", "another one"], "hello":["what's up", "How are you?"]}

@app.route("/", methods=["GET", "POST"])
def index():
    if session.get("logged_in"):
        return redirect(url_for('welcome'))
    else:
        if request.method == "POST":
            session["user"] = request.form.get("name")
            session["logged_in"] = True
            return redirect(url_for('welcome'))
        return render_template('index.html')

@app.route("/welcome", methods=["GET", "POST"])
def welcome():
    if session.get("logged_in"):
        data = {"channels": channels, "user": session['user'], "messages": messages}
        return render_template('chats2.html', channels = channels, user = session["user"], messages = messages)

@socketio.on("create channel")
def create(data):
    channel = data['contents']
    if channel in channels:
        message = "Channel already exists! Pick a different name."
        emit("channel exists", message)
    else:
        channels.append(channel)
        messages[channel] = []
        emit("add channel", channel, broadcast=True)

@socketio.on("get_messages")
def get_messages(data):
    channel_name = data['channel_name']
    msgs = messages[channel_name]
    emit("display_messages", {"msgs": msgs, "channel_name": channel_name})

@socketio.on("new_message")
def new_message(data):
    current_channel = data['current_channel']
    msg_contents = data['contents']
    all_messages = messages[current_channel]
    user = data['user']
    all_messages.append(msg_contents)
    if len(all_messages) > 100:
        x = len(all_messages)
        all_messages = all_messages[x-100::]
    emit("add_message", {"msgs": all_messages, "channel_name": current_channel, "user": user}, broadcast=True)
