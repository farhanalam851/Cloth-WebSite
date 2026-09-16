from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import get_object_or_404, render
from .models import Category, Product


def home(request):
    featured = Product.objects.filter(is_active=True, featured=True)[:8]
    latest = Product.objects.filter(is_active=True)[:8]
    categories = Category.objects.filter(is_active=True)[:6]
    return render(request, 'products/home.html', {
        'featured': featured,
        'latest': latest,
        'categories': categories,
    })


def product_list(request):
    products = Product.objects.filter(is_active=True)
    categories = Category.objects.filter(is_active=True)

    query = request.GET.get('q', '').strip()
    if query:
        products = products.filter(
            Q(name__icontains=query) | Q(description__icontains=query) | Q(sku__icontains=query)
        )

    category_slug = request.GET.get('category')
    if category_slug:
        products = products.filter(category__slug=category_slug)

    sort = request.GET.get('sort')
    if sort == 'price_low':
        products = products.order_by('price')
    elif sort == 'price_high':
        products = products.order_by('-price')

    paginator = Paginator(products, 12)
    page_obj = paginator.get_page(request.GET.get('page'))

    return render(request, 'products/product_list.html', {
        'page_obj': page_obj,
        'categories': categories,
        'query': query,
        'active_category': category_slug,
    })


def category_detail(request, slug):
    category = get_object_or_404(Category, slug=slug, is_active=True)
    products = Product.objects.filter(category=category, is_active=True)
    paginator = Paginator(products, 12)
    page_obj = paginator.get_page(request.GET.get('page'))
    return render(request, 'products/category_detail.html', {
        'category': category,
        'page_obj': page_obj,
    })


def product_detail(request, slug):
    product = get_object_or_404(Product, slug=slug, is_active=True)
    related = Product.objects.filter(category=product.category, is_active=True).exclude(pk=product.pk)[:4]
    return render(request, 'products/product_detail.html', {
        'product': product,
        'related': related,
    })
