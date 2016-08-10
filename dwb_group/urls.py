from django.conf.urls import patterns, include, url

from dwb_group.views import *


urlpatterns = [
    # -------------------------------------------------------------------------
    # --- API
    url(r"^create/(?P<book_slug>[-\w+]+)/",
        group_create,
        name="group-create"),
    url(r"^join/(?P<code>[-\w]+)/",
        group_join,
        name="group-join"),
    url(r"^(?P<group_id>\d+)/invite/",
        group_invite,
        name="group-invite"),
    url(r"^(?P<group_id>\d+)/leave/",
        group_leave,
        name="group-leave"),
    url(r"^(?P<group_id>\d+)/rename/(?P<book_slug>[-\w+]+)/",
        group_rename,
        name="group-rename"),
    url(r"^tell/",
        group_tell,
        name="group-tell-friend"),
    url(r"^message/",
        group_message,
        name="group-message"),

    # -------------------------------------------------------------------------
    # --- AJAX
    url(r"^ajax/invite/remove/",
        ajax_invite_remove,
        name="ajax_invite_remove_from_group"),
    url(r"^ajax/member/remove/",
        ajax_member_remove,
        name="ajax_member_remove_from_group"),
]
