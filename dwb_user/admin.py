from django.contrib import admin

from dwb_user.models import (
    Profile,
    Message,
    DeliveredMessage,
    )


class ProfileAdmin(admin.ModelAdmin):

    """Profile Admin."""

    list_display = [
        "user", "church_name", "is_pastor",
    ]

admin.site.register(Profile, ProfileAdmin)


class MessageAdmin(admin.ModelAdmin):

    """Message Admin."""

    list_display = [
        "user", "text",
    ]

admin.site.register(Message, MessageAdmin)


class DeliveredMessageAdmin(admin.ModelAdmin):

    """Delivered Message Admin."""

    list_display = [
        "user", "message", "is_read",
    ]

admin.site.register(DeliveredMessage, DeliveredMessageAdmin)
