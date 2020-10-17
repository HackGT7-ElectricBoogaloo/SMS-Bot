# Download the helper library from https://www.twilio.com/docs/python/install
from twilio.rest import Client
from flask import Flask, request, redirect
from twilio.twiml.messaging_response import MessagingResponse
import json
import random
import time
import hashlib
import threading
import asyncio

# Your Account Sid and Auth Token from twilio.com/console
# DANGER! This is insecure. See http://twil.io/secure
account = json.load(open('account.json', encoding="utf8"))

client = Client(account["account_sid"], account["auth_token"])


# Scripts Json
scripts = json.load(open('scripts.json', encoding="utf8"))
start_state = scripts["init"]

# States Json
states = json.load(open('states.json', encoding="utf8"))

def say_after(delay, what, number):
    time.sleep(delay)
    message = client.messages \
                .create(
                     body=what,
                     from_=account["number"],
                     to=number
                 )

def delay_state(delay, message, phone_number, phone_number_hash, next_state):
    time.sleep(delay)
    scripts[states[phone_number_hash]["currentstate"]]["isdelaying"] = False
    states[phone_number_hash]["currentstate"] = next_state
    
    if "nextState" in scripts[next_state] and next_state != "name":
        message = client.messages \
                    .create(
                        body=scripts[next_state]["message"],
                        from_=account["number"],
                        to=phone_number
                    )
        next_state = scripts[next_state][next_state]
        states[phone_number_hash]["currentstate"]

    json.dump(states, open('states.json', mode ="w"))
    message = client.messages \
                .create(
                     body=message,
                     from_=account["number"],
                     to=phone_number
                 )

app = Flask(__name__)



@app.route("/sms", methods=['GET', 'POST'])
def incoming_sms():
    """Send a dynamic reply to an incoming text message"""
    # Get the message the user sent our Twilio number
    body = request.values.get('Body', None)
    
    # Start our TwiML response
    resp = MessagingResponse()

    # Set the phone number
    phone_number = request.values.get('From')
    phone_number_hash = hashlib.md5(phone_number.encode('utf-8')).hexdigest()

    # Find the current state of the user
    if phone_number_hash not in states or body == "RESTART":
        states[phone_number_hash] = {"currentstate": start_state, "name": "George P. Burdell"}
        json.dump(states, open('states.json', mode ="w"))
        resp.message(scripts[start_state]["message"])
        return str(resp)
    
    current_state = states[phone_number_hash]["currentstate"]

    # Store name exception. Follow the same format to store any 
    # values that need to be recorded
    if current_state == "name":
        next_state = scripts[current_state]["responses"][body]

        states[phone_number_hash]["name"] = body
        states[phone_number_hash]["currentstate"] = scripts[current_state]["nextState"]

        json.dump(states, open('states.json', mode ="w"))

        reply = scripts[next_state]["message"]
        reply = reply.replace("%NAME", states[phone_number_hash]["name"])

        resp.message(reply)
        return str(resp)

    if "isdelaying" in states[phone_number_hash] and states[phone_number_hash]["isdelaying"] == False:
        random_delayed = random.choice(scripts["delayeds"])
        resp.message(random_delayed)
        return str(resp)
    
    # Determine the right reply for this message
    for response in scripts[current_state]["responses"]:
        if response.contains(body.lower()):
            next_state = scripts[current_state]["responses"][body]
            reply = scripts[next_state]["message"]
            reply = reply.replace("%NAME", states[phone_number_hash]["name"])

            if "delay" in scripts[current_state]:
                states[phone_number_hash]["isdelaying"] = True
                threading.Thread(target=say_after, args = (scripts[current_state]["delay"], reply, phone_number)).start()
                resp.message()
                return str(resp)
            else:
                states[phone_number_hash]["currentstate"] = next_state

                if "nextState" in scripts[next_state] and next_state != "name":
                    message = client.messages \
                                .create(
                                    body=scripts[next_state]["message"],
                                    from_=account["number"],
                                    to=phone_number
                                )
                    next_state = scripts[next_state][next_state]
                    states[phone_number_hash]["currentstate"]
                
                json.dump(states, open('states.json', mode ="w"))
                reply = scripts[next_state]["message"]
                resp.message(scripts[next_state]["message"])
                return str(resp)
    
    # If the response is invalid
    random_invalid = random.choice(scripts["invalids"])
    resp.message(random_invalid)
    return str(resp)
    

if __name__ == "__main__":
    app.run(host=account["server-ip"], debug=True)


