import requests
from django import forms
from django.shortcuts import redirect, render
from django.views import View
from django.urls import reverse_lazy
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth import authenticate, login
from django.contrib.auth import views as auth_views
from django.db.models import Sum
from django.core.cache import cache

from environs import Env
from geopy import distance

from foodcartapp.models import CustomerOrder, RestaurantMenuItem


class Login(forms.Form):
    username = forms.CharField(
        label='Логин', max_length=75, required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Укажите имя пользователя'
        })
    )
    password = forms.CharField(
        label='Пароль', max_length=75, required=True,
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Введите пароль'
        })
    )


class LoginView(View):
    def get(self, request, *args, **kwargs):
        form = Login()
        return render(request, "login.html", context={
            'form': form
        })

    def post(self, request):
        form = Login(request.POST)

        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']

            user = authenticate(request, username=username, password=password)
            if user:
                login(request, user)
                if user.is_staff:  # FIXME replace with specific permission
                    return redirect("restaurateur:RestaurantView")
                return redirect("start_page")

        return render(request, "login.html", context={
            'form': form,
            'ivalid': True,
        })


class LogoutView(auth_views.LogoutView):
    next_page = reverse_lazy('restaurateur:login')


def is_manager(user):
    return user.is_staff  # FIXME replace with specific permission


def fetch_coordinates(apikey, place):
    base_url = "https://geocode-maps.yandex.ru/1.x"
    params = {"geocode": place, "apikey": apikey, "format": "json"}
    response = requests.get(base_url, params=params)
    response.raise_for_status()
    places_found = response.json()['response']['GeoObjectCollection']['featureMember']
    most_relevant = places_found[0]
    lon, lat = most_relevant['GeoObject']['Point']['pos'].split(" ")
    return lat, lon

@user_passes_test(is_manager, login_url='restaurateur:login')
def view_products(request):
    restaurants = list(Restaurant.objects.order_by('name'))
    products = list(Product.objects.prefetch_related('menu_items'))

    default_availability = {restaurant.id: False for restaurant in restaurants}
    products_with_restaurants = []
    for product in products:

        availability = {
            **default_availability,
            **{item.restaurant_id: item.availability for item in product.menu_items.all()},
        }
        orderer_availability = [availability[restaurant.id] for restaurant in restaurants]

        products_with_restaurants.append(
            (product, orderer_availability)
        )

    return render(request, template_name="products_list.html", context={
        'products_with_restaurants': products_with_restaurants,
        'restaurants': restaurants,
    })


@user_passes_test(is_manager, login_url='restaurateur:login')
def view_restaurants(request):
    return render(request, template_name="restaurants_list.html", context={
        'restaurants': Restaurant.objects.all(),
    })


@user_passes_test(is_manager, login_url='restaurateur:login')
def view_orders(request):

    env = Env()
    env.read_env()

    yandex_api = env.str("YANDEX_API")

    all_orders = CustomerOrder.objects.annotate(total_order_price=Sum('customer_items__total_price')).order_by('-id')
    all_restaurant_menu_item = RestaurantMenuItem.objects.all()

    orders_and_existence = {}

    for order in all_orders:

        existence_list = cache.get(str(order.id))
        if not existence_list:
            existence_list = []
            for item in order.customer_items.all():

                product_places = all_restaurant_menu_item.filter(
                    product__id=item.product.id
                )
                all_existence = []
                for product in product_places:
                    if product.availability:
                        existence = product.restaurant.name
                        address = product.restaurant.address
                        all_existence.append(f'{existence} - {address}')

                if len(existence_list) == 0:
                    existence_list = all_existence.copy()
                    continue
                # to fetch unique restaurant
                existence_list = set(existence_list) & set(all_existence)
                cache.set(str(order.id), existence_list, 3600)

        existence_coordinates = []
        for existence in existence_list:
            restaurant = existence.split('-')
            restaurant_coordinates = cache.get(restaurant[1])
            if not restaurant_coordinates:
                restaurant_coordinates = fetch_coordinates(
                    yandex_api,
                    restaurant[1],
                )
                cache.set(restaurant[1], restaurant_coordinates, 3600)

            order_coordinates = cache.get(order.address)
            if not order_coordinates:
                order_coordinates = fetch_coordinates(
                    yandex_api,
                    order.address,
                )
                cache.set(order.address, order_coordinates, 600)

            order_distance = round(distance.distance(
                restaurant_coordinates,
                order_coordinates,
                ).km, 3
            )
            new_existence = f'{restaurant[0]} - {order_distance} км'
            existence_coordinates.append(new_existence)

        orders_and_existence[order.id] = sorted(
            existence_coordinates,
            key=lambda x: float(x.split('-')[1][1:-3])
        )

    return render(request, template_name='order_items.html', context={
        'order_items': all_orders,
        'orders_and_existence': orders_and_existence,
        }
    )
