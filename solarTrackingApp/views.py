from django.shortcuts import render, redirect
from django.contrib import messages
from .models import Contact, UserProfile, SensorData
from django.contrib.auth.hashers import make_password, check_password
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
from django.utils.datastructures import MultiValueDictKeyError


# Create your views here.
def index(request):
    return render(request, "index.html")


def about(request):
    return render(request, "about.html")


def contact(request):
    if request.method == "POST":
        name = request.POST.get("name")
        email = request.POST.get("email")
        subject = request.POST.get("subject")
        message = request.POST.get("message")
        Contact.objects.create(name=name, email=email, subject=subject, message=message)
        messages.success(request, "Thank you for contacting us..")
        return redirect("index")
    return render(request, "contact.html")


def profile(request):
    try:
        if request.session["user_id"]:
            user = UserProfile.objects.get(email=request.session["user_email"])
            return render(request, "profile.html", {"user": user})
    except:
        messages.error(request, "Please Login to Access profile!")
        return redirect("login")


def update_profile(request):
    if request.method == "POST":
        user_email = request.POST.get("email")

        # Check if the email already exists in the database
        if (
            UserProfile.objects.filter(email=user_email)
            .exclude(id=request.session.get("user_id"))
            .exists()
        ):
            messages.error(
                request,
                f"A profile with the same Email: {user_email} already exists.",
            )
            return redirect("profile")
        user = UserProfile.objects.get(email=request.session.get("user_email"))
        user.first_name = request.POST.get("first_name")
        user.last_name = request.POST.get("last_name")
        user.phone_number = request.POST.get("phone_number")
        user.address = request.POST.get("address")

        # Check if the email is being changed
        if user.email != request.session.get("email"):
            user.email = request.POST.get("email")
            user.username = request.POST.get("email")
            # Clear the session
            request.session.flush()
            request.session["user_email"] = user.email
            request.session["user_name"] = user.first_name + " " + user.last_name
            request.session["user_id"] = user.id
            user.save()
            messages.success(request, "Profile updated successfully.")
            return redirect("profile")
        else:
            messages.error(request, "Somewthing went Wrong.")
            return redirect("profile")
    else:
        return redirect("profile")


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
def update_data(request):
    if request.method == "POST":
        try:
            voltage = request.POST["voltage"]
            ldrValue1 = request.POST["ldr1"]
            ldrValue2 = request.POST["ldr2"]
            servoAngle = request.POST["servoAngle"]
            username = request.POST["username"]
            # Save data to the database
            sensor_data = SensorData.objects.create(
                voltage=voltage,
                ldrValue1=ldrValue1,
                ldrValue2=ldrValue2,
                servoAngle=servoAngle,
                username=username,
            )
            sensor_data.save()
            print(sensor_data)
            return HttpResponse("Data received and saved successfully.", status=200)
        except MultiValueDictKeyError:
            return HttpResponse("Invalid form data.", status=400)
    else:
        print("something went wrong!!!")
        return HttpResponse("Invalid request method.", status=400)


def dashboard(request):
    try:
        if request.session["user_id"]:
            # Get the latest sensor data entry
            latest_sensor_data = SensorData.objects.order_by("-timestamp").first()
            voltage_rotation = (latest_sensor_data.voltage / 5) * 180
            ldr1_rotation = (latest_sensor_data.ldrValue1 / 4095) * 180
            ldr2_rotation = (latest_sensor_data.ldrValue2 / 4095) * 180
            servo_angle = (latest_sensor_data.servoAngle / 180) * 180
            # Get all sensor data for the table
            all_sensor_data = SensorData.objects.filter(
                username=request.session["user_email"]
            ).order_by("-timestamp")

            return render(
                request,
                "dashboard.html",
                {
                    "latest_sensor_data": latest_sensor_data,
                    "all_sensor_data": all_sensor_data,
                    "voltage_rotation": voltage_rotation,
                    "ldr1_rotation": ldr1_rotation,
                    "ldr2_rotation": ldr2_rotation,
                    "servo_angle": servo_angle,
                },
            )
    except:
        messages.error(request, "please login to access dasboard!!")
        return redirect("login")
