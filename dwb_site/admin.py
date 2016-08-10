from django import forms
from django.contrib import admin
from django.contrib.flatpages.admin import FlatPageAdmin as FlatPageAdminOld
from django.contrib.flatpages.admin import FlatpageForm as FlatpageFormOld
from django.contrib.flatpages.models import FlatPage

from ckeditor.widgets import CKEditorWidget


class FlatpageForm(FlatpageFormOld):

    """Flatpage Form."""

    content = forms.CharField(
        widget=CKEditorWidget())

    class Meta:
        # this is not automatically inherited from FlatpageFormOld
        model = FlatPage
        fields = "__all__"


class FlatPageAdmin(FlatPageAdminOld):

    """Flatpage Admin."""

    form = FlatpageForm

# We have to unregister the normal admin, and then reregister ours
admin.site.unregister(FlatPage)
admin.site.register(FlatPage, FlatPageAdmin)
