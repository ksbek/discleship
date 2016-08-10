from django.conf.urls import patterns, include, url

from dwb_user.views import *


urlpatterns = [
    url(r"^login/$",
        account_login,
        name="login"),
    url(r"^register/$",
        account_register,
        name="register"),
    url(r"^logout/$",
        account_logout,
        name="logout"),
    url(r"^order_history/$",
        order_history,
        name="order_history"),
    url(r"^email_list/$",
        email_list,
        name="email_list"),
    url(r"^edit-profile/$",
        edit_profile,
        name="edit_profile"),
    url(r"^my-account/$",
        my_account,
        name="my-account"),

    # -------------------------------------------------------------------------
    # --- Password
    url(r"^password/forgot/$",
        forgot_password,
        name="forgot-password"),
    url(r"^password/renew/(?P<uidb36>[0-9A-Za-z]{1,13})-"
        "(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$",
        renew_password,
        name="renew-password"),
    url(r"^password/reset/$",
        reset_password,
        name="reset-password"),

    url(r"^send_claim_code/",
        send_claim_code,
        name="send_claim_code"),
]
