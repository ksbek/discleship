from django.contrib import admin

from dwb_book.models import (
    Book,
    Copy,
    Item,
    Marker,
    Pricing,
    )


class PricingInline(admin.TabularInline):

    """Pricing Inline."""

    model = Pricing
    extra = 1


class BookAdmin(admin.ModelAdmin):

    """Book Admin."""

    list_display = [
        "author", "language", "title", "date_available", "status", "price",
        "sort_order",
    ]
    prepopulated_fields = {
        "slug":     ("title",)
    }
    inlines = [PricingInline, ]

admin.site.register(Book, BookAdmin)


class CopyAdmin(admin.ModelAdmin):

    """Copy Admin."""

    list_display = [
        "book", "user", "status", "overall_progress",
    ]

admin.site.register(Copy, CopyAdmin)


class ItemAdmin(admin.ModelAdmin):

    """Item Admin."""

    list_display = [
        "book", "item_type", "title",
    ]

admin.site.register(Item, ItemAdmin)


class MarkerAdmin(admin.ModelAdmin):

    """Marker Admin."""

    list_display = [
        "placeholder",
    ]

admin.site.register(Marker, MarkerAdmin)
