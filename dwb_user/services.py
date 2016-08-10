from django.contrib.auth import authenticate as django_authenticate
from django.contrib.auth.models import User
from django.utils.translation import ugettext as _


def authenticate(email, password):
    """Docstring."""
    if '@' in email:
        candidates = User.objects.filter(email=email)
    else:
        candidates = User.objects.filter(username=email)

    for candidate in candidates:
        user = django_authenticate(
            username=candidate.username,
            password=password)

        if user:
            return user

    return None
