from django.db import models

# Create your models here.

class Products(models.Model):
    product_name = models.CharField(max_length=200, db_index=True)
    price = models.DecimalField(max_digits=10, decimal_places=2,  db_index=True)
    stock = models.PositiveBigIntegerField(default=0,  db_index=True)

    # string representation of model(default name of model)
    def __str__(self) -> str:
        return super().__str__() + f"({self.product_name})"  # type: ignore

    class Meta:
        verbose_name_plural = 'Products'
        ordering = ['product_name']
