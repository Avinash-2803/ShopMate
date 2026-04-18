from django.shortcuts import render, redirect
from .forms import AddressForm
from .models import Address
from cart.cart import Cart
from .models import Order,OrderItem
from django.http import JsonResponse

def add_address(request):
    try:
        address = Address.objects.get(user=request.user)
    except Address.DoesNotExist:
        address = None

    if request.method == 'POST':
        form = AddressForm(request.POST)
        if form.is_valid():
            address = form.save(commit=False)  # Don't save to the database yet
            address.user = request.user  # Associate the address with the current user
            address.save()  # Now save to the database
            return redirect('index') # redirect to wherever you want after saving
    else:
        form = AddressForm(instance=address)  # Pre-fill the form with existing address if it exists
    
    return render(request, 'orders/add_address.html', {'form': form})



def checkout(request):
    if request.user.is_authenticated:
        try:
            address = Address.objects.get(user=request.user)
            return render(request,'orders/checkout.html',{'address':address})
        except:
           return render(request,'orders/checkout.html')
    else:
        return render(request,'orders/checkout.html')
    
def place_order(request):
    order_success=False
    if request.method=="POST":
        cart = Cart(request)
        total_amount = cart.get_total_price()

        if request.user.is_authenticated:
            order = Order.objects.create(user=request.user,total_amount=total_amount)
            for item in cart:
                OrderItem.objects.create(order=order,product=item['product'],quantity=item['qty'])
            order_success=True
        else:
            order = Order.objects.create(total_amount=total_amount)
            for item in cart:
                OrderItem.objects.create(order=order,product=item['product'],quantity=item['qty'])               
            order_success=True
    return JsonResponse({'success':order_success})

def order_success(request):
    return render(request,'orders/order-success.html')

def order_failed(request):
    return render(request,'orders/order-failed.html')