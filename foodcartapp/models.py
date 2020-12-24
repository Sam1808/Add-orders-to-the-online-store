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
    STATUSES = [
        ('NEW_ORDER', 'Необработанный'),
        ('IN_PROGRESS', 'В работе'),
        ('DELEVERY', 'Доставка'),
        ('COMPLETE', 'Выполнен'),
    ]

    PAYMENT_TYPE = [
        ('ON_LINE', 'Электронно'),
        ('CASH', 'Наличными'),
    ]

    firstname = models.CharField('имя', max_length=30)
    lastname = models.CharField('фамилия', max_length=30)
    phonenumber = models.CharField('телефон', max_length=30)
    address = models.CharField('адрес', max_length=100)
    order_status = models.CharField('статус', max_length=15, choices=STATUSES, default=STATUSES[0][0])
    comment = models.TextField('комментарий', max_length=200, blank=True)
    registrated_datetime = models.DateTimeField('зарегистрирован', auto_now_add=True, null=True)
    called_datetime = models.DateTimeField('в обработке', null=True, blank=True)
    delivered_datetime = models.DateTimeField('доставлен', null=True, blank=True)
    payment_type = models.CharField('способ оплаты', max_length=10, choices=PAYMENT_TYPE, default=PAYMENT_TYPE[0][0])

    def __str__(self):
        return f"{self.firstname} {self.lastname} {self.address}"

    class Meta:
        verbose_name = 'заказ'
        verbose_name_plural = 'заказы'


class OrderDetails(models.Model):
    product = models.ForeignKey(Product, null=True, on_delete=models.CASCADE, related_name='order_items', verbose_name='бургер')
    quantity = models.PositiveIntegerField('количество')
    customer = models.ForeignKey(CustomerOrder, null=True, on_delete=models.CASCADE, related_name='customer_items')
    total_price = models.DecimalField('Итого цена', max_digits=8, decimal_places=2, default=0)

    def get_total_price(self):
        return (self.quantity * self.product_id.price)

    class Meta:
        verbose_name_plural = 'детали заказа'
