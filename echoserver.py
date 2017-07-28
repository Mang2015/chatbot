from flask import Flask, request
import json
import requests

app = Flask(__name__)

# This needs to be filled with the Page Access Token that will be provided
# by the Facebook App that will be created.

PAT = 'EAAZAuhEvzHlYBAADLrSPDOxVCHgkfyYK7omDd0jFIHKVmHCuZBqHqkAwNj5kNRQQsFTr5fp1TbWWAlQ3DoRm2zI9iU8vP2NL5Lo4nSpEUhagDvchugMAeAWlWlZC8JfSuz390ipAgAzVNKA33QdUzenL0SZBdWOZCIAH1ZADFpZCAZDZD'

@app.route('/', methods=['GET'])
def handle_verification():
  if request.args.get('hub.verify_token', '') == 'my_voice_is_my_password_verify_me':
    return request.args.get('hub.challenge', '')
  else:
    return 'Error, wrong validation token'

@app.route('/', methods=['POST'])
def handle_messages():
  payload = request.get_data()
  for sender, message in messaging_events(payload):
    send_message(PAT, sender, message)
  return "ok"

def messaging_events(payload):
  """Generate tuples of (sender_id, message_text) from the
  provided payload.
  """
  data = json.loads(payload)
  messaging_events = data["entry"][0]["messaging"]
  for event in messaging_events:
    if "message" in event and "text" in event["message"]:
      yield event["sender"]["id"], "event["message"]["text"].encode('unicode_escape')"
    else:
      yield event["sender"]["id"], "I can't echo this"


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

# event["message"]["text"].encode('unicode_escape')
