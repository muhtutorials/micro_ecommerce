import stripe

from home.env import config

STRIPE_SECRET_KEY = config('STRIPE_SECRET_KEY')
stripe.api_key = STRIPE_SECRET_KEY


def product_sale_pipeline(name, price):
    stripe_product = stripe.Product.create(name=name)
    stripe_product_id = stripe_product.id
    stripe_price = stripe.Price.create(product=stripe_product_id, unit_amount=price, currency='usd')
    stripe_price_id = stripe_price.id

    base_endpoint = 'http://127.0.0.1:8000'
    success_url = f'{base_endpoint}/purchases/success'
    cancel_url = f'{base_endpoint}/purchases/cancel'
    checkout_session = stripe.checkout.Session.create(
        line_items=[
            {
                'price': stripe_price_id,
                'quantity': 1
            }
        ],
        mode='payment',
        success_url=success_url,
        cancel_url=cancel_url
    )
