# Generated by Django 3.0.7 on 2020-12-10 13:44

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('foodcartapp', '0038_auto_20201210_1343'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customerorder',
            name='order_details',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='customer_items', to='foodcartapp.OrderDetails'),
        ),
    ]
