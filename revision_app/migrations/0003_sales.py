# Generated by Django 5.1.2 on 2024-10-22 09:36

import django.db.models.deletion
import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('revision_app', '0002_alter_products_price_alter_products_product_name_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='Sales',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('quantity_sold', models.PositiveBigIntegerField()),
                ('total_price', models.DecimalField(decimal_places=2, max_digits=10)),
                ('date_sold', models.DateTimeField(default=django.utils.timezone.now)),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='revision_app.products')),
            ],
        ),
    ]
