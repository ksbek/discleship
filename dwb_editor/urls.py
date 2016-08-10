from django.conf.urls import patterns, include, url

from dwb_editor.views import *


urlpatterns = [
    # -------------------------------------------------------------------------
    # --- Home
    url(r"^$",
        editor_home,
        name="editor-home"),

    # -------------------------------------------------------------------------
    # --- Book
    url(r"^(?P<book_id>\d+)/$",
        editor_book,
        name="editor-book"),

    # -------------------------------------------------------------------------
    # --- Chapter
    url(r"^(?P<book_id>\d+)/chapter/(?P<item_id>\d+)/$",
        editor_chapter,
        name="editor-chapter"),
    url(r"^(?P<book_id>\d+)/chapter/(?P<item_id>\d+)/delete/$",
        editor_chapter,
        name="editor-delete-chapter"),
    url(r"^(?P<book_id>\d+)/chapter/(?P<item_id>\d+)/preview/$",
        editor_preview_chapter,
        name="editor-preview-chapter"),

    # -------------------------------------------------------------------------
    # --- Item
    url(r"^(?P<book_id>\d+)/item/(?P<item_id>\d+)/$",
        editor_item,
        name="editor-item"),
    url(r"^(?P<book_id>\d+)/item/(?P<item_id>\d+)/delete/$",
        editor_delete_item,
        name="editor-delete-item"),

    # -------------------------------------------------------------------------
    # --- Attachments
    url(r"^(?P<book_id>\d+)/file/add/$",
        editor_add_file_for_download,
        name="editor-add-file-for-download"),
    url(r"^(?P<book_id>\d+)/file/(?P<file_id>\d+)/$",
        editor_edit_file_for_download,
        name="editor-edit-file-for-download"),
    url(r"^(?P<book_id>\d+)/file/(?P<file_id>\d+)/delete/$",
        editor_delete_file_for_download,
        name="editor-delete-file-for-download"),

    # -------------------------------------------------------------------------
    # --- Congratulations
    url(r"^(?P<book_id>\d+)/preview-congratulations/$",
        editor_congratulations,
        name="editor-congratulations"),
    url(r"^(?P<book_id>\d+)/preview-certificate/$",
        editor_certificate,
        name="editor-certificate"),

    # -------------------------------------------------------------------------
    # --- Sort
    url(r"^(?P<book_id>\d+)/sort-items/$",
        editor_sort_items,
        name="editor-sort-items"),
    url(r"^(?P<book_id>\d+)/sort-chapters/$",
        editor_sort_chapters,
        name="editor-sort-chapters"),
    url(r"^(?P<book_id>\d+)/add-item/$",
        editor_add_item,
        name="editor-add-item"),
]
