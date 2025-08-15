from django.contrib import admin
from .models import Category, Product, Customer, SessionCart,ItemCart

admin.site.register(Category)
admin.site.register(Product)
admin.site.register(Customer)
admin.site.register(SessionCart)    
admin.site.register(ItemCart)

