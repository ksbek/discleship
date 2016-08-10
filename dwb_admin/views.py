from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import permission_required
from django.contrib.auth.models import User
from django.contrib.flatpages.models import FlatPage
from django.shortcuts import (
    render,
    redirect,
    get_object_or_404,
    )
from django.utils.translation import ugettext as _

from dwb_admin.forms import (
    GiftPurchaseForm,
    PurchaseForm,
    FlatpageForm,
    )
from dwb_book.models import Book
from dwb_store.models import Purchase
from dwb_store.service import send_gift_code
from dwb_user.models import Message, DeliveredMessage


@staff_member_required
def admin_home(request):
    """Docstring."""
    books = Book.objects.all()

    error_msg = ""

    if request.method == "POST":
        text = request.POST.get("message", "")

        if text and len(text) < 255:
            # --- Create new Message
            message = Message.objects.create(
                user=request.user,
                text=text)

            # --- Retrieve User(s)
            users = User.objects.filter(
                is_active=True
            )

            # --- Populate newly created Message among Users
            for user in users:
                try:
                    DeliveredMessage.objects.create(
                        user=user,
                        message=message,
                    )
                except:
                    # --- Fail silently
                    pass
        else:
            error_msg = "Message is too long. Maximum 255 Characters..."

    return render(
        request, "dwb_admin/admin_home.html", {
            "books":        books,
            "error_msg":    error_msg,
        })


@staff_member_required
@permission_required("dwb_store.change_purchase")
def admin_book_purchases(request, book_id):
    """Docstring."""
    book = get_object_or_404(
        Book,
        pk=book_id)

    list = Purchase.objects.filter(
        book=book,
        status="payed"
        ).order_by("-date")

    return render(
        request, "dwb_admin/admin_purchase_list.html", {
            "book":         book,
            "purchases":    list,
        })


@staff_member_required
@permission_required("dwb_store.add_purchase")
def admin_add_purchase(request):
    """Docstring."""
    if request.method == "POST":
        purchase = Purchase()
        purchase.buyer_user = request.user
        purchase.generate_gift_code()
        purchase.price = 0
        purchase.total_charge = 0
        purchase.status = "payed"

        form = GiftPurchaseForm(
            instance=purchase,
            data=request.POST)

        if form.is_valid():
            form.save()

            return redirect(
                "admin-book-purchases",
                book_id=purchase.book.id)
    else:
        form = GiftPurchaseForm()

    return render(
        request, "dwb_admin/admin_purchase_add.html", {
            "form":     form,
        })


@staff_member_required
@permission_required("dwb_store.change_purchase")
def admin_purchase(request, purchase_id):
    """Docstring."""
    purchase = get_object_or_404(
        Purchase,
        pk=purchase_id)

    if request.method == "POST":
        form = PurchaseForm(
            instance=purchase,
            data=request.POST)

        if form.is_valid():
            form.save()

            if purchase.recipient_email:
                send_gift_code(request, purchase)

            return redirect(
                "admin-book-purchases",
                book_id=purchase.book.id)
    else:
        form = PurchaseForm(
            instance=purchase)

    return render(
        request, "dwb_admin/admin_purchase.html", {
            "purchase": purchase,
            "form":     form,
        })


@staff_member_required
@permission_required("flatpages.change_flatpage")
def admin_edit_flatpage(request, page_id):
    """Docstring."""
    flatpage = get_object_or_404(
        FlatPage,
        pk=page_id)

    if request.method == "POST":
        form = FlatpageForm(
            instance=flatpage,
            data=request.POST)

        if form.is_valid():
            form.save()

            return redirect("admin-home")
    else:
        form = FlatpageForm(
            instance=flatpage)

    return render(
        request, "dwb_admin/admin_flatpage.html", {
            "flatpage":     flatpage,
            "form":         form,
        })
