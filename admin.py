from django.contrib import admin
from myproject.models import Profile  # Correct relative import if both files are in the same app directory

# Register your models here.
admin.site.register(Profile)
