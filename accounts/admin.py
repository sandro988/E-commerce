from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .forms import CustomUserCreationForm, CustomUserChangeForm
from .models import CustomUser, OTP


class CustomUserAdmin(UserAdmin):
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm
    model = CustomUser
    list_display = [
        "email",
        "is_staff",
        "is_active",
        "is_verified",
        "is_subscribed_to_newsletter",
        "date_joined",
    ]
    list_filter = [
        "email",
        "is_staff",
        "is_active",
        "is_verified",
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
            {
                "fields": [
                    "is_staff",
                    "is_active",
                    "is_verified",
                    "groups",
                    "user_permissions",
                ]
            },
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


class OTPAdmin(admin.ModelAdmin):
    model = OTP
    list_display = ("user_email", "code", "expiry_timestamp", "is_user_verified")

    def user_email(self, obj):
        return obj.user.email

    def is_user_verified(self, obj):
        return obj.user.is_verified

    user_email.short_description = "User Email"
    is_user_verified.short_description = "Verified"

    search_fields = ["email"]


admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(OTP, OTPAdmin)
