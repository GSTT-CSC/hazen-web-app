from flask import render_template, current_app

from app.email import send_email
import jwt
import time
import uuid
from app.models import User
from app import db


def send_password_reset_email(user):
    """
    Send the user an email in order to reset their password.
    """
    token = user.get_reset_password_token()
    send_email('[Hazen] Reset Your Password',
               sender=current_app.config['ADMINS'],
               recipients=[user.email],
               text_body=render_template('email/reset_password.txt',
                                         user=user, token=token),
               html_body=render_template('email/reset_password.html',
                                         user=user, token=token))


def validate_nhs_email(user):
    token = jwt.encode({'email_auth': str(user.id), 'exp': time.time() + 600},
                       current_app.config['SECRET_KEY'],
                       algorithm='HS256')

    current_app.logger.info(f"Generated token for user {user.id}: {token}")
    send_email('[Hazen] Verify your Email',
               sender=current_app.config['ADMINS'],
               recipients=[user.email],
               text_body=render_template('email/authenticate_email.txt', user=user, token=token),
               html_body=render_template('email/authenticate_email.html', user=user, token=token))

    return token


def verify_email_auth_token(token):
    try:
        data = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=['HS256'])
        user_id = data.get('email_auth')
        current_app.logger.info(f"user ID found: {user_id}")

        if not user_id:
            return None
    except jwt.ExpiredSignatureError:
        return None  #token expired
    except jwt.InvalidTokenError:
        return None  #invalid token
    except Exception as e:
        current_app.logger.error(f"Unexpected error: {str(e)}")
        return None
    user_id_formatted = uuid.UUID(user_id)
    user = User.query.get(user_id_formatted)
    if user:
        user.email_authenticated = True
        db.session.commit()
        return user
    return None
