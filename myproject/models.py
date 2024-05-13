from django.db import models
from django.contrib.auth.models import User

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    has_paid = models.BooleanField(default=False)

    class Meta:
        app_label = 'myproject'  # Make sure this matches the name of your Django app
