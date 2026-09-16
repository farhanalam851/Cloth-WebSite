from django.contrib import admin
from .models import Order, OrderItem


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    raw_id_fields = ('product',)
    extra = 0
    readonly_fields = ('price',)


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'full_name', 'company_name', 'email', 'phone',
        'status', 'total_display', 'created_at',
    )
    list_filter = ('status', 'created_at', 'state')
    list_editable = ('status',)
    search_fields = ('full_name', 'company_name', 'email', 'phone', 'razorpay_payment_id')
    date_hierarchy = 'created_at'
    inlines = [OrderItemInline]
    readonly_fields = ('razorpay_order_id', 'razorpay_payment_id', 'razorpay_signature', 'created_at', 'updated_at')
    fieldsets = (
        ('Customer', {
            'fields': ('user', 'company_name', 'full_name', 'email', 'phone', 'gst_number')
        }),
        ('Shipping address', {
            'fields': ('address_line', 'city', 'state', 'postal_code', 'country')
        }),
        ('Order status', {
            'fields': ('status',)
        }),
        ('Payment (Razorpay)', {
            'fields': ('razorpay_order_id', 'razorpay_payment_id', 'razorpay_signature')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at')
        }),
    )

    def total_display(self, obj):
        return f'Rs. {obj.get_total_cost()}'
    total_display.short_description = 'Total'
