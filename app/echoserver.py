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

global_flag = 0
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
    global global_flag
    global temp_sender
    global temp_message
    global temp_user

    if global_flag == "store user":
        data = json.loads(payload)
        message_events = data["entry"][0]["messaging"]
        for event in message_events:
            if "message" in event:
                temp_sender = event["sender"]["id"]
                temp_user = event["message"]["text"]
        global_flag = "add user"
        send_message(PAT, temp_sender, "What information would you like to store?".encode('unicode_escape'))
        return "ok"

    elif global_flag == "add user":
        data = json.loads(payload)
        message_events = data["entry"][0]["messaging"]
        for event in message_events:
            if "message" in event:
                temp_sender = event["sender"]["id"]
                temp_message = event["message"]["text"]
        add_user_info()
        return "ok"

    elif global_flag == "list user":
        data = json.loads(payload)
        message_events = data["entry"][0]["messaging"]
        for event in message_events:
            if "message" in event:
                temp_sender = event["sender"]["id"]
                temp_message = event["message"]["text"]
        list_user_info()
        global_flag = 0
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
  messaging_events = data["entry"][0]["messaging"]

  for event in messaging_events:
    if "message" in event:
        if "Add" in event["message"]["text"]:
            # ret_message = add_user_info(event["sender"]["id"])
            global_flag = "store user"
            send_message(PAT, event["sender"]["id"],"Full name of new entry".encode('unicode_escape'))
            return
        elif "List" in event["message"]["text"]:
            # ret_message = list_user_info(event["sender"]["id"])
            global_flag = "list user"
            send_message(PAT, event["sender"]["id"], "Full name of user".encode('unicode_escape'))
            return

  if global flag == 0:
    send_message(PAT, event["sender"]["id"], "This is not a recognized command".encode('unicode_escape'))


def add_user_info():
    global global_flag
    global temp_sender
    global temp_message
    global temp_user

    user = User.query.filter_by(username = temp_user).first()
    if (user):
      global_flag = 0
      send_message(PAT, temp_sender, "User already exists".encode('unicode_escape'))
      return
    
    new_user = User(temp_user, temp_message)
    db.session.add(new_user)
    db.session.commit()

    global_flag = 0
    send_message(PAT, temp_sender, "success".encode('unicode_escape'))

def list_user_info():
    global global_flag
    global temp_sender
    global temp_message
    global information

    user = User.query.filter_by(username = temp_message).first()

    if user:
      send_message(PAT, temp_sender, user.information.encode("unicode_escape"))
    else:
      send_message(PAT, temp_sender, "No such user".encode("unicode_escape"))

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



if __name__ == '__main__':
  app.run()
