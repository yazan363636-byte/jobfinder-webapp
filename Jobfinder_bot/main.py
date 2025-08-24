from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import asyncio
from aiogram import Bot, Dispatcher, types, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.exceptions import TelegramForbiddenError
from config import BOT_TOKEN
import hh_api
import database
import keyboards  # ✅ Обязательно импортируем!

# Машина состояний
class SearchForm(StatesGroup):
    waiting_for_query = State()
    waiting_for_city = State()
    waiting_for_salary = State()
    waiting_for_experience = State()

# Создаём бота и диспетчер
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(storage=MemoryStorage())

# Обработчик /start
@dp.message(F.text == "/start")
async def start(message: types.Message):
    try:
        database.init_db()
        await message.answer(
            "Привет! 👋 Я помогу найти работу.\n"
            "Нажми '🔍 Поиск вакансий', чтобы начать.",
            reply_markup=keyboards.main_kb
        )
    except TelegramForbiddenError:
        print(f"❌ Бот заблокирован пользователем {message.from_user.id}")

# ✅ Обработчик для кнопки "Поиск вакансий"
@dp.message(F.text == "🔍 Поиск вакансий")
async def ask_query(message: types.Message, state: FSMContext):
    try:
        await message.answer("Введите профессию, например: Python разработчик")
        await state.set_state(SearchForm.waiting_for_query)
    except TelegramForbiddenError:
        print(f"❌ Бот заблокирован пользователем {message.from_user.id}")

# ✅ Обработчик профессии → город
@dp.message(SearchForm.waiting_for_query)
async def ask_city(message: types.Message, state: FSMContext):
    try:
        await state.update_data(query=message.text)
        await message.answer("Введите город (например, Москва):")
        await state.set_state(SearchForm.waiting_for_city)
    except TelegramForbiddenError:
        print(f"❌ Бот заблокирован пользователем {message.from_user.id}")

# ✅ Город → зарплата
@dp.message(SearchForm.waiting_for_city)
async def ask_salary(message: types.Message, state: FSMContext):
    try:
        await state.update_data(city=message.text)
        await message.answer("Минимальная зарплата (в рублях, например: 100000), или '-' если не важно:")
        await state.set_state(SearchForm.waiting_for_salary)
    except TelegramForbiddenError:
        print(f"❌ Бот заблокирован пользователем {message.from_user.id}")

# ✅ Зарплата → выбор опыта
@dp.message(SearchForm.waiting_for_salary)
async def ask_experience(message: types.Message, state: FSMContext):
    try:
        salary = message.text if message.text != "-" else None
        await state.update_data(salary=salary)

        kb = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="Без опыта", callback_data="exp_noExperience")],
            [InlineKeyboardButton(text="1–3 года", callback_data="exp_between1And3")],
            [InlineKeyboardButton(text="3–6 лет", callback_data="exp_between3And6")],
            [InlineKeyboardButton(text="Более 6 лет", callback_data="exp_moreThan6")],
            [InlineKeyboardButton(text="Не важно", callback_data="exp_any")]
        ])
        await message.answer("Выберите опыт работы:", reply_markup=kb)
        await state.set_state(SearchForm.waiting_for_experience)
    except TelegramForbiddenError:
        print(f"❌ Бот заблокирован пользователем {message.from_user.id}")

# ✅ Обработчик выбора опыта
@dp.callback_query(F.data.startswith("exp_"))
async def handle_experience(callback: types.CallbackQuery, state: FSMContext):
    try:
        exp_map = {
            "exp_noExperience": "noExperience",
            "exp_between1And3": "between1And3",
            "exp_between3And6": "between3And6",
            "exp_moreThan6": "moreThan6",
            "exp_any": None
        }
        data_key = callback.data.split("_")[1]
        experience = exp_map.get(data_key)

        await state.update_data(experience=experience)
        await callback.answer("✅ Выбор сохранён")

        user_data = await state.get_data()
        query = user_data['query']
        city = user_data['city']
        salary = user_data['salary']
        experience = user_data['experience']

        vacancies = hh_api.search_vacancies(query, city, salary, experience)

        if not vacancies:
            await callback.message.answer("🔍 Вакансий не найдено.")
        else:
            await callback.message.answer(f"🔍 Найдено {len(vacancies)} вакансий:")
            for vac in vacancies:
                text = f"💼 <b>{vac['title']}</b>\n"
                text += f"🏢 {vac['company']}\n"
                text += f"💰 {vac['salary']}"
                await callback.message.answer(
                    text,
                    reply_markup=keyboards.get_vacancy_kb(vac['id']),
                    parse_mode="HTML"
                )

        await state.clear()
    except Exception as e:
        print(f"⚠️ Ошибка при выборе опыта: {e}")

# Запуск
async def main():
    print("✅ Бот запущен...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())