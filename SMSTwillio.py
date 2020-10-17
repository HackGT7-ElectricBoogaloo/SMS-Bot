# Download the helper library from https://www.twilio.com/docs/python/install
from twilio.rest import Client
from flask import Flask, request, redirect
from twilio.twiml.messaging_response import MessagingResponse
import json


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


@app.route("/sms", methods=['GET', 'POST'])
def incoming_sms():
    """Send a dynamic reply to an incoming text message"""
    # Get the message the user sent our Twilio number
    body = request.values.get('Body', None)

    # Start our TwiML response
    resp = MessagingResponse()

    # Determine the right reply for this message
    if body == 'hello':
        resp.message("Hi!")
    elif body == 'bye':
        resp.message("Goodbye")
    else:
        resp.message("Not Recognized")

    return str(resp)

if __name__ == "__main__":
    app.run(host=account["server-ip"], debug=True)