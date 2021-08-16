from django.contrib.auth import get_user_model, login, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm, UserCreationForm
from django.utils.text import slugify
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth import authenticate, login, logout
from .models import Vendor,Customer
from apps.product.models import Product, ProductImage,Category
from django.contrib.auth.models import User
from django.contrib import messages
from django.core.mail import EmailMessage
from .forms import ProductForm, ProductImageForm
from django.views.generic import View
from django.urls import reverse
from .utils import token_generator
from django.utils.encoding import force_bytes,force_text,DjangoUnicodeDecodeError
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string

# from apps.product.models import Product

# def frontpage(request):
#     newest_products = Product.objects.all()[0:8]

#     return render(request, 'core/frontpage.html', {'newest_products': newest_products})

def confirm(request):
    return redirect('vendor_kyc')



def user_login(request,*args,**kwargs):
    
    if request.method == 'POST':
        # First get the username and password supplied
        username = request.POST.get('username')
        password = request.POST.get('password')
        loginid = request.POST.get('loginid')

        User = get_user_model()
        print(User)
        try:
            user = User.objects.get(username=username)
            print(user)
        except(TypeError, ValueError, OverflowError, User.DoesNotExist):
            messages.error(request,'username or password not correct')
            return redirect('user_login')
        if user is not None:
            if(user.is_active==False):
                messages.error(request,'Your account is not active, verify your email!')
                return redirect('user_login')

        # Django's built-in authentication function:
        user = authenticate(username=username, password=password)
        print(request.user)
        # If we have a user
        if loginid == "vendor":
            if user:
            #     #Check it the account is active
            #     if request.user.is_active:
            #         # Log the user in.

                    login(request,user)
                    try:
                        request.user.vendor
                    except:
                        messages.error(request,'You are not a valid vendor!')
                        return redirect('user_logout')
                    # if(vendor.verified==True):
                    #     return redirect('vendor_admin')
                    return redirect('vendor_admin')
                    # Send the user back to some page.
                    # In this case their homepage.
                    #return HttpResponseRedirect(reverse('core/frontpage.html'))
                # else:
                    # If account is not active:
                    # return HttpResponse("Your account is not active.")
            else:
                messages.error(request,'username or password not correct')
                return redirect('user_login')
        else:
            #return redirect('coming_soon')
            if user:
            #     #Check it the account is active
            #     if user.is_active:
                    # Log the user in.
                    login(request,user)
                    try:
                        request.user.customer
                    except:
                        messages.error(request,'You are not a valid customer!')
                        return redirect('user_logout')
                    # Send the user back to some page.
                    # In this case their homepage.
                    return redirect('frontpage')
                    #return HttpResponseRedirect(reverse('core/frontpage.html'))
                # else:
                #     # If account is not active:
                #     return HttpResponse("Your account is not active.")
            else:
                messages.error(request,'username or password not correct')
                return redirect('user_login')


    else:
        #Nothing has been provided for username or password.
        return render(request, 'vendor/login.html', {})

def become_vendor(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        loginid = request.POST.get('loginid')
        # password2 = request.POST.get('confirm_password')
        name = request.POST.get('username')
        try:
            User.objects.get(username=name)
            messages.error(request,'Username is already taken')
            return redirect('become_vendor')
        except:
            try:
                User.objects.get(email=email)
                messages.error(request,'Email is already taken')
                return redirect('become_vendor')
                # return render(request, 'vendor/login.html#sign-up', {})
            except:
                if loginid == "vendor":
                    # raw_password = password1
                    user = User.objects.create_user(name, email, password)
                    uidb64=urlsafe_base64_encode(force_bytes(user.pk))
                    # domain=get_current_site(request).domain
                    domain='www.eikarica.techmihirnaik.in'
                    link=reverse('activate',kwargs={'uidb64':uidb64,'token': token_generator.make_token(user)})
                    email_subject='Signed up successfully'
                    activate_url='https://'+ domain+ link
                    email_body= "Hii " + name + "\nPlease use this link to verify your account\n" + activate_url
                    user.is_active = False
                    user.save()
                    vendor = Vendor(name=name, email=email, password=password, created_by=user)
                    # current_site = get_current_site(request)
                    # email_body = render_to_string('vendor/email_template.html')
                    email=EmailMessage (
                       email_subject,
                       email_body,
                       'eikaricatmn@gmail.com',
                       [email],
                    )
                    email.send(fail_silently=False)
                    # if User.objects.filter(name = name).first():
                    #     messages.error(request, "This username is already taken")
                    #     return HttpResponse("Invalid signup details supplied.")
                    vendor.save()

                    # uidb64=force_bytes(urlsafe_based64_encode(user.pk))
                    # activate_url='http://'+domain+link
                    # email=EmailMessage (
                    #    email_subject,
                    #    email_body,
                    #    'eikaricatmn@gmail.com',
                    #    [email],

                    # )

                    # email.send(fail_silently=False)
                    
                    # if(vendor.verified==True):
                    #     return redirect('add_product')
                    messages.error(request,'Sign-up successful, check your email for further instructions!')
                    return redirect('user_login')
                else:
                    cus= User.objects.create_user(name, email, password)
                    uidb64=urlsafe_base64_encode(force_bytes(cus.pk))
                    # domain=get_current_site(request).domain
                    domain='www.eikarica.techmihirnaik.in'
                    link=reverse('activate',kwargs={'uidb64':uidb64,'token': token_generator.make_token(cus)})
                    email_subject='Signed up successfully'
                    activate_url='https://'+ domain+ link
                    email_body= "Hii " + name + "\nPlease use this link to verify your account\n" + activate_url
                    cus.is_active = False
                    cus.save()
                    customer = Customer(name=name, email=email, password=password, created_by=cus)
                    # current_site = get_current_site(request)
                    # email_body = render_to_string('vendor/email_template.html')
                    email=EmailMessage (
                       email_subject,
                       email_body,
                       'eikaricatmn@gmail.com',
                       [email],
                    )
                    email.send(fail_silently=False)
                    # if User.objects.filter(name = name).first():
                    #     messages.error(request, "This username is already taken")
                    #     return HttpResponse("Invalid signup details supplied.")
                    customer.save()

                    # uidb64=force_bytes(urlsafe_based64_encode(user.pk))
                    # activate_url='http://'+domain+link
                    # email=EmailMessage (
                    #    email_subject,
                    #    email_body,
                    #    'eikaricatmn@gmail.com',
                    #    [email],

                    # )

                    # email.send(fail_silently=False)
                    
                    # if(vendor.verified==True):
                    #     return redirect('add_product')
                    messages.error(request,'Sign-up successful, check your email for further instructions!')
                    return redirect('user_login')
    return render(request, 'vendor/login.html', {})

def coming_soon(request):
    return render(request, 'vendor/coming_soon.html',{})


class VerificationView(View):
    def get(self,request,uidb64,token):
        User = get_user_model()
        try:
            uid = force_text(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)
            print(user)
        except(TypeError, ValueError, OverflowError, User.DoesNotExist):
            user = None
        if user is not None:
            user.is_active = True
            user.save()
            messages.error(request,'Thank you for your email confirmation. Now you can login your account.')
            return redirect('user_login')
        else:
            return HttpResponse('Activation link is invalid!')


@login_required
def vendor_kyc(request):
    vendor=request.user.vendor
    if request.method == 'POST':
        print(request.FILES.get('document'))
        vendor.fullname = request.POST.get('name')
        vendor.gender = request.POST.get('gender')
        vendor.dob = request.POST.get('dob')
        address1 = request.POST.get('address1')
        address2 = request.POST.get('address2')
        address3 = request.POST.get('address3')
        address4 = request.POST.get('address4')
        address5 = request.POST.get('address5')
        vendor.nationality = request.POST.get('nationality')
        vendor.mobile = request.POST.get('phone')
        vendor.idType = request.POST.get('idtype')
        vendor.idFile = request.FILES.get('document')
        vendor.address = address1 + ", " + address2 + ", " + address3 + ", " + address4 + ", " + address5
        vendor.save()
        return redirect('vendor_admin')
    return render(request, 'vendor/vendor_kyc.html', {'vendor':vendor})

@login_required
def user_logout(request):
    # Log out the user.
    logout(request)
    # Return to homepage.
    return redirect('user_login')

@login_required
def vendor_admin(request):
    vendor=request.user.vendor
    products = vendor.products.all()
    orders = vendor.orders.all()

    for order in orders:
        order.vendor_amount = 0
        order.vendor_paid_amount = 0
        order.fully_paid = True

        for item in order.items.all():
            if item.vendor == request.user.vendor:
                if item.vendor_paid:
                    order.vendor_paid_amount += item.get_total_price()
                else:
                    order.vendor_amount += item.get_total_price()
                    order.fully_paid = False

    return render(request, 'vendor/vendor_admin.html', {'vendor': vendor, 'products': products, 'orders': orders})

@login_required
def add_product(request):
    vendor=request.user.vendor
    if(vendor.verified==False):
        return redirect('vendor_admin')
    if request.method == 'POST':
        form = ProductForm(request.POST)
        
        product = form.save(commit=False)
            # product.category= request.POST.get('category')
        product.title= request.POST.get('title')
        product.description= request.POST.get('description')
        product.price= request.POST.get('price')
        product.image=request.FILES.get('image')
        product.vendor = request.user.vendor
        product.quantity = request.POST.get('quantity')
        product.length = request.POST.get('length')
        product.breadth = request.POST.get('breadth')
        product.height = request.POST.get('height')
        product.weight = request.POST.get('weight')

        str=product.title + "-" + product.vendor.name
        product.slug = slugify(str)
        product.save()
        return redirect('vendor_admin')
        
    form = ProductForm()
    return render(request, 'vendor/add_product.html',{'form':form})

@login_required
def edit_product(request,pk):
    vendor = request.user.vendor
    product = vendor.products.get(pk=pk) 
    #print(request.FILES.get('image'))
    if request.method == 'POST':
        print("001")
        form = ProductForm(request.POST,instance=product)
        print("002")
        
        product = form.save(commit=False)
           
        product.title= request.POST.get('title')
        product.description= request.POST.get('description')
        product.price= request.POST.get('price')
        image=request.FILES.get('image')
        product.quantity = request.POST.get('quantity')
        product.length = request.POST.get('length')
        product.breadth = request.POST.get('breadth')
        product.height = request.POST.get('height')
        product.weight = request.POST.get('weight')
        if (image!=None):
            product.image=image
        product.vendor = vendor
        str1=product.title + "-" + product.vendor.name
        product.slug = slugify(str1)
        product.save()

        product = form.save(commit=True)
        print("00")
        
        return redirect('vendor_admin')
    form = ProductForm(instance=product) 
    print('terminate') 
    return render(request, 'vendor/edit_product.html',{'form':form, 'product': product}) 
    #return render(request, 'vendor/edit_product.html',{'form':form,}) 

@login_required
def delete_product(request,pk):
    print("hello delete")
    vendor = request.user.vendor
    product = vendor.products.get(pk=pk)
    print(product)
    product.delete()
    return redirect('vendor_admin')

# finally completed @Muskan Gupta
@login_required
def edit_vendor(request):
    # return redirect('coming_soon')
    vendor = request.user.vendor
    product = vendor.products.all() 
    print(type(product))
    list1=list(product)
    print(list1)
    #product=product.objects.all().values('vendor')

    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        password = request.POST.get('password')
        rpassword=request.POST.get('rpassword')
        confirm_password=request.POST.get('confirm_password')
        fullname = vendor.fullname
        gender = vendor.gender
        dob = vendor.dob
        nationality = vendor.nationality
        mobile = vendor.mobile
        idType = vendor.idType
        idFile = vendor.idFile
        address = vendor.address
        verified = vendor.verified

        if password == vendor.password:
            print("test1")
            if rpassword==confirm_password:

                #user_login(name,email,)
                vendor.created_by.delete()
                user = User.objects.create_user(name, email, rpassword)
                vendor = Vendor(name=name, email=email, password=rpassword, created_by=user)
                vendor.fullname = fullname
                vendor.gender = gender
                vendor.dob = dob
                vendor.nationality = nationality
                vendor.mobile = mobile
                vendor.idType = idType
                vendor.idFile = idFile
                vendor.address = address
                vendor.verified = verified
                vendor.save()
                #product.vendor=vendor
                
                for i in list1:
                    i.vendor=vendor
                    i.save()
                #product.save()
                logout(request)
                return redirect('user_login')
        else:
            print("not saved")
            #messages.error(request,"not saved")
            return redirect('vendor_admin')
    
    return render(request, 'vendor/edit_vendor.html', {'vendor':vendor})
    #return render(request, 'vendor/edit_vendor.html', {})

def edit_customer(request):
    try:
        if(request.user.vendor):
            return redirect('vendor_admin')
    except:
        customer = request.user.customer
        if request.method == 'POST':
            name = request.POST.get('name')
            email = request.POST.get('email')
            password = request.POST.get('password')
            rpassword=request.POST.get('rpassword')
            confirm_password=request.POST.get('confirm_password')
            if password == customer.password:
                
                if rpassword==confirm_password:

                    #user_login(name,email,)
                    customer.created_by.delete()
                    user = User.objects.create_user(name, email, rpassword)
                    customer = Customer(name=name, email=email, password=rpassword, created_by=user)
                    customer.save()
                    #product.vendor=vendor
                    # for i in list1:
                    #     i.customer=customer
                    #     i.save()
                    #product.save()
                    logout(request)
                    return redirect('user_login')
            else:
                messages.error(request,"not saved")
                return redirect('vendor_admin')
        return render(request, 'vendor/edit_customer.html', {'customer':customer})        



def vendors(request):
    vendors = Vendor.objects.all()

    return render(request, 'vendor/vendors.html', {'vendors': vendors})

def vendor(request, vendor_id):
    vendor = get_object_or_404(Vendor, pk=vendor_id)

    return render(request, 'vendor/vendor.html', {'vendor': vendor})
