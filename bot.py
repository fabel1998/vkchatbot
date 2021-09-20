import random
import logging
import vk_api
from pony.orm import db_session
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType
from settings import TOKEN, GROUP_ID
import handlers
from vkbot import settings
from vkbot.models import UserState, Registration

log = logging.getLogger('bot')
file_handler = logging.FileHandler('bot.log')
stream_handler = logging.StreamHandler()
log.addHandler(stream_handler)
log.addHandler(file_handler)
log.setLevel(logging.DEBUG)
file_handler.setLevel(logging.DEBUG)
file_handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s %(message)s'))
stream_handler.setLevel(logging.INFO)
stream_handler.setFormatter(logging.Formatter('%(levelname)s %(message)s'))

class Bot:
    """
    Сценарии регистрации на вебинар "MIIGAIK" в vk.com.
    Use python 3.9

    Поддерживает ответы на вопросы про дату, место проведение и сценарии регистрации:
    - спрашиваем имя
    - спрашиваем емайл
    - говорим об успешной регистрации
    Если шаг не пройден, задаем уточняющие вопросы пока шаг не удет пройден.
    """

    def __init__(self, group_id, token):
        """
        :param group_id: id из созданого сообщества в vk
        :param token: сектретный токен созданого сообщества
        """

        self.group_id = group_id
        self.token = token
        self.vk = vk_api.VkApi(token=token)
        self.long_poller = VkBotLongPoll(self.vk, self.group_id)
        self.api = self.vk.get_api()

    def run(self):
        """Запуск бота"""
        for event in self.long_poller.listen():
            try:
                self.on_event(event)
            except Exception:
                log.exception('ошибка в обработке события')
    @db_session
    def on_event(self, event):
        if event.type != VkBotEventType.MESSAGE_NEW:
            log.info('Мы с таким не работаем, %s', event.type)
            return

        user_id = event.object.peer_id
        text = event.object.text
        state = UserState.get(user_id=str(user_id))

        if state is not None:
            text_to_send = self.continue_scenario(text, state)
        else:
            # search intent
            for intent in settings.INTENTS:
                log.debug(f'Пользователь получил {intent}')
                if any(token in text.lower() for token in intent['tokens']):
                    if intent['answer']:
                        text_to_send = intent['answer']
                    else:
                        text_to_send = self.start_scenario(user_id, intent['scenario'])
                    break
            else:
                text_to_send = settings.DEFAULT_ANSWER

        self.api.messages.send(
            message=text_to_send,
            random_id=random.randint(0, 2 ** 20),
            peer_id=user_id,
        )

    def start_scenario(self, user_id, scenario_name):
        scenario = settings.SCENARIOS[scenario_name]
        first_step = scenario['first_step']
        step = scenario['steps'][first_step]
        text_to_send = step['text']
        UserState(user_id=str(user_id), scenario_name=scenario_name, step_name=first_step, context={})
        return text_to_send

    def continue_scenario(self, text, state):
        steps = settings.SCENARIOS[state.scenario_name]['steps']
        step = steps[state.step_name]

        handler = getattr(handlers, step['handler'])
        if handler(text=text, context=state.context):
            next_step = steps[step['next_step']]
            text_to_send = next_step['text'].format(**state.context)
            if next_step['next_step']:
                state.step_name = step['next_step']
            else:
                log.info('Зарегистрирован: {name} {email}'.format(**state.context))
                Registration(name=state.context['name'], email=state.context['email'])
                state.delete()
        else:
            text_to_send = step['failure_text'].format(**state.context)
        return text_to_send


if __name__ == '__main__':
    bot = Bot(GROUP_ID, TOKEN)
    bot.run()
