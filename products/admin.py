from django.contrib import admin
from django.utils.html import format_html
from .models import Category, Product, ProductImage


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'is_active', 'product_count')
    list_filter = ('is_active',)
    search_fields = ('name',)
    prepopulated_fields = {'slug': ('name',)}

    def product_count(self, obj):
        return obj.products.count()
    product_count.short_description = 'Products'


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = (
        'thumb', 'name', 'sku', 'category', 'price', 'moq',
        'stock', 'is_active', 'featured', 'created_at',
    )
    list_filter = ('category', 'is_active', 'featured')
    list_editable = ('price', 'stock', 'is_active', 'featured')
    search_fields = ('name', 'sku', 'description')
    prepopulated_fields = {'slug': ('name',)}
    inlines = [ProductImageInline]
    fieldsets = (
        ('Basic info', {
            'fields': ('category', 'name', 'slug', 'sku', 'fabric', 'description', 'image')
        }),
        ('Pricing & stock', {
            'fields': ('price', 'moq', 'stock')
        }),
        ('Visibility', {
            'fields': ('is_active', 'featured')
        }),
    )

    def thumb(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="height:40px;border-radius:4px;" />', obj.image.url)
        return '—'
    thumb.short_description = 'Image'
