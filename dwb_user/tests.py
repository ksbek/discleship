from django.contrib.auth.models import User
from django.test import TestCase
from django.test.client import Client


class ViewTest(TestCase):

    """View Test."""

    fixtures = [
        "auth_user.json",
    ]

    def setUp(self):
        """Docstring."""
        for user in User.objects.all():
            user.set_password("secret")
            user.save()

    def test_login(self):
        """Docstring."""
        client = Client()
        response = client.get(
            "/account/login/")
        self.assertEquals(response.status_code, 200)

        data = {
            "email":    "tom@example.com",
            "password": "secret",
        }
        response = client.post(
            "/account/login/", data)
        self.assertEquals(response.status_code, 302)

    def test_login_failed(self):
        """Docstring."""
        client = Client()

        data = {
            "email":    "tom@example.com",
            "password": "wrong",
        }
        response = client.post(
            "/account/login/", data)
        self.assertEquals(response.status_code, 200)
        self.assertContains(response, "Incorrect email address or password")

    def test_register(self):
        """Docstring."""
        client = Client()
        response = client.get(
            "/account/register/")
        self.assertEquals(response.status_code, 200)

        data = {
            "full_name":    "John Johnson",
            "email":        "john@example.com",
            "password":     "secret",
        }
        response = client.post(
            "/account/register/", data)
        self.assertEquals(response.status_code, 302)

    def test_register_duplicate_email(self):
        """Docstring."""
        client = Client()
        response = client.get("/account/register/")
        self.assertEquals(response.status_code, 200)

        data = {
            "full_name":    "John Johnson",
            "email":        "tom@example.com",
            "password":     "secret",
        }
        response = client.post(
            "/account/register/", data)
        self.assertEquals(response.status_code, 200)
        self.assertContains(response, "Email address is already registered")

    def test_edit_profile_ok(self):
        """Docstring."""
        client = Client()
        client.login(
            username="jerry",
            password="secret")

        response = client.get(
            "/account/edit-profile/")
        self.assertEquals(response.status_code, 200)

        data = {
            "first_name":   "J",
            "last_name":    "Jerry",
            "email":        "jerry@example.com",
        }
        response = client.post(
            "/account/edit-profile/", data)
        self.assertEquals(response.status_code, 302)

    def test_edit_profile_duplicate_email(self):
        """Docstring."""
        client = Client()
        client.login(
            username="jerry",
            password="secret")

        response = client.get(
            "/account/edit-profile/")
        self.assertEquals(response.status_code, 200)

        data = {
            "first_name":   "Tom",
            "last_name":    "T",
            "email":        "tom@example.com",
            }
        response = client.post(
            "/account/edit-profile/", data)
        self.assertEquals(response.status_code, 200)
        self.assertContains(response, "email address is not available")
