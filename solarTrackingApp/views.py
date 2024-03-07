import random
from django.shortcuts import render, redirect
from django.contrib import messages
from .models import Contact, UserProfile, SensorData
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
from django.utils.datastructures import MultiValueDictKeyError
from django.template.loader import render_to_string
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.utils.html import strip_tags
from .forms import SensorDataFilterForm
from django.db.models import Q
from django.utils import timezone
from rest_framework import generics
from .models import UserProfile
from .serializers import UserProfileSerializer


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
        if send_email_to_welcome(full_name=f"{first_name} {last_name}", email=email):

            # Create user profile
            user_profile = UserProfile.objects.create(
                first_name=first_name,
                last_name=last_name,
                username=email,
                email=email,
                phone_number=phone_number,
                password=user_password,
                address=address,
            )

            # Store user information in session
            request.session["user_id"] = user_profile.id
            request.session["user_email"] = user_profile.email
            request.session["user_name"] = (
                f"{user_profile.first_name} {user_profile.last_name}"
            )
            messages.success(
                request, "Account created successfully. Welcome To our Family"
            )
            return redirect("index")
        else:
            messages.error(
                request,
                "Failed to send verification mail. Try Again Later. Or make sure You have enterd the correct email",
            )
            return redirect("signup")
    else:
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
            if password == user.password:
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
            localIp = request.POST["localIp"]
            # Save data to the database
            sensor_data = SensorData.objects.create(
                voltage=voltage,
                ldrValue1=ldrValue1,
                ldrValue2=ldrValue2,
                servoAngle=servoAngle,
                username=username,
                localIp=localIp,
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
        # Check if the user is authenticated
        if "user_id" in request.session:
            form = SensorDataFilterForm(request.GET)
            latest_sensor_data = (
                SensorData.objects.filter(username=request.session["user_email"])
                .order_by("-timestamp")
                .first()
            )

            if form.is_valid():
                date = form.cleaned_data.get("date")
                start_time = form.cleaned_data.get("start_time")
                end_time = form.cleaned_data.get("end_time")
                voltage_value = form.cleaned_data.get("voltage_value")
                servo_angle = form.cleaned_data.get("servo_angle")

                all_sensor_data = SensorData.objects.filter(
                    username=request.session["user_email"]
                ).order_by("-timestamp")

                if date:
                    all_sensor_data = all_sensor_data.filter(timestamp__date=date)
                if start_time and end_time:
                    all_sensor_data = all_sensor_data.filter(
                        timestamp__time__range=(start_time, end_time)
                    )
                if voltage_value:
                    all_sensor_data = all_sensor_data.filter(voltage=voltage_value)
                if servo_angle:
                    all_sensor_data = all_sensor_data.filter(servoAngle=servo_angle)

                # Calculate rotations based on latest sensor data
                voltage_rotation = (
                    (latest_sensor_data.voltage / 4.2) * 180
                    if latest_sensor_data
                    else None
                )
                ldr1_rotation = (
                    (latest_sensor_data.ldrValue1 / 4095) * 180
                    if latest_sensor_data
                    else None
                )
                ldr2_rotation = (
                    (latest_sensor_data.ldrValue2 / 4095) * 180
                    if latest_sensor_data
                    else None
                )
                servo_rotation = (
                    (latest_sensor_data.servoAngle / 180) * 180
                    if latest_sensor_data
                    else None
                )
                return render(
                    request,
                    "dashboard.html",
                    {
                        "latest_sensor_data": latest_sensor_data,
                        "all_sensor_data": all_sensor_data,
                        "voltage_rotation": voltage_rotation,
                        "ldr1_rotation": ldr1_rotation,
                        "ldr2_rotation": ldr2_rotation,
                        "servo_angle": servo_rotation,
                        "form": form,
                    },
                )

        # If the user is not authenticated, redirect to the login page
        else:
            messages.error(request, "Please login to access the dashboard!")
            return redirect("login")

    except Exception as e:
        messages.error(request, f"An error occurred: {str(e)}")
        return redirect("login")


def send_otp(request):
    if request.method == "POST":
        user_email = request.POST.get("email")
        if UserProfile.objects.filter(email=user_email).exists():
            request.session["otp"] = str(random.randint(1000, 9999))
            request.session["otp_verification_email"] = user_email

            if send_otp_email(
                email=request.session["otp_verification_email"],
                otp=request.session["otp"],
            ):
                messages.success(
                    request,
                    f"OTP has been sent successfully to {request.session['otp_verification_email']}",
                )
                return redirect("verify_otp")
            else:
                messages.error(
                    request,
                    "Something error Occured while sending Email you can try resending after sometime",
                )
                return redirect("login")
        else:
            messages.error(
                request,
                f"This email {user_email} is not registered or incorrect email address.",
            )
            return redirect("login")
    else:
        return redirect("login")


def verify_otp(request):
    if request.method == "POST":
        user_entered_otp = request.POST.get("otp")
        if "otp" in request.session and "otp_verification_email" in request.session:
            saved_otp = request.session["otp"]
            user_email = request.session["otp_verification_email"]

            if user_entered_otp == saved_otp:
                del request.session["otp"]
                request.session["is_verified"] = True
                messages.success(
                    request, f"OTP verification successful for {user_email}"
                )
                return redirect("update_password")
            else:
                messages.error(request, "Invalid OTP. Please try again.")
                return render(request, "verify-otp.html")
        else:
            messages.error(request, "invalid Request...!")
            return redirect("login")
    else:
        return render(request, "verify-otp.html")


def update_password(request):
    if request.session.get("is_verified") == True:
        if request.method == "POST":
            password = request.POST["password"]
            confirm_password = request.POST["confirm_password"]
            if password != "" and password == confirm_password:
                user = UserProfile.objects.filter(
                    email=request.session["otp_verification_email"]
                )
                user.update(password=password)
                del request.session["otp_verification_email"]
                del request.session["is_verified"]
                messages.success(
                    request,
                    "Updated password successfully, you can now login with the new password",
                )
                return redirect("login")
            else:
                messages.error(
                    request,
                    "Passwords do not match. Please enter the same password in both fields.",
                )
                return redirect("update_password")
    else:
        messages.error(request, "invalid Request...!")
        return redirect("login")
    return render(request, "update_password.html")


def send_otp_email(email, otp):
    try:
        subject = "Solar Tracker OTP for Verification"
        email_from = settings.EMAIL_HOST_USER

        # Render the HTML template with the OTP
        html_content = render_to_string("otp_email_template.html", {"otp": otp})
        text_content = strip_tags(
            html_content
        )  # Strip HTML tags for the plain text version

        msg = EmailMultiAlternatives(subject, text_content, email_from, [email])
        msg.attach_alternative(html_content, "text/html")
        msg.send()
        return True
    except Exception as e:
        print(f"Error sending OTP email: {e}")
        return False


def resend_otp(request):
    try:

        if send_otp_email(
            email=request.session["otp_verification_email"],
            otp=request.session["otp"],
        ):
            messages.success(
                request,
                f"OTP has been re-sent to {request.session['otp_verification_email']}.",
            )
            return redirect("verify_otp")
    except:
        messages.error(
            request,
            "Something error Occured while sending Email you can try resending after sometime",
        )
        return redirect("login")


def send_email_to_welcome(full_name, email):
    try:
        subject = f"Solar Tracker Team Welcomes {full_name} To Our Family"
        email_from = settings.EMAIL_HOST_USER

        # Render the HTML template with the OTP
        html_content = render_to_string(
            "welcome_user_on_signup.html", {"full_name": full_name, "email": email}
        )
        text_content = strip_tags(
            html_content
        )  # Strip HTML tags for the plain text version

        msg = EmailMultiAlternatives(subject, text_content, email_from, [email])
        msg.attach_alternative(html_content, "text/html")
        msg.send()
        return True
    except Exception as e:
        print(f"Error sending Welcome email: {e}")
        return False


class UserProfileList(generics.ListAPIView):
    queryset = UserProfile.objects.all()
    serializer_class = UserProfileSerializer


def AndroidDashboard(request):
    try:
        # Check if the user is authenticated
        if "user_id" in request.session:
            form = SensorDataFilterForm(request.GET)
            latest_sensor_data = (
                SensorData.objects.filter(username=request.session["user_email"])
                .order_by("-timestamp")
                .first()
            )

            if form.is_valid():
                date = form.cleaned_data.get("date")
                start_time = form.cleaned_data.get("start_time")
                end_time = form.cleaned_data.get("end_time")
                voltage_value = form.cleaned_data.get("voltage_value")
                servo_angle = form.cleaned_data.get("servo_angle")

                all_sensor_data = SensorData.objects.filter(
                    username=request.session["user_email"]
                ).order_by("-timestamp")

                if date:
                    all_sensor_data = all_sensor_data.filter(timestamp__date=date)
                if start_time and end_time:
                    all_sensor_data = all_sensor_data.filter(
                        timestamp__time__range=(start_time, end_time)
                    )
                if voltage_value:
                    all_sensor_data = all_sensor_data.filter(voltage=voltage_value)
                if servo_angle:
                    all_sensor_data = all_sensor_data.filter(servoAngle=servo_angle)

                # Calculate rotations based on latest sensor data
                voltage_rotation = (
                    (latest_sensor_data.voltage / 4.2) * 180
                    if latest_sensor_data
                    else None
                )
                ldr1_rotation = (
                    (latest_sensor_data.ldrValue1 / 4095) * 180
                    if latest_sensor_data
                    else None
                )
                ldr2_rotation = (
                    (latest_sensor_data.ldrValue2 / 4095) * 180
                    if latest_sensor_data
                    else None
                )
                servo_rotation = (
                    (latest_sensor_data.servoAngle / 180) * 180
                    if latest_sensor_data
                    else None
                )
                localIp = latest_sensor_data.localIp
                return render(
                    request,
                    "android_dashboard.html",
                    {
                        "latest_sensor_data": latest_sensor_data,
                        "all_sensor_data": all_sensor_data,
                        "voltage_rotation": voltage_rotation,
                        "ldr1_rotation": ldr1_rotation,
                        "ldr2_rotation": ldr2_rotation,
                        "servo_angle": servo_rotation,
                        "localIp": localIp,
                        "form": form,
                    },
                )

        # If the user is not authenticated, redirect to the login page
        else:
            messages.error(request, "Please login to access the dashboard!")
            return redirect("login")

    except Exception as e:
        messages.error(request, f"An error occurred: {str(e)}")
        return redirect("login")


def handler404(request, exception):
    return render(request, "404.html", status=404)
