import json
from distutils.util import strtobool

from django.core.exceptions import ValidationError
from django.core.validators import URLValidator
from django.db.models import Sum, F
from django.http import JsonResponse
from requests import get
from rest_framework import throttling
from rest_framework.response import Response
from rest_framework.views import APIView
from yaml import load as load_yaml, Loader

from .models import Shop, Category, ProductInfo, Product, Parameter, ProductParameter, Order
from .serializers import ShopSerializer, OrderSerializer
from .tasks import send_email



class PartnerUpdate(APIView):
    """
    Класс для обновления прайса от поставщика
    """
    throttle_scope = 'partner_upload'

    def post(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return JsonResponse({'Status': False, 'Error': 'Log in required'}, status=403)

        if request.user.type != 'shop':
            return JsonResponse({'Status': False, 'Error': 'Только для магазинов'}, status=403)

        url = request.data.get('url')
        if url:
            validate_url = URLValidator()
            try:
                validate_url(url)
            except ValidationError as e:
                return JsonResponse({'Status': False, 'Error': str(e)})
            else:
                stream = get(url).content

                data = load_yaml(stream, Loader=Loader)
                try:
                    shop, _ = Shop.objects.get_or_create(name=data['shop'], user_id=request.user.id)
                except Exception:
                    return JsonResponse({'Status': False, 'Errors': 'Ошибка создания магазина'})

                for category in data['categories']:
                    try:
                        category_object, _ = Category.objects.get_or_create(id=category['id'], name=category['name'])
                    except Exception:
                        return JsonResponse({'Status': False, 'Errors': 'Ошибка создания категории'})
                    else:
                        category_object.shops.add(shop.id)
                        category_object.save()

                ProductInfo.objects.filter(shop_id=shop.id).delete()

                for item in data['goods']:
                    try:
                        product, _ = Product.objects.get_or_create(name=item['name'], category_id=item['category'])
                    except Exception:
                        return JsonResponse({'Status': False, 'Errors': 'Ошибка категории продукта'})
                    else:
                        product_info = ProductInfo.objects.create(product_id=product.id,
                                                                  external_id=item['id'],
                                                                  model=item['model'],
                                                                  price=item['price'],
                                                                  price_rrc=item['price_rrc'],
                                                                  quantity=item['quantity'],
                                                                  shop_id=shop.id)
                        for name, value in item['parameters'].items():
                            parameter_object, _ = Parameter.objects.get_or_create(name=name)
                            ProductParameter.objects.create(product_info_id=product_info.id,
                                                            parameter_id=parameter_object.id,
                                                            value=value)

                return JsonResponse({'Status': True})

        return JsonResponse({'Status': False, 'Errors': 'Не указаны все необходимые аргументы'})


class PartnerState(APIView):
    """
    Класс для работы со статусом поставщика
    """

    # получить текущий статус
    def get(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return JsonResponse({'Status': False, 'Error': 'Log in required'}, status=403)

        if request.user.type != 'shop':
            return JsonResponse({'Status': False, 'Error': 'Только для магазинов'}, status=403)

        shop = request.user.shop
        serializer = ShopSerializer(shop)
        return Response(serializer.data)

    # изменить текущий статус
    def post(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return JsonResponse({'Status': False, 'Error': 'Log in required'}, status=403)

        if request.user.type != 'shop':
            return JsonResponse({'Status': False, 'Error': 'Только для магазинов'}, status=403)
        state = request.data.get('state')
        if state:
            try:
                Shop.objects.filter(user_id=request.user.id).update(state=strtobool(state))
                return JsonResponse({'Status': True})
            except ValueError as error:
                return JsonResponse({'Status': False, 'Errors': str(error)})

        return JsonResponse({'Status': False, 'Errors': 'Не указаны все необходимые аргументы'})


class PartnerOrders(APIView):
    """
    Класс для получения заказов поставщиками
    """

    def get(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return JsonResponse({'Status': False, 'Error': 'Log in required'}, status=403)

        if request.user.type != 'shop':
            return JsonResponse({'Status': False, 'Error': 'Только для магазинов'}, status=403)

        order = Order.objects.filter(
            ordered_items__product_info__shop__user_id=request.user.id).exclude(state='basket').prefetch_related(
            'ordered_items__product_info__product__category',
            'ordered_items__product_info__product_parameters__parameter').select_related('contact').annotate(
            total_sum=Sum(F('ordered_items__quantity') * F('ordered_items__product_info__price'))).distinct()

        serializer = OrderSerializer(order, many=True)
        content = json.dumps(serializer.data, ensure_ascii=False)
        send_email.delay("Заказ от клиента", f"Во вложени", [request.user.email], content)
        return Response(serializer.data)
