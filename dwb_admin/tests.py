from django.contrib.auth.models import User
from django.test import TestCase
from django.test.client import Client
from dwb_book.models import Book
from dwb_store.models import Purchase


class ViewsTest(TestCase):

    """Views Test."""

    fixtures = [
        "auth_user.json",
        "dwb_book.json",
        "dwb_purchase.json",
    ]

    def setUp(self):
        """Docstring."""
        for user in User.objects.all():
            user.set_password("secret")
            user.save()

        self.client = Client()
        self.client.login(
            username="admin",
            password="secret")

    def test_home(self):
        """Docstring."""
        response = self.client.get("/admin/")
        self.assertEquals(200, response.status_code)
        self.assertTrue("Principles of Discipling" in response.content)

    def test_list_purchases(self):
        """Docstring."""
        response = self.client.get("/admin/book/1/purchases/")
        self.assertEquals(200, response.status_code)
        self.assertTrue("Principles of Discipling" in response.content)

    def test_show_purchase(self):
        """Docstring."""
        response = self.client.get("/admin/purchase/1/")
        self.assertEquals(200, response.status_code)
        self.assertTrue("Pending" in response.content)

    def test_add_purchase(self):
        """Docstring."""
        response = self.client.get("/admin/purchase/add/")
        self.assertEquals(200, response.status_code)
        self.assertTrue("Principles of Discipling" in response.content)
