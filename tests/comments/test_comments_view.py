import pytest
from django.urls import reverse
from rest_framework import status


@pytest.mark.django_db()
class TestCommentDestroyView:

    def test_owner_delete_is_ok(
            self, client, goal_factory,
            user_factory, goal_category_factory,
            goal_comment_factory
    ):
        """
        Владелец может удалить  коммент
        """
        user = user_factory.create(username='John')
        client.force_login(user)
        cat = goal_category_factory.create(user=user)
        goal = goal_factory.create(user=user, category=cat)
        goal_comm = goal_comment_factory.create(goal=goal, user=user)

        url = reverse('goals:comments', kwargs={'pk': goal_comm.id})
        response = client.delete(url)
        assert response.status_code == status.HTTP_204_NO_CONTENT

    def test_not_auth_user_failed_to_delete(
            self, client, goal_factory,
            user_factory, goal_category_factory,
            goal_comment_factory
    ):
        """
        Не авторизованный пользователь не может удалить  коммент
        """
        user = user_factory.create(username='John')
        cat = goal_category_factory.create(user=user)
        goal = goal_factory.create(user=user, category=cat)
        goal_comm = goal_comment_factory.create(goal=goal, user=user)

        url = reverse('goals:comments', kwargs={'pk': goal_comm.id})
        response = client.delete(url)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_not_owner_failed_delete(
            self, client, goal_factory,
            user_factory, goal_category_factory,
            goal_comment_factory
    ):
        """
        Не ладелец не может удалить  коммент
        """
        user = user_factory.create(username='John')
        user_2 = user_factory.create(username='Violette')
        client.force_login(user_2)
        cat = goal_category_factory.create(user=user)
        goal = goal_factory.create(user=user, category=cat)
        goal_comm = goal_comment_factory.create(goal=goal, user=user)

        url = reverse('goals:comments', kwargs={'pk': goal_comm.id})
        response = client.delete(url)
        assert response.status_code == status.HTTP_404_NOT_FOUND
