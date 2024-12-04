from datetime import datetime, timedelta, timezone
from django.conf import settings
from django.core.cache import cache
from sendgrid.helpers.mail import Mail
from sendgrid import SendGridAPIClient
from django.contrib.auth.hashers import make_password
import random
import jwt
import re


def JWT_generator(**kwargs):

        payload = {key: value for key, value in kwargs.items()}
        
        payload["exp"] = datetime.now(timezone.utc) + timedelta(days=30)
        payload["iat"] = datetime.now(timezone.utc) 

        token = jwt.encode(payload, settings.SECRET_KEY_JWT, algorithm="HS256")

        return token
    
    
def send_email(to_email, subject, message):
    mail = Mail(
        from_email = settings.DEFAULT_FROM_EMAIL,
        to_emails=to_email,
        subject=subject,
        html_content=message        
    )
    
    try:
        sg = SendGridAPIClient(settings.SENDGRID_API_KEY)
        response = sg.send(mail)
        return response.status_code == 202
            
    except Exception as e:
        print(f"Sending email error: {e}")
        return False
    
    
def code_generator(email):
    code = str(random.randint(100000, 999999))
    cache_key = f'verification_code_{email}' 
    cache.set(cache_key, code, timeout=300)
    return code


def otp_ckecker(otp, email):
    cached_otp = cache.get(f'verification_code_{email}')
    return otp == cached_otp


def validate_username(username):
    """
    Validates a username to ensure it is:
    - At least 4 characters long.
    - Contains only alphanumeric characters.
    - Starts with a letter.
    """
    if not username or len(username) < 4:
        return False, "Username must be at least 4 characters long"
    
    if not re.match(r'^[a-zA-Z][a-zA-Z0-9]*$', username):
        return False, "Username must start with a letter and contain only letters and numbers"
    
    return True, "Valid username"


def validate_email(email):
    email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not email or not re.match(email_regex, email):
        return False, "Invalid email format"
    return True, "Valid email"


def encrypt_password(password):
    return make_password(password)


def validate_password(password):
    """
    Validates a password to ensure it meets the following criteria:
    - At least 8 characters long.
    - Contains at least one uppercase letter.
    - Contains at least one lowercase letter.
    - Contains at least one digit.
    - Contains at least one special character (!@#$%^&*()-_+=<>?).
    """
    password_rules = """
        Password must meet the following criteria:
        - At least 8 characters long.
        - Contains at least one uppercase letter.
        - Contains at least one lowercase letter.
        - Contains at least one digit.
        - Contains at least one special character (!@#$%^&*()-_+=<>?).
    """

    # Regex to validate the password
    regex = r'^(?=.*[A-Z])(?=.*[a-z])(?=.*\d)(?=.*[!@#$%^&*()\-_+=<>?]).{8,}$'
    
    if not password or not re.match(regex, password):
        return False, password_rules
    
    return True, "Valid password"
