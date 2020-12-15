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
    print(order_data)  # TODO delete string

    try:
        products = order_data['products']
        firstname = order_data['firstname']
        lastname = order_data['lastname']
        phone = order_data['phonenumber']
        address = order_data['address']
    except KeyError:
        return Response("Not enough data", status=status.HTTP_400_BAD_REQUEST)

    for value in order_data.values():
        if value is None or len(value) == 0:
            return Response("Some data was lost", status=status.HTTP_400_BAD_REQUEST)

    if not isinstance(products, list) or not isinstance(firstname, str):
        return Response("Wrong data type", status=status.HTTP_400_BAD_REQUEST)

    order = CustomerOrder.objects.create(  # TODO: move order creation
        firstname=firstname,
        lastname=lastname,
        phone=phone,
        address=address,
    )

    for product in order_data['products']:
        selected_product = product['product']
        if not isinstance(selected_product, int):
            return Response("Wrong product data type", status=status.HTTP_400_BAD_REQUEST)
        order_details = OrderDetails.objects.create(
            quantity=product['quantity']
        )        
        order_details.product_id = selected_product
        order_details.customer_id = order.id
        order_details.save()

    return JsonResponse({})
