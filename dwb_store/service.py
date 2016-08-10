
from django.conf import settings
from django.core.mail import send_mail
from django.core.urlresolvers import reverse
from django.template.loader import render_to_string
from django.utils.translation import ugettext as _

import paypalrestsdk

from dwb_store.models import Purchase


def create_purchase(request, book, quantity, is_gift, is_priest):
    """Create a purchase object and URL to redirect to.

    Book status is not checked. It must be checked before calling this
    function.
    """
    p = Purchase()
    p.status = "pending"
    p.book = book
    p.quantity = quantity

    if is_priest:
        p.price = book.priest_price
    else:
        p.price = book.get_price_for_quantity(quantity)

    p.total_charge = p.price * p.quantity

    if is_gift:
        p.generate_gift_code()

    if request.user.is_authenticated():
        p.buyer_user = request.user
        p.buyer_email = request.user.email

    p.save()

    return p


def start_purchase(request, purchase):
    """Docstring."""
    return_url = request.build_absolute_uri(
        reverse("dwb_purchase_confirm", kwargs={
            "invoice_number":   purchase.invoice_number
        }))
    cancel_url = request.build_absolute_uri(
        reverse("dwb_purchase_cancel", kwargs={
            "invoice_number":   purchase.invoice_number
        }))

    if purchase.total_charge >= 0.01:
        resp = create_payment(purchase, return_url, cancel_url)

        return resp["approval_url"]
    else:
        return return_url


def send_gift_code(request, purchase):
    """Docstring."""
    if not purchase.gift_code:
        raise Exception(
            _("Gift code is missing."))

    if not purchase.recipient_email:
        raise Exception(
            _("Recipient's email address is missing"))

    to_email = purchase.recipient_email
    subject = _("Gift code to ") + purchase.book.title

    redeem_url = request.build_absolute_uri(
        reverse("dwb_redeem") + "?code=" + purchase.gift_code)
    template_data = {
        "purchase":     purchase,
        "redeem_url":   redeem_url
    }
    text_body = render_to_string("webbook/email/gift_code.txt", template_data)

    send_mail(
        subject,
        text_body,
        settings.DEFAULT_FROM_EMAIL,
        [to_email],
        fail_silently=False)


def send_invoice(request, purchase, to_email=None):
    """Docstring."""
    if to_email is None:
        to_email = purchase.buyer_email

    if to_email is None:
        raise Exception(
            _("Buyer's email address is not available."))

    subject = _("Invoice for ") + purchase.book.title

    if purchase.gift_code:
        redeem_url = request.build_absolute_uri(
            reverse("dwb_redeem") + "?code=" + purchase.gift_code)
    else:
        redeem_url = None

    template_data = {
        "purchase":     purchase,
        "redeem_url":   redeem_url
    }
    text_body = render_to_string("webbook/email/invoice.txt", template_data)

    send_mail(
        subject,
        text_body,
        settings.DEFAULT_FROM_EMAIL,
        [to_email],
        fail_silently=False)


def get_paypal_api():
    """Docstring."""
    return paypalrestsdk.Api(settings.PAYPAL)


def create_payment(purchase, return_url=None, cancel_url=None):
    """Docstring."""
    item = {
        "name":         purchase.book.title,
        "price":        str(purchase.price),
        "currency":     "USD",
        "quantity":     purchase.quantity,
    }
    transaction = {
        "item_list": {
            "items":    [item]
        },
        "amount": {
            "total":    str(purchase.total_charge),
            "currency": "USD",
        },
    }
    payment_data = {
        "intent":       "sale",
        "payer": {
            "payment_method":   "paypal"
        },
        "redirect_urls": {
            "return_url":   return_url,
            "cancel_url":   cancel_url,
        },
        "transactions": [transaction],
    }

    paypal_api = get_paypal_api()
    paypal_payment = paypalrestsdk.Payment(payment_data, api=paypal_api)

    ok = paypal_payment.create()
    if ok:
        # update purchase object
        purchase.add_api_log(paypal_payment.to_dict())

        for (key, value) in paypal_payment.to_dict().items():
            purchase.set_api_data(key, value)

        purchase.save()

        # return info
        response = {}
        response["id"] = paypal_payment.id

        for link in paypal_payment["links"]:
            response[link["rel"]] = link["href"]

        return response
    else:
        raise Exception(paypal_payment.error)


def confirm_payment(purchase, args):
    """Docstring."""
    paypal_api = get_paypal_api()

    # check if total is correct
    paypal_payment = paypalrestsdk.Payment.find(
        purchase.get_api_data("id"), api=paypal_api)

    # make sure total amount is the same
    paypal_total = float(paypal_payment["transactions"][0]["amount"]["total"])
    purchase_total = float(purchase.total_charge)

    if abs(paypal_total - purchase_total) > 0.01:
        raise Exception(
            _("Total charge does not match."))

    ok = paypal_payment.execute({
        "payer_id":     args.get("PayerID")
    })

    if ok:
        # update purchase object
        purchase.add_api_log(paypal_payment.to_dict())

        for (key, value) in paypal_payment.to_dict().items():
            purchase.set_api_data(key, value)

        purchase.save()

        # return info
        payer_info = purchase.get_api_data("payer")["payer_info"]
        response = {}
        response["billing_email"] = payer_info["email"]
        response["billing_name"] = "%s %s" % (
            payer_info["first_name"],
            payer_info["last_name"])

        return response
    else:
        raise Exception(paypal_payment.error)

    # charge now
    return True
