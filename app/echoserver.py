from flask import Flask, request
from app import app
from app.models import *
import json
import requests
import sys
import os


# This needs to be filled with the Page Access Token that will be provided
# by the Facebook App that will be created.

PAT = 'EAAZAuhEvzHlYBAKanMoNoBlKF2pZCeLZATKJOFjkcBAn4c0dy9Mb9cjHCP2X9LF5MnvPuU2MWWzUraBFBorYsyURbuVAbh0PioTNFZAqrQZApd7AWLCzylx2OESdL9RxpvbA2BLF94geswWwrOagX8RlZA0tYeCEAz1aZB0ZCTBqZCwZDZD'

temp_sender = "hi"
temp_user = "hi"
temp_message = "hi"

@app.route('/', methods=['GET'])
def handle_verification():
  if request.args.get('hub.verify_token', '') == 'my_voice_is_my_password_verify_me':
    return request.args.get('hub.challenge', '')
  else:
    return 'Error, wrong validation token'

@app.route('/', methods=['POST'])
def handle_messages():
    payload = request.get_data()

    global temp_sender
    global temp_message
    global temp_user

    current_state = State.query.filter_by(sid = 1).first()

    if current_state:
        if current_state.information == "store_user":
            data = json.loads(payload)
            message_events = data["entry"][0]["messaging"]
            for event in message_events:
              if "message" in event:
                  temp_sender = event["sender"]["id"]
                  temp_user = event["message"]["text"]
            db.session.delete(current_state)
            db.session.commit()
            new_state = State("add_user")
            db.session.add(new_state)
            db.session.commit()
            send_message(PAT, temp_sender, "What information would you like to store?".encode('unicode_escape'))
            return "ok"

        if current_state.information == "add_user":
            data = json.loads(payload)
            message_events = data["entry"][0]["messaging"]
            for event in message_events:
              if "message" in event:
                  temp_sender = event["sender"]["id"]
                  temp_message = event["message"]["text"]
            add_user_info(current_state)
            db.session.delete(current_state)
            db.session.commit()
            return "ok"

        if current_state.information == "list_user":
            data = json.loads(payload)
            message_events = data["entry"][0]["messaging"]
            for event in message_events:
              if "message" in event:
                  temp_sender = event["sender"]["id"]
                  temp_message = event["message"]["text"]
            list_user_info(current_state)
            return "ok"
    else:
        messaging_events(payload)
        return "ok"

def messaging_events(payload):
  """Generate tuples of (sender_id, message_text) from the
  provided payload.
  """
  global global_flag
  data = json.loads(payload)
  message_events = data["entry"][0]["messaging"]

  for event in message_events:
    if "message" in event:
        if "Add" in event["message"]["text"]:
            # ret_message = add_user_info(event["sender"]["id"])
            new_state = State("store_user")
            db.session.add(new_state)
            db.session.commit()
            send_message(PAT, event["sender"]["id"],"Full name of new entry".encode('unicode_escape'))

        elif "List" in event["message"]["text"]:
            # ret_message = list_user_info(event["sender"]["id"])
            new_state = State("list_user")
            db.session.add(new_state)
            db.session.commit()
            send_message(PAT, event["sender"]["id"], "Full name of user".encode('unicode_escape'))
        else:
            send_message(PAT, event["sender"]["id"], "Not a recognized command".encode('unicode_escape'))



def add_user_info(curr_state):

    global temp_sender
    global temp_message
    global temp_user

    user = User.query.filter_by(username = temp_user).first()
    if (user):
      db.session.delete(curr_state)
      db.session.commit()

      send_message(PAT, temp_sender, "User already exists".encode('unicode_escape'))
      return

    new_user = User(temp_user, temp_message)
    db.session.add(new_user)
    db.session.commit()

    send_message(PAT, temp_sender, "success".encode('unicode_escape'))

def list_user_info(curr_state):

    global temp_sender
    global temp_message
    global information

    user = User.query.filter_by(username = temp_message).first()

    if user:
      send_message(PAT, 393357704400147, user.information.encode("unicode_escape"))
    else:
      send_message(PAT, temp_sender, "No such user".encode("unicode_escape"))

    db.session.delete(curr_state)
    db.session.commit()


def send_message(token, recipient, text):
  """Send the message text to recipient with id recipient.
  """

  r = requests.post("https://graph.facebook.com/v2.6/me/messages",
    params={"access_token": token},
    data=json.dumps({
      "recipient": {"id": recipient},
      "message": {"text": text.decode('unicode_escape')}
    }),
    headers={'Content-type': 'application/json'})
