from decimal import Decimal
from django.conf import settings
from django.db import models


class Order(models.Model):
    STATUS_PENDING = 'pending'
    STATUS_PAID = 'paid'
    STATUS_FAILED = 'failed'
    STATUS_SHIPPED = 'shipped'
    STATUS_DELIVERED = 'delivered'
    STATUS_CANCELLED = 'cancelled'

    STATUS_CHOICES = [
        (STATUS_PENDING, 'Payment Pending'),
        (STATUS_PAID, 'Paid'),
        (STATUS_FAILED, 'Payment Failed'),
        (STATUS_SHIPPED, 'Shipped'),
        (STATUS_DELIVERED, 'Delivered'),
        (STATUS_CANCELLED, 'Cancelled'),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, related_name='orders',
        on_delete=models.SET_NULL, null=True, blank=True
    )

    # Buyer / business details captured at checkout
    company_name = models.CharField(max_length=150, blank=True)
    full_name = models.CharField(max_length=150)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    gst_number = models.CharField('GSTIN', max_length=20, blank=True)

    address_line = models.CharField(max_length=255)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    postal_code = models.CharField(max_length=20)
    country = models.CharField(max_length=100, default='India')

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_PENDING)

    # Razorpay tracking fields
    razorpay_order_id = models.CharField(max_length=100, blank=True)
    razorpay_payment_id = models.CharField(max_length=100, blank=True)
    razorpay_signature = models.CharField(max_length=255, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'Order #{self.id} — {self.full_name}'

    def get_total_cost(self):
        return sum(item.get_cost() for item in self.items.all())

    @property
    def is_paid(self):
        return self.status in (self.STATUS_PAID, self.STATUS_SHIPPED, self.STATUS_DELIVERED)


class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey('products.Product', related_name='order_items', on_delete=models.PROTECT)
    price = models.DecimalField(max_digits=10, decimal_places=2)  # price at time of purchase
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return str(self.id)

    def get_cost(self):
        return self.price * self.quantity
