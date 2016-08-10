from django import forms
from django.utils.html import strip_tags
from django.utils.translation import ugettext as _

from ckeditor.widgets import CKEditorWidget
from textwrap import wrap

from dwb_book.models import Book, Item, FileForDownload


class BookForm(forms.ModelForm):

    """Book Form."""

    class Meta:
        model = Book
        fields = [
            "language", "author", "title", "slug", "date_available", "price",
            "status", "cover_image", "congratulations_text",
            "certificate_background", "certificate_name_top", "style_css",
        ]
        widgets = {
            "language": forms.Select(
                attrs={
                    "class":        "form-control selectpicker",
                }),
            "author": forms.TextInput(
                attrs={
                    "class":        "form-control",
                    "placeholder":  _("Author"),
                    "maxlength":    80,
                }),
            "title": forms.TextInput(
                attrs={
                    "class":        "form-control",
                    "placeholder":  _("Title"),
                    "maxlength":    80,
                }),
            "slug": forms.TextInput(
                attrs={
                    "class":        "form-control",
                    "placeholder":  _("Slug"),
                    "maxlength":    80,
                }),
            "price": forms.TextInput(
                attrs={
                    "class":        "form-control",
                    "placeholder":  _("Price"),
                    "maxlength":    80,
                }),
            "status": forms.Select(
                attrs={
                    "class":        "form-control selectpicker",
                }),
            "congratulations_text": forms.Textarea(
                attrs={
                    "class":        "form-control",
                    "placeholder":  _("Congratulations Text"),
                    "maxlength":    10000,
                }),
            "style_css": forms.Textarea(
                attrs={
                    "class":        "form-control",
                    "placeholder":  _("Style CSS"),
                    "maxlength":    10000,
                }),
            }


class FileForDownloadForm(forms.ModelForm):

    """File for Download Form."""

    class Meta:
        model = FileForDownload
        fields = [
            "title", "file",
        ]


class HeadingForm(forms.ModelForm):

    """Heading Form."""

    class Meta:
        model = Item
        fields = [
            "item_type", "intro", "title", "content", "footnotes",
        ]

    intro = forms.CharField(
        label=_("Text above title"),
        help_text=_("Short text above the heading."),
        required=False)
    title = forms.CharField(
        label=_("Title"),
        max_length=160)
    content = forms.CharField(
        label=_("Text bellow title"),
        widget=CKEditorWidget(),
        help_text=_("Short text shown right under the heading."),
        required=False)
    footnotes = forms.CharField(
        label=_("Footnotes"),
        widget=CKEditorWidget(),
        required=False)

    widgets = {
        "item_type": forms.Select(
            attrs={
                "class":        "form-control selectpicker",
            }),
        }


class TextForm(forms.ModelForm):

    """Text Form."""

    class Meta:
        model = Item
        fields = [
            "item_type", "title", "content", "footnotes",
        ]

    title = forms.CharField(
        widget=forms.HiddenInput,
        required=False)
    content = forms.CharField(
        widget=CKEditorWidget())
    footnotes = forms.CharField(
        label=_("Footnotes"),
        widget=CKEditorWidget(),
        required=False)

    widgets = {
        "item_type": forms.Select(
            attrs={
                "class":        "form-control selectpicker",
            }),
        }

    def clean(self):
        """Docstring."""
        cleaned_data = super(TextForm, self).clean()
        cleaned_data["title"] = create_title(cleaned_data["content"])

        return cleaned_data


class TextareaForm(forms.ModelForm):

    """Textarea Form."""

    class Meta:
        model = Item
        fields = [
            "item_type", "title", "content", "footnotes",
        ]

    title = forms.CharField(
        widget=forms.HiddenInput,
        required=False)
    content = forms.CharField(
        label=_("Question"),
        widget=CKEditorWidget())
    footnotes = forms.CharField(
        label=_("Footnotes"),
        widget=CKEditorWidget(),
        required=False)

    widgets = {
        "item_type": forms.Select(
            attrs={
                "class":        "form-control selectpicker",
            }),
        }

    def clean(self):
        """Docstring."""
        cleaned_data = super(TextareaForm, self).clean()
        cleaned_data["title"] = create_title(cleaned_data["content"])

        return cleaned_data


class BooleanForm(forms.ModelForm):

    """Boolean Form."""

    class Meta:
        model = Item
        fields = [
            "item_type", "title", "content", "footnotes",
        ]

    title = forms.CharField(
        widget=forms.HiddenInput,
        required=False)
    content = forms.CharField(
        label=_("Question"),
        widget=CKEditorWidget())
    footnotes = forms.CharField(
        label=_("Footnotes"),
        widget=CKEditorWidget(),
        required=False)

    widgets = {
        "item_type": forms.Select(
            attrs={
                "class":        "form-control selectpicker",
            }),
        }

    def clean(self):
        """Docstring."""
        cleaned_data = super(BooleanForm, self).clean()
        cleaned_data["title"] = create_title(cleaned_data["content"])

        return cleaned_data


class RadioForm(forms.ModelForm):

    """Radio Form."""

    class Meta:
        model = Item
        fields = [
            "item_type", "title", "content", "data", "footnotes",
        ]

    title = forms.CharField(
        widget=forms.HiddenInput,
        required=False)
    content = forms.CharField(
        label=_("Question"),
        widget=CKEditorWidget())
    data = forms.CharField(
        label=_("Options"),
        widget=forms.Textarea,
        help_text=_("Enter one per line"))
    footnotes = forms.CharField(
        label=_("Footnotes"),
        widget=CKEditorWidget(),
        required=False)

    widgets = {
        "item_type": forms.Select(
            attrs={
                "class":        "form-control selectpicker",
            }),
        }

    def clean(self):
        """Docstring."""
        cleaned_data = super(RadioForm, self).clean()
        cleaned_data["title"] = create_title(cleaned_data["content"])

        return cleaned_data


def create_title(html):
    """Docstring."""
    entities = (
        ("&nbsp;",      " "),
        ("&amp;",       "&"),
        ("&gt;",        "<"),
        ("&lt;",        "<"),
        ("&ldquo;",     '"'),
        ("&rdquo;",     '"'),
        )

    text = strip_tags(html)

    for entity, character in entities:
        text = text.replace(entity, character)

    if len(text) > 70:
        text = wrap(text, 66)[0] + " ..."

    return text
