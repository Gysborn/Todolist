from unittest.mock import ANY

import pytest
from django.urls import reverse
from rest_framework import status

from goals.models import Board, BoardParticipant


@pytest.mark.django_db()
class TestBoardCreateView:
    url = reverse('goals:board-create')

    def test_auth_required(self, client, ):
        """
        Неавторизованные пользователи не могут создавать доску
        """
        response = client.post(self.url, data={'title': 'test_title'})
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_to_create_deleted_board(self, auth_client, ):
        """
        Нельзя создать удаленную доску
        """
        response = auth_client.post(self.url, data={'title': 'test_title', 'is_deleted': True})
        assert response.status_code == status.HTTP_201_CREATED
        assert response.json()['is_deleted'] is False
        assert Board.objects.last().is_deleted is False

    def test_user_creator_is_owner_board(self, auth_client, user):
        """
        Пользователь создавший доску ее владелец
        """
        response = auth_client.post(self.url, data={'title': 'test_title', })
        assert response.status_code == status.HTTP_201_CREATED
        board_participant = BoardParticipant.objects.get(user_id=user.id)
        assert board_participant.board_id == response.data['id']
        assert board_participant.role == BoardParticipant.Role.owner

    def _serializer_board_response(self, **kwargs):
        data = {
            'id': ANY,
            'created': ANY,
            'updated': ANY,
            'title': ANY,
            'is_deleted': False
        }
        data |= kwargs
        return data
