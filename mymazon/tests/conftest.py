import pytest

from django.conf import settings


from rest_framework.test import APIClient, force_authenticate
from model_bakery import baker


@pytest.fixture
def api_client():
    c = APIClient()
    return c


@pytest.fixture
def user_factory():
    def factory(**kwargs):
        return baker.make('api.User', **kwargs)

    return factory

@pytest.fixture
def confirm_email_token_factory():
    def factory(**kwargs):
        return baker.make('api.ConfirmEmailToken', **kwargs)

    return factory

# @pytest.fixture
# def order_factory():
#     def factory(**kwargs):
#         return baker.make('Order', **kwargs)
#
#     return factory
#
# @pytest.fixture
# def shop_factory():
#     def factory(**kwargs):
#         return baker.make('Shop', **kwargs)
#
#     return factory
#
# @pytest.fixture
# def product_factory():
#     def factory(**kwargs):
#         return baker.make('Product', **kwargs)
#
#     return factory
#
# @pytest.fixture
# def product_parameter_factory():
#     def factory(**kwargs):
#         return baker.make('ProductParameter', **kwargs)
#
#     return factory
#
# @pytest.fixture
# def parameter_factory():
#     def factory(**kwargs):
#         return baker.make('Parameter', **kwargs)
#
#     return factory
#
#
# @pytest.fixture
# def product_info_factory():
#     def factory(**kwargs):
#         return baker.make('ProductInfo', **kwargs)
#
#     return factory
#
#
#
