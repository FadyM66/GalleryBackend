from django.urls import path
from .views import *

urlpatterns = [
    # Endpoint to handle user registration
    path('register', register),  # POST request to register a new user

    # Endpoint for user login
    path('login', login),  # POST request to log in a user and get a JWT token

    # Endpoint to verify OTP for user registration
    path('verify-otp', verify_otp),  # POST request to verify OTP during registration
]
