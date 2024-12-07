from django.contrib.auth.hashers import check_password
from rest_framework.decorators import api_view
from rest_framework.response import Response
from image.utils import validate_JWT
from .models import User
from .utils import *
from core.decorators import error_handler

"""
API Views for User Registration, OTP Verification, and Login.
"""

# Registration View
@error_handler
@api_view(['POST'])
def register(request):
    """
    Handles user registration by validating input, generating OTP, and sending verification email.
    """
    data = request.data
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')

    # Validate email
    email_valid, email_message = validate_email(email)
    if not email_valid:
        return Response({"message": email_message}, status=400)
    
    # Validate username
    username_valid, username_message = validate_username(username)
    if not username_valid:
        return Response({"message": username_message}, status=400)

    
    # Validate password
    password_valid, password_message = validate_password(password)
    if not password_valid:
        return Response({"message": password_message}, status=400)

    try:
        # Check if the user already exists
        is_existed = User.objects.filter(email=email).first()
        if is_existed:
            return Response({"message": "User already exists"}, status=409)

        # Generate OTP
        otp_code = code_generator(email)
        res = send_email(
            to_email=email,
            subject="Email Verification",
            message=f"OTP Code: {otp_code}\n\nThis code is valid for 5 minutes."
        )

        # Generate JWT for registration
        token = JWT_generator(email=email, username=username, password=password)
        if not res:
            return Response({"message": "Internal error"}, status=500)

        return Response({"message": "OTP code has been sent to your email", "token": token}, status=200)

    except Exception as e:
        return Response({"message": "Internal Server Error"}, status=500)


# OTP Verification View
@error_handler
@api_view(['POST'])
def verify_otp(request):
    """
    Verifies the OTP and registers the user upon successful validation.
    """
    registration_token = request.headers.get('token')
    if not registration_token:
        return Response({"message": "Token is missing"}, status=401)

    otp_code = request.data.get('otp')
    if not otp_code:
        return Response({"message": "OTP is missing"}, status=400)

    # Validate JWT token
    token_validation = validate_JWT(registration_token)
    if not token_validation['valid']:
        return Response({"message": token_validation['error']}, status=401)

    token = token_validation['token']

    # Validate OTP
    otp_status = otp_ckecker(otp_code, token['email'])
    if not otp_status:
        return Response({"message": "Invalid OTP"}, status=401)

    try:
        # Create a new user
        new_user = User(
            username=token['username'],
            email=token['email'],
            hashed_password=encrypt_password(token['password'])
        )
        new_user.save()

        # Send success email
        send_email(
            to_email=token['email'],
            subject="Registration Successful",
            message="You have been registered successfully."
        )

        return Response({"message": "User is created successfully"}, status=201)

    except Exception as e:
        return Response({"message": "Internal Server Error"}, status=500)


# Login View
@error_handler
@api_view(['POST'])
def login(request):
    """
    Handles user login by validating credentials and generating a JWT.
    """
    data = request.data
    email = data.get('email')
    password = data.get('password')

    if not email :
        return Response({"message": "Email is missing"}, status=400)
    
    if not password :
        return Response({"message": "Password is missing"}, status=400)

    try:
        # Check if user exists
        is_existed = User.objects.filter(email=email).first()
        if not is_existed:
            return Response({"message": "User is not registered"}, status=404)

        # Verify password
        hashed_password = is_existed.hashed_password
        if not check_password(password, hashed_password):
            return Response({"message": "Invalid password"}, status=401)

        # Generate JWT for the user
        token = JWT_generator(user_id=is_existed.id, email=is_existed.email)

        return Response({"message": "Logged in successfully", "token": token}, status=200)

    except Exception as e:
        return Response({"message": "Internal Server Error"}, status=500)
