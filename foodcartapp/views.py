from django.http import JsonResponse
from django.templatetags.static import static
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.serializers import ModelSerializer, ValidationError
from django.db import transaction

from .models import Product, CustomerOrder, OrderDetails


class OrderDetailsSerializer(ModelSerializer):
    class Meta:
        model = OrderDetails
        fields = ['product', 'quantity']


class CustomerOrderSerializer(ModelSerializer):
    products = OrderDetailsSerializer(many=True, write_only=True)

    def validate_products(self, value):
        if len(value) == 0:
            raise ValidationError('List is empty')
        return value

    class Meta:
        model = CustomerOrder
        fields = ['id', 'products', 'firstname', 'lastname', 'phonenumber', 'address']


def banners_list_api(request):
    # FIXME move data to db?
    return JsonResponse([
        {
            'title': 'Burger',
            'src': static('burger.jpg'),
            'text': 'Tasty Burger at your door step',
        },
        {
            'title': 'Spices',
            'src': static('food.jpg'),
            'text': 'All Cuisines',
        },
        {
            'title': 'New York',
            'src': static('tasty.jpg'),
            'text': 'Food is incomplete without a tasty dessert',
        }
    ], safe=False, json_dumps_params={
        'ensure_ascii': False,
        'indent': 4,
    })


def product_list_api(request):
    products = Product.objects.select_related('category').available()

    dumped_products = []
    for product in products:
        dumped_product = {
            'id': product.id,
            'name': product.name,
            'price': product.price,
            'special_status': product.special_status,
            'description': product.description,
            'category': {
                'id': product.category.id,
                'name': product.category.name,
            },
            'image': product.image.url,
            'restaurant': {
                'id': product.id,
                'name': product.name,
            }
        }
        dumped_products.append(dumped_product)
    return JsonResponse(dumped_products, safe=False, json_dumps_params={
        'ensure_ascii': False,
        'indent': 4,
    })

@transaction.atomic
@api_view(['POST'])
def register_order(request):

    serializer = CustomerOrderSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    order = CustomerOrder.objects.create(
        firstname=serializer.validated_data['firstname'],
        lastname=serializer.validated_data['lastname'],
        phonenumber=serializer.validated_data['phonenumber'],
        address=serializer.validated_data['address'],
    )

    for each_product in serializer.validated_data['products']:
        order_details = OrderDetails.objects.create(
            quantity=each_product['quantity']
        )        
        order_details.product_id = each_product['product']
        order_details.customer_id = order.id
        order_details.total_price = order_details.get_total_price()
        order_details.save()

    order_content = CustomerOrderSerializer(order)

    return Response(order_content.data)
