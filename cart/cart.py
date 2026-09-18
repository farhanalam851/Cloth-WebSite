from decimal import Decimal
from products.models import Product, ProductVariant

CART_SESSION_ID = 'cart'


def _cart_key(product_id, variant_id=None):
    """Composite key so the same product in different sizes/colours can
    sit in the cart as separate lines."""
    return f'{product_id}:{variant_id}' if variant_id else str(product_id)


class Cart:
    """
    A simple session-based shopping cart.
    Works for both guest and logged-in users; contents persist for the
    browser session (upgradeable to a DB-backed cart per user later).
    """

    def __init__(self, request):
        self.session = request.session
        cart = self.session.get(CART_SESSION_ID)
        if cart is None:
            cart = self.session[CART_SESSION_ID] = {}
        self.cart = cart

    def add(self, product, quantity=1, override_quantity=False, variant=None):
        key = _cart_key(product.id, variant.id if variant else None)
        if key not in self.cart:
            self.cart[key] = {
                'product_id': product.id,
                'variant_id': variant.id if variant else None,
                'quantity': 0,
                'price': str(product.price),
            }
        if override_quantity:
            self.cart[key]['quantity'] = quantity
        else:
            self.cart[key]['quantity'] += quantity
        self.save()

    def save(self):
        self.session.modified = True

    def remove(self, key):
        if key in self.cart:
            del self.cart[key]
            self.save()

    def __iter__(self):
        product_ids = {v['product_id'] for v in self.cart.values()}
        variant_ids = {v['variant_id'] for v in self.cart.values() if v['variant_id']}

        products = {p.id: p for p in Product.objects.filter(id__in=product_ids)}
        variants = {v.id: v for v in ProductVariant.objects.filter(id__in=variant_ids)}

        for key, raw in self.cart.items():
            item = raw.copy()
            item['key'] = key
            item['product'] = products.get(item['product_id'])
            item['variant'] = variants.get(item['variant_id']) if item['variant_id'] else None
            item['price'] = Decimal(item['price'])
            item['total_price'] = item['price'] * item['quantity']
            if item['product'] is not None:
                yield item

    def __len__(self):
        return sum(item['quantity'] for item in self.cart.values())

    def get_total_price(self):
        return sum(Decimal(item['price']) * item['quantity'] for item in self.cart.values())

    def clear(self):
        del self.session[CART_SESSION_ID]
        self.save()
