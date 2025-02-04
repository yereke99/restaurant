#!/usr/bin/env python
# -*- coding: utf-8 -*-
from aiogram import types
import datetime
from load import bot
from database import Database

class Button:
    def __init__(self) -> None:
        pass

    def _create_keyboard(self, btns):

        button = types.ReplyKeyboardMarkup(resize_keyboard=True, selective=True)
        for btn in btns:
            button.add(btn)

        return button
    
    def payment(self):

        keyboard = types.InlineKeyboardMarkup()
        keyboard.add(types.InlineKeyboardButton("💳 Төлем жасау", url="https://pay.kaspi.kz/pay/cvyrauxx"))
        
        return keyboard
    
    def buy_celebrate(self):

        keyboard = types.InlineKeyboardMarkup()
        keyboard.add(types.InlineKeyboardButton("🥳 Той жасау", callback_data="buy_celebrate"))
        
        return keyboard
    
    def buy_cinema(self):

        keyboard = types.InlineKeyboardMarkup()
        keyboard.add(types.InlineKeyboardButton("🥳 Той жасау", callback_data="buy_celebrate"))
        
        return keyboard
    
    def address(self):

        keyboard = types.InlineKeyboardMarkup()
        keyboard.add(types.InlineKeyboardButton("🥳 Той жасау үшін", callback_data="buy_celebrate"))
        keyboard.add(types.InlineKeyboardButton("📍 Мекен жайымыз", url="https://2gis.kz/almaty/firm/9429940000876885/76.895478%2C43.155811?m=76.895663%2C43.155864%2F17.97"))
        
        return keyboard
    
    def all_address(self):

        keyboard = types.InlineKeyboardMarkup()
        keyboard.add(types.InlineKeyboardButton("📍 Достар мейрамханасы", url="https://2gis.kz/almaty/firm/9429940000876885/76.895478%2C43.155811?m=76.895663%2C43.155864%2F17.97"))
        
        return keyboard
    
    def addresss(self):
        return self._create_keyboard([
            "📍 Достар мейрамханысы",
        ])
    
    def offertas(self):
        keyboard = types.InlineKeyboardMarkup()
        keyboard.add(types.InlineKeyboardButton("📃 Офферта", url="https://producerr.tilda.ws/oferta"))
        keyboard.add(types.InlineKeyboardButton("📃 Оффертамен ✔️ таныстым", callback_data="accept"))
        
        return keyboard
    
    def linkTelega(self):
        keyboard = types.InlineKeyboardMarkup()
        keyboard.add(types.InlineKeyboardButton("Менеджер чат 🤖", url="https://t.me/@earllp"))
        
        return keyboard

    
    def menu(self):
        return self._create_keyboard([
            "🧧 Ұтыс билеттерім",
            "🥳 Той жасау",
            "📨 Админге хабарлама",
            #"📲 Байланыс номері",  
        ])

    def again(self):
        return self._create_keyboard([
            "🥳 Той жасау"
        ])
       

    def loto(self):
        return self._create_keyboard([
            "🧧 Ұтыс билеттерім"
       ])
    
    def digits_and_cancel(self):
        buttons = [str(i) for i in range(1, 10)] + ["🔕 Бас тарту"]
        return self._create_keyboard(buttons)

    
    def menu_not_paid(self):

        return self._create_keyboard([
            "🥳 Той жасау",
            "📨 Админге хабарлама",  
            #"📲 Байланыс номері", 
        ])
    
    def city(self):
        cities = [
            "Ақтау", "Семей", "Тараз", "Қызылорда", "Ақтөбе", "Алматы",
            "Шымкент", "Қостанай", "Петропавл", "Талдықорған", "Қарағанды",
            "Жезқазған", "Атырау", "Орал", "Өскемен", "Астана", "Павлодар",
            "Көкшетау", "Түркістан"
        ]
        return self._create_keyboard(cities)
    
    def admin(self):

        return self._create_keyboard([
            "📈 Статистика",
            "💸 Money",
            "👇 Just Clicked",
            "👥 Қолданушылар саны",
            "📑 Лото",
            "📨 Хабарлама жіберу",
            #"🎞 Кино беру",
            "🎁 Сыйлықтар",
        ])
    
    def gift(self):

        return self._create_keyboard([
            "🎁 1-ші сыйлық",
            "🎁 2-ші сыйлық",
            "🎁 3-ші сыйлық",
            "🎁 4-ші сыйлық",
            "🎁 5-ші сыйлық",
            "🎁 6-ші сыйлық",
            "🎁 7-ші сыйлық",
            "🎁 8-ші сыйлық",
            "🎁 9-ші сыйлық",
            "🎁 10-ші сыйлық",
            "🎁 🚗 Көлік",
            #"🎁 Сыйлық",
            "◀️ Кері",
        ])

    def typeMsg(self):

        return self._create_keyboard([
            "🖋 Текстік хабарлама",
            "🖼 Картинкалық хабарлама",
            "🗣 Аудио хабарлама",
            "📹 Бейне хабарлама",
            "🔕 Бас тарту",
        ])
    
    def typeUsers(self):

        return self._create_keyboard([
            "📑 Жалпы қолданушыларға",
            "💳 Төлем 🟢 жасаған 📊 қолданушаларға",
            "🔕 Бас тарту",
        ])
    
    
    def message(self):

        return self._create_keyboard([
            "📩 Жеке хабарлама",
            "📑 Жалпы қолданушыларға",
            "👇 Just Clicked",
            "💳 Төлем 🟢 жасаған 📊 қолданушаларға",
            "💳 Төлем 🔴 жасамаған 📊 қолданушаларға",
            "⬅️ Кері",
        ])
    
    def study(self):

        return self._create_keyboard([
            "💽 Бейне сабақтарды енгізу",
            "📋 Сабақтар тізімі",
            "⬅️  Кері",
        ])
    
    def cancel(self):

        return self._create_keyboard([
            "🔕 Бас тарту",
        ])
    
    def offerta(self):

        return self._create_keyboard([
            "🟢 Келісімімді беремін",
            "🔴 Жоқ, келіспеймін",
            "🔕 Бас тарту",
        ])
    
    def agreement(self):

        return self._create_keyboard([
            "🟢 Әрине",
            "🔴 Жоқ сенімді емеспін",
            "🔕 Бас тарту",
        ])
    
    def send_contact(self):

        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        keyboard.add(types.KeyboardButton("📱 Контактімен бөлісу", request_contact=True))

        return keyboard
