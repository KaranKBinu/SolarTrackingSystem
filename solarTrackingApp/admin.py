from django.contrib import admin
from .models import UserProfile


class UserProfileAdmin(admin.ModelAdmin):
    list_display = ("first_name", "last_name", "email", "phone_number", "address")
    search_fields = ("first_name", "last_name", "email", "phone_number")


admin.site.register(UserProfile, UserProfileAdmin)
