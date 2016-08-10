from datetime import datetime

from django.contrib.auth.models import User
from django.conf import settings
from django.core.urlresolvers import reverse
from django.db import models
from django.utils.text import slugify
from django.utils.translation import ugettext as _

from ckeditor.fields import RichTextField


class Book(models.Model):

    """Book Model."""

    class Meta:
        db_table = "workbook_book"

    STATUS_CHOICES = (
        ("active",  _("Active")),
        ("hidden",  _("Hidden")),
        ("draft",   _("Draft")),
        ("deleted", _("Deleted")),
    )

    language = models.CharField(
        max_length=8,
        choices=settings.LANGUAGES, default="en")
    title = models.CharField(
        max_length=255)
    slug = models.SlugField(
        max_length=255)
    author = models.CharField(
        max_length=255)
    date_available = models.DateTimeField(
        null=True, blank=True,
        help_text=_("When book became available"))
    status = models.CharField(
        max_length=255,
        choices=STATUS_CHOICES, default="draft")
    cover_image = models.ImageField(
        upload_to="workbook-cover")
    style_css = models.TextField(
        null=True, blank=True,
        help_text=_("Use class 'book-display'"))
    price = models.DecimalField(
        max_digits=18, decimal_places=2)
    priest_price = models.DecimalField(
        default=0, max_digits=18, decimal_places=2)

    first_payed_heading = models.ForeignKey(
        "Item",
        null=True, blank=True,
        related_name="+",
        limit_choices_to={
            "item_type":    "h1",
        })
    first_appendix_heading = models.ForeignKey(
        "Item",
        null=True, blank=True,
        related_name="+",
        limit_choices_to={
            "item_type":    "h1",
        })

    congratulations_text = RichTextField(
        null=True, blank=True)
    certificate_background = models.ImageField(
        upload_to="workbook-certificate",
        width_field="certificate_background_width",
        height_field="certificate_background_height")
    certificate_background_width = models.IntegerField()
    certificate_background_height = models.IntegerField()
    certificate_name_top = models.FloatField(
        "Name top-offset",
        help_text=_("Position of name from top in %"))

    sort_order = models.IntegerField(
        default=0)

    def get_price_for_quantity(self, quantity):
        """Docstring."""
        price = self.price

        for pricing in self.pricing_set.all():
            if quantity >= pricing.min_quantity:
                price = min(price, pricing.price)

        return price

    def get_prices(self):
        """Docstring."""
        data = [(1, self.price)]

        for pricing in self.pricing_set.all():
            data.append((pricing.min_quantity, pricing.price))

        return data

    def get_style(self):
        """Docstring."""
        # Get CSS for the Book
        css = self.style_css or ""

        # Get CSS for each Marker
        for marker in self.marker_set.all():
            if marker.style_css:
                css += "\n" + marker.style_css

        return css

    def get_or_create_copy(self, user):
        """Docstring."""
        if user.is_authenticated():
            try:
                return Copy.objects.get(
                    book=self,
                    user=user,
                )
            except Copy.DoesNotExist:
                copy = Copy(
                    book=self,
                    user=user,
                    status="progress",
                )
                copy.save()

                return copy
        else:
            return None

    def get_absolute_url(self):
        """Docstring."""
        return reverse(
            "book-overview", kwargs={
                "book_slug":    self.slug,
            })

    def __unicode__(self):
        """Docstring."""
        return self.title


class Pricing(models.Model):

    """Pricing Model."""

    class Meta:
        db_table = "workbook_price"
        verbose_name_plural = "pricing"
        ordering = [
            "book", "min_quantity",
        ]

    book = models.ForeignKey("Book")
    min_quantity = models.IntegerField(
        help_text=_("Minimum quantity for this pricing"))
    price = models.DecimalField(
        max_digits=18, decimal_places=2)

    def __unicode__(self):
        """Docstring."""
        return "%s '%s' for $%.2f each" % (
            self.min_quantity,
            self.book.title,
            self.price
        )


class Item(models.Model):

    """Item Model."""

    class Meta:
        db_table = "workbook_item"
        order_with_respect_to = "book"

    TYPE_CHOICES = (
        ("h1",          _("Heading 1")),
        ("h2",          _("Heading 2")),
        ("h3",          _("Heading 3")),
        ("text",        _("Text")),
        ("textarea",    _("Type-in Question")),
        ("boolean",     _("Yes/No Question")),
        ("radio",       _("Choose One Question")),
    )

    book = models.ForeignKey("Book")

    item_type = models.CharField(
        db_column="type",
        max_length=255, blank=True,
        choices=TYPE_CHOICES)
    intro = models.TextField(
        null=True, blank=True)
    title = models.CharField(
        max_length=255, blank=True)
    content = RichTextField(
        null=True, blank=True)
    footnotes = RichTextField(
        null=True, blank=True)
    data = models.TextField(
        null=True, blank=True)

    def get_options(self):
        """Docstring."""
        if self.item_type == "radio" and self.data:
            options = self.data.strip().split("\n")
            options = [o.strip() for o in options]

            return options

    def is_heading(self):
        """Docstring."""
        my_type = self.item_type

        if my_type == "h1":
            return True

        if my_type == "h2":
            return True

        if my_type == "h3":
            return True

        return False

    def is_input(self):
        """Docstring."""
        my_type = self.item_type

        if my_type == "textarea":
            return True

        if my_type == "boolean":
            return True

        if my_type == "radio":
            return True

        return False

    def get_parent(self, item_type=None):
        """Find a heading for this item.

        If this item is a heading, find bigger heading.
        """
        if item_type:
            return self.get_parent_of_type(item_type)
        else:
            return self.get_parent_of_any_type()

    def get_parent_of_any_type(self):
        """Docstring."""
        if self.item_type == "h1":
            return None

        try:
            prev = self.get_previous_item()
            while prev:
                if prev.item_type == "h1":
                    return prev

                if prev.item_type == "h2" and self.item_type != "h2":
                    return prev

                if (
                        prev.item_type == "h3" and self.item_type != "h3" and
                        self.item_type != "h2"):
                    return prev

                prev = prev.get_previous_item()

        except Item.DoesNotExist:
            return None

        return None

    def get_parent_of_type(self, item_type):
        """Docstring."""
        parent = self.get_parent_of_any_type()

        while parent and parent.item_type != item_type:
            parent = parent.get_parent_of_any_type()

        return parent

    def get_absolute_url(self):
        """Docstring."""
        return reverse(
            "book-page", kwargs={
                "book_slug":    self.book.slug,
                "index":        self._order,
            })

    def get_previous_item(self):
        """Docstring."""
        try:
            return Item.objects.filter(
                book=self.book,
                _order__lt=self._order
                ).order_by("-_order")[0]
        except IndexError:
            raise Item.DoesNotExist()

    def get_next_item(self):
        """Docstring."""
        try:
            return Item.objects.filter(
                book=self.book,
                _order__gt=self._order
                ).order_by("_order")[0]
        except IndexError:
            raise Item.DoesNotExist()

    def get_slug(self):
        """Docstring."""
        return slugify(self.title)

    slug = property(get_slug)

    def __unicode__(self):
        """Docstring."""
        return self.title


class Marker(models.Model):

    """Marker Model."""

    class Meta:
        db_table = "workbook_marker"

    book = models.ForeignKey("Book")

    placeholder = models.CharField(
        max_length=255)
    replacement = models.TextField()
    style_css = models.TextField(
        null=True, blank=True)

    def __unicode__(self):
        """Docstring."""
        return self.placeholder


class FileForDownload(models.Model):

    """File for download Model."""

    class Meta:
        db_table = "workbook_file_for_download"
        verbose_name_plural = "Files For Download"

    book = models.ForeignKey(
        "Book",
        related_name="+")
    title = models.CharField(
        max_length=255)
    file = models.FileField(
        upload_to="files-for-download")

    @property
    def url(self):
        """Docstring."""
        return self.file.url

    def __unicode__(self):
        """Docstring."""
        return self.title


class Copy(models.Model):

    """Copy Model."""

    class Meta:
        db_table = "workbook_copy"
        verbose_name_plural = "Copies"

    STATUS_CHOICES = (
        ("preview",     _("Preview")),
        ("progress",    _("In Progress")),
        ("completed",   _("Completed")),
    )

    user = models.ForeignKey(User)
    status = models.CharField(
        max_length=255,
        choices=STATUS_CHOICES)

    book = models.ForeignKey("Book")
    current_item = models.ForeignKey(
        "Item",
        null=True, blank=True)
    overall_progress = models.FloatField(
        default=0)
    completed_date = models.DateField(
        default=datetime.now,
        blank=True, null=True)
    certificate_number = models.IntegerField(
        default=0)

    def get_response_to(self, item):
        """Docstring."""
        try:
            return self.response_set.get(item=item).value
        except Response.DoesNotExist:
            return None

    def set_response_to(self, item, value):
        """Docstring."""
        if value is not None:
            value = unicode(value)

        try:
            object = self.response_set.get(item=item)
            object.value = value
            object.save()
        except Response.DoesNotExist:
            if value is not None and value != "":
                Response(copy=self, item=item, value=value).save()

    def __unicode__(self):
        """Docstring."""
        return "%s's copy of \"%s\"" % (self.user, self.book)


class Response(models.Model):

    """Response Model."""

    class Meta:
        db_table = "workbook_response"

    copy = models.ForeignKey("Copy")
    item = models.ForeignKey("Item")
    value = models.TextField(
        null=True, blank=True)

    def __unicode__(self):
        """Docstring."""
        if self.value:
            return self.value[:20]
        else:
            return "-"
