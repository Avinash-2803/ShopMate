from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .cart import Cart
from myapp.models import Product
from django.shortcuts import get_object_or_404
from django.conf import settings
import razorpay
import json

# Create your views here.

# Initialize Razorpay client once at top
razorpay_client = razorpay.Client(
    auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET)
)


def cart(request):
    cart = Cart(request)
    print("Add cart button clicked")
    if request.method == "POST":
       product_id=  request.POST.get("product_id")
       product_quantity = request.POST.get("product_quantity")
       print("product added to cart has an id:", product_id)
       print("product quantity is:", product_quantity)
       #product = Product.objects.get(id=product_id) 
       product = get_object_or_404(Product, id=product_id)
       cart.add(product=product, product_qty= product_quantity)
       cart_quantity = cart.__len__()

    return JsonResponse({'qty': cart_quantity})


def cart_overview(request):
    cart = Cart(request)
    return render(request, 'cart/cart-overview.html', {'cart': cart})


def cart_delete(request):
    cart = Cart(request)
    if request.POST.get("action") == "post":
        product_id = request.POST.get('product_id')
        cart.delete(product_id= product_id)
        cart_quantity = cart.__len__()
        Cart_total = cart.get_total_price()
        return JsonResponse({'qty': cart_quantity, 'total': Cart_total})


def cart_update(request):
    cart= Cart(request)
    if request.POST.get("action") == "post":
        product_id = request.POST.get('product_id')
        product_quantity = request.POST.get('product_quantity')
        cart.update(product_id = product_id, qty= product_quantity)
        return JsonResponse({'message': 'Cart updated successfully'})
    
# ── NEW: Create Razorpay Order ──────────────────────────────────────────────
def create_order(request):
    if request.method == "POST":
        cart = Cart(request)
        total = cart.get_total_price()          # returns a Decimal e.g. 320.0

        # Razorpay needs amount in PAISE (₹1 = 100 paise)
        amount_in_paise = int(total * 100)

        order_data = {
            "amount": amount_in_paise,
            "currency": "INR",
            "receipt": "shopmate_cart_order",
            "payment_capture": 1,               # auto-capture payment
        }

        razorpay_order = razorpay_client.order.create(data=order_data)

        return JsonResponse({
            "order_id":  razorpay_order["id"],
            "amount":    amount_in_paise,
            "currency":  "INR",
            "key":       settings.RAZORPAY_KEY_ID,
        })

    return JsonResponse({"error": "Invalid request"}, status=400)


# ── NEW: Verify Payment & Clear Cart ───────────────────────────────────────
@csrf_exempt                     # Razorpay posts back without Django CSRF token
def payment_success(request):
    if request.method == "POST":
        data = json.loads(request.body)

        try:
            # Verify signature — raises error if tampered
            razorpay_client.utility.verify_payment_signature({
                "razorpay_order_id":   data["razorpay_order_id"],
                "razorpay_payment_id": data["razorpay_payment_id"],
                "razorpay_signature":  data["razorpay_signature"],
            })

            # ✅ Verified — wipe the session cart
            cart = Cart(request)
            del request.session['cart']         # clears session cart completely
            request.session.modified = True

            return JsonResponse({"status": "success"})

        except razorpay.errors.SignatureVerificationError:
            return JsonResponse({"status": "failed"}, status=400)

    return JsonResponse({"error": "Invalid request"}, status=400)    
        
