from django.conf.urls import patterns, include, url

from dwb_store.views import *


urlpatterns = [
    url(r"^redeem/",
        store_redeem,
        name="store-redeem"),
    url(r"^buy/(?P<book_slug>[-\w+]+)/$",
        store_purchase,
        name="store-purchase"),
    url(r"^purchase/(?P<invoice_number>[-\w+]+)/confirm/$",
        store_purchase_confirm,
        name="store-purchase-confirm"),
    url(r"^purchase/(?P<invoice_number>[-\w+]+)/complete/$",
        store_purchase_complete,
        name="store-purchase-complete"),
    url(r"^purchase/(?P<invoice_number>[-\w+]+)/cancel/$",
        store_purchase_cancel,
        name="store-purchase-cancel"),
    url(r"^discounts/$",
        store_discounts,
        name="store-discounts"),
    url(r"^discounts/(?P<book_slug>[-\w+]+)/$",
        store_discounts_buy,
        name="store-discounts-buy"),
]
