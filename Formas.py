from aiogram import types
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher import FSMContext
from load import dp, bot
import asyncio
from datetime import datetime
import os
from traits import *

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
    s6 = State()  # Event түрі (personnel selection & final calculation)


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
    
    # Сначала отправляем сообщение с удалением клавиатуры (ReplyKeyboardRemove)
    sent_msg1 = await bot.send_message(
        message.from_user.id,
        text="*🍽 Ас мәзірін таңдаңыз*",
        parse_mode="Markdown",
        reply_markup=types.ReplyKeyboardRemove()
    )
    await store_bot_message(state, sent_msg1)
    
    await asyncio.sleep(1)
    
    # Затем отправляем сообщение с inline-клавиатурой выбора ас мәзірі
    sent_msg2 = await bot.send_message(
        message.from_user.id,
        text="*🍽 Ас мәзірін таңдаңыз*",
        parse_mode="Markdown",
        reply_markup=btn.meal_menu()
    )
    await store_bot_message(state, sent_msg2)


# -------------------------- Состояние s5: Выбор ас мәзірі (inline) --------------------------
@dp.callback_query_handler(lambda c: c.data in ["10000", "25000", "35000", "45000"], state=Formas.s5)
async def process_meal_selection(callback_query: types.CallbackQuery, state: FSMContext):
    await delete_last_bot_message(callback_query.message.chat.id, state)
    
    async with state.proxy() as data:
        data['mealMenu'] = callback_query.data
        data['mealPrice'] = int(callback_query.data)
    
    await Formas.next()  # Переход в s6

    await bot.send_chat_action(callback_query.from_user.id, action="typing")
    await asyncio.sleep(1)
    
    sent_msg = await bot.send_message(
        callback_query.from_user.id,
        text=f"*Сіз таңдадыңыз:* {data['mealPrice']} теңге\nТойда болатын персоналдарды таңдаңыз 👇",
        parse_mode="Markdown",
        reply_markup=btn.event_menu()
    )
    await store_bot_message(state, sent_msg)
    await callback_query.answer()


# -------------------------- Состояние s6: Выбор персонала (inline, динамическое редактирование) --------------------------
@dp.callback_query_handler(lambda c: c.data.startswith("event_"), state=Formas.s6)
async def process_event_selection(callback_query: types.CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        if 'event' not in data:
            data['event'] = []
        if 'event_sum' not in data:
            data['event_sum'] = 0

        event_mapping = {
            "event_asaba": ("🕺 Асаба", 100000),
            "event_bishi": ("👯‍♀️ Биші", 100000),
            "event_anshi": ("🎤 Әнші", 100000)
        }

        # Если нажата кнопка "✅ Дайын" – завершаем выбор и выводим итоговое сообщение
        if callback_query.data == "event_done":
            try:
                await bot.delete_message(callback_query.message.chat.id, callback_query.message.message_id)
            except Exception:
                pass

            people = data.get('people', 0)
            meal_price = data.get('mealPrice', 0)
            event_sum = data.get('event_sum', 0)
            total_sum = people * meal_price + event_sum
            prepayment = int(total_sum * 0.2)
            event_list = ', '.join(data.get('event', ["Таңдалмады"]))
            summary_text = (
                f"📊 *Тапсырыс есебі:*\n\n"
                f"👥 *Адам саны:* {people} адам\n"
                f"🍽 *Ас мәзірінің бағасы:* {meal_price} тг/адам\n"
                f"🎭 *Тойдағы персонал:* {event_list}\n"
                f"💰 *Қосымша шығындар:* {event_sum} тг\n\n"
                f"📌 *Жалпы сома:* {total_sum} тг\n"
                f"⚡ *Алдын ала төлем (20%):* {prepayment} тг\n\n"
                f"📢 Егер сіз іс-шараны ресми түрде рәсімдегіңіз келсе, алдымен 20% алдын ала төлем жасаңыз! "
                f"Қалған соманы мейрамханаға тікелей төлейсіз."
            )
            sent_msg = await bot.send_message(
                callback_query.from_user.id,
                text=summary_text,
                parse_mode="Markdown",
                reply_markup=btn.payment()
            )
            await store_bot_message(state, sent_msg)
            await callback_query.answer("Таңдау аяқталды!")
            await state.finish()
            return

        # Обработка выбора одного из пунктов персонала
        event_name, event_price = event_mapping.get(callback_query.data)
        if event_name in data['event']:
            data['event'].remove(event_name)
            data['event_sum'] -= event_price
        else:
            data['event'].append(event_name)
            data['event_sum'] += event_price

        # Формирование новой клавиатуры – показываем только невыбранные пункты
        new_buttons = [
            types.InlineKeyboardButton(text=label, callback_data=key)
            for key, (label, price) in event_mapping.items() if label not in data['event']
        ]
        new_buttons.append(types.InlineKeyboardButton("✅ Дайын", callback_data="event_done"))
        new_keyboard = types.InlineKeyboardMarkup(row_width=1)
        new_keyboard.add(*new_buttons)

        updated_text = (
            f"🎭 *Тойға қажетті персоналды таңдаңыз*\n\n"
            f"Қосылған: {', '.join(data['event']) if data['event'] else 'Ешкім таңдалмады'}\n"
            f"💰 Жалпы баға: {data['event_sum']} тг"
        )
        # Попытка редактирования сообщения с inline‑клавиатурой
        try:
            await callback_query.message.edit_text(
                text=updated_text,
                parse_mode="Markdown",
                reply_markup=new_keyboard
            )
        except MessageToEditNotFound:
            # Если сообщение для редактирования не найдено – отправляем новое сообщение
            sent_msg = await bot.send_message(
                callback_query.from_user.id,
                text=updated_text,
                parse_mode="Markdown",
                reply_markup=new_keyboard
            )
            await store_bot_message(state, sent_msg)
        await callback_query.answer(f"{event_name} {'қосылды' if event_name in data['event'] else 'алынды'}!")
