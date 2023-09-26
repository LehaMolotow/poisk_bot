# -*- coding: utf-8 -*-

import os
import json
from telebot import TeleBot, types
import telebot

import logging

logger = telebot.logger
telebot.logger.setLevel(logging.DEBUG) # Outputs debug messages to console.



bot = TeleBot('xxxxxxxxxxxxx')


users_data = {}
users_folder = 'users'


@bot.message_handler(commands=['start'])
def start(message):
    user_id = message.from_user.id
    users_data[user_id] = {
        'current_step': 0,
        'data': {}
    }
    bot.reply_to(message, 'Добро пожаловать! Пожалуйста, введите ваш возраст:')

@bot.message_handler(content_types=['photo', 'text'])
def process_message(message):
    user_id = message.from_user.id

    if user_id not in users_data:
        bot.reply_to(message, 'Для использования бота, пожалуйста, сначала зарегистрируйтесь, используя команду /start.')
        return

    current_step = users_data[user_id]['current_step']

    if message.content_type == 'text':
        if current_step == 0:
            users_data[user_id]['data']['age'] = message.text
            users_data[user_id]['current_step'] += 1
            bot.reply_to(message, 'Введите ваше имя:')
        elif current_step == 1:
            users_data[user_id]['data']['name'] = message.text
            users_data[user_id]['current_step'] += 1
            bot.reply_to(message, 'Введите ваш город:')
        elif current_step == 2:
            users_data[user_id]['data']['city'] = message.text
            users_data[user_id]['current_step'] += 1
            bot.reply_to(message, 'Введите ваш пол (М/Ж):')
        elif current_step == 3:
            users_data[user_id]['data']['gender'] = message.text
            users_data[user_id]['current_step'] += 1
            bot.reply_to(message, 'Введите вашу сексуальную ориентацию:')
        elif current_step == 4:
            users_data[user_id]['data']['sex_preferences'] = message.text
            users_data[user_id]['current_step'] += 1
            bot.reply_to(message, 'Введите ваши хобби:')
        elif current_step == 5:
            users_data[user_id]['data']['hobby'] = message.text
            users_data[user_id]['current_step'] += 1
            bot.reply_to(message, 'Отправьте мне фотографию:')
    elif message.content_type == 'photo':
        if current_step == 6:
            file_id = message.photo[-1].file_id
            file_info = bot.get_file(file_id)
            file_path = file_info.file_path

            downloaded_file = bot.download_file(file_path)
            photo_folder = 'users'
            if not os.path.exists(photo_folder):
                os.makedirs(photo_folder)

            photo_path = os.path.join(photo_folder, f'{user_id}.jpg')
            with open(photo_path, 'wb') as file:
                file.write(downloaded_file)

            users_data[user_id]['data']['photo_url'] = photo_path

            users_data[user_id]['current_step'] = 6

            markup = types.ReplyKeyboardMarkup(row_width=1)
            button = types.KeyboardButton('/find_partner')
            markup.add(button)

            bot.reply_to(message, 'Регистрация успешно завершена! Спасибо!', reply_markup=markup)

            save_user_data(user_id)
# Функция записи пользователя в  json
def save_user_data(user_id):
    # users_folder = 'users'
    user_folder = os.path.join(users_folder, str(user_id))
    if not os.path.exists(user_folder):
        os.makedirs(user_folder)

    user_data_path = os.path.join(user_folder, f'{user_id}.json')
    with open(user_data_path, 'w', encoding='utf-8') as file:
        json.dump(users_data[user_id]['data'], file, ensure_ascii=False)

@bot.message_handler(commands=['find_partner'])
def find_partner(message):
    user_id = message.from_user.id

    if user_id not in users_data:
        bot.reply_to(message, 'Для использования бота, пожалуйста, сначала зарегистрируйтесь, используя команду /start.')
        return

    bot.reply_to(message, 'Ищем подходящего партнера...')

    user_data = users_data[user_id]['data']

    partners = []

    users_folder = 'users'
    for folder_name in os.listdir(users_folder):
        if folder_name != str(user_id):
            folder_path = os.path.join(users_folder, folder_name)
            data_path = os.path.join(folder_path, f'{folder_name}.json')
            with open(data_path, 'r', encoding='utf-8') as file:
                data = json.load(file)
                if data['gender'] != user_data['gender'] and data['sex_preferences'] == user_data['sex_preferences']:
                    partners.append(data)

    if len(partners) > 0:
        partner = partners[0]
        bot.reply_to(message, f'Мы нашли для вас партнера!\n\nИмя: {partner["name"]}\nГород: {partner["city"]}\nВозраст: {partner["age"]}\nХобби: {partner["hobby"]}\n\nФото партнера: {partner["photo_url"]}')
    else:
        bot.reply_to(message, 'К сожалению, мы не нашли подходящего партнера.')

bot.polling()
