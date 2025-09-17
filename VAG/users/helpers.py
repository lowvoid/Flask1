from flask_mail import Message
from flask import url_for
from VAG import mail

def send_reset_email(user):
    token = user.get_reset_token()
    msg = Message('Name App Password Reset Request', sender= 'Name@gmail.com', recipients=[user.email],
        body= f"""To Reset Your Password, visit the following link:
        {url_for('users.reset_password', token=token , _external=True)}
        if you did not make this request, please ignore this email."""
    )
    mail.send(msg)
    