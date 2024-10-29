from django import forms
from .models import Sale
from django.contrib.auth.models import User
from .models import Products
from django.contrib.auth.forms import UserCreationForm

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
        

class ProductForm(forms.ModelForm):
    class Meta:
        model = Products
        fields = '__all__'  # Use specific fields if needed

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['product_name'].widget.attrs.update({'placeholder': 'Eg; Rice'})
        self.fields['price'].widget.attrs.update({'placeholder': 'GHS 00.00'})
        self.fields['stock'].widget.attrs.update({'placeholder': '0'})

        # Set empty values for new instances
        if self.instance and not self.instance.pk:
            self.fields['product_name'].initial = ''  # Set empty initial value
            self.fields['price'].initial = ''  
            self.fields['stock'].initial = '' 

class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ('username', 'password1', 'password2')

    def clean_password2(self):
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')

        # Custom validation for password requirements
        if password1 and password2:
            if password1 != password2:
                raise forms.ValidationError("The two password fields must match.")
            if len(password1) < 8:
                raise forms.ValidationError("Password must be at least 8 characters long.")
            if not any(char.isdigit() for char in password1):
                raise forms.ValidationError("Password must contain at least one digit.")
            if not any(char.isalpha() for char in password1):
                raise forms.ValidationError("Password must contain at least one letter.")
            if not any(char in "!@#$%^&*()-_+" for char in password1):
                raise forms.ValidationError("Password must contain at least one special character: !@#$%^&*()-_+")

        return password2