from django.urls import path
from .import views
urlpatterns= [
    path('add', views.cart, name='cart_add'),
    path('delete', views.cart_delete, name='cart_delete'),
    path('update', views.cart_update, name='cart_update'),
    path('cart-overview', views.cart_overview, name='cart-overview'),
    path('create-order', views.create_order, name='create_order'),
    path('payment-success', views.payment_success, name='payment_success'),
]