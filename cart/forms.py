from django import forms


class CartAddProductForm(forms.Form):
    # B2B orders can run into the hundreds/thousands of units, so this is a
    # free-entry integer field (with a sane upper bound) rather than a fixed
    # dropdown of 1-50.
    quantity = forms.IntegerField(
        min_value=1, max_value=100000, initial=1,
        widget=forms.NumberInput(attrs={'class': 'form-control'})
    )
    override = forms.BooleanField(required=False, initial=False, widget=forms.HiddenInput)
