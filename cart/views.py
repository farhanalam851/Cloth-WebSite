from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from products.models import Product
from .cart import Cart
from .forms import CartAddProductForm


@require_POST
def cart_add(request, product_id):
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id, is_active=True)
    form = CartAddProductForm(request.POST)
    if form.is_valid():
        cd = form.cleaned_data
        if cd['quantity'] < product.moq and not cd['override']:
            messages.warning(
                request,
                f"{product.name} has a minimum order quantity of {product.moq} units."
            )
        else:
            cart.add(product=product, quantity=cd['quantity'], override_quantity=cd['override'])
            messages.success(request, f'Added {product.name} to your cart.')
    return redirect('cart:cart_detail')


@require_POST
def cart_remove(request, product_id):
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)
    cart.remove(product)
    messages.info(request, f'Removed {product.name} from your cart.')
    return redirect('cart:cart_detail')


def cart_detail(request):
    cart = Cart(request)
    return render(request, 'cart/cart_detail.html', {'cart': cart})
