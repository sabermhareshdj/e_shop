from sqlite3 import IntegrityError
from django.shortcuts import redirect, render, get_object_or_404
from django.urls import reverse_lazy
from .models import Customer, Product
from django import forms    
from django.contrib.auth.models import User,auth
from django.contrib.auth.views import LoginView,LogoutView
from django.contrib.auth.forms import AuthenticationForm
from django.db.models import F


from django.contrib.auth import authenticate, login,logout
from .models import SessionCart, ItemCart,Product
import stripe
from django.conf import settings
# Create your views here.


def index(request):
    product = Product.get_products()
    return render(request, "index.html",{"products":product})


def cart_page(request):
    user = request.user
    total = 0
    items = ItemCart.objects.filter(user=request.user)
    for item in items:
        total += item.total_cart_value

        # item.product_name = item.product.name
    return render(request, "cart_page.html",{'items': items,'total': total})

class NewForm(forms.Form):
    name = forms.CharField(min_length=4, max_length=40,widget=forms.TextInput(attrs={'name': "name",'type': "text", 'class': "form-control", 'id': "inputName4"}))
    password = forms.CharField(min_length=4, max_length=12,widget=forms.TextInput(attrs={'name': "password", 'type': "password", 'class': 'form-control', 'id': "inputPassword4"}))
    email = forms.CharField(max_length=40,widget=forms.TextInput(attrs={'type': "email", 'type': "email", 'class': 'form-control', 'id': "inputEmail4"}))
    address = forms.CharField(max_length=300,widget=forms.TextInput(attrs={'type': "text", 'class': 'form-control', 'id': "inputAddress4", 'placeholder': "1234 Main St"}))
    city = forms.CharField(max_length=30,widget=forms.TextInput(attrs={'type': "text", 'class': 'form-control', 'id': "inputCity4"}))
    zip = forms.IntegerField(widget=forms.NumberInput(attrs={'type': "number", 'class': 'form-control', 'id': "inputZip4"}))

def sign_up(request):
    # إذا كان الطلب POST، يعني المستخدم أرسل البيانات
    if request.method == "POST":
        form = NewForm(request.POST)
        print(form.is_valid())
        if form.is_valid():
            name = form.cleaned_data["name"]
            email = form.cleaned_data["email"]
            password = form.cleaned_data["password"]

            try:
                user = User.objects.create_user(username=name, email=email, password=password)
            except IntegrityError:
                # اسم المستخدم موجود مسبقاً
                form.add_error('name', 'اسم المستخدم مستخدم بالفعل.')
                return render(request, "signup_form.html", {'form': form})

            Customer.objects.create(
                name=name,
                email=email,
                address=form.cleaned_data["address"],
                city=form.cleaned_data["city"],
                zip=form.cleaned_data["zip"]
            )
            return redirect(index)  # تأكد أن لديك url بهذا الاسم
        # لو فيه أخطاء نرجّع نفس الصفحة مع الأخطاء
        return redirect('index')
    else:
        form = NewForm()
    return render(request, "signup_form.html", {'form': NewForm})


class Loginuse(LoginView):
    def __init__(self):
        self.form = NewForm()

    def get(self, request):

        return render(request, 'login.html', {'form': self.form})
    
    def post(self, request):
        form = NewForm(request.POST)
        form.is_valid()
        username = form.cleaned_data["name"]
        password = form.cleaned_data["password"]
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('index')
        else:
            return render(request, 'login.html', {'form': self.form})


class LogOut(LogoutView):
    next_page = 'index'


def _cart_id(request):
    cart = request.session.session_key

    try:
        session = SessionCart.objects.get(user=request.user)
        return session.spc_id

    except SessionCart.DoesNotExist:
        cart = request.session.create()
        session = SessionCart(spc_id=request.session.session_key,user=request.user)
        session.save()
        
        return session.spc_id
    
def add_to_cart(request, product):
    product = Product.objects.get(slug=product)
    user = request.user.get_username()

    try:
        cart = SessionCart.objects.get(spc_id=_cart_id(request))
  
    except SessionCart.DoesNotExist:
        cart = SessionCart.objects.create(
            spc_id=_cart_id(request), user=user)
        cart.save()
    try:
        cart_items = ItemCart.objects.get(
            slug=product.slug,
            product=product.name, 
            cart=cart,
            user=user
        )

        cart_items.product_quantity += 1
        cart_items.total_cart_value += product.price
        cart_items.save()
        print(request.path)
        if request.path == f'/cart/add/{product.slug}':
            return redirect('cart')
    except ItemCart.DoesNotExist:
        cart_items = ItemCart.objects.create(slug=product.slug,user=user,
                                              active=True, product=product.name,
                                              cart=cart,product_quantity=1,
                                              product_price=product.price, 
                                              product_image=product.product_image,
                                              total_cart_value=product.price)
        cart_items.save()
    return redirect('index')

def payment_with_stripe(request):
    
    stripe.api_key = settings.STRIPE_SECRET_KEY

    li = []

    items = ItemCart.objects.filter(user=request.user).values()
    for item in items.values():
        new_data = {
            'price_data': {
                'currency': 'usd',
                'product_data': {
                    'name': item.get('product'),
                },
                'unit_amount': item.get('product_price') * 100
            },
            'quantity': item.get('product_quantity'),
        }

        li.append(new_data)

    session = stripe.checkout.Session.create(
        line_items=[*li],
        mode='payment',
        success_url='https://e-shop-application-t24l.onrender.com/payment/success',
        cancel_url='https://e-shop-application-t24l.onrender.com/payment_fail/cancel',
    )

    return redirect(session.url, code=303)

def success(request):
    return render(request, "success.html")


def remove_cart_obj(request, product):
    cart = SessionCart.objects.get(spc_id=_cart_id(request),user=request.user)
    product= get_object_or_404(Product, slug=product)
    cart_item =ItemCart.objects.get(product=product,cart=cart)
    if cart_item.product_quantity > 1:
        cart_item.product_quantity = F('product_quantity') - 1
        cart_item.total_cart_value = F('total_cart_value') - F('product_price')
        cart_item.save()
        return redirect('cart')
    else:
        # إذا كان الكمية 1، نحذف العنصر من السلة
        cart_item.delete()
        return redirect('cart')

