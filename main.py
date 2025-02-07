#!/usr/bin/env python
# -*- coding: utf-8 -*-
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher.filters import Text
from load import bot, dp
from aiogram import types
from FormaAdmin import *
from keyboard import*
from database import*
from config import*
from Forma import*
import asyncio
from traits import*
import time
from FormaAdmin import*
import os
from tests import*
from Formas import*


generator = Generator()
btn = Button()
db = Database()

PRICE = 500000

@dp.message_handler(content_types=types.ContentType.DOCUMENT)
async def pdf_received_handler(message: types.Message, state: FSMContext):
    # Проверяем, что отправленный файл — это PDF
    if message.document.mime_type == 'application/pdf':
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

        print(result)
        print(len(result))

        async with state.proxy() as data:
            data['data'] = message.text
            data['pdf_result'] = result
            data['fileName'] = file_name
            data['len'] = len(result)
            if data['len'] == 16:
                if convert_currency_to_int(result[3]) == PRICE:
                    data['count'] = int(convert_currency_to_int(result[3]) / PRICE)
                    sum = PRICE * data['count']
                    data['sum'] = sum
                    print(data['sum'])
            elif data['len'] == 8:
                if convert_currency_to_int(result[1]) == PRICE:
                    data['count'] = int(convert_currency_to_int(result[1]) / PRICE)
                    sum = PRICE * data['count']
                    data['sum'] = sum
                    print(data['sum'])
               


        if data['len'] == 16:
            print(f"Expected sum: {data['sum']}, Actual sum: {convert_currency_to_int(data['pdf_result'][3])}")

            if convert_currency_to_int(data['pdf_result'][3]) != data['sum']: 
                await bot.send_message(
                    message.from_user.id,
                    text="*Төленетін сумма қате!\nҚайталап көріңіз*",
                    parse_mode="Markdown",
                    reply_markup=btn.menu()
                ) 
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
                        reply_markup=btn.menu()
                    )   
                    return

                await Forma.s3.set()
                await bot.send_message(
                    message.from_user.id,
                    text="*Той иесінің аты жөнін жазыңыз*",
                    parse_mode="Markdown",
                )
                return
            else:
                await bot.send_message(
                    message.from_user.id,
                    text="*Дұрыс емес счетқа төледіңіз!\nҚайталап көріңіз*",
                    parse_mode="Markdown",
                    reply_markup=btn.menu_not_paid()
                )
        elif data['len'] == 8:
            print(f"Expected sum: {data['sum']}, Actual sum: {convert_currency_to_int(data['pdf_result'][1])}")

            if convert_currency_to_int(data['pdf_result'][1]) != data['sum']: 
                await bot.send_message(
                    message.from_user.id,
                    text="*Төленетін сумма қате!\nҚайталап көріңіз*",
                    parse_mode="Markdown",
                    reply_markup=btn.menu()
                ) 
                return

            
            print(data['pdf_result'][1])
            print(data['pdf_result'][3])
        
            if data['pdf_result'][3] == "Сатушының ЖСН/БСН 900315402310" or data['pdf_result'][3] == "ИИН/БИН продавца 900315402310":
                print(db.CheckLoto(data['pdf_result'][2]))
                if db.CheckLoto(data['pdf_result'][2]) == True:
                    await bot.send_message(
                        message.from_user.id,
                        text="*ЧЕК ТӨЛЕНІП ҚОЙЫЛҒАН!\nҚайталап көріңіз*",
                        parse_mode="Markdown",
                        reply_markup=btn.menu()
                    )   
                    return

                await Forma.s3.set()
                await bot.send_message(
                    message.from_user.id,
                    text="*Той иесінің аты жөнін жазыңыз*",
                    parse_mode="Markdown",

                )
                return
            else:
                await bot.send_message(
                    message.from_user.id,
                    text="*Дұрыс емес счетқа төледіңіз!\nҚайталап көріңіз*",
                    parse_mode="Markdown",
                    reply_markup=btn.menu_not_paid()
                )  

    else:
        # Если отправлен не PDF-файл, можно уведомить пользователя
        await message.reply("Тек, PDF файл жіберу керек!")
    

@dp.message_handler(commands=['admin'])
async def handler(message: types.Message):
    print(message.from_user.id)
    

    if message.from_user.id == admin or message.from_user.id == admin5:
        await bot.send_message(
        message.from_user.id,
        text="😊 *Сәлеметсіз бе %s !\nСіздің статусыңыз 👤 Админ(-ка-)*"%message.from_user.first_name,
        parse_mode="Markdown",
        reply_markup=btn.admin()
    )
        

@dp.message_handler(commands=['address'])
async def handler(message: types.Message):
    print(message.from_user.id)
    

    await bot.send_message(
        message.from_user.id,
        text="😊 *Сәлеметсіз бе %s !\nСіздің статусыңыз 👤 Админ(-ка-)*"%message.from_user.first_name,
        parse_mode="Markdown",
        reply_markup=btn.all_address()
    )

@dp.message_handler(Text(equals="📈 Статистика"), content_types=['text'])
async def handler(message: types.Message):
    if message.from_user.id in {admin, admin2, admin3, admin5}:
        # Получаем статистику из базы данных
        tik_tok_count = db.get_tiktok_count()
        instagram_count = db.get_instagram_count()
        
        # Форматируем сообщение
        stats_message = (
            f"📊 <b>Статистика:</b>\n\n"
            f"🔹 TikTok: {tik_tok_count} заходов\n"
            f"🔹 Instagram: {instagram_count} заходов\n"
        )
        
        # Отправляем сообщение
        await message.reply(stats_message, parse_mode="HTML")

@dp.message_handler(commands=['start', 'go'])
async def start_handler(message: types.Message):
    
    args = message.get_args()

    if args == "TikTok":
        # Логика для TikTok
        db.tiktok_counter()
        await Formas.s1.set()
        await bot.send_message(
                message.from_user.id,
                text="*Құрметті тойшыл қазағым! Жай ғана той жасап астыңызға темір 🚘 тұлпар мінгіңіз келсе біздің мейрамханымызда 🥳 мерей той жасаңыз\nҚандай той жасағыңыз келеді?*",
                parse_mode="Markdown",
                reply_markup=btn.typeOfCelebrate()
        )  
        return
    
    elif args == "Instagram":
        # Логика для Instagram
        db.instagram_counter()
        await Formas.s1.set()
        await bot.send_message(
                message.from_user.id,
                text="*Құрметті тойшыл қазағым! Жай ғана той жасап астыңызға темір 🚘 тұлпар мінгіңіз келсе біздің мейрамханымызда 🥳 мерей той жасаңыз\nҚандай той жасағыңыз келеді?*",
                parse_mode="Markdown",
                reply_markup=btn.typeOfCelebrate()
        ) 
        return 

    print(message.from_user.id)

    from datetime import datetime
    fileId = "AgACAgIAAxkBAAMCZ6H7ST5vYR0drn_R8JW6B0XQc00AAkjmMRtYghBJs5bEHKTuTjEBAAMCAAN5AAM2BA"

    user_id = message.from_user.id
    user_name = f"@{message.from_user.username}"
    time_now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    
    db.JustInsert(user_id, user_name, time_now)  
    
    if db.CheckUserPaid(message.from_user.id) == True:
        await Formas.s1.set()
        await bot.send_message(
                message.from_user.id,
                text="*Құрметті тойшыл қазағым! Жай ғана той жасап астыңызға темір 🚘 тұлпар мінгіңіз келсе біздің мейрамханымызда 🥳 мерей той жасаңыз\nҚандай той жасағыңыз келеді?*",
                parse_mode="Markdown",
                reply_markup=btn.typeOfCelebrate()
        ) 
        return
    

    await Formas.s1.set()
    await bot.send_message(
            message.from_user.id,
            text="*Құрметті тойшыл қазағым! Жай ғана той жасап астыңызға темір 🚘 тұлпар мінгіңіз келсе біздің мейрамханымызда 🥳 мерей той жасаңыз\nҚандай той жасағыңыз келеді?*",
            parse_mode="Markdown",
            reply_markup=btn.typeOfCelebrate()
    ) 


@dp.message_handler(Text(equals="🥳 Той жасау"), content_types=['text'])
async def handler(message: types.Message):
    
    await Formas.s1.set()
    await bot.send_message(
            message.from_user.id,
            text="*Құрметті тойшыл қазағым! Жай ғана той жасап астыңызға темір 🚘 тұлпар мінгіңіз келсе біздің мейрамханымызда 🥳 мерей той жасаңыз\nҚандай той жасағыңыз келеді?*",
            parse_mode="Markdown",
            reply_markup=btn.typeOfCelebrate()
    ) 


@dp.callback_query_handler(lambda c: c.data in ["buy_celebrate", "accept"])
async def process_callback(callback_query: types.CallbackQuery):
    # Удаляем предыдущее сообщение
    await bot.delete_message(callback_query.message.chat.id, callback_query.message.message_id)

    await bot.answer_callback_query(callback_query.id)

    if callback_query.data == "buy_celebrate":
        # Логика для "buy_cosmetics"
        await Forma.s1.set()
        await bot.send_message(
            callback_query.from_user.id,
            text="*Қанша суммаға той жасайсыз? 1 билет құны 500 000 теңге\nТөмендегі түймелерді баса отыра сумманы таңдаңыз*",
            parse_mode="Markdown",
            reply_markup=btn.digits_and_cancel()
        )
    elif callback_query.data == "accept":
        # Логика для "accept"
        await bot.send_message(
            callback_query.from_user.id,
            text="Сіз оффертаны қабылдадыңыз. Рахмет! 😊\n\nPDF - форматта чекті жіберіңіз 👇",
            reply_markup=btn.menu()
        )



# Новый хендлер для обработки отправки PDF-файла
@dp.message_handler(content_types=types.ContentType.DOCUMENT, state='*')
async def pdf_received_handler(message: types.Message, state: FSMContext):
    pass

@dp.message_handler(content_types=[types.ContentType.PHOTO, types.ContentType.VIDEO])
async def media_handler(message: types.Message, state: FSMContext):
    file_id = None

    # Проверяем тип контента
    if message.content_type == 'photo':
        # Получаем file_id самого большого размера фото
        file_id = message.photo[-1].file_id
    elif message.content_type == 'video':
        # Получаем file_id видео
        file_id = message.video.file_id

    if file_id:
        # Сохраняем file_id в состоянии
        async with state.proxy() as data:
            data['file_id'] = file_id

        # Отправляем file_id пользователю
        await bot.send_message(
            message.from_user.id,
            text=f"*FileID: {data['file_id']}*",
            parse_mode="Markdown",
        )
    else:
        await bot.send_message(
            message.from_user.id,
            text="Ошибка: неизвестный тип медиафайла.",
        ) 

@dp.message_handler(Text(equals="💸 Money"), content_types=['text'])
async def handler(message: types.Message):
    
    if message.from_user.id == admin or message.from_user.id == admin2 or message.from_user.id == admin3:
        sum = db.get_money_sum()
        await bot.send_message(
                message.from_user.id,
                text="""*💳 Жалпы қаражат: %d*"""%sum,
                parse_mode="Markdown",
                reply_markup=btn.admin()
            )    


@dp.message_handler(Text(equals="📨 Хабарлама жіберу"), content_types=['text'])
async def handler(message: types.Message):
    if message.from_user.id == admin or message.from_user.id == admin5:
        await FormaAdmin.s1.set()
        await bot.send_message(
                message.from_user.id,
                text="""*✏️ Хабарлама типін таңдаңыз*""",
                parse_mode="Markdown",
                reply_markup=btn.typeMsg()
            )     



@dp.message_handler(commands=['help'])
@dp.message_handler(Text(equals="📨 Админге хабарлама"), content_types=['text'])
async def handler(message: types.Message):
    await bot.send_message(
        message.from_user.id,
        text="""*+77005007032* - телеграм номер\n\n*+77786557207* - Айдана, БИЗНЕС ВАТСАП НОМЕР""",
        parse_mode="Markdown",
        reply_markup=btn.linkTelega()
    )


@dp.message_handler(Text(equals="📑 Лото"), content_types=['text'])
async def send_just_excel(message: types.Message):
    if message.from_user.id == admin or message.from_user.id == admin5:
        db.create_loto_excel('./excell/loto.xlsx')
        await bot.send_document(message.from_user.id, open('./excell/loto.xlsx', 'rb'))

@dp.message_handler(Text(equals="👥 Қолданушылар саны"), content_types=['text'])
async def send_client_excel(message: types.Message):
    if message.from_user.id == admin or message.from_user.id == admin5:
        db.create_client_excel('./excell/clients.xlsx')
        await bot.send_document(message.from_user.id, open('./excell/clients.xlsx', 'rb'))

@dp.message_handler(Text(equals="👇 Just Clicked"), content_types=['text'])
async def send_loto_excel(message: types.Message):
    if message.from_user.id == admin or message.from_user.id == admin5:
        db.create_just_excel('./excell/just_users.xlsx')
        await bot.send_document(message.from_user.id, open('./excell/just_users.xlsx', 'rb'))
    


@dp.message_handler(Text(equals="📨 Хабарлама жіберу"), content_types=['text'])
async def handler(message: types.Message):

    await bot.send_message(
        message.from_user.id,
        text="""*@senior_coffee_drinker*""",
        parse_mode="Markdown",
        reply_markup=btn.admin()
    ) 



@dp.message_handler(Text(equals="🧧 Ұтыс билеттерім"), content_types=['text'])
async def handler(message: types.Message):

    id_user = message.from_user.id            # Get the user ID from the message
    loto_ids = db.FetchIdLotoByUser(id_user)  # Fetch the list of id_loto for this user
    
    if loto_ids:
        ids_formatted = ", ".join(map(str, loto_ids))  # Format the list as a comma-separated string
        response_text = f"Сіздің ұтыс билеттеріңіздің ID-лары: {ids_formatted}"
    else:
        response_text = "Сіздің ұтыс билетіңіз жоқ."

    await bot.send_message(
        message.from_user.id,
        text=response_text,
        parse_mode="Markdown",
        reply_markup=btn.menu()
    )

@dp.message_handler(Text(equals="◀️ Кері"), content_types=['text'])
async def handler(message: types.Message):

    if message.from_user.id == admin or message.from_user.id == admin5:
        await bot.send_message(
        message.from_user.id,
        text="😊 *Сәлеметсіз бе %s !\nСіздің статусыңыз 👤 Админ(-ка-)*"%message.from_user.first_name,
        parse_mode="Markdown",
        reply_markup=btn.admin()
    )

async def send_pdf_with_caption(user_id, id_loto, caption):
    loto_info = db.fetch_loto_by_id(id_loto)
    if not loto_info:
        await bot.send_message(user_id, text="PDF not found.")
        return

    receipt = loto_info[3]  # Adjusted index for receipt column
    pdf_path = f"/home/cinema/pdf/{receipt}"
    
    if os.path.exists(pdf_path):
        await bot.send_document(
            user_id,
            document=open(pdf_path, 'rb'),
            caption=caption,
            reply_markup=btn.gift()
        )
    else:
        await bot.send_message(user_id, text="PDF file not found.")


