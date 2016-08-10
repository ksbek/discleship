from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import post_save
from django.utils.translation import ugettext_lazy as _


class Profile(models.Model):

    """Profile Model."""

    IS_PASTOR_CHOICES = (
        ("0",   _("No")),
        ("1",   _("Yes"))
    )

    user = models.OneToOneField(User)
    church_name = models.CharField(
        max_length=255,
        null=True, blank=True)
    is_pastor = models.CharField(
        max_length=1,
        choices=IS_PASTOR_CHOICES, default=0)

    #def create_user_profile(sender, instance, created, **kwargs):
    #    if created:
    #        Profile(user=instance).save()
    #        Profile.objects.create(user=instance)

    #post_save.connect(create_user_profile, sender=User)


class Message(models.Model):

    """(populated) Message Model."""

    user = models.ForeignKey(User)
    text = models.CharField(
        max_length=255,
        null=True, blank=True)

    def __unicode__(self):
        """Docstring."""
        return "%s" % (self.text)


class DeliveredMessage(models.Model):

    """(delivered) to the end User Message Model."""

    user = models.ForeignKey(User)
    message = models.ForeignKey(Message)

    is_read = models.BooleanField(
        default=False)

    def __unicode__(self):
        """Docstring."""
        return "%s: %s" % (
            self.user,
            self.message
        )
