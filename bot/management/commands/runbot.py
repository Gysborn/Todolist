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
        self.cartridge: dict = {}

    def _get_cat(self, pk: int) -> dict:
        """
        Выборка категорий текущего пользователя
        :param pk: user_id
        :return: словарь категорий
        """
        categories = GoalCategory.objects.filter(
            board__participants__user_id=pk,
            is_deleted=False
        )
        return {category.title: category.id for category in categories}

    def handle_save(self, msg: Message):
        """
        Сохраняет цель
        :param msg: объект Message
        :return: None
        """
        if msg.text == '/cansel':
            self.cartridge.pop(msg.chat.id)
            self.tg_client.send_message(
                msg.chat.id,
                'Действие отменено\n'
                'Для продолжения наберите /start'
            )
        else:
            cat = self.cartridge[msg.chat.id]['choice_cat']
            cats = self.cartridge[msg.chat.id]['cats']
            user_id = self.cartridge[msg.chat.id]['user_id']
            goal = Goal(title=msg.text, category_id=cats[cat], user_id=user_id)
            goal.save()
            self.cartridge.pop(msg.chat.id)
            self.tg_client.send_message(
                msg.chat.id,
                f'Готово! цель {msg.text} для категории {cat} успешно сохранена\n'
                f'Для продолжения наберите /start'
            )

    def handle_create(self, msg: Message):
        """
        Создает новую цель
        :param msg: объект Message
        :return: None
        """
        if msg.text == '/cansel':
            self.cartridge.pop(msg.chat.id)
            self.tg_client.send_message(
                msg.chat.id,
                'Действие отменено\n'
                'Для продолжения наберите /start'
            )

        elif msg.text in self.cartridge[msg.chat.id]['cats']:
            self.cartridge[msg.chat.id]['choice_cat'] = msg.text
            self.tg_client.send_message(
                msg.chat.id,
                f'Выбери заголовок или введи /cansel'
            )
            self.cartridge[msg.chat.id]['handle'] = self.handle_save

    def condition_a(self, msg: Message):
        """
        Состояние А: проверка на наличие верификации
        :param msg: объект Message
        :return: None
        """
        print('handle a')
        self.tg_client.send_message(msg.chat.id, 'Hello')
        tg_user, _ = TgUser.objects.get_or_create(chat_id=msg.chat.id)
        if tg_user.user_id is None:
            data = {'user_id': None, 'handle': self.condition_b}
            self.cartridge[msg.chat.id] = data
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
                '\n/cansel => отмена'
            )
            data = {'user_id': tg_user.user_id, 'handle': self.condition_c}
            self.cartridge[msg.chat.id] = data

    def condition_b(self, msg: Message):
        """
        Верифицирует пользователя путем отправки кода
        :param msg: объект Message
        :return: None
        """
        print('handle b')
        tg_user, _ = TgUser.objects.get_or_create(chat_id=msg.chat.id)
        code = tg_user.set_verification_code()
        self.tg_client.send_message(msg.chat.id, f'Your verification code: {code}')
        self.cartridge[msg.chat.id]['handle'] = self.condition_a

    def condition_c(self, msg: Message):
        """
        Состояние С: выдает список целей
        либо создает цель
        :param msg:
        :return: None
        """
        print('handle c')
        if msg.text == '/cansel':
            d = self.cartridge.pop(msg.chat.id)
            print(d)
            self.tg_client.send_message(
                msg.chat.id, 'Запрос отменен\nДля продолжения наберите /start'
            )

        elif msg.text == '/goals':
            obj = Goal.objects.filter(user_id=self.cartridge[msg.chat.id]['user_id'])
            result = GoalSerializer(obj, many=True)
            for d in result.data:
                self.tg_client.send_message(msg.chat.id, '#' + ' ' + d['title'])

            self.cartridge[msg.chat.id]['handle'] = self.condition_a
            self.cartridge.pop(msg.chat.id)
            self.tg_client.send_message(msg.chat.id, 'Готово! для продолжения наберите /start')

        elif msg.text == '/create':
            cats = self._get_cat(self.cartridge[msg.chat.id]['user_id'])
            self.cartridge[msg.chat.id]['cats'] = cats
            self.tg_client.send_message(
                msg.chat.id,
                f'Выбери категорию из {[c for c in cats.keys()]}'
                f'или /cansel для отмены'
            )

            self.cartridge[msg.chat.id]['handle'] = self.handle_create

        else:
            self.tg_client.send_message(
                msg.chat.id,
                'А я думала сова!\n Для продолжения наберите /start'
            )
            self.cartridge[msg.chat.id]['handle'] = self.condition_a

    def handle(self, *args, **options):
        """
        Бесконечный цикл, отлова сообщений пользователя
        :param args:
        :param options:
        :return:
        """
        offset = 0
        while True:
            res = self.tg_client.get_updates(offset=offset)
            for item in res.result:
                offset = item.update_id + 1
                self.handle_message(item.message)

    def handle_message(self, msg: Message):
        """
        Выполняет хендлы из словаря cartridge
        по ключу если ключа нет выполняет condition_a
        :param msg:
        :return: None
        """
        if msg.chat.id not in self.cartridge:
            self.condition_a(msg)
        else:
            self.cartridge[msg.chat.id]['handle'](msg)
