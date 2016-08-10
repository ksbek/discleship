from django.conf import settings
from django.conf.urls import (
    patterns,
    include,
    url,
    )
from django.conf.urls.i18n import i18n_patterns
from django.conf.urls.static import static

from django.contrib import admin

from dwb_site.views import ajax_mark_delivered_message_read

admin.autodiscover()


urlpatterns = [
    url(r"^i18n/", include("django.conf.urls.i18n")),
]

urlpatterns += [
    # -------------------------------------------------------------------------
    # --- Django
    url(r"^django-admin/", include(admin.site.urls)),

    # -------------------------------------------------------------------------
    # --- Desktop
    url(r"^", include("dwb_site.urls")),
    url(r"^account/", include("dwb_user.urls")),
    url(r"^admin/", include("dwb_admin.urls")),
    url(r"^editor/", include("dwb_editor.urls")),
    url(r"^groups/", include("dwb_group.urls")),
    url(r"^store/", include("dwb_store.urls")),
    url(r"^workbook/", include("dwb_book.urls")),

    # -------------------------------------------------------------------------
    # --- AJAX
    url(r"^ajax/message/remove/$",
        ajax_mark_delivered_message_read,
        name="ajax-mark-delivered-message-read"),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# -----------------------------------------------------------------------------
# --- Flat Pages
urlpatterns += [
    url(r"^pages/", include("django.contrib.flatpages.urls")),
    # "django.contrib.flatpages.views", (r"^(?P<url>.*/)$", "flatpage"),
]
