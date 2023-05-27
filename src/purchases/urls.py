from django.urls import path

from .views import purchase_page, purchase_success, purchase_cancel

urlpatterns = [
    path('', purchase_page, name='purchase_page'),
    path('success/', purchase_success, name='purchase_success'),
    path('cancel/', purchase_cancel, name='purchase_cancel'),
]
