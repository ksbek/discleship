from django.contrib import admin

from dwb_group.models import (
    Group,
    Invite,
    Member,
    )


class MemberInlineAdmin(admin.TabularInline):

    """Docstring."""

    model = Member


class GroupAdmin(admin.ModelAdmin):

    """Docstring."""

    list_display = [
        "name", "book", "creator", "date_started",
    ]
    inlines = [MemberInlineAdmin, ]

admin.site.register(Group, GroupAdmin)


class InviteAdmin(admin.ModelAdmin):

    """Docstring."""

    list_display = [
        "code", "date_created", "recipient_email", "recipient_name", "group",
        "status",
    ]
    readonly_fields = [
        "group", "code", "date_created", "date_accepted",  "sender_user",
        "recipient_email", "recipient_name",  "recipient_user",
    ]

admin.site.register(Invite, InviteAdmin)
