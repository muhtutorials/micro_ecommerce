from django.urls import path

from .views import product_create, product_list, product_detail, product_attachment_download, product_update

urlpatterns = [
    path('create/', product_create, name='product_create'),
    path('', product_list, name='product_list'),
    path('<slug:handle>/', product_detail, name='product_detail'),
    path('<slug:handle>/update', product_update, name='product_update'),
    path('<slug:handle>/download/<int:pk>', product_attachment_download, name='product_attachment_download'),
]
