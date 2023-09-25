import requests
import json
import telebot
import time
import math
from telebot import types
import threading 

bot = telebot.TeleBot('5404917379:AAGDk9pHQeVC4LVa40tc5q8wl093bGPjm-Q')
work = None


def monitoring_thread(chat_id):
    global work
    last_price = None
    procent = 0.001
    while work:
        url = "https://api.kuna.io"
        path = "/v4/markets/public/tickers?pairs=BTC_EUR"
        headers = {
            "accept": "application/json"
        }

        response = requests.get(url + path, headers=headers)
        new_price = response.json()
        price = new_price['data'][0]['price']

        if last_price is not None:
            price_change_percentage = (float(price) - float(last_price)) / float(last_price) * 100.0

            if math.fabs(price_change_percentage) >= procent:
                if price_change_percentage > procent:
                    bot.send_message(chat_id, f'Цена поднялась на {price_change_percentage:.2f}% до {price}')
                if price_change_percentage != 0 and price_change_percentage < procent:
                    bot.send_message(chat_id, f'Цена упала на {price_change_percentage:.2f}% до {price}')
        last_price = price
        time.sleep(300)

@bot.message_handler(commands=['start'])
def start(message):
    global work
    markup = types.ReplyKeyboardMarkup()
    button1 = types.KeyboardButton("/leave")
    markup.add(button1)
    chat_id = message.chat.id
    bot.send_message(chat_id, 'Привет, я буду мониторить цену BTC_EUR и отправлять уведомления об изменениях.', reply_markup=markup)
    
    # Запускаем функцию мониторинга в отдельном потоке
    work = True
    monitoring_thread_instance = threading.Thread(target=monitoring_thread, args=(chat_id,))
    monitoring_thread_instance.start()

@bot.message_handler(commands=['leave'])
def leave(message):
    global work
    stop = message.text.strip()
    if stop != '/leave':
        work = True
    else:
        work = False
        markup = types.ReplyKeyboardMarkup()
        markup.add(types.KeyboardButton('/start'))
        bot.send_message(message.chat.id, 'Бот остановлен', reply_markup=markup)

bot.polling(non_stop=True)
