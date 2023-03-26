from django.core.management import BaseCommand
from bot.models import TgUser
from bot.tg.client import TgClient
from bot.tg.schemas import Message
from goals.models import Goal, GoalCategory
from goals.serializers import GoalSerializer


class Command(BaseCommand):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.tg_client = TgClient()
        self.cartridge_func = self.condition_a
        self.choice_cat: str = ''
        self.cats: list = []

    def handle_save(self, msg: Message):
        if msg.text == '/cansel':
            self.tg_client.send_message(msg.chat.id, 'Для продолжения наберите /start')
            self.cartridge_func = self.condition_a
        else:
            self.tg_client.send_message(
                msg.chat.id,
                f'Категория: {self.choice_cat} Тема: {msg.text}'
            )
            self.cartridge_func = self.condition_a

    def handle_create(self, msg: Message):

        if msg.text == '/cansel':
            self.cartridge_func = self.condition_a
        elif msg.text not in self.cats:
            print(msg.text)
            self.tg_client.send_message(
                msg.chat.id,
                f'Такой категории нет: {msg.text} выберите из предложенных {self.cats}\n'
                f' или наберите /cansel'
            )
            self.cartridge_func = self.handle_create
        else:
            self.choice_cat = msg.text
            self.tg_client.send_message(
                msg.chat.id,
                'Выбери тему или наберите /cansel для отмены'
            )
            self.cartridge_func = self.handle_save

    def condition_a(self, msg: Message):
        print('handle a')
        self.tg_client.send_message(msg.chat.id, 'Hello')
        tg_user, _ = TgUser.objects.get_or_create(chat_id=msg.chat.id)

        if tg_user.user_id is None:
            self.cartridge_func = self.condition_b
            self.tg_client.send_message(
                msg.chat.id,
                'Похоже вы новенький!'
                'И вам необходимо верифицироваться.'
                'Введите любое слово'
                'И мы пришлем вам код... '
            )

        else:
            self.tg_client.send_message(
                msg.chat.id,
                'Выбериете команду:'
                '\n/goals => посмотреть цели'
                '\n/create => создать цель'
            )
            self.cartridge_func = self.condition_c

    def condition_b(self, msg: Message):
        print('handle b')
        tg_user, _ = TgUser.objects.get_or_create(chat_id=msg.chat.id)
        code = tg_user.set_verification_code()
        self.tg_client.send_message(msg.chat.id, f'Your verification code: {code}')
        self.cartridge_func = self.condition_a

    def condition_c(self, msg: Message):

        tg_user, _ = TgUser.objects.get_or_create(chat_id=msg.chat.id)
        print('handle c')
        if msg.text == '/goals':
            obj = Goal.objects.filter(user_id=tg_user.user_id)
            result = GoalSerializer(obj, many=True)
            for d in result.data:
                self.tg_client.send_message(msg.chat.id, '#' + ' ' + d['title'])

            self.cartridge_func = self.condition_a
            self.tg_client.send_message(msg.chat.id, 'Для продолжения наберите /start')

        elif msg.text == '/create':
            categories = GoalCategory.objects.filter(
                board__participants__user=tg_user.user,
                is_deleted=False
            )
            self.cats = [category.title for category in categories]
            self.tg_client.send_message(
                msg.chat.id,
                f'Выбери категорию из {self.cats} или набери /cansel для отмены'
            )
            self.cartridge_func = self.handle_create

        else:
            self.tg_client.send_message(
                msg.chat.id,
                'А я думала сова!\n Для продолжения наберите /start')
            self.cartridge_func = self.condition_a

    def handle(self, *args, **options):
        offset = 0
        while True:
            res = self.tg_client.get_updates(offset=offset)
            for item in res.result:
                offset = item.update_id + 1
                self.handle_message(item.message)

    def handle_message(self, msg: Message):
        self.cartridge_func(msg)
