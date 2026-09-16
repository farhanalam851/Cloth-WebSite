# ClothBrand — B2B Wholesale Apparel Website

A Django e-commerce site for a B2B clothing brand: product catalog with
minimum order quantities (MOQ), session cart, Razorpay checkout, business
account registration, order history, and a customized Django admin for
the shop owner to manage everything himself.

## What's included

- **Catalog** — categories, products with SKU / fabric / price / MOQ / stock,
  search, category filter, price sort, pagination.
- **Cart** — session-based, enforces MOQ per product.
- **Checkout & Payments** — collects business/shipping details, creates a
  Razorpay order, launches Razorpay Checkout (UPI/cards/netbanking),
  verifies the payment signature server-side before marking an order paid,
  decrements stock, and emails a confirmation.
- **Accounts** — business registration (company name, phone), login,
  profile (GSTIN, address), order history.
- **Admin** — branded "ClothBrand Admin", editable price/stock/status
  straight from list views, order status management, inline order items.

## 1. Setup

```bash
# from inside the clothbrand/ folder
python3 -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

pip install -r requirements.txt

python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

Visit `http://127.0.0.1:8000/` for the storefront and
`http://127.0.0.1:8000/admin/` for the admin panel.

Optional — load sample categories/products to see the site populated:

```bash
python manage.py seed_demo
```

## 2. Razorpay setup (required for payments to work)

1. Create a free account at https://dashboard.razorpay.com/signup
2. Go to **Settings → API Keys** and generate a **Test** key (starts with `rzp_test_`).
3. Set these as environment variables before running the server (don't hardcode
   them in `settings.py`):

   ```bash
   export RAZORPAY_KEY_ID=rzp_test_xxxxxxxxxxxx
   export RAZORPAY_KEY_SECRET=your_test_secret
   ```

   On Windows (PowerShell): `$env:RAZORPAY_KEY_ID="rzp_test_..."`

4. Test payments use Razorpay's test cards / UPI IDs — see
   https://razorpay.com/docs/payments/payments/test-card-upi-details/
   No real money moves in test mode.
5. When ready to go live, switch to **Live** keys from the same dashboard
   after completing Razorpay's KYC/activation process, and set the same two
   environment variables to the live values on your production server.

**How the payment flow works (for your reference):**
`orders/views.py` → `order_pay()` creates a Razorpay order server-side →
the customer pays via the Razorpay popup → Razorpay POSTs the result to
`/orders/payment-callback/` → `payment_callback()` verifies the
cryptographic signature before trusting the payment and marking the order
paid. This server-side verification is what prevents someone from faking
a "successful payment" by tampering with the browser.

## 3. Environment variables to set before deploying live

| Variable | Purpose |
|---|---|
| `DJANGO_SECRET_KEY` | Replace the default dev key with a long random string |
| `DJANGO_DEBUG` | Set to `False` in production |
| `DJANGO_ALLOWED_HOSTS` | Comma-separated list, e.g. `yourdomain.com,www.yourdomain.com` |
| `RAZORPAY_KEY_ID` / `RAZORPAY_KEY_SECRET` | Live keys from Razorpay dashboard |

With `DEBUG=False` you'll also need a real production database (Postgres is
recommended over SQLite for anything beyond a small catalog) and to serve
static/media files via whitenoise, S3, or your hosting provider's static
file handling — SQLite + local media works fine for development and small
deployments but isn't ideal for scaling.

## 4. Day-to-day admin use (for your client)

- Log in at `/admin/` with the superuser account.
- **Products → Categories**: add/edit categories.
- **Products → Products**: add products with images, set price/MOQ/stock —
  price and stock are editable directly from the product list for quick updates.
- **Orders → Orders**: see every order, its payment status, and update
  shipping status (Shipped/Delivered) as orders move along. Razorpay
  payment IDs are stored on each order for reconciliation.
- **Accounts → Profiles**: see registered business customers.

## 5. Project structure

```
clothbrand/
├── accounts/       # business registration, login, profile
├── cart/           # session cart logic
├── orders/         # checkout, Razorpay integration, order admin
├── products/       # catalog models, views, admin, seed_demo command
├── templates/       # all HTML (Bootstrap 5)
├── static/css/      # custom styling
└── clothbrand/     # settings, root urls
```

## 6. Known limitations / suggested next steps

- Cart is session-based (not tied to a logged-in user across devices) —
  fine for most storefronts, but flag if your client wants persistent
  carts across devices.
- No shipping-cost or tax calculation yet — orders total is simply
  sum(price × quantity). Add a shipping/tax step in `orders/views.py`
  if needed.
- No automated tests included yet — recommended before going live with
  real payments.
- For production, put this behind HTTPS (Razorpay requires it for live
  mode) and consider Gunicorn + Nginx or a managed platform.
