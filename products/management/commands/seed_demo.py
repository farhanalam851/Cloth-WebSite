import os

from django.core.files import File
from django.core.management.base import BaseCommand

from products.models import Banner, Category, Product, ProductVariant

SEED_ASSETS = os.path.join(os.path.dirname(__file__), '..', '..', 'seed_assets')


class Command(BaseCommand):
    help = 'Seed the database with demo categories, products, banners and variants for a clothing brand.'

    def handle(self, *args, **options):
        data = {
            'Formal Shirts': [
                ('Classic Cotton Formal Shirt', 349, 20, 500, 'Cotton'),
                ('Slim Fit Oxford Shirt', 399, 20, 350, 'Oxford Cotton'),
            ],
            'T-Shirts': [
                ('Premium Round Neck Tee', 199, 50, 1000, 'Cotton'),
                ('Polo T-Shirt', 279, 50, 700, 'Pique Cotton'),
            ],
            'Denim': [
                ('Slim Fit Denim Jeans', 599, 15, 250, 'Denim'),
                ('Relaxed Fit Denim Jeans', 649, 15, 200, 'Denim'),
            ],
            'Ethnic Wear': [
                ('Cotton Kurta', 449, 25, 300, 'Cotton'),
            ],
        }

        category_images = {
            'Formal Shirts': 'formal-shirts.jpg',
            'T-Shirts': 't-shirts.jpg',
            'Denim': 'denim.jpg',
            'Ethnic Wear': 'ethnic-wear.jpg',
        }

        created_products = []

        for cat_name, products in data.items():
            category, created = Category.objects.get_or_create(
                name=cat_name, defaults={'description': f'Wholesale {cat_name.lower()} for retailers.'}
            )
            if not category.image:
                image_path = os.path.join(SEED_ASSETS, 'categories', category_images[cat_name])
                if os.path.exists(image_path):
                    with open(image_path, 'rb') as f:
                        category.image.save(category_images[cat_name], File(f), save=True)

            for i, (name, price, moq, stock, fabric) in enumerate(products):
                sku = f'{cat_name[:3].upper()}-{i+1:03d}'
                product, _ = Product.objects.get_or_create(
                    sku=sku,
                    defaults={
                        'category': category,
                        'name': name,
                        'description': f'{name} — wholesale bulk order available. High quality {fabric.lower()} fabric, consistent sizing across bulk orders.',
                        'fabric': fabric,
                        'price': price,
                        'moq': moq,
                        'stock': stock,
                        'is_active': True,
                        'featured': i == 0,
                    }
                )
                created_products.append(product)

        # Give the first couple of products size/colour variants so the
        # storefront's variant picker has something to show out of the box.
        sizes = ['S', 'M', 'L', 'XL']
        colors = ['Black', 'White', 'Navy']
        for product in created_products[:2]:
            for size in sizes:
                for color in colors:
                    ProductVariant.objects.get_or_create(
                        product=product, size=size, color=color,
                        defaults={'stock': 40},
                    )

        # Homepage hero banners — replace these with real photography via
        # the admin whenever the client has product shoots ready.
        banner_data = [
            ('New Season Wholesale Collection', 'Premium fabrics, bulk pricing, pan-India dispatch.', 'banner1.jpg', 1),
            ('Bulk Orders, Better Margins', 'Register a business account to unlock wholesale rates.', 'banner2.jpg', 2),
            ('Formal Wear for Every Retailer', 'Consistent sizing, reliable stock, fast turnaround.', 'banner3.jpg', 3),
        ]
        if not Banner.objects.exists():
            for title, subtitle, filename, order in banner_data:
                image_path = os.path.join(SEED_ASSETS, 'banners', filename)
                if os.path.exists(image_path):
                    banner = Banner(title=title, subtitle=subtitle, order=order, button_text='Shop Now', button_link='/products/')
                    with open(image_path, 'rb') as f:
                        banner.image.save(filename, File(f), save=True)

        self.stdout.write(self.style.SUCCESS('Demo categories, products, variants and banners created.'))
