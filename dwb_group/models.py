import uuid

from django.conf import settings
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.db import models
from django.utils import timezone
from django.utils.translation import ugettext as _

from dwb_book.models import Book, Copy


def get_groups_for_user(user):
    """List of groups that user belongs to."""
    return [m.group for m in Member.objects.filter(user=user)]


def are_users_in_same_group(user_a, user_b):
    """Docstring."""
    groups_a = get_groups_for_user(user_a)
    groups_b = get_groups_for_user(user_b)

    for ga in groups_a:
        for gb in groups_b:
            if ga.id == gb.id:
                return True

    return False


class Group(models.Model):

    """Docstring."""

    class Meta:
        db_table = "dwb_group"

    book = models.ForeignKey(Book)
    creator = models.ForeignKey(User)
    name = models.CharField(
        max_length=255,
        verbose_name=_("Name"))
    date_started = models.DateTimeField(
        auto_now_add=True)

    def __unicode__(self):
        """Docstring."""
        return self.name


class Member(models.Model):

    """Docstring."""

    class Meta:
        db_table = "dwb_member"

    user = models.ForeignKey(User)
    group = models.ForeignKey(Group)
    date_joined = models.DateTimeField(
        auto_now_add=True)

    def __unicode__(self):
        """Docstring."""
        return "%s in %s" % (self.user, self.group)


class Invite(models.Model):

    """Docstring."""

    STATUS_CHOICES = (
        ("pending",     _("Pending")),
        ("accepted",    _("Accepted")),
    )

    class Meta:
        db_table = "dwb_invite"

    group = models.ForeignKey(
        Group,
        related_name="+")
    sender_user = models.ForeignKey(
        User,
        related_name="+")
    recipient_user = models.ForeignKey(
        User,
        null=True, blank=True)

    status = models.CharField(
        max_length=16,
        choices=STATUS_CHOICES, default="pending")
    recipient_email = models.EmailField(
        _("Recipient Email"),
        max_length=255,
        null=True, blank=True)
    recipient_name = models.CharField(
        _("Recipient Name"),
        max_length=255,
        null=True, blank=True)
    code = models.CharField(
        max_length=255)
    date_created = models.DateTimeField(
        auto_now_add=True)
    date_accepted = models.DateTimeField(
        null=True, blank=True)

    def mark_accepted(self, recipient=None):
        """Docstring."""
        if not self.status == "pending":
            raise Exception(
                _("This invitation cannot be used."))

        self.status = "accepted"
        self.recipient_user = recipient
        self.date_accepted = timezone.now()

    def generate_code(self):
        """Docstring."""
        if self.code:
            raise Exception(
                _("Cannot generate another code for this invite"))

        self.code = str(uuid.uuid4())

    def __unicode__(self):
        """Docstring."""
        return self.code


class Message(models.Model):

    """Docstring."""

    class Meta:
        db_table = "dwb_message"

    STATUS_CHOICES = (
        ("draft",   _("Draft")),
        ("sent",    _("Sent")),
        ("failed",  _("Failed")),
    )

    sender_user = models.ForeignKey(
        User,
        related_name="+")
    recipient_user = models.ForeignKey(
        User,
        related_name="+")

    status = models.CharField(
        max_length=16,
        choices=STATUS_CHOICES, default="draft")
    recipient_email = models.CharField(
        max_length=255,
        blank=True, null=True)
    text = models.TextField()
    date_sent = models.DateTimeField(
        auto_now_add=True)

    def send(self):
        """Docstring."""
        if self.status == "sent":
            raise Exception(
                _("Cannot send the same message twice."))

        if not self.recipient_email:
            self.recipient_email = self.recipient_user.email

        subject = _("Message from ") + self.sender_user.get_full_name()
        text_body = self.text

        ok = send_mail(
            subject,
            text_body,
            self.sender_user.email,
            [
                self.recipient_email,
            ],
            fail_silently=False
            )

        if ok:
            self.status = "sent"
        else:
            self.status = "failed"

        self.save()

        return ok
