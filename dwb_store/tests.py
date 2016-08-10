from decimal import Decimal

from django.contrib.auth.models import User
from django.http import HttpRequest
from django.test import TestCase
from django.test.client import Client

from dwb_book.models import Book
from dwb_store.models import Purchase


class TemplateTagsTest(TestCase):

    """Template Tags Test."""

    def test_float_price(self):
        """Docstring."""
        from .templatetags.webbook import price

        actual = price(1.2)
        self.assertEquals("$ 1.20 USD", actual)

    def test_decimal_price(self):
        """Docstring."""
        from .templatetags.webbook import price

        actual = price(Decimal(1.2))
        self.assertEquals("$ 1.20 USD", actual)


class ServiceTest(TestCase):

    """Service Test."""

    fixtures = [
        "auth_user.json",
        "dwb_book.json",
    ]

    def test_send_gift_code(self):
        """Docstring."""
        from .service import send_gift_code

        purchase = Purchase()
        purchase.book = Book.objects.all()[0]
        purchase.buyer_user = User.objects.all()[0]
        purchase.recipient_email = "friend@example.com"
        purchase.generate_gift_code()

        request = self.create_request()
        send_gift_code(request, purchase)

    def test_send_invoice(self):
        """Docstring."""
        from .service import send_invoice

        purchase = Purchase()
        purchase.book = Book.objects.all()[0]
        purchase.buyer_user = User.objects.all()[0]
        purchase.buyer_email = purchase.buyer_user.email
        purchase.generate_gift_code()
        purchase.total_charge = 15

        request = self.create_request()
        send_invoice(request, purchase)

    def test_create_payment(self):
        """Docstring."""
        from .service import create_payment

        book = Book.objects.all()[0]
        user = User.objects.all()[0]

        purchase = Purchase()
        purchase.book = book
        purchase.buyer_user = user
        purchase.buyer_email = user.email
        purchase.price = book.price
        purchase.total_charge = book.price

        response = create_payment(
            purchase,
            return_url="http://example.com/success",
            cancel_url="http://example.com/cancel")
        self.assertTrue("approval_url" in response)
        self.assertTrue("id" in response)

    def create_request(self):
        """Docstring."""
        request = HttpRequest()
        request.META["SERVER_NAME"] = "testserver"
        request.META["SERVER_PORT"] = 80

        return request


class DiscountsViewText(TestCase):

    """Discount View Test."""

    fixtures = [
        "auth_user.json",
        "dwb_book.json",
        "dwb_group.json",
        "dwb_member.json",
    ]

    def setUp(self):
        """Docstring."""
        for user in User.objects.all():
            user.set_password("secret")
            user.save()

        for book in Book.objects.all():
            book.price = 0
            book.save()

    def test_lending_page(self):
        """Docstring."""
        client = Client()
        response = client.get(
            "/store/discounts/")
        self.assertEquals(200, response.status_code)

    def test_status(self):
        """Docstring."""
        client = Client()
        client.login(
            username="tom",
            password="secret")

        response = client.get(
            "/store/discounts/principles-of-discipling/")
        self.assertEquals(200, response.status_code)

        response = client.get(
            "/store/discounts/future-best-seller/")
        self.assertEquals(200, response.status_code)
        self.assertContains(response, "This book is not for sale")

        response = client.get(
            "/store/discounts/top-secret/")
        self.assertEquals(404, response.status_code)

    def test_force_login(self):
        """Docstring."""
        client = Client()
        response = client.get(
            "/store/discounts/principles-of-discipling/")
        self.assertEquals(302, response.status_code)

        client.login(
            username="tom",
            password="secret")
        response = client.get(
            "/store/discounts/principles-of-discipling/")
        self.assertEquals(200, response.status_code)

    def test_purchase_and_new_group(self):
        """Docstring."""
        client = Client()
        client.login(
            username="tom",
            password="secret")

        data = {
            "quantity":     20,
            "group":        "new",
            "group_name":   "Hope 2014"
        }
        response = client.post(
            "/store/discounts/principles-of-discipling/", data)
        self.assertEquals(302, response.status_code)

        purchase = list(Purchase.objects.all())[-1]
        self.assertIsNotNone(purchase.group)
        self.assertEquals("Hope 2014", purchase.group.name)

        response = client.get(
            "/account/")
        self.assertContains(response, "Principles of Discipling")

        response = client.get(
            "/workbook/principles-of-discipling/")
        self.assertContains(response, "Hope 2014")

    def test_purchase_with_no_group(self):
        """Docstring."""
        client = Client()
        client.login(
            username="tom",
            password="secret")

        data = {
            "quantity":     20,
            "group":        "",
            "group_name":   "Hope 2014"
        }
        response = client.post(
            "/store/discounts/principles-of-discipling/", data)
        self.assertEquals(302, response.status_code)

        purchase = list(Purchase.objects.all())[-1]
        self.assertIsNone(purchase.group)

    def test_purchase_with_old_group(self):
        """Docstring."""
        client = Client()
        client.login(
            username="tom",
            password="secret")

        data = {
            "quantity":     20,
            "group":        "1"
        }
        response = client.post(
            "/store/discounts/principles-of-discipling/", data)
        self.assertEquals(302, response.status_code)

        purchase = list(Purchase.objects.all())[-1]
        self.assertIsNotNone(purchase.group)
        self.assertEquals("Cats", purchase.group.name)


class BuyViewTest(TestCase):

    """Buy View Test."""

    fixtures = [
        "auth_user.json",
        "dwb_book.json",
    ]

    def setUp(self):
        """Docstring."""
        for user in User.objects.all():
            user.set_password("secret")
            user.save()

        for book in Book.objects.all():
            book.price = 0
            book.save()

    def test_status(self):
        """Docstring."""
        client = Client()
        response = client.get(
            "/store/buy/principles-of-discipling/")
        self.assertEquals(200, response.status_code)

        client = Client()
        response = client.get(
            "/store/buy/future-best-seller/")
        self.assertEquals(200, response.status_code)
        self.assertContains(response, "This book is not for sale")

        client = Client()
        response = client.get(
            "/store/buy/top-secret/")
        self.assertEquals(404, response.status_code)

    def test_buy_for_myself_force_login(self):
        """Docstring."""
        client = Client()
        response = client.get(
            "/store/buy/principles-of-discipling/")
        self.assertEquals(200, response.status_code)

        response = client.post(
            "/store/buy/principles-of-discipling/", {
                "gift":     ""
            })
        self.assertEquals(302, response.status_code)
        self.assertTrue("/login/" in response["location"])

    def test_buy_for_myself_checkout(self):
        """Docstring."""
        client = Client()
        client.login(
            username="tom",
            password="secret")
        user = User.objects.get(
            username="tom")
        book = Book.objects.get(
            slug="principles-of-discipling")

        response = client.get(
            "/store/buy/principles-of-discipling/")
        self.assertEquals(200, response.status_code)

        response = client.post(
            "/store/buy/principles-of-discipling/", {
                "gift":     "0"
            })
        self.assertEquals(302, response.status_code)
        self.assertTrue("/confirm/" in response["location"])

        purchase = list(Purchase.objects.all())[-1]

        response = client.get(
            "/store/purchase/%s/confirm/" % (purchase.invoice_number,))
        self.assertEquals(200, response.status_code)

        response = client.post(
            "/store/purchase/%s/confirm/" % (purchase.invoice_number,))
        self.assertEquals(302, response.status_code)
        self.assertTrue("/complete/" in response["location"])

        response = client.get(
            "/store/purchase/%s/complete/" % (purchase.invoice_number,))
        self.assertEquals(200, response.status_code)

        copy = book.get_or_create_copy(user)
        self.assertEquals("progress", copy.status)

    def test_already_purchased(self):
        """Docstring."""
        client = Client()
        client.login(username="tom", password="secret")

        # make sure they already have a copy
        book = Book.objects.all()[0]
        user = User.objects.get(username="tom")
        copy = book.get_or_create_copy(user)
        copy.status = "progress"
        copy.save()

        # cannot buy another copy
        response = client.post(
            "/store/buy/principles-of-discipling/", {
                "gift":     "0"
            })
        self.assertEquals(302, response.status_code)
        self.assertTrue("/confirm/" not in response["location"])
        self.assertTrue("/workbook/principles-of-discipling/" in response["location"])

        # can buy a gift
        response = client.post(
            "/store/buy/principles-of-discipling/", {
                "gift":     "1"
            })
        self.assertEquals(302, response.status_code)
        self.assertTrue("/confirm/" in response["location"])


class RedeemViewTest(TestCase):

    """Redeem View Test."""

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

    def test_happy_case(self):
        """Docstring."""
        client = Client()
        client.login(
            username="tom",
            password="secret")

        response = client.get(
            "/store/redeem/")
        self.assertEquals(200, response.status_code)
        self.assertContains(response, ">Submit</button>")

        response = client.get(
            "/store/redeem/?code=gift-2")
        self.assertEquals(200, response.status_code)
        self.assertContains(response, ">Redeem</button>")

        response = client.post(
            "/store/redeem/?code=gift-2")
        self.assertEquals(302, response.status_code)
        self.assertEquals(
            "http://testserver/workbook/principles-of-discipling/",
            response["location"])

    def test_not_payed(self):
        """Docstring."""
        client = Client()
        client.login(
            username="tom",
            password="secret")

        response = client.get(
            "/store/redeem/?code=gift-1")
        self.assertEquals(302, response.status_code)
        self.assertEquals(
            "http://testserver/store/redeem/",
            response["location"])

        response = client.post(
            "/store/redeem/?code=gift-1")
        self.assertEquals(302, response.status_code)
        self.assertEquals(
            "http://testserver/store/redeem/",
            response["location"])
