from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .forms import CustomUserCreationForm, CustomUserChangeForm
from .models import CustomUser


class CustomAdmin(UserAdmin):
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm
    model = CustomUser
    list_display = [
        "email",
        "is_staff",
        "is_active",
        "is_subscribed_to_newsletter",
        "date_joined",
    ]
    list_filter = [
        "email",
        "is_staff",
        "is_active",
        "is_subscribed_to_newsletter",
        "date_joined",
    ]
    fieldsets = [
        [
            None,
            {
                "fields": [
                    "email",
                    "full_name",
                    "phone_number",
                    "birthdate",
                    "address",
                    "profile_image",
                    "preferred_currency",
                    "is_subscribed_to_newsletter",
                ]
            },
        ],
        [
            "Permissions",
            {"fields": ["is_staff", "is_active", "groups", "user_permissions"]},
        ],
    ]
    add_fieldsets = [
        [
            None,
            {
                "classes": [
                    "wide",
                ],
                "fields": [
                    "email",
                    "password1",
                    "password2",
                    "full_name",
                    "phone_number",
                    "birthdate",
                    "address",
                    "profile_image",
                    "preferred_currency",
                    "is_staff",
                    "is_active",
                    "groups",
                    "user_permissions",
                ],
            },
        ],
    ]
    search_fields = ["email"]
    ordering = ["email"]


admin.site.register(CustomUser, CustomAdmin)
