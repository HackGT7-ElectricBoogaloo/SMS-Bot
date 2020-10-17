# Download the helper library from https://www.twilio.com/docs/python/install
from twilio.rest import Client
from flask import Flask, request, redirect
from twilio.twiml.messaging_response import MessagingResponse
import json
import random
import time

# Your Account Sid and Auth Token from twilio.com/console
# DANGER! This is insecure. See http://twil.io/secure
account = json.load(open('account.json', encoding="utf8"))

# client = Client(account["account_sid"], account["auth_token"])

# message = client.messages \
#                 .create(
#                      body="Join Earth's mightiest heroes. Like Kevin Bacon.",
#                      from_=account["number"],
#                      to="+1<number>"
#                  )

# print(message.sid)

app = Flask(__name__)

# Scripts Json
scripts = json.load(open('scripts.json', encoding="utf8"))
start_state = scripts["init"]

# States Json
states = json.load(open('states.json', encoding="utf8"))


@app.route("/sms", methods=['GET', 'POST'])
def incoming_sms():
    """Send a dynamic reply to an incoming text message"""
    # Get the message the user sent our Twilio number
    body = request.values.get('Body', None)
    
    # Start our TwiML response
    resp = MessagingResponse()

    # Set the phone number
    phone_number = request.values.get('From')

    # Find the current state of the user
    if phone_number not in states or body == "RESTART":
        states[phone_number] = {"currentstate": start_state, "name": "NO_NAME"}
        json.dump(states, open('states.json', mode ="w"))
        resp.message(scripts[start_state]["message"])
        return str(resp)
    
    current_state = states[phone_number]["currentstate"]

    # Store name exception. Follow the same format to store any 
    # values that need to be recorded
    if current_state == "name":
        states[phone_number]["name"] = body
        json.dump(states, open('states.json', mode ="w"))
        return str(resp)

    # Determine the right reply for this message
    elif body in scripts[current_state]["responses"]:
        next_state = scripts[current_state]["responses"][body]
        states[phone_number] = {"currentstate": next_state}
        json.dump(states, open('states.json', mode ="w"))
        reply  = scripts[next_state]["message"]

        resp.message(scripts[next_state]["message"])
    # If the response is invalid
    else:
        random_invalid = random.choice(scripts["invalids"])
        resp.message(random_invalid)

    return str(resp)
    

if __name__ == "__main__":
    app.run(host=account["server-ip"], debug=True)