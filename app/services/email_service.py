from flask import current_app
from ..extensions import mail
from flask_mail import Mail, Message

def send_reset_email(email, token):
    try:
        reset_link = f"http://localhost/5173/reset-password?token={token}"
        
        msg = Message(
            "Password Reset Request",
            sender=current_app.config['MAIL_DEFAULT_SENDER'],
            recipients=[email],
            html=f"""
            <h2>Password Reset Request</h2>
            <p>Click the link below to reset your password:</p>
            <a href="{reset_link}">{reset_link}</a>
            <p>This link expires in 30 minutes.</p>
            """
        )
        mail.send(msg)
        return True
    except Exception as e:
        current_app.logger.error(f"Email sending failed: {str(e)}")
        return False