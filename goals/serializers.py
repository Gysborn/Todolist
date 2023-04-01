from django.db import transaction
from django.utils import timezone
from rest_framework.exceptions import ValidationError, PermissionDenied
from rest_framework.fields import CurrentUserDefault, HiddenField, ChoiceField
from rest_framework.relations import PrimaryKeyRelatedField, SlugRelatedField
from rest_framework.serializers import ModelSerializer

from core.models import User
from core.serialisers import ProfileSerializer
from goals.models import GoalCategory, Goal, GoalComment, Board, BoardParticipant


class GoalCategoryCreateSerializer(ModelSerializer):
    user = HiddenField(default=CurrentUserDefault())

    class Meta:
        model = GoalCategory
        read_only_fields = ("id", "created", "updated", "user", "is_deleted")
        fields = "__all__"


class GoalCategorySerializer(ModelSerializer):
    user = ProfileSerializer(read_only=True)

    class Meta:
        model = GoalCategory
        fields = "__all__"
        read_only_fields = ("id", "created", "updated", "user")


class GoalCreateSerializer(ModelSerializer):
    category = PrimaryKeyRelatedField(
        queryset=GoalCategory.objects.filter(is_deleted=False)
    )
    user = HiddenField(default=CurrentUserDefault())

    class Meta:
        model = Goal
        fields = '__all__'
        read_only_fields = ('id', 'created', 'updated', 'user')

    def validate_category(self, value):
        if value.is_deleted:
            raise ValidationError("not allowed in deleted category")

        if value.user != self.context["request"].user:
            raise ValidationError("not owner of category")

        return value

    def validate_due_date(self, value):
        if value and value < timezone.now().date():
            raise ValidationError('Failed to set due date in the past')
        return value


class GoalSerializer(ModelSerializer):
    class Meta:
        model = Goal
        fields = '__all__'
        read_only_fields = ('id', 'created', 'updated', 'user')

    def validate_category(self, value):
        if value.is_deleted:
            raise ValidationError("not allowed in deleted category")

        return value


class GoalCommentCreateSerializer(ModelSerializer):
    user = HiddenField(default=CurrentUserDefault())

    def validate_goal(self, value):
        if value.status == Goal.Status.archived:
            raise ValidationError('Goal non found')
        if not BoardParticipant.objects.filter(
                board_id=value.category.board_id,
                role__in=[BoardParticipant.Role.owner, BoardParticipant.Role.writer],
                user_id=self.context['request'].user.id
        ).exists():
            raise PermissionDenied
        return value

    class Meta:
        model = GoalComment
        fields = '__all__'
        read_only_fields = ('id', 'created', 'updated', 'user')


class GoalCommentSerializer(ModelSerializer):
    user = ProfileSerializer(read_only=True)

    class Meta:
        model = GoalComment
        fields = '__all__'
        read_only_fields = ('id', 'created', 'updated', 'user', 'goal')


class BoardCreateSerializer(ModelSerializer):
    class Meta:
        model = Board
        read_only_fields = ("id", "created", "updated", "is_deleted")
        fields = "__all__"


class BoardParticipantSerializer(ModelSerializer):
    role = ChoiceField(
        required=True, choices=BoardParticipant.Role.choices[1:]
    )
    user = SlugRelatedField(
        slug_field="username", queryset=User.objects.all()
    )

    class Meta:
        model = BoardParticipant
        fields = "__all__"
        read_only_fields = ("id", "created", "updated", "board", "is_deleted")


class BoardSerializer(ModelSerializer):
    participants = BoardParticipantSerializer(many=True)
    user = HiddenField(default=CurrentUserDefault())

    class Meta:
        model = Board
        fields = "__all__"
        read_only_fields = ("id", "created", "updated", "is_deleted")

    def update(self, instance, validated_data):
        with transaction.atomic():
            BoardParticipant.objects.filter(
                board=instance).exclude(user=self.context['request'].user).delete()
            BoardParticipant.objects.bulk_create([
                BoardParticipant(
                    user=participant['user'],
                    role=participant['role'],
                    board=instance
                )
                for participant in validated_data.pop('participants', [])
            ])
            if title := validated_data.get('title'):
                instance.title = title
                instance.save(update_fields=('title',))
        return instance
