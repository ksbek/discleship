from datetime import date, datetime

import json
import random

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth.tokens import (
    default_token_generator as token_generator
    )
from django.contrib.auth.views import auth_login, logout
from django.core.mail import send_mail, EmailMultiAlternatives
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect, Http404
from django.http.response import HttpResponse, HttpResponseBadRequest
from django.shortcuts import (
    get_object_or_404,
    redirect,
    render,
    render_to_response,
    )
from django.template.loader import render_to_string
from django.utils.http import int_to_base36, base36_to_int
from django.utils.translation import ugettext as _

from dwb_book.models import Book, Copy
from dwb_store.models import Purchase, PurchaseClaim, User
from dwb_user.forms import (
    LoginForm,
    RegisterForm,
    ProfileForm,
    ProfileInfoForm,
    ResetPasswordForm,
    )
from dwb_user.models import Profile, DeliveredMessage
from dwb_user.services import authenticate


def account_login(request):
    """Docstring."""
    if request.GET.get("next"):
        request.session["redirect_after_login"] = request.GET.get("next")

    login_form = LoginForm(
        request.POST or None, request.FILES or None)

    if request.method == "POST":
        if not request.POST.get("remember_me", None):
            request.session.set_expiry(0)

        redirect_after_login = request.session.get("redirect_after_login")

        if login_form.is_valid():
            user = login_form.cleaned_data["user"]

            login(request, user)

            if redirect_after_login:
                request.session["redirect_after_login"] = None

                return redirect(
                    request.build_absolute_uri(redirect_after_login)
                    )
            else:
                return redirect("my-account")

    return render(
        request, "dwb_user/login.html", {
            "login_form":       login_form,
            "register_form":    RegisterForm(),
        })


def account_register(request):
    """Docstring."""
    register_form = RegisterForm(
        request.POST or None, request.FILES or None)

    if request.method == "POST":
        if register_form.is_valid():
            # register user
            user = User()
            user.username = "user-%d" % (random.randint(0, 1000*1000*1000),)
            user.email = register_form.cleaned_data["email"]
            user.first_name = register_form.cleaned_data["first_name"]
            user.last_name = register_form.cleaned_data["last_name"]
            user.set_password(register_form.cleaned_data["password"])
            user.last_login = datetime.now()
            user.save()

            user_profile = Profile()
            user_profile.user = user
            user_profile.is_pastor = register_form.cleaned_data["is_pastor"]
            user_profile.church_name = register_form.cleaned_data[
                "church_name"]
            user_profile.save()

            # login
            user.backend = "django.contrib.auth.backends.ModelBackend"
            login(request, user)

            # redirect
            return redirect("my-account")

    return render(
        request, "dwb_user/login.html", {
            "login_form":       LoginForm(),
            "register_form":    register_form,
        })


def account_logout(request):
    """Docstring."""
    logout(request)

    return redirect("index")


def forgot_password(request):
    """Forgot Password."""
    if request.method == "POST":
        user = get_object_or_404(
            User,
            email=request.POST.get("email", ""),
            )

        try:
            uidb36 = int_to_base36(user.id)
            token = token_generator.make_token(user)

            DOMAIN_NAME = request.get_host()
            url = reverse(
                "renew-password", kwargs={
                    "uidb36":   uidb36,
                    "token":    token,
                })
            reset_link = "http://{domain}{url}".format(
                domain=DOMAIN_NAME,
                url=url,
                )

            # -----------------------------------------------------------------
            # --- Send templated Email
            from_email = settings.DEFAULT_FROM_EMAIL
            headers = {
                "Reply-To": settings.DEFAULT_FROM_EMAIL,
            }
            subj_content = "Password Reset Request"
            text_content = render_to_string(
                "dwb_user/emails/forgot_password.txt",
                {
                    "site_name":    "Discipleship Workbooks",
                    "reset_link":   reset_link,
                },
            )

            mail = EmailMultiAlternatives(
                subject=subj_content,
                body=text_content,
                from_email=from_email,
                to=[
                    user.email,
                ],
                cc=[],
                bcc=[],
                headers=headers,
            )
            mail.send()

            messages.success(
                request,
                _("Email has been sent successfully."))

            return redirect("my-account")

        except Exception as e:
            print ">>> EXCEPTION >>>", str(e)

    return render(
        request, "dwb_user/registration/password_forgot_form.html", {})


def renew_password(request, uidb36=None, token=None):
    """Renew Password."""
    assert uidb36 is not None and token is not None

    try:
        uid_int = base36_to_int(uidb36)
        user = User.objects.get(
            id=uid_int,
            )
    except (ValueError, User.DoesNotExist):
        user = None

    if user is not None and token_generator.check_token(user, token):
        # ---------------------------------------------------------------------
        # --- Instant log-in after confirmation
        user.backend = "django.contrib.auth.backends.ModelBackend"
        #auth_login(request, user)
        login(request, user)

        return HttpResponseRedirect(
            reverse("reset-password"))
    else:
        messages.error(
            request,
            _("An error has occurred within processing your Request."))

        return redirect("my-account")


@login_required
def reset_password(request):
    """Reset Password."""
    form = ResetPasswordForm(
        request.POST or None)

    if request.method == "POST":
        if form.is_valid():
            request.user.set_password(form.cleaned_data["password"])
            request.user.save()

            messages.success(
                request,
                _("Your Password has been reset successfully."))

            return redirect("my-account")

    return render(
        request, "dwb_user/registration/password_reset_form.html", {
            "form":     form,
        })


@login_required
def edit_profile(request):
    """Docstring."""
    user = request.user
    profile, created = Profile.objects.get_or_create(
        user=user)

    form = ProfileForm(
        request.POST or None, request.FILES or None,
        instance=user)
    infoform = ProfileInfoForm(
        request.POST or None, request.FILES or None,
        instance=profile)

    if request.method == "POST":
        if form.is_valid():
            form.save()
            infoform.save()

            return redirect("my-account")

    return render(
        request, "dwb_user/edit_profile.html", {
            "form":     form,
            "infoform": infoform
        })


@login_required
def my_account(request):
    """Docstring."""
    my_copies = Copy.objects.filter(
        user=request.user,
        book__language=request.LANGUAGE_CODE,)

    all_books = Book.objects.filter(
        status="active",
        language=request.LANGUAGE_CODE,
    ).order_by("-date_available")

    my_books = [c.book for c in my_copies]

    # --- Retrieve unread Messages
    my_messages = DeliveredMessage.objects.filter(
        user=request.user,
        is_read=False,
    )

    return render(
        request, "dwb_user/my_account.html", {
            "my_copies":    my_copies,
            "my_books":     my_books,
            "other_books":  [b for b in all_books if b not in my_books],
            "my_messages":  my_messages,
        })


@login_required
def order_history(request):
    """Docstring."""
    user = request.user
    orders = Purchase.objects.filter(
        buyer_user=user.id,
        status="payed"
    ).select_related().order_by("-date")
    claims = PurchaseClaim.objects.filter().select_related()

    return render(
        request, "dwb_user/order_history.html", {
            "orders":   orders,
            "claims":   claims,
        })


@login_required
def email_list(request):
    """Docstring."""
    users = User.objects.filter().select_related()

    return render(
        request, "dwb_user/email_list.html", {
            "users":    users,
        })


@login_required
def send_claim_code(request):
    """Docstring."""
    user = request.user
    to_email = request.POST.get("recipient-email")
    subject = _("Gift code from DiscipleshipWorkbooks")

    text_body = request.POST.get("message")

    send_mail(
        subject,
        text_body,
        user.email,
        [to_email]
    )

    return HttpResponse(
        json.dumps({
            "success":  "Message was sent."
        })
    )
