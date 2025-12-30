import smtplib                # mail transfer protocol 


sender = " sender@gmail.com"
receiver = "receiver@gmail.com"
password = "password123"
subject = "Python eamil test"
body = "I wrote an email ! : D"


# header                          """ # triple cots are used to assign multiple lines in it
message = f"""From: Pranaykumar{sender}
To : Vinaykumar{receiver}
Subject : {subject}\n                   
{body}
"""

server = smtplib.SMTP("smtp.gamil.com", 587)                # 587 default port number to submit mail
server.starttls()


try:
    server.login(sender, password)
    print("Logged in.... ")
    server.sendmail(sender, receiver, message)
    print("Email has been sent")
    
except socket.gaierror: [Errno 11001] getaddrinfo failed:
    print("unable to sign in")
