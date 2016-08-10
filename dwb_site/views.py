from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.http import (
    HttpResponse,
    HttpResponseRedirect,
    Http404
    )
from django.shortcuts import (
    render,
    redirect,
    get_object_or_404,
    )
from django.utils.translation import ugettext as _
from django.views.decorators.csrf import csrf_exempt

from dwb_book.models import Book, Copy
from dwb_group.forms import InviteForm
from dwb_group.models import (
    Group,
    Member,
    Invite,
    )
from dwb_store.service import create_purchase, start_purchase
from dwb_user.models import DeliveredMessage


def index(request):
    """Docstring."""
    all_books = Book.objects.filter(
        Q(status="active") |
        Q(status="draft"),
        language=request.LANGUAGE_CODE,
    ).order_by("-sort_order")

    if request.user.is_authenticated():
        my_copies = Copy.objects.filter(
            user=request.user.id)
        purchased_books = [c.book for c in my_copies if c.status != "preview"]
    else:
        my_copies = []
        purchased_books = []

    if request.user.is_authenticated():
        return redirect("my-account")
    else:
        return render(
            request, "dwb_site/index.html", {
                "purchased_books":  purchased_books,
                "all_books":        all_books,
            })


# -----------------------------------------------------------------------------
# --- AJAX
# -----------------------------------------------------------------------------
@csrf_exempt
@login_required
def ajax_mark_delivered_message_read(request):
    """Docstring."""
    if request.is_ajax():
        message_id = request.POST.get("message_id", "")

        # --- Retrieve Message
        msg = get_object_or_404(
            DeliveredMessage,
            id=message_id,
        )

        msg.is_read = True
        msg.save()

        return HttpResponse()

    return HttpResponse(status=404)
