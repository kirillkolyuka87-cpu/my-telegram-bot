from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram import F
import asyncio
import logging
import os

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Инициализация бота и диспетчера
BOT_TOKEN = os.getenv('BOT_TOKEN')
if not BOT_TOKEN:
    logger.error("BOT_TOKEN not found!")
    exit(1)

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# Фиксированные значения
EXCHANGE_RATE = 12.0
SERVICE_FEE = 1000
CHINA_SHIPPING = 800

# Состояния
class CalculatorStates(StatesGroup):
    waiting_for_product_price = State()

# Клавиатуры
def get_main_keyboard():
    keyboard = [
        [types.KeyboardButton(text='💸 Калькулятор'), types.KeyboardButton(text='📊 Актуальный курс')],
        [types.KeyboardButton(text='🛒 ОФОРМЛЕНИЕ ЗАКАЗА'), types.KeyboardButton(text='ℹ️ О нас')]
    ]
    return types.ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True)

def get_calc_keyboard():
    keyboard = [[types.KeyboardButton(text='🔙 Вернуться в меню')]]
    return types.ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True)

# Обработчики бота
@dp.message(Command('start'))
async def cmd_start(message: types.Message):
    await message.answer(
        "Добро пожаловать в бот-калькулятор!\nВыберите нужный раздел:",
        reply_markup=get_main_keyboard()
    )

@dp.message(F.text == '📊 Актуальный курс')
async def cmd_exchange_rate(message: types.Message):
    text = (
        f"📊 <b>Актуальный курс юаня:</b> {EXCHANGE_RATE} ₽\n\n"
        f"💼 <b>Комиссия сервиса:</b> {SERVICE_FEE} ₽\n"
        f"🚚 <b>Доставка по Китаю:</b> {CHINA_SHIPPING} ₽\n"
        f"      (Китай → Владивосток)\n\n"
        f"📦 После Владивостока доставка СДЭК/Почты России оплачивается отдельно! 🫶"
    )
    await message.answer(text, parse_mode='HTML')

@dp.message(F.text == '🛒 ОФОРМЛЕНИЕ ЗАКАЗА')
async def cmd_order(message: types.Message):
    text = (
        "🛒 <b>ОФОРМЛЕНИЕ ЗАКАЗА</b>\n\n"
        "📞 <b>Для заказа:</b> @volosatie_ushki\n\n"
        "📋 <b>Укажите:</b>\n"
        "• Ссылку на товар\n"
        "• Размер\n"
        "• Цвет\n\n"
        "⏱️ <b>Ответ за 5-15 минут</b>"
    )
    await message.answer(text, parse_mode='HTML')

@dp.message(F.text == 'ℹ️ О нас')
async def cmd_about(message: types.Message):
    text = (
        "ℹ️ <b>О нас</b>\n\n"
        "📦 Мы помогаем с заказами из Китая\n"
        "💰 Фиксированная комиссия\n"
        "🏷️ Скидки постоянным клиентам\n"
        "🤝 Наши менеджеры на связи 24/7\n"
        "🛡️ Страхование товара"
    )
    await message.answer(text, parse_mode='HTML')

@dp.message(F.text == '💸 Калькулятор')
async def cmd_calculator(message: types.Message, state: FSMContext):
    await message.answer(
        "Калькулятор стоимости заказа:\n\nВведите цену товара в юанях (¥):",
        reply_markup=get_calc_keyboard()
    )
    await state.set_state(CalculatorStates.waiting_for_product_price)

@dp.message(CalculatorStates.waiting_for_product_price)
async def process_product_price(message: types.Message, state: FSMContext):
    if message.text == '🔙 Вернуться в меню':
        await state.clear()
        await message.answer("Главное меню:", reply_markup=get_main_keyboard())
        return

    try:
        price = float(message.text.replace(',', '.'))
        cost_rub = price * EXCHANGE_RATE
        total = cost_rub + CHINA_SHIPPING + SERVICE_FEE
        
        text = (
            f"💸 <b>Итого к оплате: {total:.1f} ₽</b> 🔥\n\n"
            f"📈 <b>Курс юаня (¥):</b> {EXCHANGE_RATE} ₽\n"
            f"🧮 <b>Расчет заказа:</b>\n"
            f"      ¥{price} × {EXCHANGE_RATE} ₽ = <b>{cost_rub:.1f} ₽</b>\n"
            f"🚚 <b>Доставка по Китаю:</b> {CHINA_SHIPPING} ₽\n"
            f"      (Маршрут: Китай → Владивосток)\n"
            f"⚙️ <b>Сервисный сбор:</b> {SERVICE_FEE} ₽\n\n"
            f"📦 <b>После Владивостока доставка СДЭК/Почты России оплачивается отдельно!</b> 🫶"
        )
        
        await message.answer(text, parse_mode='HTML')
        await state.clear()
        await message.answer("Хотите рассчитать еще один заказ?", reply_markup=get_calc_keyboard())
        await state.set_state(CalculatorStates.waiting_for_product_price)
        
    except ValueError:
        await message.answer("Пожалуйста, введите корректное число:")

@dp.message(F.text == '🔙 Вернуться в меню')
async def cmd_back(message: types.Message):
    await message.answer("Главное меню:", reply_markup=get_main_keyboard())

# Запуск бота
async def main():
    logger.info("Starting Telegram bot on Koyeb...")
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())
