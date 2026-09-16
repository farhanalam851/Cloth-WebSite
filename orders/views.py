import razorpay
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from cart.cart import Cart
from .forms import OrderCreateForm
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
                        price=item['price'],
                        quantity=item['quantity'],
                    )

            return redirect('orders:order_pay', order_id=order.id)
    else:
        initial = {}
        if request.user.is_authenticated:
            initial = {'full_name': request.user.get_full_name(), 'email': request.user.email}
        form = OrderCreateForm(initial=initial)

    return render(request, 'orders/order_create.html', {'cart': cart, 'form': form})


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

    # Reduce stock for each item
    for item in order.items.select_related('product'):
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
