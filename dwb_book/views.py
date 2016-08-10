import cStringIO as StringIO
import datetime
import random
import sys

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import (
    render,
    redirect,
    get_object_or_404,
    )
from django.template.loader import render_to_string
from django.utils.translation import ugettext as _

from cgi import escape
from xhtml2pdf import pisa

from dwb_book.forms import DeleteForm
from dwb_book.models import (
    Book,
    Copy,
    Item,
    )
from dwb_book.services import (
    apply_markers,
    can_user_access_item,
    delete_copy_data,
    get_chapter_items,
    get_chapters_user_can_access,
    get_last_item_for_access,
    get_page_items,
    get_table_of_content,
    html_to_pdf,
    update_progress,
    )
from dwb_group.models import (
    Group,
    Member,
    Invite,
    )


def book_overview(request, book_slug):
    """Overview of the book, including progress of the current user."""
    book = get_object_or_404(Book, slug=book_slug)

    if not request.user.is_authenticated():
        return redirect(
            "book-toc",
            book_slug=book.slug)

    copy = book.get_or_create_copy(
        user=request.user)

    # get info about groups
    groups = []
    for group in [m.group for m in Member.objects.filter(
            user=request.user,
            group__book=book)]:
        # only creator of group can message the entire group
        can_message_group = (group.creator == request.user)

        group_info = {
            "id":                   group.id,
            "name":                 group.name,
            "members":              [],
            "invitees":             [],
            "can_message_group":    can_message_group,
        }

        # ---------------------------------------------------------------------
        # --- Get Group Members
        """
        for group_user in [m.user for m in group.member_set.all()]:
            their_copy = book.get_or_create_copy(user=group_user)

            if group_user == request.user:
                group_info["my_progress"] = their_copy.overall_progress
            else:
                group_info["members"].append({
                    "id":           group_user.id,
                    "full_name":    group_user.get_full_name(),
                    "progress":     their_copy.overall_progress,
                })
        """
        for group_member in [m for m in group.member_set.all()]:
            their_copy = book.get_or_create_copy(
                user=group_member.user)

            if group_member.user == request.user:
                group_info["my_progress"] = their_copy.overall_progress
            else:
                group_info["members"].append({
                    "id":           group_member.user.id,
                    "full_name":    group_member.user.get_full_name(),
                    "progress":     their_copy.overall_progress,
                    "member_id":    group_member.id,
                })

        for invite in Invite.objects.filter(group=group, status="accepted"):
            their_copy = book.get_or_create_copy(
                user=group_member.user)
            group_info["members"].append({
                "id": invite.recipient_user_id,
                "full_name": invite.recipient_user.get_full_name(),
                "progress": their_copy.overall_progress,
                "member_id": invite.id,
            })

        # ---------------------------------------------------------------------
        # --- Get pending Invites to the Group
        invites = Invite.objects.filter(
            group=group,
            status="pending",
        )

        for group_invitee in invites:
            group_info["invitees"].append({
                "id":           group_invitee.id,
                "full_name":    group_invitee.recipient_name,
                "email":        group_invitee.recipient_email,
                "code":         group_invitee.code,
            })

        groups.append(group_info)

    return render(
        request, "dwb_book/book_overview.html", {
            "book":     book,
            "copy":     copy,
            "groups":   groups,
        })


def book_toc(request, book_slug):
    """Docstring."""
    book = get_object_or_404(
        Book,
        slug=book_slug,
    )

    if request.user.is_authenticated():
        copy = book.get_or_create_copy(user=request.user)
    else:
        copy = None

    toc = get_table_of_content(book, copy)

    return render(
        request, "dwb_book/book_toc.html", {
            "book":     book,
            "copy":     copy,
            "chapters": [
                item for item in toc if not item["is_appendix"]
            ],
            "appendix": [
                item for item in toc if item["is_appendix"]
            ],
        })


def book_resume(request, book_slug):
    """Docstring."""
    book = get_object_or_404(
        Book,
        slug=book_slug,
    )
    copy = book.get_or_create_copy(request.user)

    if not copy:
        return redirect(
            "book-toc",
            book_slug=book.slug)

    if copy.current_item:
        return redirect(
            "book-page",
            book_slug=book.slug,
            index=copy.current_item._order)

    return redirect(
        "book-toc",
        book_slug=book.slug)


def book_page(request, book_slug, index):
    """Docstring."""
    book = get_object_or_404(
        Book,
        slug=book_slug,
    )
    all_items = get_page_items(book, index)
    first_item = all_items[0]
    input_items = [i for i in all_items if i.is_input()]

    if first_item.item_type == "h1":
        chapter_title = first_item.title
    else:
        chapter_title = first_item.get_parent("h1").title

    if request.user.is_authenticated():
        copy = book.get_or_create_copy(request.user)
    else:
        copy = None

    # permissions; check they are at the end of preview
    if not can_user_access_item(request.user, all_items[0]):
        return redirect(
            "book-toc",
            book_slug=book.slug)

    if request.method == "POST":
        # save changes
        if copy:
            for item in input_items:
                value = request.POST.get("item-%d" % (item.id,))

                if value is not None:
                    copy.set_response_to(item, value)

                copy.save()

        if request.POST.get("action") == "continue":
            #  move to next page
            try:
                next_item = all_items[-1].get_next_item()
            except Item.DoesNotExist:
                next_item = None

            if copy:
                if next_item:
                    update_progress(copy, next_item)
                    copy.save()
                else:
                    copy.current_item = None
                    copy.status = "completed"
                    copy.overall_progress = 100

                    if copy.certificate_number == 0:
                        copy.completed_date = datetime.date.today()
                        copy.certificate_number = random.randint(
                            1000000, 9999999)

                    copy.save()

            # check for congratulations page
            if not next_item or next_item == book.first_appendix_heading:
                if copy and copy.status == "completed":
                    return redirect(
                        "book-congratulations",
                        book_slug=book.slug)

            # continue to next page
            return redirect(
                "book-page",
                book_slug=book.slug,
                index=next_item._order)
        else:
            # show current page again
            current_item = all_items[0]

            return redirect(
                "book-page",
                book_slug=book.slug,
                index=current_item._order)

    items = []
    footnotes = ""
    markers = book.marker_set.all()

    for item in all_items:
        item_data = {
            "id":           item.id,
            "item_type":    item.item_type,
            "intro":        item.intro,
            "title":        item.title or "",
            "content":      apply_markers(item.content, markers),
        }

        if item.is_input():
            item_data["options"] = item.get_options()

            if copy:
                item_data["response"] = copy.get_response_to(item) or ""
            else:
                item_data["response"] = ""

        items.append(item_data)

        if item.footnotes:
            footnotes += item.footnotes

    return render(
        request, "dwb_book/book_page.html", {
            "book":             book,
            "copy":             copy,
            "items":            items,
            "first_item":       items[0],
            "chapter_title":    chapter_title,
            "has_inputs":       len(input_items),
            "footnotes":        footnotes,
        })


@login_required
def book_congratulations(request, book_slug):
    """Docstring."""
    book = get_object_or_404(
        Book,
        slug=book_slug,
    )
    copy = Copy.objects.get(
        book=book,
        user=request.user,
    )

    if copy.status != "completed":
        return redirect(
            "book-toc",
            book_slug=book.slug)

    return render(
        request, "dwb_book/book_congratulations.html", {
            "book":     book,
            "copy":     copy,
        })


@login_required
def book_certificate_print(request, book_slug):
    """Docstring."""
    book = get_object_or_404(
        Book,
        slug=book_slug,
    )
    copy = Copy.objects.get(
        book=book,
        user=request.user,
    )

    if copy.status != "completed":
        return redirect(
            "book-toc",
            book_slug=book.slug)

    return render(
        request, "dwb_book/book_print_certificate.html", {
            "book":     book,
            "copy":     copy,
        })


@login_required
def book_copy_delete(request, book_slug):
    """Docstring."""
    book = get_object_or_404(
        Book,
        slug=book_slug,
    )
    copy = get_object_or_404(
        Copy,
        book=book,
        user=request.user,
    )

    if request.method == "POST":
        delete_form = DeleteForm(request.POST)

        if delete_form.is_valid():
            if delete_form.cleaned_data.get("confirm") == "yes":
                delete_copy_data(copy)
                messages.info(
                    request,
                    _("All data was deleted from your workbook."))

            return redirect(
                "book-overview",
                book_slug=book.slug)
    else:
        delete_form = DeleteForm()

    return render(
        request, "dwb_book/book_copy_delete.html", {
            "delete_form":  delete_form,
            "copy":         copy,
            "book":         book,
        })


@login_required
def book_export(request, book_slug):
    """Docstring."""
    book = get_object_or_404(
        Book,
        slug=book_slug,
    )
    copy = get_object_or_404(
        Copy,
        book=book,
        user=request.user,
    )

    chapters = get_chapters_user_can_access(book, request.user)

    if request.method == "POST":
        # get items to export
        if request.POST.get("chapter_id"):
            chapter_id = int(request.POST.get("chapter_id"))
            chapter = next((c for c in chapters if c.id == chapter_id), None)

            if not chapter:
                return HttpResponseForbidden(
                    _("You don't have permission to export this chapter."))

            items_to_export = get_chapter_items(book, chapter)
        else:
            chapter = None
            last_item = get_last_item_for_access(book, request.user)
            items_to_export = book.item_set.filter(
                _order__lte=last_item._order)

        # generate HTML representation of the workbook
        markers = book.marker_set.all()
        items = []

        for item_object in items_to_export:
            item_data = {
                "id":           item_object.id,
                "intro":        item_object.intro,
                "title":        item_object.title or "",
                "content":      apply_markers(item_object.content, markers),
                "options":      item_object.get_options(),
                "item_type":    item_object.item_type,
                "is_input":     item_object.is_input(),
                "is_heading":   item_object.is_heading(),
            }

            if item_object.is_input:
                item_data["response"] = copy.get_response_to(item_object)

            items.append(item_data)

        data = {
            "book":         book,
            "copy":         copy,
            "items":        items,
            "STATIC_URL":   settings.STATIC_URL or "",
            "BASE_URL":     request.build_absolute_uri("/"),
        }
        html = render_to_string("dwb_book/export/copy.html", data)

        # --- Convert to PDF
        result = StringIO.StringIO()
        pdf = pisa.pisaDocument(
            StringIO.StringIO(html.encode("UTF-8")), result)

        if not pdf.err:
            return HttpResponse(
                result.getvalue(),
                content_type="application/pdf")
        return HttpResponse(
            "We had some errors<pre>%s</pre>" % escape(html))

        pdf = html_to_pdf(html)

        # create response
        if chapter:
            filename = "%s-%s.pdf" % (book.slug, chapter.slug)
        else:
            filename = book.slug + ".pdf"

        response = HttpResponse(pdf, content_type="application/pdf")
        response["Content-Disposition"] = "attachment;filename=" + filename

        return response
    else:
        return render(
            request, "dwb_book/book_export.html", {
                "book":     book,
                "copy":     copy,
                "chapters": chapters,
            })


@login_required
def book_certificate_export(request, book_slug):
    """Docstring."""
    book = get_object_or_404(
        Book,
        slug=book_slug,
    )
    copy = get_object_or_404(
        Copy,
        book=book,
        user=request.user,
    )

    # convert to PDF
    html = render_to_string("dwb_book/book_certificate.html", {
        "book":         book,
        "copy":         copy,
        "user":         request.user,
        "STATIC_URL":   settings.STATIC_URL or "",
        "BASE_URL":     request.build_absolute_uri("/"),
    })
    pdf = html_to_pdf(html)

    filename = "certificate.pdf"
    response = HttpResponse(pdf, content_type="application/pdf")
    response["Content-Disposition"] = "attachment;filename=" + filename

    return response


def book_purchase_to_continue(request, book_slug):
    """User needs to purchase the book to continue."""
    book = get_object_or_404(
        Book,
        slug=book_slug,
    )

    messages.info(
        request,
        "You completed preview of %s. Buy full access to continue." % (
            book.title))

    return redirect(
        "book-purchase",
        book_slug=book.slug)


@login_required
def book_sponsor(request, book_slug, group_id):
    """Docstring."""
    # make sure current user belongs to this group
    book = get_object_or_404(
        Book,
        slug=book_slug)
    group = get_object_or_404(
        Group,
        id=group_id,
        book=book)
    member = get_object_or_404(
        Member,
        group=group,
        user=request.user)

    # check status of this book
    if book.status != "active":
        messages.error(
            request,
            _("This book is not available for purchase at this time."))

        return redirect(
            "book-overview",
            book_slug=book.slug)

    form = InviteForm(
        request.POST or None, request.FILES or None,
        instance=invite)

    if request.method == "POST":
        invite = Invite()
        invite.sender_user = request.user
        invite.group = group
        invite.status = "pending"
        invite.generate_code()

        if form.is_valid():
            form.save()

            purchase = create_purchase(
                request, book, quantity=1, is_gift=True, is_priest=False)
            purchase.group = group
            purchase.save()
            redirect_url = start_purchase(request, purchase)

            return redirect(redirect_url)

    return render(
        request, "dwb_book/book_sponsor.html", {
            "form":     form,
            "book":     book,
            "group":    group,
        })
