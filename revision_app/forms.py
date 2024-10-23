from django import forms
from .models import Sale

class SalesForm(forms.ModelForm):
    class Meta:
        model = Sale
        fields = ['product', 'quantity_sold']  # Include fields for product and quantity
        widgets = {
            'product': forms.Select(attrs={'class': 'form-control'}),
            'quantity_sold': forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
        }
    
    def clean(self):
        cleaned_data = super().clean()
        product = cleaned_data.get('product')
        quantity_sold = cleaned_data.get('quantity_sold')

        # Check if product and quantity_sold are provided
        if product and quantity_sold:
            # Validate available stock
            if quantity_sold > product.stock:
                # Raise a validation error to prevent form submission
                raise forms.ValidationError('Not enough stock available.')

            # Calculate total price
            cleaned_data['total_price'] = product.price * quantity_sold

        return cleaned_data
