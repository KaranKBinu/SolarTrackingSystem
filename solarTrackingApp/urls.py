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
    path("update_data", views.update_data, name="update_data"),
    path("dashboard/", views.dashboard, name="dashboard"),
    path("update_profile/", views.update_profile, name="update_profile"),
]
