from django.db import models
from django.urls import reverse
from django.utils.text import slugify


class Category(models.Model):
    name = models.CharField(max_length=120, unique=True)
    slug = models.SlugField(max_length=140, unique=True, blank=True)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name_plural = 'Categories'
        ordering = ['name']

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('products:category_detail', args=[self.slug])


class Product(models.Model):
    category = models.ForeignKey(Category, related_name='products', on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=220, unique=True, blank=True)
    sku = models.CharField('SKU', max_length=50, unique=True)
    description = models.TextField(blank=True)
    fabric = models.CharField(max_length=120, blank=True, help_text='e.g. Cotton, Polyester blend')

    # B2B pricing: this is the per-unit wholesale price
    price = models.DecimalField(max_digits=10, decimal_places=2, help_text='Price per unit (INR)')
    moq = models.PositiveIntegerField('Minimum Order Quantity', default=1)

    stock = models.PositiveIntegerField(default=0)
    image = models.ImageField(upload_to='products/', blank=True, null=True)

    is_active = models.BooleanField(default=True)
    featured = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return f'{self.name} ({self.sku})'

    def get_absolute_url(self):
        return reverse('products:product_detail', args=[self.slug])

    @property
    def in_stock(self):
        return self.stock > 0


class ProductImage(models.Model):
    """Extra gallery images for a product, in addition to the main image."""
    product = models.ForeignKey(Product, related_name='gallery', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='products/gallery/')
    alt_text = models.CharField(max_length=150, blank=True)

    def __str__(self):
        return f'Image for {self.product.name}'
