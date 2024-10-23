# from django.contrib import admin
# from .models import Products, Sale

# class SalesAdmin(admin.ModelAdmin):
#     list_display = ('product', 'quantity_sold', 'total_price', 'date_sold')
#     search_fields = ('product__product_name',)  # Search by product name



from django.contrib import admin
from .models import Products, Sale

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

admin.site.register(Products, ProductsAdmin)
admin.site.register(Sale, SaleAdmin)