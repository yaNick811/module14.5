from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher import FSMContext
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
import crud_functions
import os

API_TOKEN = ''
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot, storage=MemoryStorage())

class UserState(StatesGroup):
    growth = State()
    age = State()
    weight = State()

class RegistrationState(StatesGroup):
    username = State()
    email = State()
    age = State()
    balance = State()

# Главная клавиатура меню
keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
keyboard.add(KeyboardButton('Рассчитать'))
keyboard.add(KeyboardButton('Информация'))
keyboard.add(KeyboardButton('Купить'))
keyboard.add(KeyboardButton('Регистрация'))

inline_keyboard = InlineKeyboardMarkup()
inline_keyboard.add(InlineKeyboardButton('Рассчитать норму калорий', callback_data='calories'))
inline_keyboard.add(InlineKeyboardButton('Формулы расчёта', callback_data='formulas'))

# Inline меню с 4 кнопками
buying_inline_keyboard = InlineKeyboardMarkup()
for i in range(1, 5):
    buying_inline_keyboard.add(InlineKeyboardButton(f'Product{i}', callback_data='product_buying'))

# Инициализация базы данных и заполнение данными
crud_functions.initiate_db()
crud_functions.populate_products()

@dp.message_handler(commands=['start'])
async def start_message(message: types.Message):
    print('Привет! Я бот помогающий твоему здоровью.')
    await message.answer('Привет! Я бот помогающий твоему здоровью. Для расчета калорий нажмите "Рассчитать".', reply_markup=keyboard)

@dp.message_handler(text='Рассчитать')
async def main_menu(message: types.Message):
    await message.answer('Выберите опцию:', reply_markup=inline_keyboard)

@dp.callback_query_handler(text='formulas')
async def get_formulas(call: types.CallbackQuery):
    await call.message.answer("Формула Миффлина-Сан Жеора для женщин:\n"
                              "10 * вес (кг) + 6.25 * рост (см) - 5 * возраст (лет) - 161")
    await call.answer()

@dp.callback_query_handler(text='calories')
async def set_age(call: types.CallbackQuery):
    await call.message.answer('Введите свой возраст:', reply_markup=types.ReplyKeyboardRemove())
    await UserState.age.set()

@dp.message_handler(state=UserState.age)
async def set_growth(message: types.Message, state: FSMContext):
    await state.update_data(age=int(message.text))
    data = await state.get_data()
    await message.answer(f"Возраст: {data['age']}")
    await message.answer('Введите свой рост:')
    await UserState.growth.set()

@dp.message_handler(state=UserState.growth)
async def set_weight(message: types.Message, state: FSMContext):
    await state.update_data(growth=int(message.text))
    data = await state.get_data()
    await message.answer(f"Рост: {data['growth']}")
    await message.answer('Введите свой вес:')
    await UserState.weight.set()

@dp.message_handler(state=UserState.weight)
async def send_calories(message: types.Message, state: FSMContext):
    await state.update_data(weight=int(message.text))
    data = await state.get_data()
    await message.answer(f"Вес: {data['weight']}")

    age = data['age']
    growth = data['growth']
    weight = data['weight']

    calories = 10 * weight + 6.25 * growth - 5 * age - 161

    await message.answer(f"Ваша норма калорий: {calories} ккал в день.")
    await state.finish()

@dp.message_handler(text='Купить')
async def get_buying_list(message: types.Message):
    products = crud_functions.get_all_products()
    for product in products:
        id, title, description, price = product
        await message.answer(f'Название: {title} | Описание: {description} | Цена: {price}')
        # Проверка на существование файла перед открытием
        if os.path.exists(f'{id}.png'):
            with open(f'{id}.png', 'rb') as photo:
                await message.answer_photo(photo=types.InputFile(photo))
        else:
            await message.answer(f'Фото для продукта {title} не найдено.')

    await message.answer('Выберите продукт для покупки:', reply_markup=buying_inline_keyboard)

@dp.callback_query_handler(text='product_buying')
async def send_confirm_message(call: types.CallbackQuery):
    await call.message.answer('Вы успешно приобрели продукт!')
    await call.answer()

@dp.message_handler(text='Регистрация')
async def sign_up(message: types.Message):
    await message.answer('Введите имя пользователя (только латинский алфавит):')
    await RegistrationState.username.set()

@dp.message_handler(state=RegistrationState.username)
async def set_username(message: types.Message, state: FSMContext):
    username = message.text
    if crud_functions.is_included(username):
        await message.answer('Пользователь существует, введите другое имя:')
    else:
        await state.update_data(username=username)
        await message.answer('Введите свой email:')
        await RegistrationState.email.set()

@dp.message_handler(state=RegistrationState.email)
async def set_email(message: types.Message, state: FSMContext):
    email = message.text
    await state.update_data(email=email)
    await message.answer('Введите свой возраст:')
    await RegistrationState.age.set()

@dp.message_handler(state=RegistrationState.age)
async def set_age(message: types.Message, state: FSMContext):
    age = int(message.text)
    data = await state.get_data()
    username = data['username']
    email = data['email']
    crud_functions.add_user(username, email, age)
    await message.answer('Регистрация успешно завершена!')
    await state.finish()

@dp.message_handler()
async def all_message(message: types.Message):
    print("Введите команду /start, чтобы начать общение.")
    await message.answer('Введите команду /start, чтобы начать общение.')

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)