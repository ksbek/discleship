from django import forms
from django.utils.translation import ugettext_lazy as _


class DeleteForm(forms.Form):

    """Delete Form."""

    confirm_choices = (
        ("no",  _("No, do not delete")),
        ("yes", _("Yes, delete all data")),
       )
    confirm = forms.ChoiceField(
        choices=confirm_choices,
        widget=forms.Select(
            attrs={
                "class":        "form-control",
            }),
        )
