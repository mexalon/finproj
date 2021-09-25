import json
import pytest
from django.test import override_settings

from django.urls import reverse
from django_rest_passwordreset.models import ResetPasswordToken
from rest_framework.status import HTTP_200_OK, HTTP_403_FORBIDDEN

from api.models import User, Shop


@pytest.mark.parametrize(
    ['password', 'expected_status'],
    (
            ('123456', False),
            ('VEryLongAndComplicatedPassWith8274652936fnd!!!@@@', True)
    )
)
@pytest.mark.django_db
def test_user_create(api_client, password, expected_status):
    """Тест созданя пользователя """
    some_user = {
        "first_name": "testfirstname",
        "last_name": "testlastname",
        "email": "somemail@gmail.com",
        "password": password,
        "company": "wygfk",
        "position": "ehgcwaekurgu"
    }

    url = reverse("api:user-register")
    resp = api_client.post(url, data=some_user)

    assert resp.status_code == HTTP_200_OK
    assert resp.json().get('Status') is expected_status


@pytest.mark.django_db
def test_user_confirm(api_client, user_factory, confirm_email_token_factory):
    """Тест конфирмации пользователя """
    u = user_factory()
    t = confirm_email_token_factory()
    u.confirm_email_tokens.add(t)

    url = reverse("api:user-register-confirm")

    resp = api_client.post(url, data={"email": u.email, "token": "wrong_key"})
    assert resp.status_code == HTTP_200_OK
    assert resp.json().get('Status') is False

    resp = api_client.post(url, data={"email": u.email, "token": t.key})
    assert resp.status_code == HTTP_200_OK
    assert resp.json().get('Status') is True


@pytest.mark.parametrize(
    ['password', 'expected_status'],
    (
            ('123456', False),
            ('VEryLongAndComplicatedPassWith8274652936fnd!!!@@@', True)
    )
)
@pytest.mark.django_db
def test_user_login(api_client, user_factory, password, expected_status):
    """Тест логина """
    somemail = "somemail@gmail.com"
    somepass = "VEryLongAndComplicatedPassWith8274652936fnd!!!@@@"

    some_user = {
        "first_name": "testfirstname",
        "last_name": "testlastname",
        "email": somemail,
        "password": somepass,
        "company": "wygfk",
        "position": "ehgcwaekurgu"
    }

    url = reverse("api:user-register")
    resp = api_client.post(url, data=some_user)
    assert resp.json().get('Status') is True

    u = User.objects.get(email=somemail)
    u.is_active = True
    u.save()

    url = reverse("api:user-login")
    resp = api_client.post(url, data={"email": somemail, "password": password})
    assert resp.status_code == HTTP_200_OK
    assert resp.json().get('Status') is expected_status


@pytest.mark.django_db
def test_user_details(api_client, user_factory):
    """Тест редактирования пользоваткля """
    url = reverse("api:user-details")
    u = user_factory()
    resp = api_client.get(url)

    assert resp.status_code == HTTP_403_FORBIDDEN
    assert resp.json().get('Status') is False

    api_client.force_authenticate(user=u)
    resp = api_client.get(url)
    assert resp.status_code == HTTP_200_OK
    assert resp.json().get('email') == u.email

    resp = api_client.post(url, data={"type": "shop"})
    resp = api_client.get(url)
    assert resp.json().get('type') == "shop"


@pytest.mark.django_db
def test_user_pass_reset(api_client, user_factory):
    """Тест смены пароля пользователя """
    url = reverse("api:password-reset")
    u = user_factory()
    api_client.force_authenticate(user=u)
    """сброс"""
    resp = api_client.post(url, data={"email": u.email})
    assert resp.status_code == HTTP_200_OK

    t = ResetPasswordToken.objects.get(user=u)

    """новый пароль"""
    url = reverse("api:password-reset-confirm")
    resp = api_client.post(url, data={"email": u.email, "password": "New_passsword_123", "token": t.key})
    assert resp.json().get('status') == "OK"

    """логин с новым паролем"""
    url = reverse("api:user-login")
    resp = api_client.post(url, data={"email": u.email, "password": "New_passsword_123"})
    assert resp.status_code == HTTP_200_OK
    assert resp.json().get('Status') is True


@pytest.mark.django_db
def test_user_contacts(api_client, user_factory):
    """Тест контактов пользователя """
    url = reverse("api:user-contact")
    u = user_factory()
    api_client.force_authenticate(user=u)
    contact = {
        "city": "Moscow",
        "street": "Some str.",
        "phone": "+9991234567"
    }

    """создание"""
    resp = api_client.post(url, data=contact)
    assert resp.status_code == HTTP_200_OK

    resp = api_client.get(url)
    for entry in list(contact.keys()):
        assert resp.json()[0].get(entry) == contact.get(entry)

    c = u.contacts.first().id

    """редактирование"""
    resp = api_client.put(url, data={"building": 1, "id": c})
    assert resp.status_code == HTTP_200_OK
    assert resp.json().get('Status') is True
    assert u.contacts.get(id=c).building == '1'

    """удаление"""
    resp = api_client.delete(url, data={"items": c})
    assert resp.status_code == HTTP_200_OK
    assert resp.json().get('Status') is True


@pytest.mark.django_db
def test_partner_upload(api_client, user_factory):
    """Тест загрузки працса """
    price = 'https://raw.githubusercontent.com/mexalon/finproj/master/mymazon/data_for_ulpoad/shop1.yml'
    url = reverse("api:partner-update")
    u = user_factory()
    api_client.force_authenticate(user=u)

    """без статуса магазина"""
    resp = api_client.post(url, data={"url": price})
    assert resp.status_code == HTTP_403_FORBIDDEN
    assert resp.json().get('Status') is False

    """смена статуса"""
    resp = api_client.post(reverse("api:user-details"), data={"type": "shop"})
    resp = api_client.get(reverse("api:user-details"))
    assert resp.json().get('type') == "shop"

    """загрузка прайса"""
    resp = api_client.post(url, data={"url": price})
    assert resp.status_code == HTTP_200_OK
    assert resp.json().get('Status') is True

    s = Shop.objects.filter(user=u).first()
    assert s.name == "Связной"


@pytest.mark.django_db
def test_partner_state(api_client, user_factory, shop_factory):
    """Тест статуса магазина """
    url = reverse("api:partner-state")
    s = shop_factory()
    u = user_factory()
    u.shop = s
    u.save()
    api_client.force_authenticate(user=u)

    """пользователь не магазин"""
    resp = api_client.get(url)
    assert resp.status_code == HTTP_403_FORBIDDEN
    assert resp.json().get('Status') is False

    """смена типа пользователя"""
    resp = api_client.post(reverse("api:user-details"), data={"type": "shop"})

    """с правильным типом пользователя"""
    resp = api_client.get(url)
    assert resp.status_code == HTTP_200_OK
    assert resp.json().get('state') is True

    """смена статуса"""
    resp = api_client.post(url, data={"state": "off"})
    assert resp.status_code == HTTP_200_OK
    assert resp.json().get('Status') is True


@override_settings(CELERY_ALWAYS_EAGER=True)
@pytest.mark.django_db
def test_partner_orders(api_client, user_factory, shop_factory, order_factory, order_item_factory,
                        product_info_factory, product_factory, category_factory):
    """Тест получения заказов поставщиком """
    """Нужен запущенный сервер редис! docker run --name=redis -p 6379:6379 redis"""
    url = reverse("api:partner-orders")

    u = user_factory(type='shop', email='example@gmail.com')
    s = shop_factory(user=u)
    cust = user_factory()
    cat = category_factory()
    p = product_factory(category=cat)
    pi = product_info_factory(product=p, shop=s)
    o = order_factory(user=cust, state='new')
    oi = order_item_factory(order=o, product_info=pi, quantity=1)

    api_client.force_authenticate(user=u)

    resp = api_client.get(url)
    assert resp.status_code == HTTP_200_OK
    assert resp.json()[0].get('id', False)


@pytest.mark.django_db
def test_products(api_client, user_factory, shop_factory, order_factory,
                  product_info_factory, product_factory, category_factory):
    """Тест поиска продукта """

    url = reverse("api:products")

    s = shop_factory()
    cust = user_factory()
    cat = category_factory()
    p = product_factory(category=cat)
    pi = product_info_factory(product=p, shop=s)

    api_client.force_authenticate(user=cust)
    shop_id = s.id
    category_id = cat.id

    resp = api_client.get(url, shop_id=s.id, category_id=cat.id)
    assert resp.status_code == HTTP_200_OK
    assert resp.json()[0].get('id', False)


@pytest.mark.django_db
def test_basket(api_client, user_factory, shop_factory, order_factory, order_item_factory,
                product_info_factory, product_factory, category_factory):
    """Тест корзины """
    url = reverse("api:basket")

    s = shop_factory()
    cust = user_factory()
    cat = category_factory()
    p = product_factory(category=cat)
    pi = product_info_factory(product=p, shop=s)
    o = order_factory(user=cust, state='basket')
    # oi = order_item_factory(order=o)

    api_client.force_authenticate(user=cust)

    resp = api_client.get(url)
    assert resp.status_code == HTTP_200_OK
    assert resp.json()[0].get('id', False)

    """товар --> корзина"""
    b = {'items': json.dumps([{'product_info': 1, 'quantity': 11}])}
    """вообще не очевидный формат для данных :/"""
    resp = api_client.post(url, data=b)
    assert resp.status_code == HTTP_200_OK

    """изменение количества"""
    b = {"items": json.dumps([{"id": 1, "quantity": 23}, ])}
    resp = api_client.put(url, data=b)
    assert resp.status_code == HTTP_200_OK

    """удаление из корзины"""
    b = {"items": 1}
    resp = api_client.delete(url, data=b)
    assert resp.status_code == HTTP_200_OK


@pytest.mark.parametrize(["is_staff", "exp_status"],
                         (
                                 (False, HTTP_403_FORBIDDEN),
                                 (True, HTTP_200_OK)
                         )
                         )
@pytest.mark.django_db
def test_order(api_client, user_factory, shop_factory, order_factory, order_item_factory,
               product_info_factory, product_factory, category_factory, contact_factory, is_staff, exp_status):
    """Тест заказов """
    url = reverse("api:order-list")

    s = shop_factory()
    cust = user_factory()
    cont = contact_factory(user=cust)
    cat = category_factory()
    p = product_factory(category=cat)
    pi = product_info_factory(product=p, shop=s)
    o = order_factory(user=cust, state='basket')
    oi = order_item_factory(order=o, product_info=pi, quantity=1)

    """размещение заказа"""
    o_id = o.id
    c_id = cont.id
    b = {'id': o_id, 'contact': c_id}
    cust.is_staff = is_staff
    cust.save()

    api_client.force_authenticate(user=cust)
    resp = api_client.post(url, data=b)
    assert resp.status_code == HTTP_200_OK
    assert resp.json().get('Status') is True

    """список заказов"""
    resp = api_client.get(url)
    assert resp.status_code == HTTP_200_OK
    assert resp.json()[0].get('id', False)

    """извлечение заказа"""
    url = reverse("api:order-detail", args=[o_id])
    resp = api_client.get(url)
    assert resp.status_code == HTTP_200_OK
    assert resp.json().get('id', False)

    """изменение статуса заказа, доступно только для админа"""
    url = reverse("api:order-detail", args=[o_id])
    b = {'state': 'confirmed'}
    resp = api_client.patch(url, data=b)
    assert resp.status_code == exp_status
