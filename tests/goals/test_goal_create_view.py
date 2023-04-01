import pytest
from django.urls import reverse
from rest_framework import status


@pytest.mark.django_db()
class TestGoalCreateView:
    url = reverse('goals:goal-create')

    def test_auth_required(self, client):
        """
        Неавторизованные пользователи не могут создавать цели
        """
        response = client.post(self.url, data={'title': 'test_title', 'category': 2})
        assert response.status_code == status.HTTP_403_FORBIDDEN

