import json

from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import permission_required
from django.http import HttpResponse
from django.shortcuts import (
    render,
    redirect,
    get_object_or_404
    )
from django.utils.translation import ugettext as _

from dwb_book.models import (
    Book,
    Item,
    FileForDownload,
    )
from dwb_book.services import apply_markers, get_chapter_items
from dwb_editor.services import sort_book_items, sort_book_chapters
from dwb_editor.forms import (
    BookForm,
    FileForDownloadForm,
    HeadingForm,
    TextForm,
    TextareaForm,
    BooleanForm,
    RadioForm,
    )
from dwb_store.models import Purchase


@staff_member_required
def editor_home(request):
    """Docstring."""
    books = Book.objects.all()

    return render(
        request, "dwb_editor/editor_home.html", {
            "books":    books,
        })


@staff_member_required
def editor_book(request, book_id):
    """Docstring."""
    book = get_object_or_404(
        Book,
        pk=book_id)
    headings = Item.objects.filter(
        book=book,
        item_type="h1")

    form = BookForm(
        request.POST or None, request.FILES or None,
        instance=book)

    if request.method == "POST" and request.user.has_perm(
            "dwb_book.can_change"):
        if form.is_valid():
            book.save()

            return redirect(
                "editor-book",
                book_id=book.id)

    files_for_download = FileForDownload.objects.filter(
        book=book)

    return render(
        request, "dwb_editor/editor_book.html", {
            "book":                 book,
            "headings":             headings,
            "files_for_download":   files_for_download,
            "form":                 form,
        })


@staff_member_required
def editor_chapter(request, book_id, item_id):
    """Docstring."""
    book = get_object_or_404(
        Book,
        pk=book_id)
    chapter = book.item_set.get(
        pk=item_id)
    items = list(get_chapter_items(book, chapter))

    return render(
        request, "dwb_editor/editor_chapter.html", {
            "book":         book,
            "items":        items,
            "first_item":   items[0],
            "last_item":    items[-1]
        })


@staff_member_required
def editor_preview_chapter(request, book_id, item_id):
    """Docstring."""
    book = get_object_or_404(
        Book,
        pk=book_id)
    chapter = book.item_set.get(
        pk=item_id)

    items = []
    footnotes = ""
    markers = book.marker_set.all()

    for item_object in get_chapter_items(book, chapter):
        item_data = {
            "id":           item_object.id,
            "item_type":    item_object.item_type,
            "intro":        item_object.intro,
            "title":        item_object.title or "",
            "content":      apply_markers(item_object.content, markers),
            "options":      item_object.get_options(),
            }

        if item_object.footnotes:
            footnotes += item_object.footnotes

        items.append(item_data)

    return render(
        request, "dwb_editor/editor_preview_chapter.html", {
            "book":         book,
            "items":        items,
            "first_item":   items[0],
            "footnotes":    footnotes
        })


@staff_member_required
def editor_sort_chapters(request, book_id):
    """Docstring."""
    book = get_object_or_404(
        Book,
        pk=book_id)

    if request.method == "POST":
        items = request.POST.getlist("items")

        if not items:
            items = request.POST.getlist("items[]")

        if items:
            items = [int(i) for i in items]
            sort_book_chapters(book, items)

    response_data = {}

    return HttpResponse(
        json.dumps(response_data),
        content_type="application/json")


@staff_member_required
def editor_add_item(request, book_id):
    """Docstring."""
    book = get_object_or_404(
        Book,
        pk=book_id)

    item = None

    if request.method == "POST":
        item_title = request.POST.get("title", "").strip()
        item_type = request.POST.get("item_type")

        if item_type:
            item = Item(item_type=item_type, book=book)
            item.title = item_title
            item.save()

            if request.POST.get("insert_after"):
                # insert the item in the right position
                insert_after = int(request.POST.get("insert_after"))
                item_order = book.get_item_order()
                item_order = list(item_order)
                item_order.remove(item.id)

                insert_index = item_order.index(insert_after) + 1
                item_order.insert(insert_index, item.id)
                book.set_item_order(item_order)
                book.save()

    # redirect to item or book
    if item and item.item_type == "h1":
        return redirect(
            "editor-book",
            book_id=book.id)

    return redirect(
        "editor-item",
        book_id=book.id,
        item_id=item.id)


@staff_member_required
def editor_delete_item(request, book_id, item_id):
    """Docstring."""
    book = get_object_or_404(
        Book,
        pk=book_id)
    item = get_object_or_404(
        Item,
        pk=item_id,
        book=book_id)

    def check_item_for_delete(item):
        if item.item_type == "h1":
            try:
                if item.get_next_item().item_type != "h1":
                    return _("Cannot delete heading which has sub-content")
            except Item.DoesNotExist:
                pass  # no next item

        return None

    if request.method == "POST":
        error_message = check_item_for_delete(item)

        if error_message is None:
            parent = item.get_parent("h1")
            item.delete()

            if parent:
                return redirect(
                    "editor-chapter",
                    book_id=book.id,
                    item_id=parent.id)
            else:
                return redirect(
                    "editor-book",
                    book_id=book.id)
        else:
            messages.error(request, error_message)

    return render(
        request, "dwb_editor/delete_item.html", {
            "book":     book,
            "item":     item
        })


@staff_member_required
def editor_item(request, book_id, item_id):
    """Docstring."""
    def get_form(data=None, instance=None):
        if (
                instance.item_type == "h1" or
                instance.item_type == "h2" or
                instance.item_type == "h3"):
            return HeadingForm(
                data, instance=instance)

        if instance.item_type == "text":
            return TextForm(
                data, instance=instance)

        if instance.item_type == "textarea":
            return TextareaForm(
                data, instance=instance)

        if instance.item_type == "boolean":
            return BooleanForm(
                data, instance=instance)

        if instance.item_type == "radio":
            return RadioForm(
                data, instance=instance)

    book = get_object_or_404(
        Book,
        pk=book_id)
    item = get_object_or_404(
        Item,
        pk=item_id,
        book=book_id)

    form = get_form(
        request.POST or None,
        item)

    if request.method == "POST":
        if form.is_valid():
            form.save()

            if item.item_type == "h1":
                chapter = item
            else:
                chapter = item.get_parent("h1")

            if chapter:
                return redirect(
                    "editor-chapter",
                    book_id=book.id,
                    item_id=chapter.id)
            else:
                return redirect(
                    "editor-book",
                    book_id=book.id)

    return render(
        request, "dwb_editor/editor_item.html", {
            "book":     book,
            "item":     item,
            "form":     form,
        })


@staff_member_required
def editor_sort_items(request, book_id):
    """Docstring."""
    book = get_object_or_404(
        Book,
        pk=book_id)

    if request.method == "POST":
        items = request.POST.getlist("items")

        if not items:
            items = request.POST.getlist("items[]")

        if items:
            items = [int(i) for i in items]
            sort_book_items(book, items)

    response_data = {}

    return HttpResponse(
        json.dumps(response_data),
        content_type="application/json")


@staff_member_required
def editor_add_file_for_download(request, book_id):
    """Docstring."""
    book = get_object_or_404(
        Book,
        pk=book_id)

    form = FileForDownloadForm(
        request.POST or None, request.FILES or None,
        instance=instance)

    if request.method == "POST":
        instance = FileForDownload(book=book)

        if form.is_valid():
            form.save()

            return redirect(
                "editor-book",
                book_id=book.id)

    return render(
        request, "dwb_editor/file_for_download/add.html", {
            "book":     book,
            "form":     form,
        })


@staff_member_required
def editor_edit_file_for_download(request, book_id, file_id):
    """Docstring."""
    book = get_object_or_404(
        Book,
        pk=book_id)
    file_for_download = get_object_or_404(
        FileForDownload,
        pk=file_id,
        book=book)

    form = FileForDownloadForm(
        request.POST or None, request.FILES or None,
        instance=file_for_download)

    if request.method == "POST":
        if form.is_valid():
            form.save()

            return redirect(
                "editor-book",
                book_id=book.id)

    return render(
        request, "dwb_editor/file_for_download/edit.html", {
            "book":                 book,
            "file_for_download":    file_for_download,
            "form":                 form,
        })


@staff_member_required
def editor_delete_file_for_download(request, book_id, file_id):
    """Docstring."""
    book = get_object_or_404(
        Book,
        pk=book_id)
    file_for_download = get_object_or_404(
        FileForDownload,
        pk=file_id,
        book=book)

    if request.method == "POST":
        file_for_download.delete()

        return redirect(
            "editor-book",
            book_id=book.id)

    return render(
        request, "dwb_editor/file_for_download/delete.html", {
            "book":                 book,
            "file_for_download":    file_for_download,
        })


@staff_member_required
def editor_congratulations(request, book_id):
    """Docstring."""
    book = get_object_or_404(
        Book,
        pk=book_id)

    return render(
        request, "dwb_book/book_congratulations.html", {
            "name":     request.user.get_full_name(),
            "book":     book,
        })


@staff_member_required
def editor_certificate(request, book_id):
    """Docstring."""
    book = get_object_or_404(
        Book,
        pk=book_id)

    return render(
        request, "dwb_book/book_print_certificate.html", {
            "name":     request.user.get_full_name(),
            "book":     book,
        })
