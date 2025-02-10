from aiogram import types
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher import FSMContext
from load import dp, bot
import asyncio
from datetime import datetime
import os
from traits import *
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.exceptions import MessageToEditNotFound
import calendar
from datetime import date, timedelta


# Здесь подключаются ваши модули для кнопок и базы данных
from keyboard import *
from database import Database
from aiogram.utils.exceptions import MessageToEditNotFound  # Импортируем исключение

PRICE = 500000

generator = Generator()
btn = Button()
db = Database()

# Ensure the directory exists
os.makedirs('./pdf/', exist_ok=True)


class Formas(StatesGroup):
    s1 = State()  # Тойдың түрі (celebration type)
    s2 = State()  # Қай қала (city selection)
    s3 = State()  # Мейрамхана (restaurant selection)
    s4 = State()  # Адам саны (people count)
    s5 = State()  # Ас мәзірі (meal selection)
    s6 = State()  # Той өтетін күн!
    s7 = State()  # Event түрі (personnel selection & final calculation)


# Функция для удаления последнего сообщения бота (хранится в состоянии)
async def delete_last_bot_message(chat_id: int, state: FSMContext):
    async with state.proxy() as data:
        if "last_bot_message_id" in data:
            try:
                await bot.delete_message(chat_id, data["last_bot_message_id"])
            except Exception:
                pass
            data.pop("last_bot_message_id", None)


# Функция для сохранения id отправленного ботом сообщения
async def store_bot_message(state: FSMContext, message: types.Message):
    async with state.proxy() as data:
        data["last_bot_message_id"] = message.message_id


# -------------------------- Состояние s1: Ввод типа торжества --------------------------
@dp.message_handler(state=Formas.s1)
async def process_s1(message: types.Message, state: FSMContext):
    # Удаляем предыдущее сообщение бота, если оно есть
    await delete_last_bot_message(message.chat.id, state)
    
    async with state.proxy() as data:
        data['type_of_celebrate'] = message.text

    await Formas.next()  # Переход в s2

    await bot.send_chat_action(message.from_user.id, action="typing")
    await asyncio.sleep(1)
    
    sent_msg = await bot.send_message(
        message.from_user.id,
        text="*Қаланы таңдаңыз!*",
        parse_mode="Markdown",
        reply_markup=btn.cities()  # Inline-клавиатура для выбора города (например, "Алматы")
    )
    await store_bot_message(state, sent_msg)


# -------------------------- Состояние s2: Выбор города (inline) --------------------------
@dp.callback_query_handler(lambda c: c.data == "almaty", state=Formas.s2)
async def process_s2(callback_query: types.CallbackQuery, state: FSMContext):
    await delete_last_bot_message(callback_query.message.chat.id, state)
    
    async with state.proxy() as data:
        data['city'] = "Алматы"
    
    await Formas.next()  # Переход в s3

    await bot.send_chat_action(callback_query.from_user.id, action="typing")
    await asyncio.sleep(1)
    
    sent_msg = await bot.send_message(
        callback_query.from_user.id,
        text="*🏢 Мейрамхананы таңдаңыз*",
        parse_mode="Markdown",
        reply_markup=btn.restaurant()  # Inline-клавиатура для выбора ресторана
    )
    await store_bot_message(state, sent_msg)
    await callback_query.answer()


# -------------------------- Состояние s3: Выбор ресторана (inline) --------------------------
@dp.callback_query_handler(lambda c: c.data == "dostar", state=Formas.s3)
async def process_s3(callback_query: types.CallbackQuery, state: FSMContext):
    await delete_last_bot_message(callback_query.message.chat.id, state)
    
    async with state.proxy() as data:
        data['restaurant'] = "🏢 Достар мейрамханысы"
    
    await Formas.next()  # Переход в s4

    await bot.send_chat_action(callback_query.from_user.id, action="typing")
    await asyncio.sleep(1)
    
    sent_msg = await bot.send_message(
        callback_query.from_user.id,
        text="*👤 Адам санын таңдаңыз*",
        parse_mode="Markdown",
        reply_markup=btn.countPeople()
    )
    await store_bot_message(state, sent_msg)
    await callback_query.answer()


# -------------------------- Состояние s4: Ввод количества людей --------------------------
@dp.message_handler(state=Formas.s4)
async def process_s4(message: types.Message, state: FSMContext):
    await delete_last_bot_message(message.chat.id, state)
    
    async with state.proxy() as data:
        data['people'] = int(message.text)
    
    await Formas.next()  # Переход в s5

    await bot.send_chat_action(message.from_user.id, action="typing")
    await asyncio.sleep(1)
    
    
    await asyncio.sleep(1)
    
    # Затем отправляем сообщение с inline-клавиатурой выбора ас мәзірі
    sent_msg2 = await bot.send_message(
        message.from_user.id,
        text="*🍽 Ас мәзірін таңдаңыз*",
        parse_mode="Markdown",
        reply_markup=btn.meal_menu()
    )
    await store_bot_message(state, sent_msg2)


# -----------------------------------------------------------------------------
# --- INLINE-КАЛЕНДАРЬ для выбора даты (состояние s6) ---

def add_months(sourcedate: date, months: int) -> date:
    """
    Возвращает дату первого числа месяца, смещённого на months от sourcedate.
    """
    month = sourcedate.month - 1 + months
    year = sourcedate.year + month // 12
    month = month % 12 + 1
    return date(year, month, 1)

def generate_calendar(offset: int = 0) -> InlineKeyboardMarkup:
    """
    Генерирует inline-календарь для месяца с указанным offset.
    Отображаются даты от завтрашнего дня до трёх месяцев вперёд.
    """
    today = date.today()
    allowed_start = today + timedelta(days=1)
    allowed_end = add_months(today, 3)  # Ограничение – три месяца вперед (первое число месяца)
    
    # Определяем целевой месяц (offset=0 – текущий месяц, offset=1 – следующий и т.д.)
    target_date = add_months(today, offset)
    first_day = target_date  # Первый день выбранного месяца
    days_in_month = calendar.monthrange(first_day.year, first_day.month)[1]
    
    keyboard = InlineKeyboardMarkup(row_width=7)
    
    # Заголовок с названием месяца и года
    header_text = first_day.strftime('%B %Y')
    keyboard.add(InlineKeyboardButton(header_text, callback_data="ignore"))
    
    # Заголовок дней недели
    days_header = ["Пн", "Вт", "Ср", "Чт", "Пт", "Сб", "Вс"]
    keyboard.add(*[InlineKeyboardButton(day, callback_data="ignore") for day in days_header])
    
    # Определяем, с какого дня недели начинается месяц (понедельник = 0)
    first_weekday = first_day.weekday()
    buttons = [InlineKeyboardButton(" ", callback_data="ignore") for _ in range(first_weekday)]
    
    # Заполняем кнопками с номерами дней
    for day in range(1, days_in_month + 1):
        current_date = date(first_day.year, first_day.month, day)
        # Если дата раньше завтрашнего дня или позже допустимого конца – делаем кнопку неактивной
        if current_date < allowed_start or current_date > allowed_end:
            buttons.append(InlineKeyboardButton("⛔", callback_data="ignore"))
        else:
            buttons.append(InlineKeyboardButton(str(day), callback_data=f"cal_date_{current_date.isoformat()}"))
    
    # Добавляем ряды по 7 кнопок (неделя)
    for i in range(0, len(buttons), 7):
        keyboard.add(*buttons[i:i+7])
    
    # Кнопки навигации (если возможно перемещение назад/вперёд)
    nav_buttons = []
    if offset > 0:
        nav_buttons.append(InlineKeyboardButton("⏪ Назад", callback_data=f"cal_prev_{offset-1}"))
    if offset < 3:  # Ограничим навигацию тремя месяцами
        nav_buttons.append(InlineKeyboardButton("Вперёд ⏩", callback_data=f"cal_next_{offset+1}"))
    if nav_buttons:
        keyboard.add(*nav_buttons)
    
    return keyboard

# -------------------------- Состояние s5: Выбор ас мәзірі (inline) --------------------------
@dp.callback_query_handler(lambda c: c.data in ["10000", "25000", "35000", "45000"], state=Formas.s5)
async def process_meal_selection(callback_query: types.CallbackQuery, state: FSMContext):
    # Удаляем предыдущее сообщение бота (если есть)
    await delete_last_bot_message(callback_query.message.chat.id, state)
    
    # Сохраняем выбранный ас мәзірі и его цену
    async with state.proxy() as data:
        data['mealMenu'] = callback_query.data
        data['mealPrice'] = int(callback_query.data)
    
    # Переходим в следующее состояние – выбор даты (s6)
    await Formas.next()
    
    await bot.send_chat_action(callback_query.from_user.id, action="typing")
    await asyncio.sleep(1)
    
    # Отправляем сообщение с выбранной ценой и прикреплённым динамическим календарём
    sent_msg = await bot.send_message(
        callback_query.from_user.id,
        text=f"*Сіз таңдадыңыз:* {data['mealPrice']} теңге\nӨтетін күнді таңдаңыз:",
        parse_mode="Markdown",
        reply_markup=generate_calendar(0)  # Функция, генерирующая календарь (начиная с текущего смещения 0)
    )
    await store_bot_message(state, sent_msg)
    await callback_query.answer()


# Обработчики inline-кнопок календаря (состояние s6)
@dp.callback_query_handler(lambda c: c.data.startswith("cal_prev_"), state=Formas.s6)
async def calendar_prev(callback_query: types.CallbackQuery, state: FSMContext):
    offset = int(callback_query.data.split("_")[-1])
    await callback_query.message.edit_reply_markup(reply_markup=generate_calendar(offset))
    await callback_query.answer()

@dp.callback_query_handler(lambda c: c.data.startswith("cal_next_"), state=Formas.s6)
async def calendar_next(callback_query: types.CallbackQuery, state: FSMContext):
    offset = int(callback_query.data.split("_")[-1])
    await callback_query.message.edit_reply_markup(reply_markup=generate_calendar(offset))
    await callback_query.answer()

@dp.callback_query_handler(lambda c: c.data.startswith("cal_date_"), state=Formas.s6)
async def calendar_date(callback_query: types.CallbackQuery, state: FSMContext):
    # Извлекаем выбранную дату в формате YYYY-MM-DD
    date_str = callback_query.data.replace("cal_date_", "")
    async with state.proxy() as data:
        data['event_date'] = date_str
    # Подтверждаем выбор даты – редактируем сообщение
    await callback_query.message.edit_text(
        text=f"Сіз таңдадыңыз: {date_str}",  # "Вы выбрали: {date_str}"
        parse_mode="Markdown"
    )
    await callback_query.answer()
    # Переходим в следующее состояние s7 – выбор персонала
    await Formas.next()
    # Отправляем сообщение с inline-клавиатурой для выбора персонала
    personnel_keyboard = InlineKeyboardMarkup(row_width=1)
    personnel_keyboard.add(
        InlineKeyboardButton("🕺 Асаба", callback_data="event_asaba"),
        InlineKeyboardButton("👯‍♀️ Биші", callback_data="event_bishi"),
        InlineKeyboardButton("🎤 Әнші", callback_data="event_anshi"),
        InlineKeyboardButton("✅ Дайын", callback_data="event_done")
    )
    await bot.send_message(
        callback_query.from_user.id,
        text="🎭 *Тойға қажетті персоналды таңдаңыз*",  # "Выберите персонал для мероприятия:"
        parse_mode="Markdown",
        reply_markup=personnel_keyboard
    )

# -----------------------------------------------------------------------------
# --- Состояние s7: Персоналды таңдау (бағасы есепке алынбайды, тек мәтін ретінде) ---
@dp.callback_query_handler(lambda c: c.data.startswith("event_"), state=Formas.s7)
async def process_event_selection(callback_query: types.CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        if 'event' not in data:
            data['event'] = []
        # Персоналды таңдаудың мэпингі (бағалар есепке алынбайды)
        event_mapping = {
            "event_asaba": "🕺 Асаба",
            "event_bishi": "👯‍♀️ Биші",
            "event_anshi": "🎤 Әнші"
        }
        # Егер "✅ Дайын" батырмасы басылса – таңдау аяқталады
        if callback_query.data == "event_done":
            try:
                await bot.delete_message(callback_query.message.chat.id, callback_query.message.message_id)
            except Exception:
                pass

            # Алдыңғы күйден қажетті мәндерді аламыз
            people = data.get('people', 0)
            meal_price = data.get('mealPrice', 0)
            event_list = data.get('event', [])
            event_date = data.get('event_date', 'Көрсетілмеген')

            # Жалпы соманы есептейміз (мысалы, адам саны * ас мәзірінің бағасы)
            total_sum = people * meal_price  
            # Розыгрышқа қатысу үшін 20% алдын ала төлем
            prepayment = int(total_sum * 0.2)

            summary_text = (
                f"📊 *Тапсырыс есебі:*\n\n"
                f"👥 *Адам саны:* {people} адам\n"
                f"🍽 *Ас мәзірінің бағасы:* {meal_price} тг/адам\n"
                f"🎭 *Тойдағы персонал:* {', '.join(event_list) if event_list else 'Таңдалмады'}\n"
                f"📅 *Өтетін іс-шара күні:* {event_date}\n\n"
                f"💰 *Жалпы сома:* {total_sum} тг\n"
                f"⚡ *Розыгрышқа қатысу үшін, жалпы соманың 20% алдын ала төлем жасау қажет:* {prepayment} тг\n\n"
                f"✅ Төлем жасалған соң сізге розыгрыш нөмірі беріледі!"
            )
            sent_msg = await bot.send_message(
                callback_query.from_user.id,
                text=summary_text,
                parse_mode="Markdown",
                reply_markup=btn.payment()  # Төлем жасауға арналған клавиатура, қажет болса
            )
            await store_bot_message(state, sent_msg)
            await callback_query.answer("Таңдау аяқталды!")
            await state.finish()
            return

        # Егер басқа батырма басылса – нақты персоналды таңдау өңделеді
        event_name = event_mapping.get(callback_query.data)
        if event_name is None:
            return
        if event_name in data['event']:
            data['event'].remove(event_name)
        else:
            data['event'].append(event_name)
        # Жаңартылған клавиатура – таңдалмаған опцияларды көрсетеді
        new_buttons = [
            InlineKeyboardButton(text=label, callback_data=key)
            for key, label in event_mapping.items() if label not in data['event']
        ]
        new_buttons.append(InlineKeyboardButton("✅ Дайын", callback_data="event_done"))
        new_keyboard = InlineKeyboardMarkup(row_width=1)
        new_keyboard.add(*new_buttons)
        updated_text = (
            f"🎭 *Тойға қажетті персоналды таңдаңыз*\n\n"
            f"Қосылған: {', '.join(data['event']) if data['event'] else 'Ешкім таңдалмады'}"
        )
        try:
            await callback_query.message.edit_text(
                text=updated_text,
                parse_mode="Markdown",
                reply_markup=new_keyboard
            )
        except MessageToEditNotFound:
            sent_msg = await bot.send_message(
                callback_query.from_user.id,
                text=updated_text,
                parse_mode="Markdown",
                reply_markup=new_keyboard
            )
            await store_bot_message(state, sent_msg)
        await callback_query.answer(f"{event_name} {'қосылды' if event_name in data['event'] else 'алынды'}!")
