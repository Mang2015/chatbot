from flask import Flask, request
import json
import requests
import sys

app = Flask(__name__)

# This needs to be filled with the Page Access Token that will be provided
# by the Facebook App that will be created.

PAT = 'EAAZAuhEvzHlYBAKanMoNoBlKF2pZCeLZATKJOFjkcBAn4c0dy9Mb9cjHCP2X9LF5MnvPuU2MWWzUraBFBorYsyURbuVAbh0PioTNFZAqrQZApd7AWLCzylx2OESdL9RxpvbA2BLF94geswWwrOagX8RlZA0tYeCEAz1aZB0ZCTBqZCwZDZD'
information = {}
global_flag = 0
temp_sender = "hi"
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

    if global_flag == 1:
        data = json.loads(payload)
        message_events = data["entry"][0]["messaging"]
        for event in message_events:
            if "message" in event:
                temp_sender = event["sender"]["id"]
                temp_message = event["message"]["text"]
        return "ok"
    else:
        messaging_events(payload)
        return "ok"

def messaging_events(payload):
  """Generate tuples of (sender_id, message_text) from the
  provided payload.
  """
  data = json.loads(payload)
  messaging_events = data["entry"][0]["messaging"]

  for event in messaging_events:
    if "message" in event:
        if "add" in event["message"]["text"]:
            ret_message = add_user_info(event["sender"]["id"])
            send_message(PAT, event["sender"]["id"], ret_message.encode('unicode_escape'))
        elif "list" in event["message"]["text"]:
            ret_message = list_user_info(event["sender"]["id"])
            send_message(PAT, event["sender"]["id"], ret_message.encode('unicode_escape'))
        else:
            send_message(PAT, event["sender"]["id"], "This is not a recognized command".encode('unicode_escape'))

def add_user_info(sender):
    global global_flag
    global temp_sender
    global temp_message
    global information
    global_flag = 1
    # question = "Full name of new entry".encode('unicode_escape')

    new_user = input(send_message(PAT, sender, "Full name of new entry".encode('unicode_escape')))

    question = "What information would you like to store?".encode('unicode_escape')
    send_message(PAT, temp_sender, question)

    information[new_user] = temp_message

    global_flag = 0
    return "success"

def list_user_info(sender):
    global global_flag
    global temp_sender
    global temp_message
    global information
    global_flag = 1
    question = "Full name of user".encode('unicode_escape')
    send_message(PAT, sender, question)

    for name in information:
        if name in temp_message:
          return information[name]
        else:
            continue

    global_flag = 0
    return "No such user"

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
