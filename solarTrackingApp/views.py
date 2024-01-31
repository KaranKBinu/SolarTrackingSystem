from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from django.contrib import messages
from .models import UserProfile
from django.contrib.auth.hashers import make_password, check_password


# Create your views here.
def index(request):
    return render(request, "index.html")


def about(request):
    return render(request, "about.html")


def contact(request):
    return render(request, "contact.html")


def signup(request):
    if request.method == "POST":
        first_name = request.POST["first_name"]
        last_name = request.POST["last_name"]
        email = request.POST["user_email"]
        phone_number = request.POST["phone_no"]
        user_password = request.POST["password"]
        confirm_password = request.POST["confirm_password"]
        address = request.POST["user_address"]

        # Check if passwords match
        if user_password != confirm_password:
            messages.error(request, "Passwords do not match. Please try again.")
            return redirect("signup")

        # Check if email already exists
        if UserProfile.objects.filter(email=email).exists():
            messages.error(request, f"An account with {email} already exists.")
            return redirect("signup")

        # Hash the password before saving it
        hashed_password = make_password(user_password)

        # Create user profile
        user_profile = UserProfile.objects.create(
            first_name=first_name,
            last_name=last_name,
            email=email,
            phone_number=phone_number,
            password=hashed_password,
            address=address,
        )

        # Store user information in session
        request.session["user_id"] = user_profile.id
        request.session["user_email"] = user_profile.email
        request.session[
            "user_name"
        ] = f"{user_profile.first_name} {user_profile.last_name}"

        messages.success(request, "Account created successfully. Welcome To our Family")
        return redirect("index")

    return render(request, "signup.html")


def user_login(request):
    return render(request, "login.html")
