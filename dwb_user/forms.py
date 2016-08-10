import re

from django import forms
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _

from .models import Profile


class LoginForm(forms.Form):

    """Login Form."""

    email = forms.CharField(
        label=_("Email Address"),
        widget=forms.TextInput(
            attrs={
                "class":        "form-control",
                "placeholder":  _("Email Address"),
                "value":        "",
            }))
    password = forms.CharField(
        label=_("Password"),
        widget=forms.PasswordInput(
            attrs={
                "min_length":   6,
                "max_length":   30,
                "class":        "form-control",
                "placeholder":  _("Password"),
                "value":        "",
            }))
    remember_me = forms.BooleanField(
        label=_("Keep me logged in"),
        required=False,
        initial=True)

    def clean(self):
        """Docstring."""
        from .services import authenticate

        cleaned_data = super(LoginForm, self).clean()

        if cleaned_data.get("email") and cleaned_data.get("password"):
            user = authenticate(
                cleaned_data.get("email"),
                cleaned_data.get("password"))

            if user:
                cleaned_data["user"] = user
            else:
                raise forms.ValidationError(
                    _("Incorrect email address or password."))

        return cleaned_data


class RegisterForm(forms.Form):

    """Register Form."""

    full_name = forms.CharField(
        label=_("Your Name"),
        widget=forms.TextInput(
            attrs={
                "min_length":   6,
                "class":        "form-control",
                "placeholder":  _("Your Name"),
                "value":        "",
            }))
    email = forms.EmailField(
        label=_("Email Address"),
        widget=forms.TextInput(
            attrs={
                "class":        "form-control",
                "placeholder":  _("Email Address"),
                "value":        "",
            }))
    password = forms.CharField(
        label=_("Password"),
        widget=forms.PasswordInput(
            attrs={
                "min_length":   6,
                "max_length":   30,
                "class":        "form-control",
                "placeholder":  _("Password"),
                "value":        "",
            }))
    is_pastor = forms.ChoiceField(
        (
            ("0",   _("No")),
            ("1",   _("Yes"))
        ),
        label=_("Are you a Pastor/Leader?"))
    church_name = forms.CharField(
        label=_("If yes, enter your church name"),
        required=False,
        widget=forms.TextInput(
            attrs={
                "class":        "form-control",
                "placeholder":  _("Church Name"),
                "value":        "",
            }))

    def clean(self):
        """Docstring."""
        cleaned_data = super(RegisterForm, self).clean()

        # get first name and last name from full name
        if cleaned_data.get("full_name"):
            full_name = cleaned_data["full_name"]
            full_name = full_name.strip()
            full_name = re.sub(r"\s+", " ", full_name)
            name_parts = full_name.split(" ", 1)

            if len(name_parts) == 2:
                cleaned_data["first_name"] = name_parts[0]
                cleaned_data["last_name"] = name_parts[1]
            else:
                cleaned_data["first_name"] = full_name
                cleaned_data["last_name"] = ""

        # check for duplicate email
        if cleaned_data.get("email"):
            others = User.objects.filter(
                email__iexact=cleaned_data["email"]
                ).count()

            if others:
                raise forms.ValidationError(
                    _("Provided email address is already registered."))

        return cleaned_data


class ProfileForm(forms.ModelForm):

    """Profile Form."""

    class Meta:
        model = User
        fields = [
            "first_name", "last_name", "email",
        ]
        widgets = {
            "first_name": forms.TextInput(
                attrs={
                    "class":        "form-control",
                    "placeholder":  _("First Name"),
                    "maxlength":    30,
                }),
            "last_name": forms.TextInput(
                attrs={
                    "class":        "form-control",
                    "placeholder":  _("Last Name"),
                    "maxlength":    30,
                }),
            "email": forms.EmailInput(
                attrs={
                    "class":        "form-control",
                    "placeholder":  _("Email"),
                }),
            }

    def clean_first_name(self):
        """Docstring."""
        value = self.cleaned_data.get("first_name", "")
        value = value.strip()

        if value == "":
            raise forms.ValidationError(
                _("First name is required."))

        return value

    def clean_last_name(self):
        """Docstring."""
        value = self.cleaned_data.get("last_name", "")
        value = value.strip()

        if value == "":
            raise forms.ValidationError(
                _("Last name is required."))

        return value

    def clean_email(self):
        """Docstring."""
        value = self.cleaned_data.get("email", "")
        value = value.strip()

        if value == "":
            raise forms.ValidationError(
                _("Email address is required."))

        others = User.objects.filter(email__iexact=value)

        for other in others:
            if self.instance and other.id != self.instance.id:
                raise forms.ValidationError(
                    _("This email address is not available."))

        return value


class ProfileInfoForm(forms.ModelForm):

    """Profile Info Form."""

    def __init__(self, *args, **kwargs):
        """Docstring."""
        super(ProfileInfoForm, self).__init__(*args, **kwargs)

        self.fields["is_pastor"].label = _("Is Pastor")
        self.fields["church_name"].label = _("Church Name")

    class Meta:
        model = Profile
        fields = [
            "is_pastor", "church_name",
        ]
        widgets = {
            "church_name": forms.TextInput(
                attrs={
                    "class":        "form-control",
                    "placeholder":  _("Church Name"),
                    "maxlength":    30,
                }),
            }


class EmailClaimCodeForm(forms.Form):

    """Email Claim Code Form."""

    recipient_name = forms.CharField(
        label=_("Name"),
        max_length=255)
    recipient_email = forms.EmailField(
        label=_("Email"))


# -----------------------------------------------------------------------------
# --- RESET PASSWORD FORM
# -----------------------------------------------------------------------------
class ResetPasswordForm(forms.Form):

    """Reset Password Form."""

    password = forms.CharField(
        label=_("Password"),
        widget=forms.PasswordInput(
            attrs={
                "min_length":   6,
                "max_length":   30,
                "class":        "form-control",
                "placeholder":  _("Password"),
                "value":        "",
            }))
    retry = forms.CharField(
        label=_("Retry"),
        widget=forms.PasswordInput(
            attrs={
                "min_length":   6,
                "max_length":   30,
                "class":        "form-control",
                "placeholder":  _("Retry"),
                "value":        "",
            }))

    def clean_retry(self):
        """Docstring."""
        if self.cleaned_data["retry"] != self.cleaned_data.get("password", ""):
            raise forms.ValidationError(
                _("Passwords don't match"))

        return self.cleaned_data["retry"]
