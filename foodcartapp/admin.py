from django.contrib import admin
from django.shortcuts import reverse
from django.utils.html import format_html
from django.http import HttpResponseRedirect

from .models import Product
from .models import ProductCategory
from .models import Restaurant
from .models import RestaurantMenuItem
from .models import CustomerOrder
from .models import OrderDetails


class RestaurantMenuItemInline(admin.TabularInline):
    model = RestaurantMenuItem
    extra = 0


class OrderDetailsInline(admin.TabularInline):
    model = OrderDetails

@admin.register(Restaurant)
class RestaurantAdmin(admin.ModelAdmin):
    search_fields = [
        'name',
        'address',
        'contact_phone',
    ]
    list_display = [
        'name',
        'address',
        'contact_phone',
    ]
    inlines = [
        RestaurantMenuItemInline
    ]


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = [
        'get_image_list_preview',
        'name',
        'category',
        'price',
    ]
    list_display_links = [
        'name',
    ]
    list_filter = [
        'category',
    ]
    search_fields = [
        # FIXME SQLite can not convert letter case for cyrillic words properly, so search will be buggy.
        # Migration to PostgreSQL is necessary
        'name',
        'category',
    ]

    inlines = [
        RestaurantMenuItemInline
    ]
    fieldsets = (
        ('Общее', {
            'fields': [
                'name',
                'category',
                'image',
                'get_image_preview',
                'price',
            ]
        }),
        ('Подробно', {
            'fields': [
                'special_status',
                'description',
            ],
            'classes': [
                'wide'
            ],
        }),
    )

    readonly_fields = [
        'get_image_preview',
    ]

    class Media:
        css = {
            "all": (
                "admin/foodcartapp.css",
            )
        }

    def get_image_preview(self, obj):
        if not obj.image:
            return 'выберите картинку'
        return format_html('<img src="{url}" height="200"/>', url=obj.image.url)
    get_image_preview.short_description = 'превью'

    def get_image_list_preview(self, obj):
        if not obj.image or not obj.id:
            return 'нет картинки'
        edit_url = reverse('admin:foodcartapp_product_change', args=(obj.id,))
        return format_html('<a href="{edit_url}"><img src="{src}" height="50"/></a>', edit_url=edit_url, src=obj.image.url)
    get_image_list_preview.short_description = 'превью'


@admin.register(ProductCategory)
class ProductAdmin(admin.ModelAdmin):
    pass

class RestaurantMenuItemInline(admin.TabularInline):
    model = RestaurantMenuItem
    extra = 0

@admin.register(CustomerOrder)
class CustomerOrderAdmin(admin.ModelAdmin):
    list_display = [
        'firstname',
        'lastname',
        'phonenumber',
        'address',
        'order_status',
        'registrated_datetime',
    ]
    list_display_links = [
        'firstname',
        'lastname',
        'phonenumber',
        'address',
    ]

    inlines = [
        OrderDetailsInline
    ]

    fieldsets = (
        ('Заказчик', {
            'fields': [
                'firstname',
                'lastname',
                'phonenumber',
                'address',
            ]
        }),
        ('Описание заказа', {
            'fields': [
                'order_status',
                'payment_type',
                'comment',
                'registrated_datetime',
                'called_datetime',
                'delivered_datetime',
            ],
        }),
    )

    readonly_fields = ['registrated_datetime']

    def field2(self, obj):  # to show non-editable order datatime info
        return '*** CLASSIFIED *** {}'.format(obj.registrated_datetime)

    def response_post_save_change(self, request, obj):
        res = super().response_post_save_change(request, obj)
        if "next" in request.GET:
            return HttpResponseRedirect(request.GET['next'])
        else:
            return res
