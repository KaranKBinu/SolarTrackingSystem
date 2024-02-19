from django.db import models


class UserProfile(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    username = models.EmailField(default="")
    email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=15)
    password = models.CharField(max_length=100)
    address = models.TextField()

    def __str__(self):
        return f"{self.first_name} {self.last_name}"


class SensorData(models.Model):
    timestamp = models.DateTimeField(auto_now_add=True)
    voltage = models.FloatField()
    ldrValue1 = models.IntegerField()
    ldrValue2 = models.IntegerField()
    servoAngle = models.FloatField()
    username = models.EmailField(default="")

    def __str__(self):
        return f"Time:{self.timestamp} - Voltage : {self.voltage} - Servo Angle :{self.servoAngle} - Username :{self.username}"


class Contact(models.Model):
    name = models.CharField(max_length=255)
    email = models.EmailField()
    subject = models.CharField(max_length=255)
    message = models.TextField()

    def __str__(self):
        return f"{self.name} - {self.subject}"
