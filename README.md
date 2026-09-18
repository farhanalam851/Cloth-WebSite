# ClothBrand — B2B Wholesale Apparel Website

A Django e-commerce site for a B2B clothing brand: product catalog with
minimum order quantities (MOQ), session cart, Razorpay checkout, business
account registration, order history, and a customized Django admin for
the shop owner to manage everything himself.

## What's included

- **Catalog** — categories, products with SKU / fabric / price / MOQ / stock,
  search, category filter, price sort, pagination.
- **Size & colour variants** — optionally add size/colour combinations per
  product (each with its own stock); products without variants just use a
  single stock count as before.
- **Reviews & ratings** — logged-in customers can leave a 1–5 star rating
  with an optional comment; one review per customer per product (re-submitting
  updates their existing review). Average rating shown on the product page.
- **Cart** — session-based, enforces MOQ per product, tracks size/colour as
  separate cart lines.
- **Checkout & Payments** — collects business/shipping details, calculates
  GST and a flat shipping charge on top of the subtotal, creates a Razorpay
  order, launches Razorpay Checkout (UPI/cards/netbanking), verifies the
  payment signature server-side before marking an order paid, decrements
  stock (per-variant where applicable), and emails a confirmation.
- **Invoice PDF** — customers can download a PDF tax invoice for any paid
  order, showing itemized products (with size/colour), subtotal, GST, shipping,
  and total.
- **Accounts** — business registration (company name, phone), login,
  profile (GSTIN, address), order history with pay/cancel actions for
  pending orders and invoice download for paid ones.
- **Admin** — branded "ClothBrand Admin", editable price/stock/status
  straight from list views, order status management, inline order items,
  inline size/colour variant management, review moderation, homepage
  banner management, category images.
- **Premium storefront design** — hero image carousel, trust badges,
  category showcase with imagery, customer testimonials, and a
  business-account call-to-action strip, all using Playfair Display /
  Inter fonts and a refined dark-and-brass colour palette.

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

Optional — load sample categories/products/banners to see the site populated:

```bash
python manage.py seed_demo
```

This also creates 3 homepage banners and 4 category images using simple
placeholder gradients (no real photography included) — just enough to see
the new premium layout working. Replace them with real product/brand
photos any time via **Products → Banners** and **Products → Categories**
in the admin; nothing else needs to change.

## 2. Razorpay setup (required for payments to work)

1. Create a free account at https://dashboard.razorpay.com/signup
2. Go to **Settings → API Keys** and generate a **Test** key (starts with `rzp_test_`).
3. In the `clothbrand` folder (same level as `manage.py`), copy `.env.example`
   to a new file named `.env` and paste in your real key and secret:

   ```
   RAZORPAY_KEY_ID=rzp_test_xxxxxxxxxxxx
   RAZORPAY_KEY_SECRET=your_test_secret
   ```

   `.env` is loaded automatically every time you run the server (no need
   to type `export` or `$env:` in a new terminal each time) and is already
   excluded from version control via `.gitignore`, so your real keys never
   get committed.
4. Restart the server after creating/editing `.env` — environment values
   are only read when Django starts.
5. Test payments use Razorpay's test cards / UPI IDs — see
   https://razorpay.com/docs/payments/payments/test-card-upi-details/
   No real money moves in test mode.
6. When ready to go live, switch to **Live** keys from the same dashboard
   after completing Razorpay's KYC/activation process, and update `.env`
   on your production server with the live values.

**How the payment flow works (for your reference):**
`orders/views.py` → `order_pay()` creates a Razorpay order server-side →
the customer pays via the Razorpay popup → Razorpay POSTs the result to
`/orders/payment-callback/` → `payment_callback()` verifies the
cryptographic signature before trusting the payment and marking the order
paid. This server-side verification is what prevents someone from faking
a "successful payment" by tampering with the browser.

If the Razorpay keys are missing or wrong, `order_pay()` catches the error
and shows a generic "Payment Failed" page instead of crashing — if you
ever see that page, it almost always means `.env` is missing, misnamed,
or has the wrong keys.

## 3. Environment variables to set before deploying live

Set these the same way, either in `.env` (recommended for a single server)
or as real environment variables if your host manages them separately.

| Variable | Purpose |
|---|---|
| `DJANGO_SECRET_KEY` | Replace the default dev key with a long random string |
| `DJANGO_DEBUG` | Set to `False` in production |
| `DJANGO_ALLOWED_HOSTS` | Comma-separated list, e.g. `yourdomain.com,www.yourdomain.com` |
| `RAZORPAY_KEY_ID` / `RAZORPAY_KEY_SECRET` | Live keys from Razorpay dashboard |
| `SHIPPING_FLAT_RATE` | Flat shipping charge per order (default ₹99) |
| `TAX_RATE_PERCENT` | GST percentage applied to the subtotal (default 18%) |

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
  Scroll down on a product's edit page to add size/colour variants (each with
  its own stock) if this product needs them — leave empty for simple products.
- **Products → Reviews**: moderate/delete customer reviews if needed.
- **Products → Banners**: manage the homepage hero carousel — add a title,
  subtitle, image, and optional button link. Order controls which slide
  shows first; untick "Active" to hide a banner without deleting it.
- **Products → Categories**: add a category image, shown on the homepage's
  "Shop by Category" section.
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
