from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from rest_framework.serializers import ModelSerializer

from bot.models import TgUser
from core.models import User


class TgUserSerializer(ModelSerializer):
    tg_id = serializers.SlugField(source='chat_id', read_only=True)

    class Meta:
        model = TgUser
        fields = ('tg_id', 'verification_code', 'user_id')
        read_only_fields = ('tg_id', 'user_id')

    def validate_verification_code(self, code):
        try:
            self.tg_user = TgUser.objects.get(verification_code=code)
        except TgUser.DoesNotExist:
            raise ValidationError('Code not valid')

        return code

    def update(self, instance, validated_data):
        return self.tg_user
