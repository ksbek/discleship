from django.conf import settings
from django.conf.urls import patterns, include, url

from dwb_site.views import *


urlpatterns = [
    # -------------------------------------------------------------------------
    # --- Desktop
    url(r"^$",
        index,
        name="index"),
]
