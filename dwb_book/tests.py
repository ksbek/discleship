# -*- coding: utf-8 -*-

from django.test import TestCase
from django.test.client import Client


class ModelTest(TestCase):

    """Model Test."""

    fixtures = [
        "auth_user.json",
        "dwb_book.json",
        "dwb_item.json",
        "dwb_copy.json",
    ]

    def test_book_item_order(self):
        """Docstring."""
        from .models import Book

        book = Book.objects.get(
            pk=1)
        book.set_item_order([11, 10])

        items = book.item_set.all()
        self.assertEquals(8, len(items))
        self.assertEquals(11, items[0].id)
        self.assertEquals(0, items[0]._order)
        self.assertEquals(10, items[1].id)
        self.assertEquals(1, items[1]._order)

    def test_get_parent(self):
        """Docstring."""
        from .models import Book, Item

        book = Book.objects.get(
            pk=1)

        Item(book=book, item_type="h1", title="A").save()
        Item(book=book, item_type="h2", title="AA").save()
        Item(book=book, item_type="h2", title="AB").save()
        Item(book=book, item_type="h2", title="AC").save()
        Item(book=book, item_type="h3", title="ACA").save()
        Item(book=book, item_type="h3", title="ACB").save()
        Item(book=book, item_type="h2", title="AD").save()
        Item(book=book, item_type="h1", title="B").save()
        Item(book=book, item_type="h1", title="C").save()

        item = Item.objects.get(title="ACB")
        item = item.get_previous_item()
        self.assertEquals("ACA", item.title)
        item = item.get_previous_item()
        self.assertEquals("AC", item.title)

        found = Item.objects.get(title="ACB").get_parent()
        self.assertEquals("AC", found.title)

        found = Item.objects.get(title="ACB").get_parent("h1")
        self.assertEquals("A", found.title)

        found = Item.objects.get(title="C").get_parent()
        self.assertIsNone(found)

    def test_copy_set_response_to(self):
        """Docstring."""
        from .models import Copy, Item

        copy = Copy.objects.filter(
            book=1)[0]
        item = Item.objects.get(
            pk=14)

        copy.set_response_to(item, 0)
        self.assertEquals("0", copy.get_response_to(item))

        copy.set_response_to(item, "yeah")
        self.assertEquals("yeah", copy.get_response_to(item))

        copy.set_response_to(item, "yahoo")
        self.assertEquals("yahoo", copy.get_response_to(item))

    def test_get_pricing(self):
        """Docstring."""
        from .models import Book, Pricing

        book = Book.objects.get(
            pk=1)
        book.price = 55
        book.save()

        Pricing(book=book, min_quantity=40, price=40).save()
        Pricing(book=book, min_quantity=10, price=50).save()
        Pricing(book=book, min_quantity=80, price=35).save()
        Pricing(book=book, min_quantity=20, price=45).save()

        self.assertEquals(book.get_price_for_quantity(0), 55)
        self.assertEquals(book.get_price_for_quantity(9), 55)
        self.assertEquals(book.get_price_for_quantity(10), 50)
        self.assertEquals(book.get_price_for_quantity(11), 50)
        self.assertEquals(book.get_price_for_quantity(19), 50)
        self.assertEquals(book.get_price_for_quantity(20), 45)
        self.assertEquals(book.get_price_for_quantity(21), 45)
        self.assertEquals(book.get_price_for_quantity(40), 40)
        self.assertEquals(book.get_price_for_quantity(41), 40)
        self.assertEquals(book.get_price_for_quantity(80), 35)
        self.assertEquals(book.get_price_for_quantity(81), 35)


class ServiceTest(TestCase):

    """Service Test."""

    fixtures = [
        "auth_user.json",
        "dwb_book.json",
        "dwb_item.json",
    ]

    def test_apply_markers_simple(self):
        """Docstring."""
        from .models import Marker
        from .services import apply_markers

        original = "pre [my marker] post"
        marker = Marker(
            placeholder="[my marker]",
            replacement="<span>smile</span>")

        actual = apply_markers(original, [marker])
        self.assertEquals(actual, "pre <span>smile</span> post")

    def test_apply_markers_nbsp(self):
        """Docstring."""
        from .models import Marker
        from .services import apply_markers

        original = "pre [my&nbsp;marker] post"
        marker = Marker(
            placeholder="[my marker]",
            replacement="<span>smile</span>")

        actual = apply_markers(original, [marker])
        self.assertEquals(actual, "pre <span>smile</span> post")

    def test_get_page_items(self):
        """Docstring."""
        from .models import Book, Item
        from .services import get_page_items

        book = Book.objects.get(pk=1)

        Item(
            book=book,
            item_type="h1",
            title="A",
            _order=0).save()  # 0
        Item(
            book=book,
            item_type="h2",
            title="AA").save()
        Item(
            book=book,
            item_type="text",
            title="AB").save()
        Item(
            book=book,
            item_type="h2",
            title="AC").save()  # 3
        Item(
            book=book,
            item_type="h3",
            title="ACA").save()
        Item(
            book=book,
            item_type="h3",
            title="ACB").save()  # 5
        Item(
            book=book,
            item_type="h2",
            title="AD").save()  # 6
        Item(
            book=book,
            item_type="h1",
            title="B").save()  # 7
        Item(
            book=book,
            item_type="h1",
            title="C").save()  # 8

        items = get_page_items(book, 0)
        self.assertTrue(3, len(items))
        self.assertTrue("A", items[0].title)

        items = get_page_items(book, 3)
        self.assertTrue(2, len(items))
        self.assertTrue("AC", items[0].title)

        items = get_page_items(book, 5)
        self.assertTrue(1, len(items))
        self.assertTrue("ACB", items[0].title)

        items = get_page_items(book, 6)
        self.assertTrue(1, len(items))
        self.assertTrue("AD", items[0].title)

        items = get_page_items(book, 7)
        self.assertTrue(1, len(items))
        self.assertTrue("B", items[0].title)

        items = get_page_items(book, 8)
        self.assertTrue(1, len(items))
        self.assertTrue("C", items[0].title)

    def test_update_progress(self):
        """Docstring."""
        from .models import Book, Copy, Item
        from .services import update_progress

        book = Book.objects.get(
            pk=1)
        copy = Copy(
            book=book)
        item_10 = Item.objects.get(
            pk=10)
        item_13 = Item.objects.get(
            pk=13)

        # progress should be updated when going forward
        update_progress(copy, item_13)
        self.assertEqual(42, int(copy.overall_progress))
        self.assertEqual(item_13, copy.current_item)

        # nothing should change if we are going back
        update_progress(copy, item_10)
        self.assertEqual(42, int(copy.overall_progress))
        self.assertEqual(item_13, copy.current_item)

    def test_update_progress_to_appendix(self):
        """Docstring."""
        from .models import Book, Copy, Item
        from .services import update_progress

        book = Book.objects.get(
            pk=1)
        copy = Copy(
            book=book)
        item_17 = Item.objects.get(
            pk=17)

        # nothing should change if we are going back
        update_progress(copy, item_17)
        self.assertEqual(100, int(copy.overall_progress))
        self.assertEqual(None, copy.current_item)
        self.assertEqual("completed", copy.status)

    def test_delete_copy_data(self):
        """Docstring."""
        from .models import Book, Copy, Item
        from django.contrib.auth.models import User
        from .services import delete_copy_data

        # create a copy with some data
        book = Book.objects.get(
            pk=1)
        user = User.objects.get(
            pk=1)
        item = Item.objects.get(
            pk=14)
        copy = Copy(
            book=book,
            user=user)
        copy.overall_progress = 50
        copy.save()

        copy.set_response_to(item, "Yes!!")
        copy.save()

        # check it
        self.assertEquals(1, copy.response_set.count())

        # delete and check it
        delete_copy_data(copy)
        self.assertEquals(0, copy.overall_progress)
        self.assertEquals(0, copy.response_set.count())

    def test_get_chapter_items(self):
        """Docstring."""
        from .models import Book, Item
        from .services import get_chapter_items

        book = Book()
        book.price = 1
        book.certificate_background_width = 100
        book.certificate_background_height = 100
        book.certificate_name_top = 50
        book.save()

        item_a = Item(
            book=book,
            title="a",
            item_type="h1")
        item_a.save()
        item_b = Item(
            book=book,
            title="b",
            item_type="h2")
        item_b.save()
        item_c = Item(
            book=book,
            title="c",
            item_type="h2")
        item_c.save()
        item_d = Item(
            book=book,
            title="d",
            item_type="h1")
        item_d.save()
        item_e = Item(
            book=book,
            title="e",
            item_type="h1")
        item_e.save()

        # check chapter A
        items = get_chapter_items(book, item_a)
        self.assertEqual(3, len(items))
        self.assertEqual(item_a, items[0])
        self.assertEqual(item_b, items[1])
        self.assertEqual(item_c, items[2])

        # check chapter A, passing item B
        items = get_chapter_items(book, item_b)
        self.assertEqual(3, len(items))
        self.assertEqual(item_a, items[0])
        self.assertEqual(item_b, items[1])
        self.assertEqual(item_c, items[2])

        # check chapter D
        items = get_chapter_items(book, item_d)
        self.assertEqual(1, len(items))
        self.assertEqual(item_d, items[0])

        # check chapter E
        items = get_chapter_items(book, item_d)
        self.assertEqual(1, len(items))

    def test_html_to_pdf__unicode(self):
        """Docstring."""
        from dwb_book.services import html_to_pdf

        pdf_content = html_to_pdf(u"<html><body>ąę</body></html>")
        self.assertTrue(pdf_content)


class BookViewTest(TestCase):

    """Book View Test."""

    fixtures = [
        "auth_user.json",
        "dwb_book.json",
        "dwb_item.json",
        "dwb_copy.json",
    ]

    def setUp(self):
        """Docstring."""
        from django.contrib.auth.models import User

        for user in User.objects.all():
            user.set_password("secret")
            user.save()

    def test_homepage(self):
        """Docstring."""
        client = Client()

        response = client.get("/")
        self.assertEquals(response.status_code, 200)
        self.assertContains(response, "My Little Book")
        self.assertContains(response, "Principles of Discipling")
        self.assertContains(response, "Future Best Seller")
        self.assertNotContains(response, "Secret Project")

    def test_homepage_when_logged_in(self):
        """All books user owns should show first."""
        client = Client()
        response = client.login(
            username="tom",
            password="secret")
        self.assertTrue(response)

        response = client.get("/")
        self.assertEquals(response.status_code, 200)
        self.assertContains(response, "My Little Book")
        self.assertContains(response, "Principles of Discipling")
        self.assertContains(response, "Future Best Seller")
        self.assertNotContains(response, "Secret Project")

    def test_book_overview_when_logged_in(self):
        """Docstring."""
        client = Client()
        response = client.login(
            username="tom",
            password="secret")

        response = client.get("/workbook/principles-of-discipling/")
        self.assertEquals(response.status_code, 200)
        self.assertContains(response, "Principles of Discipling")

    def test_book_toc(self):
        """Docstring."""
        client = Client()
        response = client.get(
            "/workbook/principles-of-discipling/table-of-content/")

        self.assertEquals(response.status_code, 200)
        self.assertContains(response, "Principles of Discipling")
        self.assertContains(response, "Introduction")

    def test_congratulations_page(self):
        """Docstring."""
        from .models import Copy

        copy = Copy.objects.get(
            book__slug="principles-of-discipling",
            user__username="jerry")
        copy.status = "completed"
        copy.save()

        client = Client()
        response = client.login(
            username="jerry",
            password="secret")
        response = client.get(
            "/workbook/principles-of-discipling/congratulations/")
        self.assertEquals(response.status_code, 200)
        self.assertContains(response, "certificate")
        self.assertContains(response, "Print")

    def test_congratulations_for_not_complete_book(self):
        """Docstring."""
        from .models import Copy

        copy = Copy.objects.get(
            book__slug="principles-of-discipling",
            user__username="jerry")
        copy.status = "progress"
        copy.save()

        client = Client()
        response = client.login(
            username="jerry",
            password="secret")
        response = client.get(
            "/workbook/principles-of-discipling/congratulations/")
        self.assertEquals(response.status_code, 302)

    def test_print_certificate(self):
        """Docstring."""
        from .models import Copy

        copy = Copy.objects.get(
            book__slug="principles-of-discipling",
            user__username="jerry")
        copy.status = "completed"
        copy.save()

        client = Client()
        response = client.login(
            username="jerry",
            password="secret")
        response = client.get(
            "/workbook/principles-of-discipling/certificate/")
        self.assertContains(response, "window.print")

    def test_print_certificate_for_not_completed_book(self):
        """Docstring."""
        from .models import Copy

        copy = Copy.objects.get(
            book__slug="principles-of-discipling",
            user__username="jerry")
        copy.status = "progress"
        copy.save()

        client = Client()
        response = client.login(
            username="jerry",
            password="secret")
        response = client.get(
            "/workbook/principles-of-discipling/certificate/")
        self.assertEquals(response.status_code, 302)


class PageViewTest(TestCase):

    """Page View Test."""

    fixtures = [
        "auth_user.json",
        "dwb_book.json",
        "dwb_item.json",
        "dwb_marker.json",
    ]

    def setUp(self):
        """Docstring."""
        from django.contrib.auth.models import User

        for user in User.objects.all():
            user.set_password("secret")
            user.save()

    def test_show_page(self):
        """Docstring."""
        client = Client()
        response = client.get("/workbook/principles-of-discipling/0/")
        self.assertEqual(200, response.status_code)
        self.assertContains(response, "intro_to_welcome")
        self.assertContains(response, "First footnote")

    def test_save_page(self):
        """Docstring."""
        client = Client()
        response = client.post(
            "/workbook/principles-of-discipling/0/", {
                "action":   "save"
            })
        self.assertEqual(302, response.status_code)
        self.assertTrue("/0/" in response["location"])

    def test_continue_page(self):
        """Docstring."""
        client = Client()
        response = client.post(
            "/workbook/principles-of-discipling/0/", {
                "action":   "continue"
            })
        self.assertEqual(302, response.status_code)
        self.assertTrue("/3/" in response["location"])

    def test_marker(self):
        """Docstring."""
        response = self.client.get(
            "/workbook/principles-of-discipling/0/")
        self.assertContains(response, "<span>Fact File</span>")


class PageSumitTest(TestCase):

    """Page Sumit Test."""

    fixtures = [
        "auth_user.json",
        "dwb_book.json",
        "dwb_item.json",
    ]

    def setUp(self):
        """Docstring."""
        from django.contrib.auth.models import User
        from .models import Copy

        for user in User.objects.all():
            user.set_password("secret")
            user.save()

        self.client = Client()
        self.client.login(
            username="tom",
            password="secret")

        self.client.get(
            "/workbook/principles-of-discipling/1/")

        for copy in Copy.objects.all():
            copy.status = "progress"
            copy.save()

    def test_happy_case(self):
        """Docstring."""
        self.client.post(
            "/workbook/principles-of-discipling/0/", {
                "action":   "continue"
            })
        self.client.post(
            "/workbook/principles-of-discipling/1/", {
                "action":   "continue"
            })
        self.client.post(
            "/workbook/principles-of-discipling/2/", {
                "action":   "continue"
            })
        response = self.client.post(
            "/workbook/principles-of-discipling/3/", {
                "action":   "save",
                "item-14":  "i love it!"
            })
        self.assertEqual(302, response.status_code)

        response = self.client.get(
            "/workbook/principles-of-discipling/3/")
        self.assertEqual(200, response.status_code)
        self.assertContains(response, "i love it!")

    def test_boolean_item(self):
        """Docstring."""
        self.client.post(
            "/workbook/principles-of-discipling/0/", {
                "action":   "continue"
            })
        self.client.post(
            "/workbook/principles-of-discipling/1/", {
                "action":   "continue"
            })
        self.client.post(
            "/workbook/principles-of-discipling/2/", {
                "action":   "continue"
            })
        self.client.post(
            "/workbook/principles-of-discipling/3/", {
                "action":   "continue"
            })

        response = self.client.get(
            "/workbook/principles-of-discipling/4/")
        self.assertNotContains(response, "checked")

        response = self.client.post(
            "/workbook/principles-of-discipling/4/", {
                "action":   "save",
                "item-15":  "Yes"
            })
        self.assertEqual(302, response.status_code)

        response = self.client.get(
            "/workbook/principles-of-discipling/4/")
        self.assertContains(response, "checked")

    def test_radio_item(self):
        """Docstring."""
        self.client.post(
            "/workbook/principles-of-discipling/0/", {
                "action":   "continue"
            })
        self.client.post(
            "/workbook/principles-of-discipling/1/", {
                "action":   "continue"
            })
        self.client.post(
            "/workbook/principles-of-discipling/2/", {
                "action":   "continue"
            })
        self.client.post(
            "/workbook/principles-of-discipling/3/", {
                "action":   "continue"
            })
        self.client.post(
            "/workbook/principles-of-discipling/4/", {
                "action":   "continue"
            })

        response = self.client.get(
            "/workbook/principles-of-discipling/5/")
        self.assertNotContains(response, "checked")
        self.assertContains(response, '"yes"')
        self.assertContains(response, '"no"')
        self.assertContains(response, '"maybe"')

        response = self.client.post(
            "/workbook/principles-of-discipling/5/", {
                "action":   "save",
                "item-16":  "Yes"
            })
        self.assertEqual(302, response.status_code)

        response = self.client.get(
            "/workbook/principles-of-discipling/5/")
        self.assertContains(response, "checked")


class ExportTest(TestCase):

    """Export Test."""

    fixtures = [
        "auth_user.json",
        "dwb_book.json",
        "dwb_item.json",
    ]

    def setUp(self):
        """Docstring."""
        from django.contrib.auth.models import User
        from .models import Copy

        for user in User.objects.all():
            user.set_password("secret")
            user.save()

        self.client = Client()
        self.client.login(
            username="tom",
            password="secret")

        self.client.get(
            "/workbook/principles-of-discipling/1/")

        for copy in Copy.objects.all():
            copy.status = "progress"
            copy.save()

    def test_view_export_page(self):
        """Docstring."""
        response = self.client.get(
            "/workbook/principles-of-discipling/export/")
        self.assertEqual(200, response.status_code)

    def test_export_all(self):
        """Docstring."""
        response = self.client.post(
            "/workbook/principles-of-discipling/export/")
        self.assertEqual(200, response.status_code)

    def test_export_chapter(self):
        """Docstring."""
        response = self.client.post(
            "/workbook/principles-of-discipling/export/", {
                "chapter_id":   "10"
            })
        self.assertEqual(200, response.status_code)
