from django.contrib.auth.models import User
from django.db import models


class Restaurant(models.Model):
    name = models.CharField('название', max_length=50)
    address = models.CharField('адрес', max_length=100, blank=True)
    contact_phone = models.CharField('контактный телефон', max_length=50, blank=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'ресторан'
        verbose_name_plural = 'рестораны'


class ProductQuerySet(models.QuerySet):
    def available(self):
        return self.distinct().filter(menu_items__availability=True)


class ProductCategory(models.Model):
    name = models.CharField('название', max_length=50)

    class Meta:
        verbose_name = 'категория'
        verbose_name_plural = 'категории'

    def __str__(self):
        return self.name


class Product(models.Model):
    name = models.CharField('название', max_length=50)
    category = models.ForeignKey(ProductCategory, null=True, blank=True, on_delete=models.SET_NULL,
                                 verbose_name='категория', related_name='products')
    price = models.DecimalField('цена', max_digits=8, decimal_places=2)
    image = models.ImageField('картинка')
    special_status = models.BooleanField('спец.предложение', default=False, db_index=True)
    description = models.TextField('описание', max_length=200, blank=True)

    objects = ProductQuerySet.as_manager()

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'товар'
        verbose_name_plural = 'товары'


class RestaurantMenuItem(models.Model):
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE, related_name='menu_items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='menu_items')
    availability = models.BooleanField('в продаже', default=True, db_index=True)

    def __str__(self):
        return f"{self.restaurant.name} - {self.product.name}"

    class Meta:
        verbose_name = 'пункт меню ресторана'
        verbose_name_plural = 'пункты меню ресторана'
        unique_together = [
            ['restaurant', 'product']
        ]


class CustomerOrder(models.Model):
    firstname = models.CharField('имя', max_length=30)
    lastname = models.CharField('фамилия', max_length=30)
    phone = models.CharField('телефон', max_length=30)
    address = models.CharField('адрес', max_length=30)

    def __str__(self):
        return f"{self.firstname} {self.lastname} {self.address}"

    class Meta:
        verbose_name = 'заказ'
        verbose_name_plural = 'заказы'


class OrderDetails(models.Model):
    product = models.ForeignKey(Product, null=True, on_delete=models.CASCADE, related_name='order_items', verbose_name='бургер')
    quantity = models.PositiveIntegerField('количество', default=0)
    customer = models.ForeignKey(CustomerOrder, null=True, on_delete=models.CASCADE, related_name='customer_items')

    class Meta:
        verbose_name_plural = 'детали заказа'