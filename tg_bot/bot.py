from telegram import Bot, Update, InlineKeyboardButton, InlineKeyboardMarkup, ParseMode
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackQueryHandler
from datetime import datetime
from timetable_tg_bot.tg_bot.config import TOKEN
from timetable_tg_bot.tg_bot.db import init_db, add_message, day_list, delete_day_values


week = [
    'понедельник',
    'вторник',
    'среда',
    'четверг',
    'пятница',
    'суббота',
    'воскесенье',
]
BUTTON_TODAY = 'callback_button_today'
BUTTON_DELETE = 'callback_button_delete'
BUTTON_LIST = 'callback_button_list'
BUTTON_MENU = 'callback_button_menu'


KEYS = {
    week[0]: 'Понедельник',
    week[1]: 'Вторник',
    week[2]: 'Среда',
    week[3]: 'Четверг',
    week[4]: 'Пятница',
    week[5]: 'Суббота',
    week[6]: 'Воскресенье',
    BUTTON_TODAY: 'Сегодня',
    BUTTON_DELETE: 'Очистить',
    BUTTON_LIST: 'Список',
    BUTTON_MENU: 'Меню',
}


def keyboard_inline_menu():
    keyboard = [
        [
            InlineKeyboardButton(KEYS[BUTTON_TODAY], callback_data=BUTTON_TODAY),
            InlineKeyboardButton(KEYS[BUTTON_LIST], callback_data=BUTTON_LIST),
        ],
    ]
    return InlineKeyboardMarkup(keyboard)


def keyboard_inline_list():
    keyboard = [
        [
            InlineKeyboardButton(KEYS[week[0]], callback_data=week[0]),
            InlineKeyboardButton(KEYS[week[1]], callback_data=week[1]),
            InlineKeyboardButton(KEYS[week[2]], callback_data=week[2]),
        ],
        [
            InlineKeyboardButton(KEYS[week[3]], callback_data=week[3]),
            InlineKeyboardButton(KEYS[week[4]], callback_data=week[4]),
            InlineKeyboardButton(KEYS[week[5]], callback_data=week[5]),
        ],
        [
            InlineKeyboardButton(KEYS[week[6]], callback_data=week[6]),
            InlineKeyboardButton(KEYS[BUTTON_MENU], callback_data=BUTTON_MENU),
        ],
    ]
    return InlineKeyboardMarkup(keyboard)


def keyboard_inline_day():
    keyboard = [
        [
            InlineKeyboardButton(KEYS[BUTTON_DELETE], callback_data=BUTTON_DELETE),
        ],
        [
            InlineKeyboardButton(KEYS[BUTTON_MENU], callback_data=BUTTON_MENU),
            InlineKeyboardButton(KEYS[BUTTON_LIST], callback_data=BUTTON_LIST),
        ],
    ]
    return InlineKeyboardMarkup(keyboard)


def do_start(bot: Bot, update: Update):
    bot.send_message(
        chat_id=update.message.chat_id,
        text='Привет.\nИспользуй /help для просмотра команд.',
    )


def do_menu(bot: Bot, update: Update):
    text = 'Меню:'
    bot.send_message(
        chat_id=update.message.chat_id,
        text=text,
        reply_markup = keyboard_inline_menu(),
    )


def keyboard_callback_handler(bot: Bot, update: Update, chat_data=None, **kwargs):
    query = update.callback_query
    data = query.data

    if data == BUTTON_MENU:
        query.edit_message_text(
            text='Меню:',
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=keyboard_inline_menu(),
        )
    elif data == BUTTON_LIST:
        query.edit_message_text(
            text='Список:',
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=keyboard_inline_list(),
        )
    elif data == BUTTON_TODAY:
        user = update.effective_user
        today = KEYS[week[datetime.weekday(datetime.now())]]
        dl = day_list(
            user_id=user.id,
            day=today.lower(),
        )
        li = ''
        for i in range(len(dl)):
            li += dl[i][0] + '\n'
        query.edit_message_text(
            text='{}\n\n{}'.format(today, li),
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=keyboard_inline_day(),
        )
    elif data in week:
        user = update.effective_user
        day = KEYS[data]
        dl = day_list(
            user_id=user.id,
            day=day.lower(),
        )
        li = ''
        for i in range(len(dl)):
            li += '- '+dl[i][0]+'\n'
        query.edit_message_text(
            text='{}\n\n{}'.format(day, li),
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=keyboard_inline_day(),
        )
    elif data == BUTTON_DELETE:
        user = update.effective_user
        text = update.effective_message.text.split('\n')
        day = text[0]
        print(day)
        delete_day_values(
            user_id=user.id,
            day=day.lower(),
        )
        query.edit_message_text(
            text='День "{}" очищен.'.format(day),
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=keyboard_inline_list(),
        )


def do_help(bot: Bot, update: Update):
    bot.send_message(
        chat_id=update.message.chat_id,
        text='Это бот-органайзер.\n'
             'Пример сохранения записи:\n'
             'Понедельник===16:30 тестовая пара\n'
             'Добавьте больше занятий несколькими сообщениями.\n\n'
             'Список доступных команд:\n'
             '/menu - меню бота,\n'
             '/time - время сервера,\n'
             '/help - помощь.',
    )


def do_echo(bot: Bot, update: Update):
    user = update.effective_user
    text = update.effective_message.text
    split_text = text.split('===')
    new_text = ''
    for i in range(1, len(split_text)):
        new_text += split_text[i]
    if split_text[0].lower() in week:
        add_message(
            user_id=user.id,
            day=split_text[0].lower(),
            text=new_text,
        )
        bot.send_message(
            chat_id=update.message.chat_id,
            text='Принято.',
        )
    else:
        bot.send_message(
            chat_id=update.message.chat_id,
            text='Не вышло.'
        )


def main():
    init_db()
    bot = Bot(
        token=TOKEN,
    )
    updater = Updater(
        bot=bot,
    )
    start_handler = CommandHandler('start', do_start)
    menu_handler = CommandHandler('menu', do_menu)
    help_handler = CommandHandler('help', do_help)
    buttons_handler = CallbackQueryHandler(callback=keyboard_callback_handler, pass_chat_data=True)
    message_handler = MessageHandler(Filters.text, do_echo)

    updater.dispatcher.add_handler(start_handler)
    updater.dispatcher.add_handler(menu_handler)
    updater.dispatcher.add_handler(help_handler)
    updater.dispatcher.add_handler(buttons_handler)
    updater.dispatcher.add_handler(message_handler)

    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
