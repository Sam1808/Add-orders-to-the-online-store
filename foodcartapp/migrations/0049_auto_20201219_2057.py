# Generated by Django 3.0.7 on 2020-12-19 20:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('foodcartapp', '0048_auto_20201217_1212'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customerorder',
            name='address',
            field=models.CharField(max_length=100, verbose_name='адрес'),
        ),
    ]