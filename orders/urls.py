from django.urls import path
from . import views

app_name = 'orders'

urlpatterns = [
    path('create/', views.order_create, name='order_create'),
    path('pay/<int:order_id>/', views.order_pay, name='order_pay'),
    path('payment-callback/', views.payment_callback, name='payment_callback'),
    path('success/<int:order_id>/', views.order_success, name='order_success'),
    path('failed/<int:order_id>/', views.order_failed, name='order_failed'),
    path('history/', views.order_history, name='order_history'),
    path('cancel/<int:order_id>/', views.order_cancel, name='order_cancel'),
]
