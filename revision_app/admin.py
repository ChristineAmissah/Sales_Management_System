from django.contrib import admin
from .models import Products, Sale
from django.contrib.auth.models import User
from .forms import ChangePasswordForm 
from django.contrib.auth.hashers import make_password
from django.shortcuts import render

class ProductsAdmin(admin.ModelAdmin):
    list_display = ('unique_key', 'product_name', 'price', 'stock')
    readonly_fields = ('unique_key',)
    search_fields = ('product_name', 'unique_key')

    def numbering(self, obj):
        return obj.id 
    
    numbering.short_description = 'No'  # This sets the column title in the admin

class SaleAdmin(admin.ModelAdmin):
    list_display = ('unique_key', 'product', 'quantity_sold', 'total_price', 'date_sold')
    readonly_fields = ('unique_key', 'total_price')
    search_fields = ('product__product_name', 'unique_key')
    list_filter = ('date_sold',)  # Filter by sale date
    ordering = ('-date_sold',)  # Order by most recent sale
    search_fields = (
        'product__product_name',  # Search by product name
        'unique_key',             # Search by unique key
        'salesperson__username',   # Search by salesperson's username (or the appropriate field)
        'total_price',
        'quantity_sold',
        'date_sold'
    )

class UserAdmin(admin.ModelAdmin):
    actions = ['change_password']

    def change_password(self, request, queryset):
        if 'apply' in request.POST:
            form = ChangePasswordForm(request.POST)
            if form.is_valid():
                new_password = form.cleaned_data['new_password']
                for user in queryset:
                    user.password = make_password(new_password)  # Hash the password
                    user.save()
                self.message_user(request, "Password(s) updated successfully.")
                return None
        else:
            form = ChangePasswordForm()

        return render(request, 'admin/change_password.html', {'form': form, 'users': queryset})

    change_password.short_description = "Change password for selected users"

admin.site.register(Products, ProductsAdmin)
admin.site.register(Sale, SaleAdmin)
admin.site.unregister(User)
admin.site.register(User, UserAdmin)
