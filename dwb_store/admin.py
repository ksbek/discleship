
from django.contrib import admin

from dwb_store.models import *


class ReadonlyTabularInline(admin.TabularInline):

    """Readonly Inline."""

    can_delete = False
    extra = 0
    editable_fields = []

    def get_readonly_fields(self, request, obj=None):
        """Docsting."""
        fields = []

        for field in self.model._meta.get_all_field_names():
            if not field == "id":
                if field not in self.editable_fields:
                    fields.append(field)

        return fields

    def has_add_permission(self, request):
        """Docsting."""
        return False


class PurchaseClaimInline(ReadonlyTabularInline):

    """Purchase Claim inline."""

    model = PurchaseClaim


class PurchaseAdmin(admin.ModelAdmin):

    """Purchase Admin."""

    list_display = [
        "invoice_number", "date", "book", "total_charge", "status",
    ]
    readonly_fields = [
        "invoice_number", "uuid", "date", "price", "total_charge", "group",
        "gift_code", "api_log", "api_data",
    ]
    inlines = [PurchaseClaimInline, ]

admin.site.register(Purchase, PurchaseAdmin)
