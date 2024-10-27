from django import forms
from .models import Sale
from django.contrib.auth.models import User

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

class UserEditForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'is_staff']

class ChangePasswordForm(forms.Form):
    new_password = forms.CharField(widget=forms.PasswordInput, label="New Password")
    confirm_password = forms.CharField(widget=forms.PasswordInput, label="Confirm Password")

    def clean(self):
        cleaned_data = super().clean()
        new_password = cleaned_data.get("new_password")
        confirm_password = cleaned_data.get("confirm_password")

        if new_password != confirm_password:
            raise forms.ValidationError("Passwords do not match.")