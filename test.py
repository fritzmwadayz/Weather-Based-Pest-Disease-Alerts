import smtplib
server = smtplib.SMTP("smtp.yandex.com", 587)
server.starttls()
server.login("your_email@yandex.com", "password")
server.sendmail("from@yandex.com", ["to@example.com"], "Test message")
server.quit()
print("Success!")
