from django.contrib import admin
from django.urls import path
from store.views import (index,
                         cart_page, 
                         sign_up, 
                         Loginuse,LogOut,
                         add_to_cart,
                         payment_with_stripe,
                         success,
                         remove_cart_obj)
from django.contrib.auth.views import LogoutView

urlpatterns = [
    path('', index, name='index'),
    path("cart", cart_page, name="cart"),
    path("signup", sign_up, name="signup"),
    path("login", Loginuse.as_view(), name="login_use"),
    path("logout/", LogOut.as_view(), name="logout_use"),
    path('<slug:product>', add_to_cart, name='create_cart'),
    path('cart/create-checkout-session', payment_with_stripe, name='stripe_payment'),
    path('payment/success',success,name='success'),
    path('cart/add/<slug:product>', add_to_cart, name='add_cart'),
    path('remove/<slug:product>', remove_cart_obj, name='remove_from_cart'),

]