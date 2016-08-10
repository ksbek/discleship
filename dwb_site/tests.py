from django.contrib.auth.models import User
from django.test import TestCase
from django.test.client import Client


class ViewHomeTest(TestCase):

    """View 'Home' Tests."""

    fixtures = [
        "auth_user.json",
        "dwb_book.json",
    ]

    def setUp(self):
        """Docstring."""
        from django.contrib.auth.models import User
        for user in User.objects.all():
            user.set_password("secret")
            user.save()

    def test_show_home(self):
        """Check if home page shows."""
        client = Client()
        response = client.get("/")
        self.assertEquals(response.status_code, 200)
        self.assertContains(response, "Welcome")
        self.assertContains(response, "Principles of Discipling")
        self.assertContains(response, "principles-of-discipling")
        self.assertContains(response, "My Little Book")
        self.assertContains(response, "Future Best Seller")

        self.assertNotContains(response, "Secret Project")
        self.assertNotContains(response, "top-secret")

    def test_overview_with_groups(self):
        """Docstring."""
        from dwb_book.models import Book
        from dwb_group.models import Group, Member

        # assign to users to one group
        book = Book.objects.all()[0]
        user_a = User.objects.all()[0]
        user_b = User.objects.all()[1]

        group = Group(
            name="Group AAA",
            book=book)
        group.creator = user_a
        group.save()

        Member(
            group=group,
            user=user_a
        ).save()
        Member(
            group=group,
            user=user_b
        ).save()

        book.get_or_create_copy(user_a)
        book.get_or_create_copy(user_b)

        # check if progress is shown
        client = Client()
        client.login(
            username=user_a.username,
            password="secret")

        response = client.get(
            "/workbook/%s/" % (book.slug,))
        self.assertContains(response, "Groups")
        self.assertContains(response, group.name)
        self.assertContains(response, user_b.get_full_name())


class SponsorViewTest(TestCase):

    """View 'Sponsor' Tests."""

    fixtures = [
        "auth_user.json",
        "dwb_book.json",
        "dwb_group.json",
        "dwb_member.json".
    ]

    def setUp(self):
        """Docstring."""
        for user in User.objects.all():
            user.set_password("secret")
            user.save()

    def test_get(self):
        """Docstring."""
        client = Client()
        client.login(
            username="tom",
            password="secret")

        response = client.get(
            "/workbook/principles-of-discipling/sponsor/1/")
        self.assertEquals(200, response.status_code)

    def test_submit(self):
        """Docstring."""
        client = Client()
        client.login(
            username="tom",
            password="secret")

        response = client.post(
            "/workbook/principles-of-discipling/sponsor/1/")
        self.assertEquals(302, response.status_code)
        self.assertTrue("paypal.com" in response["location"])

    def test_wrong_group(self):
        """Docstring."""
        client = Client()
        client.login(
            username="tom",
            password="secret")

        response = client.get("/workbook/principles-of-discipling/sponsor/2/")
        self.assertEquals(404, response.status_code)
