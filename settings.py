TOKEN = '24043770fd7cbb46c290944d1ae74c22d83504d0f82f8bc8453a43609bc38c842474a419ffa3537b7c8f6'
GROUP_ID = 206861912

INTENTS = [
    {
        'name': 'Дата проведения',
        'tokens': ('когда', 'сколько', 'дата', 'дату'),
        'scenario': None,
        'answer': 'Конференция проводится 15-го апреля, регистрация начнется в 10 утра'
    },
    {
        'name': 'Место проведения',
        'tokens': ('где', 'место', 'локация', 'адрес', 'метро'),
        'scenario': None,
        'answer': 'Конференция пройдет в конференц-зале, справа от главного входа в университет'
    },
    {
        'name': 'Регистрация',
        'tokens': ('регист', 'добав'),
        'scenario': 'registration',
        'answer': None
    }
]

SCENARIOS = {
    'registration': {
        'first_step': 'step1',
        'steps': {
            'step1': {
                'text': 'Чтобы зарегистрироваться, введите ваше имя. Оно будет на бэйджике',
                'failure_text': 'Имя долэно состоять из 3-30 букв и дефиса. Поробуйте ещё раз',
                'handler': 'handle_name',
                'next_step': 'step2'
            },
            'step2': {
                'text': 'Введите email. Мы отправи на него все данные.',
                'failure_text': 'Во введенном адресе ошибка. Попробуйте ещё раз',
                'handler': 'handle_email',
                'next_step': 'step3'
            },
            'step3': {
                'text': 'Спасибо за регистрацию, {name}! Мы отправили на {email} билет, распечатайте его.',
                'failure_text': None,
                'handler': None,
                'next_step': None
            }
        }
    }
}

DEFAULT_ANSWER = 'Не знаю как на это ответить.' \
                 'Могу сказать когда и где проводится конференция, а так жезарегистрировать вас. Просто спросите'

DB_CONFIG = dict(
    provider='postgres',
    user='postgres',
    password='vampir98',
    host='localhost',
    database='vk_chat_bot'
)