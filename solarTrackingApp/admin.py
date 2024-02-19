from django.contrib import admin
from .models import Contact, UserProfile, SensorData


class UserProfileAdmin(admin.ModelAdmin):
    list_display = ("first_name", "last_name", "email", "phone_number", "address")
    search_fields = ("first_name", "last_name", "email", "phone_number")


admin.site.register(UserProfile, UserProfileAdmin)


class SensorDataAdmin(admin.ModelAdmin):
    list_filter = ("timestamp", "servoAngle", "voltage")
    list_display = ("timestamp", "servoAngle", "voltage")


admin.site.register(SensorData, SensorDataAdmin)


class ContactAdmin(admin.ModelAdmin):
    list_display = ("name", "email", "subject", "message")
    search_fields = ("name", "email", "subject")
    list_filter = ("subject",)


admin.site.register(Contact, ContactAdmin)
