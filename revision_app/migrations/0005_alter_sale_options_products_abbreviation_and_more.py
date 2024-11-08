# Generated by Django 5.1.2 on 2024-10-22 16:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('revision_app', '0004_rename_sales_sale'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='sale',
            options={'verbose_name': 'Sale', 'verbose_name_plural': 'Sales'},
        ),
        migrations.AddField(
            model_name='products',
            name='abbreviation',
            field=models.CharField(blank=True, editable=False, max_length=2),
        ),
        migrations.AddField(
            model_name='sale',
            name='abbreviation',
            field=models.CharField(blank=True, editable=False, max_length=2),
        ),
    ]
