from django.contrib import admin

# Register your models here.
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser


class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ("username", "email", "role", "is_staff")
    fieldsets = UserAdmin.fieldsets + (("Role Information", {"fields": ("role",)}),)


admin.site.register(CustomUser, CustomUserAdmin)
