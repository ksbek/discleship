from django.test import TestCase
from django.test.client import Client

from dwb_book.models import Book, Item, FileForDownload


class ServicesTest(TestCase):

    """Service Test."""

    def test_sort_book_items(self):
        """Docstring."""
        from .services import sort_book_items

        book = Book()
        book.price = 1
        book.certificate_background_width = 100
        book.certificate_background_height = 100
        book.certificate_name_top = 50
        book.save()

        item_a = Item(
            book=book,
            title="a")
        item_a.save()
        item_b = Item(
            book=book,
            title="b")
        item_b.save()
        item_c = Item(
            book=book,
            title="c")
        item_c.save()
        item_d = Item(
            book=book,
            title="d")
        item_d.save()
        item_e = Item(
            book=book,
            title="e")
        item_e.save()
        item_f = Item(
            book=book,
            title="f")
        item_f.save()

        sort_book_items(book, [item_c.id, item_a.id, item_f.id])

        new_order = book.get_item_order()
        self.assertEquals(new_order[0], item_b.id)
        self.assertEquals(new_order[1], item_c.id)
        self.assertEquals(new_order[2], item_a.id)
        self.assertEquals(new_order[3], item_f.id)
        self.assertEquals(new_order[4], item_d.id)
        self.assertEquals(new_order[5], item_e.id)

    def test_sort_book_chapters(self):
        """Docstring."""
        from .services import sort_book_chapters

        book = Book()
        book.price = 1
        book.certificate_background_width = 100
        book.certificate_background_height = 100
        book.certificate_name_top = 50
        book.save()

        item_a = Item(
            book=book,
            item_type="h1",
            title="a")
        item_a.save()
        item_b = Item(
            book=book,
            item_type="text",
            title="b")
        item_b.save()
        item_c = Item(
            book=book,
            item_type="text",
            title="c")
        item_c.save()
        item_d = Item(
            book=book,
            item_type="h1",
            title="d")
        item_d.save()
        item_e = Item(
            book=book,
            item_type="text",
            title="e")
        item_e.save()
        item_f = Item(
            book=book,
            item_type="text",
            title="f")
        item_f.save()

        sort_book_chapters(book, [item_d.id, item_a.id])
        new_order = book.get_item_order()

        self.assertEquals(new_order[0], item_d.id)
        self.assertEquals(new_order[1], item_e.id)
        self.assertEquals(new_order[2], item_f.id)
        self.assertEquals(new_order[3], item_a.id)
        self.assertEquals(new_order[4], item_b.id)
        self.assertEquals(new_order[5], item_c.id)


class ViewTest(TestCase):

    """View Test."""

    fixtures = [
        "auth_user.json",
        "dwb_book.json",
        "dwb_item.json",
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
        client.login(
            username="admin",
            password="secret")
        response = client.get("/editor/")
        self.assertEquals(response.status_code, 200)
        self.assertContains(response, "Principles of Discipling")

    def test_show_book(self):
        """Docstring."""
        client = Client()
        client.login(
            username="admin",
            password="secret")
        response = client.get("/editor/1/")
        self.assertEquals(response.status_code, 200)
        self.assertContains(response, "Principles of Discipling")

    def test_show_chapter(self):
        """Docstring."""
        client = Client()
        client.login(
            username="admin",
            password="secret")
        response = client.get("/editor/1/chapter/10/")
        self.assertEquals(response.status_code, 200)
        self.assertContains(response, "Introduction")

    def test_show_h1_item(self):
        """Docstring."""
        client = Client()
        client.login(username="admin", password="secret")
        response = client.get("/editor/1/item/10/")
        self.assertEquals(response.status_code, 200)
        self.assertContains(response, "Introduction")

    def test_show_text_item(self):
        """Docstring."""
        client = Client()
        client.login(
            username="admin",
            password="secret")
        response = client.get("/editor/1/item/11/")
        self.assertEquals(response.status_code, 200)
        self.assertContains(response, "Welcome")

    def test_show_text_footnotes(self):
        """Docstring."""
        client = Client()
        client.login(
            username="admin",
            password="secret")
        response = client.get("/editor/1/item/12/")
        self.assertEquals(response.status_code, 200)
        self.assertContains(response, "First footnote")

    def test_file_for_download(self):
        """Docstring."""
        from StringIO import StringIO

        imgfile = StringIO(
            "GIF87a\x01\x00\x01\x00\x80\x01\x00\x00\x00\x00ccc,\x00"
            "\x00\x00\x00\x01\x00\x01\x00\x00\x02\x02D\x01\x00;")
        imgfile.name = "test_img_file.gif"

        client = Client()
        client.login(
            username="admin",
            password="secret")

        response = client.post("/editor/1/file/add/")
        self.assertEquals(response.status_code, 200)

        response = client.post(
            "/editor/1/file/add/", {
                "title":    "Imagine",
                "file":     imgfile
            })

        print(response.content)

        self.assertEquals(response.status_code, 302)

        response = client.get("/editor/1/file/1/")

        self.assertEquals(response.status_code, 200)
        self.assertContains(response, "Imagine")

        response = client.post(
            "/editor/1/file/1/", {
                "title":    "Success"
            })

        self.assertEquals(response.status_code, 302)
