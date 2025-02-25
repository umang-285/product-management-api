from django.contrib import admin
from .models import User


@admin.register(User)
class User(admin.ModelAdmin):
    list_display = ['id', 'email', 'is_staff', 'is_superuser']
