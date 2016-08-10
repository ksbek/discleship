import datetime
import os
import pipes
import random
import subprocess

from pyvirtualdisplay import Display
from StringIO import StringIO
from tempfile import NamedTemporaryFile

from django.conf import settings
from django.db.models import Q

from django.utils.translation import ugettext as _

from dwb_book.models import Item, Copy


def apply_markers(text, markers):
    """Docstring."""
    if not text or len(text.strip()) == 0:
        return text  # text is empty

    for marker in markers:
        # simple case
        placeholder = marker.placeholder
        text = text.replace(marker.placeholder, marker.replacement)

        # handle HTML &nbsp;
        placeholder = marker.placeholder.replace(" ", "&nbsp;")
        text = text.replace(placeholder, marker.replacement)

    return text


def get_table_of_content(book, copy=None):
    """Docstring."""
    # get index value of important headings
    if book.first_appendix_heading:
        appendix_index = book.first_appendix_heading._order
    else:
        appendix_index = None

    if book.first_payed_heading:
        payed_index = book.first_payed_heading._order
    else:
        payed_index = None

    if copy:
        access_max_index = get_last_item_for_access(book, copy.user)._order
    else:
        access_max_index = get_last_item_for_access(book, None)._order

    # find all headings
    items = Item.objects.filter(
        (Q(item_type="h1") | Q(item_type="h2") | Q(item_type="h3")) &
        Q(book=book)
    )
    toc = []

    for item in items:
        is_appendix = (appendix_index and item._order >= appendix_index)

        if is_appendix:
            is_free = True
            can_access = True
        else:
            is_free = (payed_index and item._order < payed_index)
            can_access = item._order <= access_max_index

        info = {
            "item":         item,
            "can_access":   can_access,
            "is_appendix":  is_appendix,
            "is_free":      is_free,
        }
        toc.append(info)

    # done
    return toc


def get_page_items(book, index):
    """Docstring."""
    # find heading for this item
    this_item = Item.objects.get(
        book=book,
        _order=index
    )

    if this_item.is_heading():
        first_item = this_item
    else:
        first_item = this_item.get_parent()

    # find headings for current items
    if first_item.item_type == "h1":
        headings = ["h1"]
    elif first_item.item_type == "h2":
        headings = ["h1", "h2"]
    elif first_item.item_type == "h3":
        headings = ["h1", "h2", "h3"]
    else:
        headings = []

    # find items under current heading
    items = [first_item]
    current_item = first_item
    has_content = False

    while True:
        try:
            current_item = current_item.get_next_item()
        except Item.DoesNotExist:
            break

        if current_item.is_heading():
            if current_item.item_type in headings:
                return items
            elif has_content:
                return items
            else:
                headings.append(current_item.item_type)
        else:
            has_content = True

        items.append(current_item)

    return items


def get_chapters_user_can_access(book, user):
    """Return a list of h1 items that user can access."""
    last_item = get_last_item_for_access(book, user)

    items = book.item_set.filter(
        item_type="h1",
        _order__lte=last_item._order,
    )

    return items


def get_chapter_items(book, h1):
    """Docstring."""
    if h1.book != book:
        raise Exception(
            _("Chapter not found"))

    # find H1 for this item
    if h1.item_type == "h1":
        first_item = h1
    else:
        first_item = h1.get_parent(item_type="h1")

    # find items under this H1
    try:
        next_h1 = Item.objects.filter(
            book=book,
            item_type="h1",
            _order__gt=first_item._order
        )[0]
        items = Item.objects.filter(
            book=book,
            _order__gte=first_item._order,
            _order__lt=next_h1._order
        ).all()
    except IndexError:
        # this was last H1
        items = Item.objects.filter(
            book=book,
            _order__gte=first_item._order
        ).all()

    return items


def get_last_item_for_access(book, user):
    """Docstring."""
    copy = None

    try:
        if user and user.is_authenticated():
            copy = Copy.objects.get(
                book=book,
                user=user,
            )
    except Copy.DoesNotExist:
        pass

    if copy and copy.status == "completed":
        # can access everything
        return book.item_set.last()

    if copy and copy.status == "progress":
        # can access current page and earlier
        if copy.current_item:
            page = get_page_items(book, copy.current_item._order)
            return page[-1]

    # preview access only
    if book.first_payed_heading:
        return book.first_payed_heading.get_previous_item()

    page = get_page_items(book, book.item_set.first()._order)

    return page[-1]


def can_user_access_item(user, item):
    """Docstring."""
    last_item = get_last_item_for_access(item.book, user)

    try:
        appendix_index = item.book.first_appendix_heading._order

        return item._order <= last_item._order or item._order >= appendix_index
    except:
        return item._order <= last_item._order


def update_progress(copy, new_item):
    """Update progress to given item. Does not save copy."""
    # sanity check
    if copy.book != new_item.book:
        raise Exception(
            _("Invalid item for book"))

    if copy.status != "completed" and copy.status != "progress":
        return

    # make sure we don't go back in progress
    if copy.current_item and copy.current_item._order > new_item._order:
        return

    # calculate progress
    if copy.book.first_appendix_heading:
        appendix_index = copy.book.first_appendix_heading._order
        total_items = copy.book.item_set.filter(
            _order__lt=appendix_index
        ).count()
    else:
        appendix_index = None
        total_items = copy.book.item_set.count()

    if appendix_index and new_item._order >= appendix_index:
        copy.status = "completed"
        copy.current_item = None
        copy.overall_progress = 100

        if copy.certificate_number == 0:
            copy.completed_date = datetime.date.today()
            copy.certificate_number = random.randint(1000000, 9999999)
    else:
        copy.current_item = new_item
        copy.overall_progress = 100.0 * new_item._order / total_items


def delete_copy_data(copy):
    """Docstring."""
    copy.overall_progress = 0
    copy.current_item = None

    if copy.status == "completed":
        copy.status = "progress"

    copy.save()

    for response in copy.response_set.all():
        response.delete()


def html_to_pdf(html):
    """Docstring."""
    html_file = None
    pdf_file = None
    display = None

    try:
        display = Display(visible=0, size=(800, 600))
        display.start()

        html_file = NamedTemporaryFile(delete=False, suffix=".html")
        html_file.write(html.encode("utf-8", "ignore"))
        html_file.close()

        pdf_file = NamedTemporaryFile(delete=False, suffix=".pdf")
        pdf_file.close()

        DEVNULL = open(os.devnull, "wb")

        cmd = [
            "wkhtmltopdf",
            html_file.name,
            pdf_file.name
        ]
        subprocess.call(
            cmd
        )
        DEVNULL.close()

        f = open(pdf_file.name, "rb")
        pdf_content = f.read()
        f.close()

        if not pdf_content:
            raise Exception(
                _("Failed to create PDF"))

        return pdf_content

    finally:
        # clean up
        try:
            if display:
                display.stop()
        except:
            pass

        try:
            if html_file:
                os.unlink(html_file.name)
        except:
            pass

        try:
            if pdf_file:
                os.unlink(pdf_file.name)
        except:
            pass
