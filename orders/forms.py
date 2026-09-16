from django import forms
from .models import Order


class OrderCreateForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = [
            'company_name', 'full_name', 'email', 'phone', 'gst_number',
            'address_line', 'city', 'state', 'postal_code', 'country',
        ]
        widgets = {
            'company_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Business / company name'}),
            'full_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'gst_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Optional'}),
            'address_line': forms.TextInput(attrs={'class': 'form-control'}),
            'city': forms.TextInput(attrs={'class': 'form-control'}),
            'state': forms.TextInput(attrs={'class': 'form-control'}),
            'postal_code': forms.TextInput(attrs={'class': 'form-control'}),
            'country': forms.TextInput(attrs={'class': 'form-control'}),
        }
