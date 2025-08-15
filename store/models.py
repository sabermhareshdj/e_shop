from django.db import models
from cloudinary.models import CloudinaryField


# Create your models here.
class Category(models.Model):
    slug = models.SlugField(max_length=250, unique=True,default='slug')
    name = models.CharField(max_length=60)

    def __str__(self):
        return self.name


class Product(models.Model):
    name = models.CharField(max_length=60,unique=True)
    slug = models.SlugField(max_length=250, unique=True,default='slug')
    price = models.IntegerField(default=0)
    category = models.ForeignKey(Category, on_delete=models.CASCADE,default=1)
    description = models.CharField(max_length=2000,default=' ')
    product_image = CloudinaryField('image')
    quantity = models.IntegerField(default=0)

    @staticmethod
    def get_products():
        return Product.objects.all()
    

    def __str__(self):
        return self.name

class Customer(models.Model):
    name = models.CharField(max_length=40)
    email = models.CharField(max_length=40,unique=True)
    password = models.CharField(max_length=12)
    address = models.CharField(max_length=300)
    city = models.CharField(max_length=30)
    zip = models.IntegerField(default=0)

    def __str__(self):
        return self.name

class SessionCart(models.Model):
    spc_id = models.CharField(max_length=100)
    user = models.CharField(max_length=40)

    def __str__(self):
        return f'{self.spc_id}'


class ItemCart(models.Model):
    user = models.CharField(max_length=40)
    cart = models.ForeignKey(SessionCart, on_delete=models.CASCADE)
    active = models.BooleanField(default=False)
    product = models.CharField(max_length=40)
    product_quantity = models.IntegerField(default=0)
    product_price = models.IntegerField(default=0)
    total_cart_value = models.IntegerField(default=0)
    product_image = CloudinaryField('image')
    slug = models.CharField(max_length=40,default=None)
    

 