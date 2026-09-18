from django.conf import settings
from django.db import models
from django.urls import reverse
from django.utils.text import slugify


class Category(models.Model):
    name = models.CharField(max_length=120, unique=True)
    slug = models.SlugField(max_length=140, unique=True, blank=True)
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to='categories/', blank=True, null=True)
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
        if self.has_variants:
            return any(v.stock > 0 for v in self.variants.all())
        return self.stock > 0

    @property
    def has_variants(self):
        return self.variants.exists()

    @property
    def total_stock(self):
        """Combined stock across all variants, or the base stock field if this product has none."""
        if self.has_variants:
            return sum(v.stock for v in self.variants.all())
        return self.stock

    @property
    def average_rating(self):
        reviews = self.reviews.all()
        if not reviews:
            return None
        return round(sum(r.rating for r in reviews) / len(reviews), 1)

    @property
    def review_count(self):
        return self.reviews.count()


class ProductVariant(models.Model):
    SIZE_CHOICES = [
        ('XS', 'XS'), ('S', 'S'), ('M', 'M'), ('L', 'L'),
        ('XL', 'XL'), ('XXL', 'XXL'), ('FREE', 'Free Size'),
    ]

    product = models.ForeignKey(Product, related_name='variants', on_delete=models.CASCADE)
    size = models.CharField(max_length=10, choices=SIZE_CHOICES, default='FREE')
    color = models.CharField(max_length=50)
    stock = models.PositiveIntegerField(default=0)

    class Meta:
        unique_together = ('product', 'size', 'color')
        ordering = ['size', 'color']

    def __str__(self):
        return f'{self.product.name} — {self.get_size_display()} / {self.color}'

    @property
    def in_stock(self):
        return self.stock > 0


class Review(models.Model):
    product = models.ForeignKey(Product, related_name='reviews', on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='reviews', on_delete=models.CASCADE)
    rating = models.PositiveSmallIntegerField(choices=[(i, str(i)) for i in range(1, 6)])
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('product', 'user')  # one review per customer per product
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.rating}★ — {self.product.name} by {self.user.username}'


class ProductImage(models.Model):
    """Extra gallery images for a product, in addition to the main image."""
    product = models.ForeignKey(Product, related_name='gallery', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='products/gallery/')
    alt_text = models.CharField(max_length=150, blank=True)

    def __str__(self):
        return f'Image for {self.product.name}'


class Banner(models.Model):
    """
    Hero banner slides for the homepage. The shop owner manages these
    entirely from the admin — no code changes needed to swap seasonal
    promotions, sale banners, or new-arrival announcements.
    """
    title = models.CharField(max_length=150)
    subtitle = models.CharField(max_length=250, blank=True)
    image = models.ImageField(upload_to='banners/', help_text='Recommended: 1600×600px or wider, landscape orientation.')
    button_text = models.CharField(max_length=50, blank=True, default='Shop Now')
    button_link = models.CharField(max_length=200, blank=True, help_text='e.g. /products/ or a category URL')
    order = models.PositiveIntegerField(default=0, help_text='Lower numbers show first.')
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['order', 'id']

    def __str__(self):
        return self.title
