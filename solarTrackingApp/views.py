from django.shortcuts import render, redirect
from django.contrib import messages
from .models import UserProfile
from django.contrib.auth.hashers import make_password, check_password
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse


# Create your views here.
def index(request):
    return render(request, "index.html")


def about(request):
    return render(request, "about.html")


def contact(request):
    return render(request, "contact.html")


def profile(request):
    if request.session["user_id"]:
        user = UserProfile.objects.get(email=request.session["user_email"])
        return render(request, "profile.html", {"user": user})
    else:
        messages.success(request, "Please Login to Access this Page!")
        return redirect("login")


def signup(request):
    if request.method == "POST":
        first_name = request.POST["first_name"]
        last_name = request.POST["last_name"]
        email = request.POST["user_email"]
        phone_number = request.POST["phone_no"]
        user_password = request.POST["password"]
        confirm_password = request.POST["confirm_password"]
        address = request.POST["user_address"]
        userlist = [
            first_name,
            last_name,
            email,
            phone_number,
            user_password,
            confirm_password,
            address,
        ]
        for user in userlist:
            if user == "":
                messages.error(request, f"All Fields are Mandatory")
                return redirect("signup")
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
            username=email,
            email=email,
            phone_number=phone_number,
            password=hashed_password,
            address=address,
        )

        # Store user information in session
        request.session["user_id"] = user_profile.id
        request.session["user_email"] = user_profile.email
        request.session["user_name"] = (
            f"{user_profile.first_name} {user_profile.last_name}"
        )

        messages.success(request, "Account created successfully. Welcome To our Family")
        return redirect("index")

    return render(request, "signup.html")


def user_login(request):
    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]

        try:
            # Query the user by username
            user = UserProfile.objects.get(username=username)
            print(user)
            # Check if the provided password matches the stored password
            if check_password(password, user.password):
                # Store user information in session (optional)
                request.session["user_id"] = user.id
                request.session["user_email"] = user.email
                request.session["user_name"] = f"{user.first_name} {user.last_name}"
                messages.success(request, "Login success, Welcome Back..!")
                return redirect("index")
            else:
                messages.error(request, "Make sure you have entered correct password!!")
                return redirect("login")

        except UserProfile.DoesNotExist:
            messages.error(request, "User does not exist. Please try again.")
            return redirect("login")

    return render(request, "login.html")


def user_logout(request):
    # Clear session data
    request.session.clear()
    messages.success(request, "Logged out successfully.")
    return redirect("index")


@csrf_exempt
def receive_data(request):
    if request.method == "POST":
        voltage = request.POST.get("voltage")
        ldr1 = request.POST.get("ldr1")
        ldr2 = request.POST.get("ldr2")
        servo_angle = request.POST.get("servo_angle")

        # Process the received data as needed
        # For now, just print the data
        print(
            f"Received data - Voltage: {voltage}, LDR 1: {ldr1}, LDR 2: {ldr2}, Servo Angle: {servo_angle}"
        )

        response_data = f"Received data - Voltage: {voltage}, LDR 1: {ldr1}, LDR 2: {ldr2}, Servo Angle: {servo_angle}"
        return HttpResponse(response_data, status=200)
    else:
        return HttpResponse("Invalid request method", status=400)
