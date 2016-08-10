from django.conf import settings
from django.core.urlresolvers import reverse
from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.views import redirect_to_login
from django.http import HttpResponse, HttpResponseNotFound
from django.shortcuts import (
    render,
    redirect,
    get_object_or_404,
    )
from django.utils import timezone
from django.utils.translation import ugettext as _

from dwb_book.models import Book, Copy
from dwb_store.forms import EmailClaimCodeForm
from dwb_store.models import Purchase, PurchaseClaim
from dwb_store.service import create_purchase, start_purchase
from dwb_store.service import (
    create_purchase,
    start_purchase,
    confirm_payment,
    send_gift_code,
    send_invoice,
    )
from dwb_group.models import (
    Member,
    Group,
    Invite,
    )
from dwb_user.models import Profile


def store_discounts(request):
    """Docstring."""
    books = Book.objects.filter(
        status="active",
        language=request.LANGUAGE_CODE,
        )

    return render(
        request, "webbook/store/discounts.html", {
            "books":    books,
        })


def store_discounts_buy(request, book_slug):
    """Docstring."""
    # make sure they are logged in
    if not request.user.is_authenticated():
        messages.info(
            request,
            _("You need to log in or register to continue."))

        return redirect_to_login(request.build_absolute_uri())

    # get basic data
    book = get_object_or_404(
        Book,
        slug=book_slug)

    if book.status != "active" and book.status != "draft":
        return HttpResponseNotFound()

    groups = [m.group for m in Member.objects.filter(
        user=request.user, group__book=book)]

    # process request
    if request.method == "POST":
        # create purchase object
        quantity_input = int(request.POST.get("quantity", "1"))
        profile = Profile.objects.get(
            user=request.user)

        if profile.is_pastor == "0":
            is_priest = False
        else:
            is_priest = True

        purchase = create_purchase(
            request,
            book,
            quantity=quantity_input,
            is_gift=True,
            is_priest=is_priest)

        # assign group if needed
        group_input = request.POST.get("group")

        group = None
        if group_input == "new":
            if request.POST.get("group_name"):
                group = Group()
                group.book = book
                group.name = request.POST.get("group_name")
                group.creator = request.user
                group.save()

                # book.get_or_create_copy(user=request.user)

                member = Member()
                member.user = request.user
                member.group = group
                member.save()
        elif group_input:
            group = next((g for g in groups if str(g.id) == group_input), None)

        if group:
            purchase.group = group
            purchase.save()

        # redirect
        redirect_url = start_purchase(request, purchase)

        return redirect(redirect_url)

    return render(
        request, "webbook/store/discounts_buy.html", {
            "book":     book,
            "groups":   groups,
        })


def store_purchase(request, book_slug):
    """Docstring."""
    book = get_object_or_404(
        Book,
        slug=book_slug)

    if book.status != "active" and book.status != "draft":
        return HttpResponseNotFound()

    is_gift = request.POST.get("gift") and request.POST.get("gift") != "0"

    if request.method == "POST":
        if book.status != "active":
            return redirect(
                "dwb_purchase",
                book_slug=book.slug)

        # check if they need to log in
        if not is_gift and not request.user.is_authenticated():
            messages.info(
                request,
                _("You need to log in or register to purchase a workbook."))

            return redirect_to_login(request.build_absolute_uri())

        # check if they have a copy
        if not is_gift:
            copy = book.get_or_create_copy(request.user)

            if copy.status != "preview":
                messages.info(
                    request,
                    _("You already have a copy of this book."))

                return redirect(
                    "dwb_overview",
                    book_slug=book.slug)

        profile, created = Profile.objects.get_or_create(
            user=request.user)

        if profile.is_pastor == "0":
            is_priest = False
        else:
            is_priest = True

        purchase = create_purchase(
            request,
            book,
            quantity=1,
            is_gift=is_gift,
            is_priest=is_priest)
        redirect_url = start_purchase(request, purchase)

        return redirect(redirect_url)

    return render(
        request, "webbook/store/purchase.html", {
            "book":     book,
        })


def store_purchase_confirm(request, invoice_number):
    """Docstring."""

    p = get_object_or_404(
        Purchase,
        invoice_number=invoice_number)

    cancel_url = reverse("dwb_purchase_cancel", kwargs={
        "invoice_number":   p.invoice_number
    })
    complete_url = reverse("dwb_purchase_complete", kwargs={
        "invoice_number":   p.invoice_number
    })

    # check state
    if p.status == "payed":
        return redirect(complete_url)

    if p.status == "canceled":
        return redirect(cancel_url)

    if p.status != "pending":
        raise Exception(
            _("Invalid status of a purchase."))

    if p.buyer_user and p.buyer_user != request.user:
        raise Exception(
            _("Permission denied."))

    form = None

    if p.is_gift():
        if request.method == "POST":
            form = EmailClaimCodeForm(request.POST)

            if form.is_valid():
                # finalize payment
                if p.total_charge >= 0.01:
                    resp = confirm_payment(p, request.GET)

                    if not p.buyer_email:
                        p.buyer_email = resp["billing_email"]

                p.date = timezone.now()

                p.recipient_email = form.cleaned_data["recipient_email"]
                p.recipient_name = form.cleaned_data["recipient_name"]
                p.status = "payed"
                p.save()

                # send emails
                if p.buyer_email:
                    send_invoice(request, p)

                if p.recipient_email:
                    send_gift_code(request, p)

                return redirect(complete_url)
        else:
            form_data = {
                "recipient_name":   p.recipient_name,
                "recipient_email":  p.recipient_email,
            }
            form = EmailClaimCodeForm(
                initial=form_data)
    else:
        copy = p.book.get_or_create_copy(request.user)

        # check if they own a copy
        if copy.status != "preview":
            assert p.status == "pending"

            p.status = "canceled"
            p.save()

            messages.info(
                request,
                _(
                    "Purchase was cancelled. "
                    "You already have a copy of this book."))

            return redirect(
                "dwb_overview",
                book_slug=p.book.slug)

        if request.method == "POST":
            # finalize payment
            if p.total_charge >= 0.01:
                resp = confirm_payment(p, request.GET)

                if not p.buyer_email:
                    p.buyer_email = resp["billing_email"]

            p.status = "payed"
            p.date = timezone.now()
            p.save()

            # activate the copy
            copy.status = "progress"
            copy.save()

            if p.buyer_email:
                send_invoice(request, p, p.buyer_email)

            if (
                    request.user.is_authenticated() and request.user.email and
                    request.user.email != p.buyer_email):
                send_invoice(request, p, request.user.email)

            return redirect(complete_url)

    # Make sure to submit form to the same URL as the request.
    # Otherwise important data in query string might get lost.
    return render(
        request, "webbook/store/confirm.html", {
            "book":         p.book,
            "purchase":     p,
            "cancel_url":   cancel_url,
            "form":         form,
        })


def store_purchase_complete(request, invoice_number):
    """Show success page for this purchase.

    Important: authentication is not required. Do not show sensitive
    information.
    """
    p = get_object_or_404(
        Purchase,
        status="payed",
        invoice_number=invoice_number)

    return render(
        request, "webbook/store/complete.html", {
            "purchase": p,
            "book":     p.book,
        })


def store_purchase_cancel(request, invoice_number):
    """Docstring."""
    try:
        p = Purchase.objects.get(
            invoice_number=invoice_number)

        # check status
        if p.status == "pending":
            p.status = "canceled"
            p.save()

        if p.status == "payed":
            return redirect("dwb_purchase_complete", kwargs={
                "invoice_number":   p.invoice_number
            })
    except Purchase.DoesNotExist:
        pass

    messages.info(
        request,
        _("Your purchase was canceled."))

    return redirect("home")


def store_redeem(request):
    """Docstring."""
    if not request.user.is_authenticated():
        messages.info(
            request,
            _("You need to log in to redeem your gift code."))

        return redirect_to_login(request.build_absolute_uri())

    purchase = None
    book = None

    code = request.POST.get("code") or request.GET.get("code")

    # get and check purchase
    if code:
        # get purchase info
        try:
            purchase = Purchase.objects.get(
                status="payed",
                gift_code=code)
        except Purchase.DoesNotExist:
            messages.error(
                request,
                _("Submitted gift code was not found"))

            return redirect("dwb_redeem")

        book = purchase.book
        copy = book.get_or_create_copy(request.user)

        # check if already owns a copy
        if copy.status != "preview":
            if PurchaseClaim.objects.filter(
                    purchase=purchase,
                    copy=copy).count() > 0:
                messages.success(
                    request,
                    _("Your gift code has been redeemed."))
            else:
                messages.info(
                    request,
                    _("You own a copy of this book."))

            if purchase.group:
                invite = _create_invite_for_purchase(purchase)

                return redirect(
                    "dwb_join_group",
                    code=invite.code)
            else:
                return redirect(
                    "dwb_overview",
                    book_slug=book.slug)

        # check if already used
        if purchase.claims.count() >= purchase.quantity:
            if purchase.claims.count() > 1:
                messages.error(
                    request,
                    _("Submitted gift code was used maximum number of times."))
            else:
                messages.error(
                    request,
                    _("Submitted gift code was already used."))

            return redirect("dwb_redeem")

    if purchase and copy and request.method == "POST":
        # redeem now
        copy.status = "progress"
        copy.save()

        claim = PurchaseClaim()
        claim.user = request.user
        claim.copy = copy
        claim.purchase = purchase
        claim.save()

        messages.success(
            request,
            _("Your gift code has been redeemed."))

        if purchase.group:
            invite = _create_invite_for_purchase(purchase)

            return redirect(
                "dwb_join_group",
                code=invite.code)

        return redirect(
            "dwb_overview",
            book_slug=book.slug)

    return render(
        request, "webbook/store/redeem.html", {
            "code": code,
            "book": book,
        })


def _create_invite_for_purchase(purchase):
    """Docstring."""
    invite = Invite()
    invite.status = "pending"
    invite.sender_user = purchase.buyer_user
    invite.group = purchase.group
    invite.generate_code()
    invite.save()

    return invite
