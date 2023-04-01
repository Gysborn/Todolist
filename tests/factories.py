import factory
from django.utils import timezone
from pytest_factoryboy import register

from core.models import User
from goals.models import Board, BoardParticipant, Goal, GoalCategory, GoalComment


@register()
class UserFactory(factory.django.DjangoModelFactory):
    username = factory.Faker('user_name')
    password = factory.Faker('password')

    class Meta:
        model = User

    @classmethod
    def _create(cls, model_class, *args, **kwargs):
        return User.objects.create_user(*args, **kwargs)


class DatesFactoryMixin(factory.django.DjangoModelFactory):
    created = factory.LazyFunction(timezone.now)
    updated = factory.LazyFunction(timezone.now)

    class Meta:
        abstract = True


@register()
class BoardFactory(DatesFactoryMixin):
    title = factory.Faker('sentence')

    class Meta:
        model = Board

    @factory.post_generation
    def with_owner(self, create, owner, **kwargs):
        if owner:
            BoardParticipant.objects.create(board=self, user=owner, role=BoardParticipant.Role.owner)


@register()
class BoardParticipantFactory(DatesFactoryMixin):
    board = factory.SubFactory(BoardFactory)
    user = factory.SubFactory(UserFactory)

    class Meta:
        model = BoardParticipant


# Для целей
@register()
class GoalCategoryFactory(DatesFactoryMixin):
    title = factory.Faker('sentence')
    board = factory.SubFactory(BoardFactory)
    user = factory.SubFactory(UserFactory)

    class Meta:
        model = GoalCategory


@register()
class GoalFactory(DatesFactoryMixin):
    title = factory.Faker('sentence')
    category = factory.SubFactory(GoalCategoryFactory)
    user = factory.SubFactory(UserFactory)

    class Meta:
        model = Goal


@register()
class GoalCommentFactory(DatesFactoryMixin):
    text = factory.Faker('sentence')

    class Meta:
        model = GoalComment
