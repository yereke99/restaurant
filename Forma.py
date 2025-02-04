from aiogram import types
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types.message import Message
from load import dp, bot
from aiogram import types 
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
import logging
from keyboard import*
from database import Database
import datetime
from main import*
import asyncio
from config import admin, admin2, admin3
from datetime import datetime
from traits import *
import time
from traits import*
from config import*
import os
from aiogram.types import InputMediaPhoto, InputMediaVideo
from tests import *

PRICE = 500000

generator = Generator()
btn = Button()
db = Database()

# Dont touch!
#file_id = "BAACAgIAAxkBAAIBfmZVvFgHXNy6dEjDe2rDHuGlC3jrAALaTQAC1jOpSiMaJlO20CwKNQQ"  

c1 = "AgACAgIAAxkBAAMVZyYg7KuSuN_IPDYgM5ULXX7AzhkAAqzhMRvQzjBJDkg8df7HrdYBAAMCAAN5AAM2BA"
c2 = "AgACAgIAAxkBAAMXZyYg7ivtTtgaTt3uOn_SthmgAqQAAq3hMRvQzjBJKU9TV6vMYh4BAAMCAAN5AAM2BA"
c3 = "AgACAgIAAxkBAAMZZyYg8clEejb320N0ZrK_Jb5YAV8AAq7hMRvQzjBJhxNPNuDLOMkBAAMCAAN5AAM2BA"

# Ensure the directory exists
os.makedirs('./pdf/', exist_ok=True)

class Forma(StatesGroup):
    s1 = State()  # Той билет саны
    s2 = State()  # Read PDF
    s3 = State()  # FIO
    s4 = State()  # Контакт
    s5 = State()  # Адресс


@dp.message_handler(state='*', commands='🔕 Бас тарту')
@dp.message_handler(Text(equals='🔕 Бас тарту', ignore_case=True), state='*')
async def cancell_handler(message: types.Message, state: FSMContext):
    """
    :param message: Бастартылды
    :param state: Тоқтату
    :return: finish
    """
    
    current_state = await state.get_state()
    if current_state is None:
        return

    logging.info('Бас тарту!')
    
    await state.finish()
    await message.reply('Сіз тапсырыстан бас тарттыңыз.', reply_markup=btn.menu_not_paid())



@dp.message_handler(lambda message: not message.text.isdigit(), state=Forma.s1)
async def handler(message: types.Message):
    return await message.reply("Сандармен жазыңыз 🔢")


@dp.message_handler(lambda message: message.text.isdigit(), state=Forma.s1)
async def handler(message: types.Message, state: FSMContext):

    """
    state: number
    """
    try:
        await Forma.next()

        async with state.proxy() as data:
            data['count'] = int(message.text)

        sum = PRICE * data['count']

        async with state.proxy() as data:
            data['sum'] = sum

        await bot.send_message(
            message.from_user.id,
            text="""Сіздің чегіңіз тексерілуде. Жақын арада  жауабын береміз"""
        
        )
        await bot.send_message(
            message.from_user.id,
            text="*Kaspi Pay - төлем жүйесін қолдана отыра 💳 төлем жасаңыз\n🥳 Той жасау 💳 бағасы: %d теңге*"%sum,
            parse_mode="Markdown",
            reply_markup=btn.payment()
        ) 
        
    except Exception as e:
        print(e) 
        await Forma.s1.set()
        await bot.send_message(
            message.from_user.id,
            text="*Қанша суммаға той жасайсыз? Төмендегі түймелерді баса отыра сумманы таңдаңыз*",
            parse_mode="Markdown",
            reply_markup=btn.digits_and_cancel()
        )   

        await bot.send_message(
            admin,
            text="Error: %s"%str(e),
        )   

@dp.message_handler(lambda message: not (message.document and message.document.mime_type == 'application/pdf'), state=Forma.s2, content_types=types.ContentType.DOCUMENT)
async def pdf_validator(message: types.Message, state: FSMContext):
    await message.reply(".pdf файл форматымен жіберіңіз!")
    await Forma.s2.set()

@dp.message_handler(state=Forma.s2, content_types=types.ContentType.DOCUMENT)
async def handler(message: types.Message, state: FSMContext):

    try:
        document = message.document

        # Generate a unique filename
        user_id = message.from_user.id
        timestamp = int(time.time())
        random_int = Generator.generate_random_int()
        file_name = f"{user_id}_{timestamp}_{random_int}.pdf"
        file_path = os.path.join('./pdf/', file_name)

        # Download the PDF file
        file_info = await bot.get_file(document.file_id)
        await bot.download_file(file_info.file_path, file_path)

        # Process the PDF file
        pdf_reader = PDFReaders(file_path)
        pdf_reader.open_pdf()
        #result = pdf_reader.extract_specific_info()
        result = pdf_reader.extract_detailed_info()
        pdf_reader.close_pdf()


        async with state.proxy() as data:
            data['data'] = message.text
            data['pdf_result'] = result
            data['fileName'] = file_name

        print(data['pdf_result'])
        
        if convert_currency_to_int(data['pdf_result'][3]) != data['sum']: 
            await bot.send_message(
                message.from_user.id,
                text="*Төленетін сумма қате!\nҚайталап көріңіз*",
                parse_mode="Markdown",
                reply_markup=btn.menu_not_paid()
            )  
            await state.finish() 
            return
        
        print(data['pdf_result'][3])
        print(data['pdf_result'][11])
       
        if data['pdf_result'][10] == "Сатушының ЖСН/БСН 900315402310" or data['pdf_result'][10] == "ИИН/БИН продавца 900315402310":
            print(db.CheckLoto(data['pdf_result'][6]))
            if db.CheckLoto(data['pdf_result'][6]) == True:
                await bot.send_message(
                    message.from_user.id,
                    text="*ЧЕК ТӨЛЕНІП ҚОЙЫЛҒАН!\nҚайталап көріңіз*",
                    parse_mode="Markdown",
                    reply_markup=btn.menu_not_paid()
                )  
                await state.finish() 
                return

            await Forma.next()
            await bot.send_message(
                message.from_user.id,
                text="*Аты жөніңізді жазыңыз*",
                parse_mode="Markdown",
                reply_markup=types.ReplyKeyboardRemove()

            )
            return
    
        await bot.send_message(
                message.from_user.id,
                text="*Дұрыс емес счетқа төледіңіз!\nҚайталап көріңіз*",
                parse_mode="Markdown",
                reply_markup=btn.menu_not_paid()
            )  
        await state.finish() 

    except Exception as e:
        print(e)
        await bot.send_message(
            admin,
            text="Error: %s"%str(e),
        ) 

        username = message.from_user.username
        user_id = message.from_user.id
        # Формирование сообщения
        caption = f"Файл от пользователя:\n\n👤 Username: @{username if username else 'Нет username'}\n🆔 User ID: {user_id}"
        for admin_id in [admin, admin2, admin3, admin4, admin5]:
            try:
                # Отправляем PDF файл администратору
                file_path = "/home/restaurant/pdf/" +data['fileName']
                with open(file_path, 'rb') as file:
                    await bot.send_document(admin_id, document=file, caption=caption)
            except Exception as ex:
                print(f"Не удалось отправить файл администратору {admin_id}: {str(ex)}")
        
        await Forma.s2.set()
        await bot.send_message(
                message.from_user.id,
                text="Төлем жасаған соң чекті 📲 .pdf форматында жіберіңіз!\n\n*НАЗАР АУДАРЫҢЫЗ ЧЕКТІ МОДЕРАТОР ТЕКСЕРЕДІ\n\n ЕСКЕРТУ ❗️\nЖАЛҒАН ЧЕК ЖІБЕРУ НЕМЕСЕ БАСҚАДА ДҰЫРЫС ЕМЕС ЧЕКТЕР ЖІБЕРУ АВТОМАТТЫ ТҮРДЕ ҰТЫС ОЙЫННАН ШЫҒАРЫЛАДЫ*",
                parse_mode="Markdown",
                reply_markup=btn.cancel()
            ) 
        

@dp.message_handler(state=Forma.s3)
async def handler(message: types.Message, state: FSMContext):
    
    async with state.proxy() as data:
        data['fio'] = message.text
    
    await Forma.next()

    await bot.send_message(
        message.from_user.id,
        text="*Сізбен кері 📲 байланысқа шығу үшін байланыс нөміріңізді қалдырыңыз! Төменде тұрған \n\n📱 Контактімен бөлісу кнопкасын басыныз\n\nЕШҚАШАН САНДАРМЕН ЖАЗБАЙМЫЗ ‼️*",
        parse_mode="Markdown",
        reply_markup=btn.send_contact()
    )
    
    
    
@dp.message_handler(state=Forma.s4, content_types=types.ContentType.CONTACT)
async def handler(message: types.Message, state: FSMContext):

    async with state.proxy() as data:
        data['contact'] = message.contact.phone_number
    
    await Forma.next() 
    
    db.increase_money(data['sum'])

    await bot.send_message(
            message.from_user.id,
            text="""*Той өтетін мейрамхана мекенжайын таңдаңыз!*""",
            parse_mode="Markdown",
            reply_markup=btn.addresss()
        )

    

@dp.message_handler(state=Forma.s5)
async def handler(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['city'] = message.text

    if db.InsertClient(
        message.from_user.id,
        message.from_user.username,
        data['fio'],
        data['contact'],
        data['city'],
        datetime.now(),
        "paid",
        "true"
    ):
        time_now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        if data['len'] == 16:
            for i in range(int(data['count'])):
                gen = generator.generate_random_int()
                db.InsertLoto(
                    message.from_user.id,
                    gen,
                    data['pdf_result'][6], # data['pdf_result'][6]
                    message.from_user.username,
                    data['fileName'],
                    data['fio'],
                    data['contact'],
                    data['city'],
                    time_now,
                )
        elif data['len'] == 8:
            for i in range(int(data['count'])):
                gen = generator.generate_random_int()
                db.InsertLoto(
                    message.from_user.id,
                    gen,
                    data['pdf_result'][2], # data['pdf_result'][2]
                    message.from_user.username,
                    data['fileName'],
                    data['fio'],
                    data['contact'],
                    data['city'],
                    time_now,
                )

        # Отправка уведомления пользователю
        await bot.send_message(
            message.from_user.id,
            text="""Құттықтаймыз сіз той жасауға сәтті төлем жасадыңыз!
Қосымша сұрақтарыңыз болса👇🏻
/help - батырмасын басыңыз
""",
            parse_mode="Markdown",
            reply_markup=btn.menu()
        )

        # Отправка уведомления администраторам
        admin_ids = [admin, admin2, admin3, admin4, admin5]  # Список ID администраторов
        file_path = f"/home/restaurant/pdf/{data['fileName']}"  # Убедитесь, что путь к файлу корректен
        if data['len'] == 16:
            for admin_id in admin_ids:
                try:
                    await bot.send_document(
                        admin_id,
                        document=open(file_path, 'rb'),
                        caption=(
                            f"✅ *Жаңа тапсырыс төленді!*\n\n"
                            f"📋 Тапсырыс мәліметтері:\n"
                            f"👤 ФИО: {data['fio']}\n"
                            f"📞 Байланыс: {data['contact']}\n"
                            f"📍 Қала: {data['city']}\n"
                            f"💸 Төлем сомасы: {data['pdf_result'][3]} KZT\n"
                            f"📁 Файл атауы: {data['fileName']}\n\n"
                            "🔔 Бұл тапсырысты өңдеуге дайын болыңыз."
                        ),
                        parse_mode="Markdown"
                    )
                except Exception as e:
                    logging.error(f"Не удалось отправить сообщение администратору {admin_id}: {e}")
        elif data['len'] == 8:
            for admin_id in admin_ids:
                try:
                    await bot.send_document(
                        admin_id,
                        document=open(file_path, 'rb'),
                        caption=(
                            f"✅ *Жаңа тапсырыс төленді!*\n\n"
                            f"📋 Тапсырыс мәліметтері:\n"
                            f"👤 ФИО: {data['fio']}\n"
                            f"📞 Байланыс: {data['contact']}\n"
                            f"📍 Қала: {data['city']}\n"
                            f"💸 Төлем сомасы: {data['pdf_result'][1]} KZT\n"
                            f"📁 Файл атауы: {data['fileName']}\n\n"
                            "🔔 Бұл тапсырысты өңдеуге дайын болыңыз."
                        ),
                        parse_mode="Markdown"
                    )
                except Exception as e:
                    logging.error(f"Не удалось отправить сообщение администратору {admin_id}: {e}")

        await state.finish()
    else:
        await bot.send_message(
            message.from_user.id,
            text="*Ой 🤨 бір нәрседен қате кетті\nҚайталап көріңіз*",
            parse_mode="Markdown",
            reply_markup=btn.menu_not_paid()
        )
        await state.finish()

    
