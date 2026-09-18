from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from .forms import ReviewForm
from .models import Banner, Category, Product, Review


def home(request):
    banners = Banner.objects.filter(is_active=True)
    featured = Product.objects.filter(is_active=True, featured=True)[:8]
    latest = Product.objects.filter(is_active=True)[:8]
    categories = Category.objects.filter(is_active=True)[:6]
    testimonials = (
        Review.objects.filter(rating__gte=4)
        .select_related('product', 'user')
        .order_by('-created_at')[:3]
    )
    return render(request, 'products/home.html', {
        'banners': banners,
        'featured': featured,
        'latest': latest,
        'categories': categories,
        'testimonials': testimonials,
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

    user_review = None
    if request.user.is_authenticated:
        user_review = Review.objects.filter(product=product, user=request.user).first()
    review_form = ReviewForm(instance=user_review)

    return render(request, 'products/product_detail.html', {
        'product': product,
        'related': related,
        'review_form': review_form,
        'user_review': user_review,
    })


@login_required
@require_POST
def review_add(request, slug):
    product = get_object_or_404(Product, slug=slug, is_active=True)
    existing = Review.objects.filter(product=product, user=request.user).first()
    form = ReviewForm(request.POST, instance=existing)
    if form.is_valid():
        review = form.save(commit=False)
        review.product = product
        review.user = request.user
        review.save()
        messages.success(request, 'Thanks — your review has been saved.')
    else:
        messages.error(request, 'Please choose a rating before submitting.')
    return redirect(product.get_absolute_url())
