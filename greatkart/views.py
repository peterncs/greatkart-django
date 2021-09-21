from django.db.models import Avg
from django.shortcuts import render
from store.models import Product, ReviewRating

def home(request):
    products = Product.objects.all().filter(is_available=True)
    sorted_products = sorted(products, key=lambda product: product.rating_average(), reverse=True)
    context = {
        'products': sorted_products,
    }

    return render(request, 'home.html', context)
