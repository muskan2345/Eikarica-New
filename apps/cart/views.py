from django.core.mail.message import EmailMessage
from apps.order.models import Order
import razorpay 
import ast

from django.conf import settings
from django.contrib import messages
from django.shortcuts import render, redirect

from .cart import Cart
from .forms import CheckoutForm

from apps.order.utilities import checkout, notify_customer, notify_vendor
from apps.vendor.models import Vendor, Customer

def cart_detail(request):
    try:
        if request.user.customer:
            cart = Cart(request)
    except:
        if request.user.vendor:
            cart = Cart(request)

    remove_from_cart = request.GET.get('remove_from_cart', '')
    change_quantity = request.GET.get('change_quantity', '')
    quantity = request.GET.get('quantity', 0)

    if remove_from_cart:
        cart.remove(remove_from_cart)

        return redirect('cart')
    
    if change_quantity:
        cart.add(change_quantity, quantity, True)

        return redirect('cart')

    return render(request, 'cart/cart.html')

def success(request, order):
    cart = Cart(request)
    order=ast.literal_eval(order)
    first_name = order['first_name']
    last_name = order['last_name']
    email = order['email']
    phone = order['phone']
    address = order['address']
    zipcode = order['zipcode']
    place = order['place']
    amount = order['amount']

    # order = checkout(request, first_name, last_name, email, address, zipcode, place, phone, amount)
    response = request.POST
    params_dict = {
        'razorpay_order_id': response['razorpay_order_id'],
        'razorpay_payment_id': response['razorpay_payment_id'],
        'razorpay_signature': response['razorpay_signature']
    }

    client = razorpay.Client(auth=(('rzp_live_HGmBto0xC8WCRv','8TBgcTbNtQGj5sKZxLlvzJ7g')))
    
    try:
        status = client.utility.verify_payment_signature(params_dict)
        order = checkout(request, first_name, last_name, email, address, zipcode, place, phone, amount)
        cart.clear()
        notify_customer(order)
        notify_vendor(order)
        return render(request, 'cart/success.html', {'status':True})
    except:
        return render(request, 'cart/success.html', {'status':False})

def payment(request):
    cart = Cart(request)
    if request.method == 'POST':
        form = CheckoutForm(request.POST)

        if form.is_valid():
        
            # try:    # stripe.api_key = settings.STRIPE_SECRET_KEY

            # stripe_token = form.cleaned_data['stripe_token']

            
            # charge = stripe.Charge.create(
            #     amount=int(cart.get_total_cost() * 100),
            #     currency='USD',
            #     description='Charge from Interiorshop',
            #     source=stripe_token
            # )
                amount=int(cart.get_total_cost() * 100)
                client = razorpay.Client(auth=('rzp_live_HGmBto0xC8WCRv','8TBgcTbNtQGj5sKZxLlvzJ7g'))
                response_payment = client.order.create(dict(amount=amount,
                                                        currency='INR'))
                print(response_payment)
                # request.session['first_name'] = form.cleaned_data['first_name']
                # request.session['last_name'] = form.cleaned_data['last_name']
                # request.session['email'] = form.cleaned_data['email']
                # request.session['phone'] = form.cleaned_data['phone']
                # request.session['address'] = form.cleaned_data['address']
                # request.session['zipcode'] = form.cleaned_data['zipcode']
                # request.session['place'] = form.cleaned_data['place']

                first_name = form.cleaned_data['first_name']
                last_name = form.cleaned_data['last_name']
                email = form.cleaned_data['email']
                phone = form.cleaned_data['phone']
                address = form.cleaned_data['address']
                zipcode = form.cleaned_data['zipcode']
                place = form.cleaned_data['place']

                checkoutdict = dict(first_name=first_name,
                                    last_name=last_name,
                                    email=email,
                                    address=address,
                                    zipcode=zipcode,
                                    place=place,
                                    phone=phone,
                                    amount=amount/100)

                # order = checkout(request, first_name, last_name, email, address, zipcode, place, phone, cart.get_total_cost())
                
                # response_payment['first_name']=first_name

                return render(request, 'cart/razorpay_payment.html', {'payment': response_payment, 'order':checkoutdict})
            # except Exception:
            #     messages.error(request, 'There was something wrong with the payment')
    return render(request, 'cart/cart.html')
