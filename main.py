import smtplib
from email.mime.text import MIMEText

#Google server connection
smtpSslHost = 'smtp.gmail.com'
smtpSslPort = 465

username = "boogaloosms@gmail.com"
password = "2Boog27!"

source = "boogaloosms@gmail.com"
destinations = ["6784163334@txt.att.net", "7862731689@messaging.sprintpcs.com", "7063082111@vtext.com"]

#server connection
server = smtplib.SMTP_SSL(smtpSslHost, smtpSslPort)
server.login(username, password)

#message contents
#Use MIMEText to send only text
message = MIMEText('TestMessage')
message["subject"] = "TestSubject"
message["from"] = "mysterious stranger"
for destination in destinations:
    message["to"] = destination
    server.sendmail(source, destination, message.as_string())

#closing server
server.quit()