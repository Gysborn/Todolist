import pytest
from django.urls import reverse
from rest_framework import status


@pytest.mark.django_db()
class TestCoreSignupView:
    url = reverse('core:signup')

    def test_signup_is_ok(self, client):
        """
        Проверяет корректность регистрации
        """
        response = client.post(self.url, data={
            'username': 'test_user',
            'password': 'rfhfvtkm',
            'password_repeat': 'rfhfvtkm'
        })
        assert response.status_code == status.HTTP_201_CREATED

    def test_signup_passwords_dont_match(self, client):
        """
        Пароли не совпадают
        """
        response = client.post(self.url, data={
            'username': 'test_user',
            'password': 'rfhfvtkm',
            'password_repeat': 'asdf'
        })
        assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db()
class TestCorerPofileSignupView:
    url = reverse('core:profile')

    def test_get_profile_is_ok(self, auth_client, ):
        """
        Проверяет корректность получения профиля
        """

        response = auth_client.get(self.url)
        assert response.status_code == status.HTTP_200_OK

    def test_get_profile_no_auth_user(self, client, ):
        """
        Неавторизованный пользователь не может просматривать профиль
        """

        response = client.get(self.url)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_login_is_ok(self, client, user_factory, ):
        """
        Корректность работы логина
        """

        user_new = user_factory.create(password='AssertionError')
        response = client.post('/core/login', data={
            'username': user_new.username,
            'password': 'AssertionError',
        })
        assert response.status_code == status.HTTP_200_OK

    def test_login_with_short_pass_ok(self, client, user_factory, ):
        """
        Короткий пароль не пройдет
        """

        user_new = user_factory.create(password='Ass')
        response = client.post('/core/login', data={
            'username': user_new.username,
            'password': 'Ass',
        })
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_login_with_simple_pass_ok(self, client, user_factory, ):
        """
        Простой пароль не пройдет
        """

        user_new = user_factory.create(password='123456789')
        response = client.post('/core/login', data={
            'username': user_new.username,
            'password': '123456789',
        })
        assert response.status_code == status.HTTP_400_BAD_REQUEST
