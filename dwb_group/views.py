import json

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth.views import redirect_to_login
from django.core.mail import send_mail
from django.core.urlresolvers import reverse
from django.http import HttpResponse
from django.shortcuts import (
    render,
    redirect,
    get_object_or_404
    )
from django.template.loader import render_to_string
from django.utils.translation import ugettext as _

from dwb_group.forms import (
    GroupForm,
    InviteForm,
    InviteMessageForm,
    )
from dwb_group.models import (
    Group,
    Member,
    Invite,
    Message,
    are_users_in_same_group,
    )

from dwb_book.models import Book


@login_required
def group_create(request, book_slug):
    """Docsting."""
    book = get_object_or_404(
        Book,
        slug=book_slug)

    form = GroupForm(
        request.POST or None, request.FILES or None,
        user=request.user, book=book)

    if request.method == "POST":
        if form.is_valid():
            group = form.save()

            # assign user to the group
            member = Member(
                user=request.user,
                group=group)
            member.save()

            messages.success(
                request,
                _("Your group was created."))

            return redirect(
                "book-overview",
                book_slug=book.slug)

    return render(
        request, "dwb_group/group_create.html", {
            "create_form":  form,
        })


@login_required
def group_rename(request, group_id, book_slug):
    """Docsting."""
    book = get_object_or_404(
        Book,
        slug=book_slug)
    group = Group.objects.get(
        id=group_id)

    form = GroupForm(
        request.POST or None, request.FILES or None,
        instance=group)

    if request.method == "POST":
        if form.is_valid():
            form.save()

            messages.success(
                request,
                _("Your group was renamed."))

            return redirect(
                "dwb_overview",
                book_slug=book.slug)

    return render(
        request, "dwb_group/group_rename.html", {
            "rename_form":  form,
        })


@login_required
def group_join(request, code):
    """Docsting."""
    invite = get_object_or_404(
        Invite,
        code=code)
    group = invite.group
    book = group.book

    # make sure they log in
    if not request.user.is_authenticated():
        messages.info(
            request,
            _("You need to log in or register before you can join a group."))

        return redirect_to_login(
            request.build_absolute_uri())

    # check if invite is active
    if invite.status != "pending":
        if invite.status == "accepted":
            messages.info(
                request,
                _("Invitation to group was already used."))
        else:
            messages.info(
                request,
                _("Invitation to group is no longer active."))
        return redirect("my-account")

    if request.method == "POST":
        # add them if they are not part of the group
        Member.objects.get_or_create(
            user=request.user,
            group=group)

        # mark invite as used
        invite.mark_accepted(request.user)
        invite.save()

        # get copy of book
        book.get_or_create_copy(
            user=request.user)

        # done
        return redirect(
            "book-overview",
            book_slug=book.slug)

    return render(
        request, "dwb_group/group_join.html", {
            "book":     book,
            "group":    group,
            "invite":   invite,
        })


@login_required
def group_invite(request, group_id):
    """Docsting."""
    try:
        member = Member.objects.get(
            user=request.user,
            group=group_id)
    except Member.DoesNotExist:
        messages.error(
            request,
            _("You do not belong to this group."))

        return redirect("dwb_account")

    group = member.group

    form = InviteForm(
        request.POST or None, request.FILES or None,
        user=request.user, group=group)
    msg_form = InviteMessageForm(request.POST or None)

    if request.method == "POST":
        if form.is_valid() and msg_form.is_valid():
            instance = form.save(commit=False)
            instance.generate_code()
            instance.save()

            invite_url = request.build_absolute_uri(
                reverse(
                    "group-join", kwargs={
                        "code":     instance.code,
                    })
            )
            message_text = render_to_string(
                "dwb_group/email/invite_to_group.txt", {
                    "invite":           instance,
                    "invite_message":   msg_form.cleaned_data[
                        "invite_message"],
                    "invite_url":       invite_url
                }
            )
            message_subject = _("Invite to a group on Discipleship Workbooks")
            send_mail(
                message_subject,
                message_text,
                instance.sender_user.email,
                [
                    instance.recipient_email
                ]
            )

            messages.success(
                request,
                _("Invitation was sent."))

            return redirect(
                "book-overview",
                book_slug=group.book.slug)

    return render(
        request, "dwb_group/group_invite.html", {
            "group":                group,
            "invite_form":          form,
            "invite_message_form":  msg_form,
        })


@login_required
def group_leave(request, group_id):
    """Docsting."""
    try:
        member = Member.objects.get(
            user=request.user,
            group=group_id)
    except Member.DoesNotExist:
        return redirect("dwb_account")

    group = member.group

    if request.method == "POST":
        member.delete()

        messages.success(
            request,
            _("You left the group."))

        return redirect(
            "dwb_overview",
            book_slug=group.book.slug)

    return render(
        request, "dwb_group/group_leave.html", {
            "group":    group,
        })


@login_required
def group_tell(request):
    """Docsting."""
    if request.method == "POST":
        email = request.POST.get("recipient-email")
        text = request.POST.get("message-text")
        book_url = request.POST.get("book-url")

        if email:
            message_subject = _("Invite to a group on Discipleship Workbooks")
            message_text = render_to_string(
                "dwb_group/email/tell_a_friend.txt", {
                    "sender":   request.user,
                    "text":     text,
                    "book_url": book_url,
                }
            )
            send_mail(
                message_subject,
                message_text,
                request.user.email,
                [
                    email,
                ]
            )
            return HttpResponse(
                json.dumps({
                    "success":  _("Message was sent.")
                }))
        else:
            return HttpResponse(
                json.dumps({
                    "error":    _("Recipient was not provided."),
                })
            )

    return HttpResponse(
        json.dumps({
            "error":    _("Invalid request.")
        })
    )


@login_required
def group_message(request):
    """Docsting."""
    if request.method == "POST":
        group_id = request.POST.get("group_id")
        user_id = request.POST.get("user_id")

        if user_id:
            return message_user(request)
        elif group_id:
            return message_group(request)
        else:
            return HttpResponse(
                json.dumps({
                    "error":    _("Recipient was not provided."),
                })
            )

    return HttpResponse(
        json.dumps({
            "error":    _("Invalid request.")
        })
    )


@login_required
def message_group(request):
    """Docsting."""
    if request.method == "POST":
        group_id = request.POST.get("group_id")
        text = request.POST.get("text")

        # make sure user belongs to the group
        try:
            member = Member.objects.get(
                user=request.user,
                group=group_id)
            group = member.group
        except Member.DoesNotExist:
            return HttpResponse(
                json.dumps({
                    "error":    _("You cannot message this group."),
                })
            )

        if group.creator != request.user:
            return HttpResponse(
                json.dumps({
                    "error":    _(
                        "Only person who created this group "
                        "can message everyone."),
                })
            )

        # make sure we send a message to someone who is in the same group
        if text is None or str(text).strip() == "":
            return HttpResponse(
                json.dumps({
                    "error":    _("We cannot send an empty message."),
                })
            )

        for recipient in [m.user for m in group.member_set.all()]:
            msg = Message(
                sender_user=request.user,
                recipient_user=recipient)
            msg.text = text
            msg.save()
            msg.send()

        return HttpResponse(
            json.dumps({
                "success": _("Message was sent.")
            })
        )
    else:
        return HttpResponse(
            json.dumps({
                "error": _("Invalid request.")
            })
        )


@login_required
def message_user(request):
    """Docsting."""
    if request.method == "POST":
        recipient_id = request.POST.get("user_id")
        text = request.POST.get("text")

        try:
            recipient = User.objects.get(
                id=recipient_id)
        except User.DoesNotExist:
            return HttpResponse(
                json.dumps({
                    "error":    _("You cannot message this user."),
                })
            )

        # make sure we send a message to someone who is in the same group
        if text is None or str(text).strip() == "":
            return HttpResponse(
                json.dumps({
                    "error":    _("We cannot send an empty message.")
                })
            )

        if are_users_in_same_group(recipient_id, request.user):
            msg = Message(
                sender_user=request.user,
                recipient_user=recipient)
            msg.text = text
            msg.save()
            msg.send()

            return HttpResponse(
                json.dumps({
                    "success":  _("Message was sent.")
                })
            )
        else:
            return HttpResponse(
                json.dumps({
                    "error":    _("You cannot message this user.")
                })
            )
    else:
        return HttpResponse(
            json.dumps({
                "error":    _("Invalid request.")
            })
        )


# -----------------------------------------------------------------------------
# --- AJAX
# -----------------------------------------------------------------------------
@login_required
def ajax_invite_remove(request):
    """Docsting."""
    if request.is_ajax():
        invite_code = request.POST.get("invite_code", "")

        # Retrieve TimeTable Entry
        invite = get_object_or_404(
            Invite,
            code=invite_code,
        )
        invite.delete()

        return HttpResponse(status=200)

    return HttpResponse(status=404)


@login_required
def ajax_member_remove(request):
    """Docsting."""
    if request.is_ajax():
        member_id = request.POST.get("member_id", "")

        # Retrieve TimeTable Entry
        member = get_object_or_404(
            Member,
            id=member_id,
            group__creator=request.user,
        )
        member.delete()

        return HttpResponse(status=200)

    return HttpResponse(status=404)
