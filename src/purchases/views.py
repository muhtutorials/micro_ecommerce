from django.shortcuts import render
from django.http import HttpResponseBadRequest, HttpResponse, HttpResponseRedirect
from django.urls import reverse
import stripe

from home.env import config
from products.models import Product
from purchases.models import Purchase

STRIPE_SECRET_KEY = config('STRIPE_SECRET_KEY')
stripe.api_key = STRIPE_SECRET_KEY

BASE_ENDPOINT = 'http://127.0.0.1:8000'


def purchase_page(request):
    if not request.method == 'POST' or not request.user.is_authenticated:
        return HttpResponseBadRequest()
    handle = request.POST.get('handle')
    product = Product.objects.get(handle=handle)
    stripe_price_id = product.stripe_price_id
    if stripe_price_id is None:
        return HttpResponseBadRequest()

    success_url = f'{BASE_ENDPOINT}/purchases/success'
    cancel_url = f'{BASE_ENDPOINT}/purchases/cancel'
    checkout_session = stripe.checkout.Session.create(
        line_items=[
            {
                'price': stripe_price_id,
                'quantity': 1
            }
        ],
        mode='payment',
        success_url=success_url,
        cancel_url=cancel_url,
        payment_method_types=['card']
    )
    purchase = Purchase.objects.create(
        user=request.user,
        product=product,
        stripe_checkout_session_id=checkout_session.id
    )
    request.session['purchase_id'] = purchase.id
    return HttpResponseRedirect(checkout_session.url)


def purchase_success(request):
    purchase_id = request.session.get('purchase_id')
    if purchase_id:
        purchase = Purchase.objects.get(id=purchase_id)
        purchase.completed = True
        purchase.save()
        del request.session['purchase_id']
        return HttpResponseRedirect(purchase.product.get_absolute_url())
    return HttpResponse('success')


def purchase_cancel(request):
    purchase_id = request.session.get('purchase_id')
    if purchase_id:
        purchase = Purchase.objects.get(id=purchase_id)
        del request.session['purchase_id']
        return HttpResponseRedirect(purchase.product.get_absolute_url())
    return HttpResponse('cancel')
