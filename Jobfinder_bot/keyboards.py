from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton


# Главное меню
main_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="🔍 Поиск вакансий")],
        [KeyboardButton(text="❤️ Избранное")]
    ],
    resize_keyboard=True,        # Клавиатура подстраивается под размер текста
    one_time_keyboard=False      # Клавиатура остаётся, не исчезает после нажатия
)


# Кнопки под вакансией
def get_vacancy_kb(vacancy_id: int):
    """
    Генерирует инлайн-клавиатуру для вакансии.
    :param vacancy_id: ID вакансии (целое число)
    :return: InlineKeyboardMarkup
    """
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔍 Подробнее на HH", url=f"https://hh.ru/vacancy/{vacancy_id}")],
        [InlineKeyboardButton(text="❤️ Сохранить в избранное", callback_data=f"save_{vacancy_id}")]
    ])