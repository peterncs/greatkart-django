from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404

from accounts.models import UserProfile
from store.models import Product, Variation
from carts.models import Cart, CartItem
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponse


# Create your views here.

def _cart_id(request):
    cart_id = request.session.session_key
    if not cart_id:
        cart_id = request.session.create()
    return cart_id


def add_cart(request, product_id):
    current_user = request.user
    product = Product.objects.get(id=product_id)
    # If the user is authenticated
    if current_user.is_authenticated:

        # Get the product variation
        product_variation = []
        if request.method == 'POST':
            for item in request.POST:
                key = item
                value = request.POST[key]
                try:
                    variation = Variation.objects.get(product=product, variation_category__iexact=key,
                                                      variation_value__iexact=value)
                    product_variation.append(variation)
                except:
                    pass

        # Increment the quantity of or Add the variation of the product if it exists in the cart
        is_cart_item_exists = CartItem.objects.filter(product=product, user=current_user).exists()
        if is_cart_item_exists:
            cart_item = CartItem.objects.filter(product=product, user=current_user)

            # Store all existing product variation and cart item id into list
            ex_var_list = []
            cart_item_id_list = []
            for item in cart_item:
                existing_variation = item.variations.all()
                ex_var_list.append(list(existing_variation))
                cart_item_id_list.append(item.id)

            # Increment the quantity of the product variation if it already exists in the cart
            if product_variation in ex_var_list:
                index = ex_var_list.index(product_variation)
                item_id = cart_item_id_list[index]
                item = CartItem.objects.get(id=item_id)
                item.quantity += 1
                item.save()

            # Add the product variation to the cart if it does not exist in the cart
            else:
                item = CartItem.objects.create(product=product, user=current_user, quantity=1)
                item.variations.add(*product_variation)
                item.save()

        # Add the product if it does not exist in the cart
        else:
            item = CartItem.objects.create(product=product, user=current_user, quantity=1)
            item.variations.add(*product_variation)
            item.save()

        return redirect('cart')

    # If the user is not authenticated
    else:
        # Get the cart by cart_id present in the session
        try:
            cart = Cart.objects.get(cart_id=_cart_id(request))
        except Cart.DoesNotExist:
            cart = Cart.objects.create(
                cart_id=_cart_id(request)
            )
        cart.save()

        # Get the product variation
        product_variation = []
        if request.method == 'POST':
            for item in request.POST:
                key = item
                value = request.POST[key]
                try:
                    variation = Variation.objects.get(product=product, variation_category__iexact=key,
                                                      variation_value__iexact=value)
                    product_variation.append(variation)
                except:
                    pass

        # Increment the quantity of or Add the variation of the product if it exists in the cart
        is_cart_item_exists = CartItem.objects.filter(product=product, cart=cart).exists()
        if is_cart_item_exists:
            cart_item = CartItem.objects.filter(product=product, cart=cart)

            # Store all existing product variation and cart item id into list
            ex_var_list = []
            cart_item_id_list = []
            for item in cart_item:
                existing_variation = item.variations.all()
                ex_var_list.append(list(existing_variation))
                cart_item_id_list.append(item.id)

            # Increment the quantity of the product variation if it already exists in the cart
            if product_variation in ex_var_list:
                index = ex_var_list.index(product_variation)
                item_id = cart_item_id_list[index]
                item = CartItem.objects.get(id=item_id)
                item.quantity += 1
                item.save()

            # Add the product variation to the cart if it does not exist in the cart
            else:
                item = CartItem.objects.create(product=product, cart=cart, quantity=1)
                item.variations.add(*product_variation)
                item.save()

        # Add the product if it does not exist in the cart
        else:
            item = CartItem.objects.create(product=product, cart=cart, quantity=1)
            item.variations.add(*product_variation)
            item.save()

        return redirect('cart')


# Define a function that decreases the quantity of a cart item
def remove_cart(request, product_id, cart_item_id):
    product = get_object_or_404(Product, id=product_id)
    try:
        if request.user.is_authenticated:
            cart_item = CartItem.objects.get(product=product, user=request.user, id=cart_item_id)
        else:
            cart = Cart.objects.get(cart_id=_cart_id(request))
            cart_item = CartItem.objects.get(product=product, cart=cart, id=cart_item_id)
        if cart_item.quantity > 1:
            cart_item.quantity -= 1
            cart_item.save()
        else:
            cart_item.delete()
    except:
        pass
    return redirect('cart')


# Define a function that remove a cart item from the cart
def remove_cart_item(request, product_id, cart_item_id):
    product = get_object_or_404(Product, id=product_id)
    if request.user.is_authenticated:
        cart_item = CartItem.objects.get(product=product, user=request.user, id=cart_item_id)
    else:
        cart = Cart.objects.get(cart_id=_cart_id(request))
        cart_item = CartItem.objects.get(product=product, cart=cart, id=cart_item_id)
    cart_item.delete()
    return redirect('cart')


def cart(request, total=0, quantity=0, cart_items=None):
    tax = 0
    grand_total = 0
    try:
        if request.user.is_authenticated:
            cart_items = CartItem.objects.filter(user=request.user, is_active=True)
        else:
            cart = Cart.objects.get(cart_id=_cart_id(request))
            cart_items = CartItem.objects.filter(cart=cart, is_active=True)
        for cart_item in cart_items:
            total += (cart_item.product.price * cart_item.quantity)
            quantity += cart_item.quantity
        tax = total * 0.02
        grand_total = total + tax
    except ObjectDoesNotExist:
        pass

    context = {
        'total': total,
        'quantity': quantity,
        'cart_items': cart_items,
        'tax': tax,
        'grand_total': grand_total,
    }
    return render(request, 'store/cart.html', context)


@login_required(login_url='login')
def checkout(request, total=0, quantity=0, cart_items=None):
    tax = 0
    grand_total = 0
    try:
        if request.user.is_authenticated:
            cart_items = CartItem.objects.filter(user=request.user, is_active=True)
        else:
            cart = Cart.objects.get(cart_id=_cart_id(request))
            cart_items = CartItem.objects.filter(cart=cart, is_active=True)
        for cart_item in cart_items:
            total += (cart_item.product.price * cart_item.quantity)
            quantity += cart_item.quantity
        tax = total * 0.02
        grand_total = total + tax
    except ObjectDoesNotExist:
        pass

    user_profile = UserProfile.objects.get(user=request.user)

    context = {
        'total': total,
        'quantity': quantity,
        'cart_items': cart_items,
        'tax': tax,
        'grand_total': grand_total,
        'user_profile': user_profile,
    }
    return render(request, 'store/checkout.html', context)
