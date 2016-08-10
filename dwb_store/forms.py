from django import forms
from django.utils.translation import ugettext as _


class EmailClaimCodeForm(forms.Form):

    """Email Claim Code Form."""

    recipient_name = forms.CharField(
        label=_("Name"),
        max_length=255)
    recipient_email = forms.EmailField(
        label=_("Email"))
