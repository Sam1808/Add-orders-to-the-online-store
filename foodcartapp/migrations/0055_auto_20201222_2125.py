# Generated by Django 3.0.7 on 2020-12-22 21:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('foodcartapp', '0054_customerorder_comment'),
    ]

    operations = [
        migrations.AddField(
            model_name='customerorder',
            name='called_datetime',
            field=models.DateTimeField(null=True, verbose_name='в обработке'),
        ),
        migrations.AddField(
            model_name='customerorder',
            name='delivered_datetime',
            field=models.DateTimeField(null=True, verbose_name='доставлен'),
        ),
        migrations.AddField(
            model_name='customerorder',
            name='registrated_datetime',
            field=models.DateTimeField(auto_now_add=True, null=True, verbose_name='зарегистирован'),
        ),
    ]
