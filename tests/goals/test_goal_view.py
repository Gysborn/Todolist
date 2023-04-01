import pytest
from django.urls import reverse
from rest_framework import status


@pytest.mark.django_db()
class TestGoalRetrieveView:
    @pytest.fixture(autouse=True)
    def setup(self, goal):
        self.url = self.get_url(goal.id)

    @staticmethod
    def get_url(goal_pk: int):
        return reverse('goals:goal', kwargs={'pk': goal_pk})

    def test_auth_required(self, client, ):
        """
        Неавторизованные пользователи не могут просматривать цель
        """
        response = client.get(self.url)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_auth_required_delete_goal(self, client, ):
        """
        Неавторизованные пользователи не могут удалять цели
        """
        response = client.delete(self.url)
        assert response.status_code == status.HTTP_403_FORBIDDEN
