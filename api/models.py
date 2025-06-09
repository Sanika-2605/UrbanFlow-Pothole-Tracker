from django.db import models

class User(models.Model):
    name = models.CharField(max_length=100)
    phone = models.CharField(max_length=15, unique=True)
    otp_verified = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.name} - {self.phone}"

class PotholeReport(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    image = models.ImageField(upload_to='pothole_images/')
    location = models.CharField(max_length=255)
    latitude = models.FloatField()
    longitude = models.FloatField()
    width = models.FloatField()
    height = models.FloatField()
    depth = models.FloatField()
    severity = models.CharField(max_length=10)  # Yellow, Orange, Red
    submitted_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Pothole by {self.user.name} at {self.location} - Severity: {self.severity}"



# Create your models here.
