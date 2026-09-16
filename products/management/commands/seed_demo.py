from django.core.management.base import BaseCommand
from products.models import Category, Product


class Command(BaseCommand):
    help = 'Seed the database with demo categories and products for a clothing brand.'

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

        for cat_name, products in data.items():
            category, _ = Category.objects.get_or_create(
                name=cat_name, defaults={'description': f'Wholesale {cat_name.lower()} for retailers.'}
            )
            for i, (name, price, moq, stock, fabric) in enumerate(products):
                sku = f'{cat_name[:3].upper()}-{i+1:03d}'
                Product.objects.get_or_create(
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

        self.stdout.write(self.style.SUCCESS('Demo categories and products created.'))
