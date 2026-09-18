import razorpay
from decimal import Decimal
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.db import transaction
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from cart.cart import Cart
from .forms import OrderCreateForm
from .invoice import generate_invoice_pdf
from .models import Order, OrderItem


def get_razorpay_client():
    return razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))


@login_required
def order_create(request):
    cart = Cart(request)
    if len(cart) == 0:
        messages.warning(request, 'Your cart is empty.')
        return redirect('products:product_list')

    if request.method == 'POST':
        form = OrderCreateForm(request.POST)
        if form.is_valid():
            with transaction.atomic():
                order = form.save(commit=False)
                if request.user.is_authenticated:
                    order.user = request.user
                order.save()

                for item in cart:
                    OrderItem.objects.create(
                        order=order,
                        product=item['product'],
                        variant=item['variant'],
                        size=item['variant'].get_size_display() if item['variant'] else '',
                        color=item['variant'].color if item['variant'] else '',
                        price=item['price'],
                        quantity=item['quantity'],
                    )

                order.calculate_shipping_and_tax()

            return redirect('orders:order_pay', order_id=order.id)
    else:
        initial = {}
        if request.user.is_authenticated:
            initial = {'full_name': request.user.get_full_name(), 'email': request.user.email}
        form = OrderCreateForm(initial=initial)

    # Live estimate shown on the checkout page itself — the exact same
    # calculation Order.calculate_shipping_and_tax() will apply once the
    # order is actually created.
    subtotal = cart.get_total_price()
    shipping_estimate = settings.SHIPPING_FLAT_RATE if subtotal > 0 else Decimal('0.00')
    tax_estimate = (subtotal * settings.TAX_RATE_PERCENT / Decimal('100')).quantize(Decimal('0.01'))
    total_estimate = subtotal + shipping_estimate + tax_estimate

    return render(request, 'orders/order_create.html', {
        'cart': cart,
        'form': form,
        'subtotal': subtotal,
        'shipping_estimate': shipping_estimate,
        'tax_estimate': tax_estimate,
        'tax_rate_percent': settings.TAX_RATE_PERCENT,
        'total_estimate': total_estimate,
    })


@login_required
def order_pay(request, order_id):
    """
    Creates a Razorpay order for this order's total and renders the
    checkout page that launches Razorpay's payment popup (Checkout.js).
    """
    order = get_object_or_404(Order, id=order_id, user=request.user)
    amount_paise = int(order.get_total_cost() * 100)  # Razorpay expects the smallest currency unit

    client = get_razorpay_client()
    try:
        razorpay_order = client.order.create({
            'amount': amount_paise,
            'currency': settings.RAZORPAY_CURRENCY,
            'payment_capture': 1,
            'notes': {'order_id': str(order.id)},
        })
    except Exception:
        # Razorpay unreachable / bad keys / network issue — never show the
        # customer a raw stack trace, send them to a friendly failure page.
        messages.error(request, 'We could not start the payment process. Please try again in a moment.')
        return render(request, 'orders/order_failed.html', {'order': order})

    order.razorpay_order_id = razorpay_order['id']
    order.save(update_fields=['razorpay_order_id'])

    context = {
        'order': order,
        'razorpay_key_id': settings.RAZORPAY_KEY_ID,
        'razorpay_order_id': razorpay_order['id'],
        'amount_paise': amount_paise,
        'callback_url': request.build_absolute_uri('/orders/payment-callback/'),
    }
    return render(request, 'orders/order_pay.html', context)


@csrf_exempt
@require_POST
def payment_callback(request):
    """
    Razorpay Checkout.js posts here after the popup completes.
    We verify the signature server-side before trusting the payment.
    """
    params = {
        'razorpay_order_id': request.POST.get('razorpay_order_id', ''),
        'razorpay_payment_id': request.POST.get('razorpay_payment_id', ''),
        'razorpay_signature': request.POST.get('razorpay_signature', ''),
    }

    order = get_object_or_404(Order, razorpay_order_id=params['razorpay_order_id'])
    client = get_razorpay_client()

    try:
        client.utility.verify_payment_signature(params)
    except razorpay.errors.SignatureVerificationError:
        order.status = Order.STATUS_FAILED
        order.save(update_fields=['status'])
        return redirect('orders:order_failed', order_id=order.id)

    order.razorpay_payment_id = params['razorpay_payment_id']
    order.razorpay_signature = params['razorpay_signature']
    order.status = Order.STATUS_PAID
    order.save(update_fields=['razorpay_payment_id', 'razorpay_signature', 'status'])

    # Reduce stock for each item — per-variant if this product has variants,
    # otherwise the product's own stock field.
    for item in order.items.select_related('product', 'variant'):
        if item.variant:
            item.variant.stock = max(0, item.variant.stock - item.quantity)
            item.variant.save(update_fields=['stock'])
        else:
            product = item.product
            product.stock = max(0, product.stock - item.quantity)
            product.save(update_fields=['stock'])

    # Clear the cart
    Cart(request).clear()

    # Send confirmation email (console backend in dev)
    send_mail(
        subject=f'Order confirmation — #{order.id}',
        message=(
            f'Hi {order.full_name},\n\n'
            f'Thank you for your order #{order.id}. '
            f'Total paid: Rs. {order.get_total_cost()}.\n\n'
            f'We will be in touch with shipping details shortly.'
        ),
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[order.email],
        fail_silently=True,
    )

    return redirect('orders:order_success', order_id=order.id)


@login_required
def order_success(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user, status=Order.STATUS_PAID)
    return render(request, 'orders/order_success.html', {'order': order})


@login_required
def order_failed(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    return render(request, 'orders/order_failed.html', {'order': order})


@login_required
def order_history(request):
    orders = Order.objects.filter(user=request.user)
    return render(request, 'orders/order_history.html', {'orders': orders})


@login_required
@require_POST
def order_cancel(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    if order.status != Order.STATUS_PENDING:
        messages.warning(request, "Only orders that are still pending payment can be cancelled.")
    else:
        order.status = Order.STATUS_CANCELLED
        order.save(update_fields=['status'])
        messages.success(request, f'Order #{order.id} has been cancelled.')
    return redirect('orders:order_history')


@login_required
def order_invoice(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user, status=Order.STATUS_PAID)
    buffer = generate_invoice_pdf(order)
    response = HttpResponse(buffer, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="invoice_order_{order.id}.pdf"'
    return response
