from django.shortcuts import render, redirect
from django.template.loader import render_to_string
from django.core.mail import EmailMessage

from carts.models import CartItem
from orders.models import Order, Payment, OrderProduct
from store.models import Product
from .forms import OrderForm
from datetime import datetime

import json
from django.http import HttpResponse, JsonResponse


# Create your views here.

def place_order(request):
    current_user = request.user
    if current_user.is_authenticated:
        cart_items = CartItem.objects.filter(user=current_user)
        cart_count = cart_items.count()
        if cart_count <= 0:
            return redirect('store')

        total = 0
        quantity = 0
        for cart_item in cart_items:
            total += (cart_item.product.price * cart_item.quantity)
            quantity += cart_item.quantity
        tax = total * 0.02
        grand_total = total + tax

        if request.method == 'POST':
            form = OrderForm(request.POST)
            if form.is_valid():
                data = Order()
                data.user = current_user
                data.first_name = form.cleaned_data['first_name']
                data.last_name = form.cleaned_data['last_name']
                data.phone = form.cleaned_data['phone']
                data.email = form.cleaned_data['email']
                data.address_line_1 = form.cleaned_data['address_line_1']
                data.address_line_2 = form.cleaned_data['address_line_2']
                data.country = form.cleaned_data['country']
                data.state = form.cleaned_data['state']
                data.city = form.cleaned_data['city']
                data.order_note = form.cleaned_data['order_note']
                data.order_total = grand_total
                data.tax = tax
                data.ip = request.META.get('REMOTE_ADDR')
                data.save()

                order_number = datetime.today().strftime('%Y%m%d') + str(data.id)
                data.order_number = order_number
                data.save()

                order = Order.objects.get(user=current_user, is_ordered=False, order_number=order_number)
                context = {
                    'order': order,
                    'cart_items': cart_items,
                    'total': total,
                    'tax': tax,
                    'grand_total': grand_total,
                }
                return render(request, 'orders/payments.html', context)
        else:
            return redirect('checkout')
    else:
        return redirect('login')


def payments(request):
    body = json.loads(request.body)
    order = Order.objects.get(user=request.user, is_ordered=False, order_number=body['orderID'])

    # Store transaction details inside Payment model
    payment = Payment(
        user=request.user,
        payment_id=body['transID'],
        payment_method=body['payment_method'],
        amount_paid=order.order_total,
        status=body['status'],
    )
    payment.save()

    order.payment = payment
    order.is_ordered = True
    order.save()

    # Move the cart items to Order Product table
    cart_items = CartItem.objects.filter(user=request.user)
    for cart_item in cart_items:
        order_product = OrderProduct(
            order_id=order.id,
            payment=payment,
            user_id=request.user.id,
            product_id=cart_item.product_id,
            quantity=cart_item.quantity,
            product_price=cart_item.product.price,
            ordered=True
        )
        order_product.save()

        order_product = OrderProduct.objects.get(id=order_product.id)
        order_product.variations.set(cart_item.variations.all())
        order_product.save()

        # Reduce the quantity of the sold products
        product = Product.objects.get(id=cart_item.product_id)
        product.stock -= cart_item.quantity
        product.save()

    # Clear cart
    CartItem.objects.filter(user=request.user).delete()

    # Send order received email to customer
    mail_subject = 'Thank you for your order'
    message = render_to_string('orders/order_received_email.html', {
        'user': request.user,
        'order': order,
    })
    to_email = request.user.email
    send_email = EmailMessage(mail_subject, message, to=[to_email])
    send_email.send()

    # Send order number and transaction id back to sendData method via JsonResponse
    data = {
        'order_number': order.order_number,
        'transID': order.payment.payment_id,
    }
    return JsonResponse(data)


def order_complete(request):
    order_number = request.GET.get('order_number')
    transID = request.GET.get('payment_id')
    try:
        order = Order.objects.get(order_number=order_number, is_ordered=True)
        ordered_products = OrderProduct.objects.filter(order_id=order.id)

        subtotal = order.order_total - order.tax

        context = {
            'order': order,
            'ordered_products': ordered_products,
            'subtotal':subtotal
        }
        return render(request, 'orders/order_complete.html', context)
    except (Payment.DoesNotExist, Order.DoesNotExist):
        return redirect('home')
