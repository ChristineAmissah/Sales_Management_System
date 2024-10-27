from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User

class Products(models.Model):
    product_name = models.CharField(max_length=200, db_index=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, db_index=True)
    stock = models.PositiveBigIntegerField(default=0, db_index=True)
    unique_key = models.CharField(
        max_length=2,
        blank=True,
        editable=False,
        unique=True
    )

    def save(self, *args, **kwargs):
        if self.product_name:
            self.unique_key = f"{self.product_name[0].lower()}{self.product_name[-1].lower()}"
        super().save(*args, **kwargs)

    def __str__(self):
        return self.product_name

    class Meta:
        verbose_name_plural = 'Products'
        ordering = ['product_name']


class Sale(models.Model):
    product = models.ForeignKey(Products, on_delete=models.CASCADE)
    quantity_sold = models.PositiveBigIntegerField()
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    salesperson = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)  # Link the sale to a user
    date_sold = models.DateTimeField(default=timezone.now)
    unique_key = models.CharField(
        max_length=2,
        blank=True,
        editable=False
    )

    def save(self, *args, **kwargs):
         # Calculate total price
        self.total_price = self.quantity_sold * self.product.price
        self.unique_key = self.product.unique_key
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.product.product_name} - {self.quantity_sold} units"

    class Meta:
        verbose_name = 'Sale'
        verbose_name_plural = 'Sales'