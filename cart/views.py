from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from products.models import Product, ProductVariant
from .cart import Cart
from .forms import CartAddProductForm


@require_POST
def cart_add(request, product_id):
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id, is_active=True)
    form = CartAddProductForm(request.POST)

    if not form.is_valid():
        messages.error(request, 'Please choose a valid quantity.')
        return redirect(product.get_absolute_url())

    cd = form.cleaned_data
    variant = None

    if product.has_variants:
        variant_id = request.POST.get('variant_id')
        if not variant_id:
            messages.warning(request, 'Please select a size and colour before adding to cart.')
            return redirect(product.get_absolute_url())
        variant = get_object_or_404(ProductVariant, id=variant_id, product=product)
        if cd['quantity'] > variant.stock:
            messages.warning(request, f'Only {variant.stock} units left in {variant.get_size_display()} / {variant.color}.')
            return redirect(product.get_absolute_url())

    if cd['quantity'] < product.moq and not cd['override']:
        messages.warning(
            request,
            f"{product.name} has a minimum order quantity of {product.moq} units."
        )
    else:
        cart.add(product=product, quantity=cd['quantity'], override_quantity=cd['override'], variant=variant)
        messages.success(request, f'Added {product.name} to your cart.')
    return redirect('cart:cart_detail')


@require_POST
def cart_remove(request, key):
    cart = Cart(request)
    cart.remove(key)
    messages.info(request, 'Removed item from your cart.')
    return redirect('cart:cart_detail')


def cart_detail(request):
    cart = Cart(request)
    return render(request, 'cart/cart_detail.html', {'cart': cart})
