import smtplib
from email.mime.text import MIMEText
from dotenv import load_dotenv
import os

load_dotenv()

def send_reset_email(email, token):
    sender = os.getenv('EMAIL_SENDER')
    password = os.getenv('EMAIL_PASSWORD')

    msg = MIMEText(f'Click the link to reset your password: http://your-frontend-url/reset-password?token={token}')
    msg['Subject'] = 'Password Reset'
    msg['From'] = sender
    msg['To'] = email

    with smtplib.SMTP('smtp.gmail.com', 587) as server:
        server.starttls()
        server.login(sender, password)
        server.sendmail(sender, [email], msg.as_string())