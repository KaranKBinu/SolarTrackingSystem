from . import views
from django.urls import path

urlpatterns = [
    path("", views.index, name="index"),
    path("about/", views.about, name="about"),
    path("contact/", views.contact, name="contact"),
    path("signup/", views.signup, name="signup"),
    path("user-login/", views.user_login, name="login"),
    path("user-logout/", views.user_logout, name="logout"),
    path("user-profile/", views.profile, name="profile"),
    path("update-data", views.update_data, name="update_data"),
    path("dashboard/", views.dashboard, name="dashboard"),
    path("update-profile/", views.update_profile, name="update_profile"),
    path("send-otp/", views.send_otp, name="send_otp"),
    path("verify-otp/", views.verify_otp, name="verify_otp"),
    path("update-password/", views.update_password, name="update_password"),
    path("resend_otp/", views.resend_otp, name="resend_otp"),
    path("android-dashboard/", views.AndroidDashboard, name="android_dashboard"),
    path("api/userprofiles/", views.UserProfileList.as_view(), name="userprofile-list"),
]
