from django.contrib import admin
from django.utils.html import format_html
from .models import Banner, Category, Product, ProductImage, ProductVariant, Review


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('thumb', 'name', 'slug', 'is_active', 'product_count')
    list_filter = ('is_active',)
    search_fields = ('name',)
    prepopulated_fields = {'slug': ('name',)}

    def product_count(self, obj):
        return obj.products.count()
    product_count.short_description = 'Products'

    def thumb(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="height:36px;border-radius:4px;" />', obj.image.url)
        return '—'
    thumb.short_description = 'Image'


@admin.register(Banner)
class BannerAdmin(admin.ModelAdmin):
    list_display = ('thumb', 'title', 'subtitle', 'order', 'is_active')
    list_editable = ('order', 'is_active')
    list_filter = ('is_active',)

    def thumb(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="height:40px;border-radius:4px;" />', obj.image.url)
        return '—'
    thumb.short_description = 'Preview'


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1


class ProductVariantInline(admin.TabularInline):
    model = ProductVariant
    extra = 1


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = (
        'thumb', 'name', 'sku', 'category', 'price', 'moq',
        'stock', 'is_active', 'featured', 'rating_display', 'created_at',
    )
    list_filter = ('category', 'is_active', 'featured')
    list_editable = ('price', 'stock', 'is_active', 'featured')
    search_fields = ('name', 'sku', 'description')
    prepopulated_fields = {'slug': ('name',)}
    inlines = [ProductImageInline, ProductVariantInline]
    fieldsets = (
        ('Basic info', {
            'fields': ('category', 'name', 'slug', 'sku', 'fabric', 'description', 'image')
        }),
        ('Pricing & stock', {
            'fields': ('price', 'moq', 'stock'),
            'description': 'If you add size/colour variants below, stock is tracked per variant instead — this field is only used as a fallback for products with no variants.',
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

    def rating_display(self, obj):
        avg = obj.average_rating
        if avg is None:
            return '—'
        return f'{avg} ★ ({obj.review_count})'
    rating_display.short_description = 'Rating'


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('product', 'user', 'rating', 'created_at')
    list_filter = ('rating', 'created_at')
    search_fields = ('product__name', 'user__username', 'comment')
