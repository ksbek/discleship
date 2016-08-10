from django import forms
from django.contrib.flatpages.models import FlatPage
from django.utils.translation import ugettext_lazy as _

from dwb_store.models import Purchase


class GiftPurchaseForm(forms.ModelForm):

    """Gift Purchase Form."""

    class Meta:
        model = Purchase
        fields = [
            "book", "recipient_name", "recipient_email", "quantity",
        ]
        widgets = {
            "book": forms.Select(
                attrs={
                    "class":        "form-control selectpicker",
                }),
            "recipient_name": forms.TextInput(
                attrs={
                    "class":        "form-control",
                    "placeholder":  _("Recipient Name"),
                    "maxlength":    80,
                }),
            "recipient_email": forms.TextInput(
                attrs={
                    "class":        "form-control",
                    "placeholder":  _("Recipient Email"),
                    "maxlength":    80,
                }),
            "quantity": forms.TextInput(
                attrs={
                    "class":        "form-control",
                }),
            }


class PurchaseForm(forms.ModelForm):

    """Purchase Form."""

    class Meta:
        model = Purchase
        fields = [
            "quantity", "status",
        ]


class FlatpageForm(forms.ModelForm):

    """Flat Page Form."""

    class Meta:
        model = FlatPage
        fields = [
            "content",
        ]

        widgets = {
            "content": forms.Textarea(
                attrs={
                    "class":        "form-control",
                    "placeholder":  _("Content"),
                }),
            }
