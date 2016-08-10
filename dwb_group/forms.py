from django import forms
from django.utils.translation import ugettext_lazy as _

from .models import Group, Invite


class GroupForm(forms.ModelForm):

    """Docstring."""

    def __init__(self, *args, **kwargs):
        """Docstring."""
        self.user = kwargs.pop("user", None)
        self.book = kwargs.pop("book", None)

        super(GroupForm, self).__init__(*args, **kwargs)

        if self.instance and self.instance.pk:
            pass

        self.fields["name"].label = _("Name")

    class Meta:
        model = Group
        fields = [
            "name",
        ]
        widgets = {
            "name": forms.TextInput(
                attrs={
                    "class":        "form-control",
                    "placeholder":  _("Group Name"),
                    "maxlength":    30,
                }),
            }

    def save(self, commit=True):
        """Docstring."""
        instance = super(GroupForm, self).save(commit=False)
        instance.creator = self.user
        instance.book = self.book

        if commit:
            instance.save()

        return instance


class InviteForm(forms.ModelForm):

    """Docstring."""

    def __init__(self, *args, **kwargs):
        """Docstring."""
        self.user = kwargs.pop("user", None)
        self.group = kwargs.pop("group", None)

        super(InviteForm, self).__init__(*args, **kwargs)

        if self.instance and self.instance.pk:
            pass

        self.fields["recipient_name"].label = _("Recipient Name")
        self.fields["recipient_email"].label = _("Recipient Email")

    class Meta:
        model = Invite
        fields = [
            "recipient_name", "recipient_email",
        ]
        widgets = {
            "recipient_name": forms.TextInput(
                attrs={
                    "class":        "form-control",
                    "placeholder":  _("Recipient Name"),
                    "maxlength":    30,
                }),
            "recipient_email": forms.EmailInput(
                attrs={
                    "class":        "form-control",
                    "placeholder":  _("Recipient Email"),
                }),
            }

    def save(self, commit=True):
        """Docstring."""
        instance = super(InviteForm, self).save(commit=False)
        instance.sender_user = self.user
        instance.group = self.group

        if commit:
            instance.save()

        return instance


class InviteMessageForm(forms.Form):

    """Docstring."""

    invite_message = forms.CharField(
        label=_("Message"),
        widget=forms.Textarea(
            attrs={
                "class":        "form-control",
                "placeholder":  _("Enter your Message here..."),
                "value":        "",
            }))
