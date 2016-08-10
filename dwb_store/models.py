from datetime import date

import json
import random
import uuid

from django.contrib.auth.models import User
from django.db import models
from django.utils.translation import ugettext as _

from ckeditor.fields import RichTextField

from dwb_book.models import Book, Copy


class Purchase(models.Model):

    """Represent a single request to purchase a book.

    It's status can be "pending", "payed", "canceled" or "failed".
    The default status is "pending". Once the status is changed, it cannot be
    changed again: payed purchase always stays payed.
    """

    class Meta:
        db_table = "dwb_purchase"

    STATUS_CHOICES = (
        ("pending",     _("Pending")),
        ("payed",       _("Payed")),
        ("canceled",    _("Canceled")),
        ("failed",      _("Failed")),
    )

    invoice_number = models.CharField(
        max_length=36,
        unique=True)
    uuid = models.CharField(
        max_length=36,
        unique=True)
    status = models.CharField(
        max_length=16,
        choices=STATUS_CHOICES, default="pending")
    book = models.ForeignKey(Book)
    quantity = models.PositiveIntegerField(
        default=1)
    group = models.ForeignKey(
        "dwb_group.Group",
        related_name="+",
        null=True, blank=True,
        help_text=_("Group to join."))

    buyer_user = models.ForeignKey(
        User,
        null=True, blank=True)
    buyer_email = models.EmailField(
        null=True, blank=True)

    recipient_name = models.CharField(
        max_length=255,
        null=True, blank=True)
    recipient_email = models.EmailField(
        null=True, blank=True)

    date = models.DateTimeField(
        auto_now_add=True)
    price = models.DecimalField(
        max_digits=18, decimal_places=2)
    total_charge = models.DecimalField(
        max_digits=18, decimal_places=2)
    gift_code = models.CharField(
        max_length=255,
        blank=True, null=True)
    api_log = models.TextField(
        blank=True)
    api_data = models.TextField(
        default="{}")

    church_name = models.CharField(
        max_length=255,
        null=True, blank=True)

    def add_api_log(self, info):
        """Docstring."""
        if not isinstance(info, basestring):
            # serialize if needed
            info = json.dumps(info)

        self.api_log += info + "\n\n"

    def set_api_data(self, key, value):
        """Docstring."""
        data = json.loads(self.api_data)
        data[key] = value
        self.api_data = json.dumps(data)

    def get_api_data(self, key):
        """Docstring."""
        data = json.loads(self.api_data)

        return data.get(key)

    def is_gift(self):
        """Docstring."""
        return bool(self.gift_code)

    def save(self, *args, **kwargs):
        """Docstring."""
        if not self.invoice_number:
            today = date.today()
            self.invoice_number = "%s-%d" % (
                today.strftime("%Y%m%d"),
                random.randint(10**7, 10**8-1))

        if not self.uuid:
            self.uuid = str(uuid.uuid4())

        super(Purchase, self).save(*args, **kwargs)

    def generate_gift_code(self):
        """Docstring."""
        if self.gift_code:
            raise Exception(
                _("Cannot generate another code for this purchase"))

        self.gift_code = str(uuid.uuid4())[9:23]


class PurchaseClaim(models.Model):

    """Purchase Claim Model."""

    class Meta:
        db_table = "dwb_purchase_claim"

    uuid = models.CharField(
        max_length=36,
        unique=True)
    user = models.ForeignKey(User)
    copy = models.ForeignKey(Copy)
    purchase = models.ForeignKey(
        Purchase,
        related_name="claims")
    date = models.DateTimeField(
        auto_now_add=True)

    def save(self, *args, **kwargs):
        """Docstring."""
        if not self.uuid:
            self.uuid = uuid.uuid4()

        super(PurchaseClaim, self).save(*args, **kwargs)
