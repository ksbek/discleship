from django.conf.urls import patterns, include, url

from dwb_admin.views import *


urlpatterns = [
    url(r"^$",
        admin_home,
        name="admin-home"),
    url(r"^book/(?P<book_id>\d+)/purchases/$",
        admin_book_purchases,
        name="admin-book-purchases"),
    url(r"^page/(?P<page_id>\d+)/$",
        admin_edit_flatpage,
        name="admin-edit-flatpage"),
    url(r"^purchase/add/$",
        admin_add_purchase,
        name="admin-add-purchase"),
    url(r"^purchase/(?P<purchase_id>\d+)/$",
        admin_purchase,
        name="admin-purchase"),
]
