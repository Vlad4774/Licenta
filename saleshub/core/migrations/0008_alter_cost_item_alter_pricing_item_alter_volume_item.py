# Generated by Django 5.1.6 on 2025-03-15 19:57

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0007_remove_cost_product_remove_pricing_product_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='cost',
            name='item',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='costs', to='core.item'),
        ),
        migrations.AlterField(
            model_name='pricing',
            name='item',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='pricing', to='core.item'),
        ),
        migrations.AlterField(
            model_name='volume',
            name='item',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='volumes', to='core.item'),
        ),
    ]
