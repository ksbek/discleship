from django.contrib.auth.models import User
from django.test import TestCase
from django.test.client import Client

from dwb_group.models import *


class MessageModelTest(TestCase):

    """Message Model Test."""

    fixtures = [
        "auth_user.json",
    ]

    def test_send(self):
        """Docstring."""
        message = Message()
        message.sender_user = User.objects.all()[0]
        message.recipient_user = User.objects.all()[0]
        message.text = "Yahoo!"
        ok = message.send()

        self.assertTrue(ok)


class ViewTest(TestCase):

    """View Test."""

    fixtures = [
        "auth_user.json",
        "dwb_book.json",
        "dwb_item.json",
        "dwb_group.json",
        "dwb_member.json",
    ]

    def setUp(self):
        """Docstring."""
        for user in User.objects.all():
            user.set_password("secret")
            user.save()

    def test_create_group(self):
        """Docstring."""
        client = Client()
        client.login(
            username="tom",
            password="secret")

        # get the page
        response = client.get(
            "/groups/create/principles-of-discipling/")
        self.assertEquals(response.status_code, 200)

        # submit
        response = client.post(
            "/groups/create/principles-of-discipling/", {
                "name":     "Big Cats"
            })
        self.assertEquals(response.status_code, 302)

        # check if group was created
        response = client.get(
            "/workbook/principles-of-discipling/")
        self.assertEquals(response.status_code, 200)
        self.assertContains(response, "Big Cats")

    def test_create_group_no_title(self):
        """Docstring."""
        client = Client()
        client.login(
            username="tom",
            password="secret")
        response = client.get(
            "/groups/create/principles-of-discipling/")
        self.assertEquals(response.status_code, 200)

        response = client.post(
            "/groups/create/principles-of-discipling/", {
                "title":    ""
            })
        self.assertEquals(response.status_code, 200)

    def test_leave_group_not_joined(self):
        """Docstring."""
        client = Client()
        client.login(
            username="tom",
            password="secret")

        response = client.get(
            "/groups/2/leave/")
        self.assertEquals(response.status_code, 302)

    def test_leave_group(self):
        """Docstring."""
        client = Client()
        client.login(
            username="tom",
            password="secret")

        # get the page
        response = client.get
        ("/groups/1/leave/")
        self.assertEquals(response.status_code, 200)

        # submit form
        response = client.post(
            "/groups/1/leave/")
        self.assertEquals(response.status_code, 302)

        # make sure we cannot leave the group again
        response = client.get(
            "/groups/1/leave/")
        self.assertEquals(response.status_code, 302)

    def test_send_invite(self):
        """Docstring."""
        client = Client()
        client.login(
            username="tom",
            password="secret")

        # get the page
        response = client.get(
            "/groups/1/invite/")
        self.assertEquals(response.status_code, 200)

        # get the page
        response = client.post(
            "/groups/1/invite/",
            data={
                "email":    "dog@example.com"
            }
        )
        self.assertEquals(response.status_code, 302)

    def test_join_invalid_code(self):
        """Docstring."""
        invite = Invite()
        invite.sender_user = User.objects.get(
            id=1)
        invite.group = Group.objects.get(
            id=1)
        invite.code = "inv123"
        invite.status = "pending"
        invite.recipient_name = "Jack"
        invite.recipient_email = "jack@example.com"

        client = Client()
        client.login(
            username="tom",
            password="secret")

        response = client.get(
            "/groups/join/wrong/")
        self.assertEquals(response.status_code, 404)

    def test_join_force_login(self):
        """Docstring."""
        invite = Invite()
        invite.sender_user = User.objects.get(
            id=1)
        invite.group = Group.objects.get(
            id=1)
        invite.code = "inv123"
        invite.status = "pending"
        invite.recipient_name = "Jack"
        invite.recipient_email = "jack@example.com"
        invite.save()

        client = Client()

        response = client.get(
            "/groups/join/inv123/")
        self.assertEquals(response.status_code, 302)

    def test_join(self):
        """Docstring."""
        invite = Invite()
        invite.sender_user = User.objects.get(
            id=1)
        invite.group = Group.objects.get(
            id=1)
        invite.code = "inv123"
        invite.status = "pending"
        invite.recipient_name = "Jack"
        invite.recipient_email = "jack@example.com"
        invite.save()

        client = Client()
        client.login(
            username="tom",
            password="secret")

        response = client.get(
            "/groups/join/inv123/")
        self.assertEquals(response.status_code, 200)

        response = client.post(
            "/groups/join/inv123/")
        self.assertEquals(response.status_code, 302)

    def test_send_message_to_group(self):
        """Docstring."""
        client = Client()
        client.login(
            username="tom",
            password="secret")

        data = {
            "group_id": "1",
            "text":     "test",
        }
        response = client.post(
            "/groups/message/", data)
        self.assertEquals(response.status_code, 200)
        self.assertContains(response, "Message was sent")

    def test_send_message_to_group_not_owner(self):
        """Docstring."""
        # assign group to another user
        group = Group.objects.get(
            pk=1)
        jerry = User.objects.get(
            username="jerry")

        group.creator = jerry
        group.save()

        client = Client()
        client.login(
            username="tom",
            password="secret")

        data = {
            "group_id": "1",
            "text":     "test",
        }
        response = client.post(
            "/groups/message/", data)
        self.assertEquals(response.status_code, 200)
        self.assertContains(
            response, "Only person who created this group can message")

    def test_send_message_to_group_fail(self):
        """Docstring."""
        client = Client()
        client.login(
            username="tom",
            password="secret")

        data = {
            "group_id": "2",
            "text":     "test",
        }
        response = client.post(
            "/groups/message/", data)
        self.assertEquals(response.status_code, 200)
        self.assertContains(response, "You cannot message this group.")

    def test_send_message_to_group_not_found(self):
        """Docstring."""
        client = Client()
        client.login(
            username="tom",
            password="secret")

        data = {
            "group_id": "2222",
            "text":     "test",
        }
        response = client.post(
            "/groups/message/", data)
        self.assertEquals(response.status_code, 200)
        self.assertContains(response, "You cannot message this group.")

    def test_send_message_to_user(self):
        """Docstring."""
        client = Client()
        client.login(
            username="tom",
            password="secret")

        data = {
            "user_id":  "1",
            "text":     "test",
        }
        response = client.post(
            "/groups/message/", data)
        self.assertEquals(response.status_code, 200)
        self.assertContains(response, "Message was sent")

    def test_send_message_to_user_fail(self):
        """Docstring."""
        client = Client()
        client.login(
            username="tom",
            password="secret")

        data = {
            "user_id":  "2",
            "text":     "test",
        }
        response = client.post(
            "/groups/message/", data)
        self.assertEquals(response.status_code, 200)
        self.assertContains(response, "You cannot message this user.")

    def test_send_message_to_user_not_found(self):
        """Docstring."""
        client = Client()
        client.login(
            username="tom",
            password="secret")

        data = {
            "user_id":  "2222",
            "text":     "test",
        }
        response = client.post(
            "/groups/message/", data)
        self.assertEquals(response.status_code, 200)
        self.assertContains(response, "You cannot message this user.")
