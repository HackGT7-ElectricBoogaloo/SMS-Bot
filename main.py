#https://humberto.io/blog/sending-and-receiving-emails-with-python/

import email
import imaplib
import smtplib
from email.mime.text import MIMEText

smtpSslHost = "smtp.gmail.com"
smtpSslPort = 465

username = "boogaloosms@gmail.com"
password = "2Boog27!"
sendingServer = 'imap.gmail.com'

source = "boogaloosms@gmail.com"
destinations = ["6784163334@txt.att.net", "7862731689@messaging.sprintpcs.com", "7063082111@vtext.com"]
    
def sendMessage(destinations, message):
    #message contents
    #Use MIMEText to send only text
    for destination in destinations:
        message["to"] = destination
        server.sendmail(source, destination, message.as_string())

#Google server connection for sending
server = smtplib.SMTP_SSL(smtpSslHost, smtpSslPort)
server.login(username, password)
#Server connection for receiving
mail = imaplib.IMAP4_SSL(sendingServer)
mail.login(username, password)

###Carnivorous

#slecting inbox
mail.select('inbox')
#returns status and list of ids
#Example data: [b'1 2 3 4 5 6 7']
status, data = mail.search(None, 'ALL')
#split blocks in data into usable ids
mailIds = []
for block in data:
    #example: [b'1', b'2', b'3', b'4', b'5', b'6', b'7']
    mailIds += block.split()
#fetch email per id
for i in mailIds:
    ##RFC822 format comes as a tuple with header, message, closing byte
    status, data = mail.fetch(i, "(RFC822)")
    for responsePart in data:
        if isinstance(responsePart, tuple):
            #Here header would be first element, message would be second, closing byte would be third
            
            #grab the message
            message = email.message_from_bytes(responsePart[1])
            #who send the message
            mailFrom = message["from"]
            #message subject
            mailSubject = message["subject"]

            #separate text if not just plaintext
            if message.is_multipart():
                mailContent = ''
                #multipart messagess containt things other than plaintext, so filter for that
                for part in message.get_payload():
                    if part.get_content_type() == "text/plain":
                        mailContent += part.get_payload()
            else:
                mailContent = message.get_payload()

            print(mailFrom)
            print(mailSubject)
            print(mailContent)
###End Carnivorous

#Sending message
message = MIMEText('TestMessage')
message["subject"] = "TestSubject"
message["from"] = "mysterious stranger"
#sendMessage(destinations, message)

#closing server
server.quit()