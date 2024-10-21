from django.contrib import admin
from .models import Products

class ProductAdmin(admin.ModelAdmin):
    list_display = ('numbering', 'product_name', 'price', 'stock')
    search_fields = ('numbering', 'product_name', 'price', 'stock')

    def numbering(self, obj):
        return obj.id 
    
    numbering.short_description = 'No'  # This sets the column title in the admin

# Register the model and the customized admin class
admin.site.register(Products, ProductAdmin)
