import pytest
from rest_framework.test import APIClient
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


@pytest.fixture
def shop_factory():
    def factory(**kwargs):
        return baker.make('api.Shop', **kwargs)

    return factory


@pytest.fixture
def order_factory():
    def factory(**kwargs):
        return baker.make('api.Order', **kwargs)

    return factory


@pytest.fixture
def order_item_factory():
    def factory(**kwargs):
        return baker.make('api.OrderItem', **kwargs)

    return factory


@pytest.fixture
def product_info_factory():
    def factory(**kwargs):
        return baker.make('api.ProductInfo', **kwargs)

    return factory


@pytest.fixture
def product_factory():
    def factory(**kwargs):
        return baker.make('api.Product', **kwargs)

    return factory


@pytest.fixture
def category_factory():
    def factory(**kwargs):
        return baker.make('api.Category', **kwargs)

    return factory


@pytest.fixture
def contact_factory():
    def factory(**kwargs):
        return baker.make('api.Contact', **kwargs)

    return factory

