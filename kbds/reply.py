from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove

more_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="Продолжить поиск")
        ]
    ],
    resize_keyboard=True,
    input_field_placeholder="Вам подошла данная статья?"
)

start_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="Добавить")
        ],
        {
            KeyboardButton(text="Поиск")
        }
    ],
    resize_keyboard=True,
    input_field_placeholder="Что вы хотите сделать?"
)

close_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="Да")
        ],
        {
            KeyboardButton(text="Нет")
        }
    ],
    resize_keyboard=True,
    input_field_placeholder="Что вы хотите сделать?"
)

remove_kbd = ReplyKeyboardRemove()