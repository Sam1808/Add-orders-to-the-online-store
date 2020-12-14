from django.http import JsonResponse
from django.templatetags.static import static
from rest_framework.decorators import api_view
from rest_framework import status
from rest_framework.response import Response

from .models import Product, CustomerOrder, OrderDetails


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


@api_view(['POST'])
def register_order(request):
    order_data = request.data
    print(order_data)  # delete string

    try:
        products = order_data['products']
    except KeyError:
        return Response("There is no 'products'", status=status.HTTP_400_BAD_REQUEST)

    if not isinstance(products, list) or len(products)==0:
        return Response(f"{order_data['products']} is not list or null", status=status.HTTP_400_BAD_REQUEST)

    order = CustomerOrder.objects.create(
        firstname=order_data['firstname'],
        lastname=order_data['lastname'],
        phone=order_data['phonenumber'],
        address=order_data['address'],
    )

    for product in order_data['products']:
        order_details = OrderDetails.objects.create(
            quantity=product['quantity']
        )        
        order_details.product_id = product['product']
        order_details.customer_id = order.id
        order_details.save()

    return JsonResponse({})
