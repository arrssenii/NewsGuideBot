# Импортируем необходимые классы.
import telebot
from telebot import types  # для работы с ботом
import requests  # для сбора данных
import pyshorteners  # для коротких ссылок
from config import token  # токен

short = pyshorteners.Shortener()  # объект класса, укорачивающего ссылки
bot = telebot.TeleBot(token)  # объект класса TeleBot


def helppy(message):  # команда помощи со списком и описанием команд
    bot.send_message(message.chat.id,
                     "🗞Новость - одна свежая новость\n\n"
                     "🗞Новости🗞 - несколько свежих новостей подряд\n\n"
                     "🔍Поиск - поиск новости по ключевому слову\n\n"
                     "📈Курс валют - актуальный курс валют\n\n"
                     "🔗Сайт - ссылка на сайт проекта News Guide\n\n"
                     "📩Контакты - контакты разработчика\n\n"
                     "⚠Помощь - список команд. вы только что вызвали.")


def news():  # cбор новостей
    # собираем запрос
    request = "https://newsapi.org/v2/top-headlines?country=ru&apiKey=499c7a59bd714f83abbee6644022628e"
    response = requests.get(request)  # Выполняем запрос.
    json_response = response.json()['articles']  # преобразуем ответ в json-объект
    return json_response  # возвращаем


# команда которая отправляет пользователю свежайшую (для апишки) новость на русском языке
def fresh_news(message):
    news_api = []  # список для хранения будущих новостей
    response = news()  # достаём новости
    for article in response:  # пробегаемся по ним, оставляя только нужное
        source = (article['source']['name'])
        title = (article['title'])
        url = article['url']
        news_api.append({'source': source, 'title': title, 'url': url})  # добавляем всё, что нужно, в список
    # отправляем пользователю заголовок, источник и ссылку на новость
    bot.send_message(message.chat.id, f'{news_api[0]["title"]}\n'
                                      f'Источник - {news_api[0]["source"]}\n'
                                      f'Читать новость - {short.tinyurl.short(news_api[0]["url"])}')


def some_news(message, context):  # команда выводящая несколько новостей
    news_api = []  # список для хранения будущих новостей
    response = news()  # достаём новости
    for article in response:  # пробегаемся по ним, собирая всё "по полочкам"
        source = (article['source']['name'])
        title = (article['title'])
        url = article['url']
        time = article['publishedAt']
        # добавляем всё, что нужно, в список
        news_api.append({'source': source, 'title': title, 'url': url, 'time': time})
    for i in range(int(context)):
        bot.send_message(message.chat.id, f'{news_api[i]["title"]}\n'
                                          f'Источник - {news_api[i]["source"]}\n'
                                          f'Опубликовано {news_api[i]["time"][:10]} '
                                          f'в {news_api[i]["time"][11:16]}\n'
                                          f'Читать новость - {short.tinyurl.short(news_api[i]["url"])}')


def contacts(message):  # команда выдаёт пользователю мои ФИ и способы связаться
    bot.send_message(message.chat.id, 'Семенихин Арсений\nvk - https://vk.com/arssemenikhin\ntg - @arrssenii')


def site(message):  # команда выводит сайт проекта
    bot.send_message(message.chat.id, 'Сайт проекта - http://kirillka00.pythonanywhere.com/home')


def currate(message):  # команда выводит актуальный курс валют
    response = requests.get("https://www.cbr-xml-daily.ru/daily_json.js")  # собираем запрос
    currencies = []  # список для хранения данных
    if response.status_code == 200:  # в хорошем случае
        content = response.json()
        data = [i for i in content['Valute']]
        for i in data:
            values = content['Valute'][i]  # отбираем только нужные данные
            value = values['Value']
            charCode = values['CharCode']
            # отбираем только некоторые (интересные) валюты
            if charCode == 'USD' or charCode == 'EUR' or charCode == 'PLN' or charCode == 'JPY' \
                    or charCode == 'KRW' or charCode == 'CHF' \
                    or charCode == 'CZK' or charCode == 'UAH' or charCode == 'CNY' \
                    or charCode == 'AMD' or charCode == 'BYN' or \
                    charCode == 'GBP' or charCode == 'AUD':
                currencies.append({'CharCode': charCode, 'Value': value})
        text = ''  # заготовка для сообщение
        for i in currencies:
            text += f'1 {i["CharCode"]} = {round(i["Value"], 3)} RUB\n'
        bot.send_message(message.chat.id, text)  # выдаём ответ пользователю
    else:  # если что-то пошло не так, выводим в консоль ошибку
        bot.send_message(message.chat.id, 'Техническая ошибка. Повторите попытку позже.')
        print('Ошибка:')
        print(response)
        print("Http статус:", response.status_code, "(", response.reason, ")")


def back(message):  # команда назад
    markup = types.ReplyKeyboardMarkup(resize_keyboard=False)
    item_news = types.KeyboardButton('🗞Новость')
    item_somenews = types.KeyboardButton('🗞Новости🗞')
    item_course = types.KeyboardButton('📈Курс валют')
    item_site = types.KeyboardButton('🔗Сайт')
    item_contact = types.KeyboardButton('📩Контакты')
    item_help = types.KeyboardButton('⚠Помощь')
    item_search = types.KeyboardButton('🔍Поиск')
    markup.add(item_news, item_somenews, item_course, item_search,
               item_site, item_contact, item_help)
    bot.send_message(message.chat.id, '⬅Назад', reply_markup=markup)


def search_news(message, context):  # команда для поиска новости по ключевому слову
    if context:  # если ключевое слово было введено
        request = f"https://newsapi.org/v2/everything?language=ru&q={context}&sortBy=popularity&searchIn=title" \
                  f"&apiKey=499c7a59bd714f83abbee6644022628e"  # собираем запрос
        response = requests.get(request)  # Выполняем запрос.
        news_api = []  # список для хранения будущих новостей
        if response:
            json_response = response.json()  # Преобразуем ответ в json-объект
            responce = json_response['articles']  # достаём новости
            for article in responce:  # пробегаемся по ним, оставляя только нужное
                source = (article['source']['name'])
                title = (article['title'])
                url = article['url']
                news_api.append({'source': source, 'title': title, 'url': url})  # добавляем всё, что нужно, в список
        if news_api:
            bot.send_message(message.chat.id, f'{news_api[0]["title"]}\n'
                                      f'Источник - {news_api[0]["source"]}\n'
                                      f'Читать новость - {short.tinyurl.short(news_api[0]["url"])}')
        else:
            if response.json()["totalResults"] == 0:
                bot.send_message(message.chat.id, 'Нет результатов.')  # если результатов 0, то сообщаем пользователю
            else:  # если же проблема не в отсутствии результатов, то сообщаем пользователю и пишем в консоль об ошибке
                bot.send_message(message.chat.id, 'Техническая ошибка. '
                                                  'Попробуйте ввести слово ещё раз или повторите попытку позже.')
                print('Ошибка:')
                print(request)
                print("Http статус:", response.status_code, "(", response.reason, ")")


@bot.message_handler(commands=['start'])
def start(message):  # команда старта
    markup = types.ReplyKeyboardMarkup(resize_keyboard=False)
    item_news = types.KeyboardButton('🗞Новость')
    item_somenews = types.KeyboardButton('🗞Новости🗞')
    item_course = types.KeyboardButton('📈Курс валют')
    item_site = types.KeyboardButton('🔗Сайт')
    item_contact = types.KeyboardButton('📩Контакты')
    item_help = types.KeyboardButton('⚠Помощь')
    item_search = types.KeyboardButton('🔍Поиск')
    markup.add(item_news, item_somenews, item_course, item_search,
               item_site, item_contact, item_help)  # кастомная клавиатура
    bot.send_message(message.chat.id,
                     'Я - бот проекта News Guide.\nЧтобы узнать, что я могу, нажмите "⚠Помощь"\n'
                     'Сайт проекта - http://kirillka00.pythonanywhere.com/home', reply_markup=markup)


@bot.message_handler(content_types=['text'])  # обработчик команд
def bot_message(message):
    if message.text == '⚠Помощь':  # помощь
        helppy(message)
    elif message.text == '🗞Новость':  # новость
        fresh_news(message)
    elif message.text == '🗞Новости🗞':  # несколько новостей
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        item2 = types.KeyboardButton('2️⃣')
        item3 = types.KeyboardButton('3️⃣')
        item4 = types.KeyboardButton('4️⃣')
        item5 = types.KeyboardButton('5️⃣')
        back = types.KeyboardButton('⬅Назад')  # кнопка назад, если пользователь передумал
        markup.add(item2, item3, item4, item5, back)
        msg = bot.send_message(message.chat.id, 'Сколько?', reply_markup=markup)  # вызов другой клавиатуры
        bot.register_next_step_handler(msg, user_answer)  # пошаговый обработчик отсылает к функции user_answer
    elif message.text == '🔍Поиск':  # поиск
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        back = types.KeyboardButton('⬅Назад')
        markup.add(back)  # кнопка назад, если пользователь передумал
        msg = bot.send_message(message.chat.id, 'Введите ключевое слово.', reply_markup=markup)
        bot.register_next_step_handler(msg, user_answer2)  # пошаговый обработчик отсылает к функции user_answer2
    elif message.text == '📈Курс валют':  # курс валют
        currate(message)
    elif message.text == '🔗Сайт':  # сайт
        site(message)
    elif message.text == '📩Контакты':  # контакты
        contacts(message)
    elif message.text == '⬅Назад':  # команда назад
        def back(message):
            markup = types.ReplyKeyboardMarkup(resize_keyboard=False)
            item_news = types.KeyboardButton('🗞Новость')
            item_somenews = types.KeyboardButton('🗞Новости🗞')
            item_course = types.KeyboardButton('📈Курс валют')
            item_site = types.KeyboardButton('🔗Сайт')
            item_contact = types.KeyboardButton('📩Контакты')
            item_help = types.KeyboardButton('⚠Помощь')
            item_search = types.KeyboardButton('🔍Поиск')
            markup.add(item_news, item_somenews, item_course, item_search,
                       item_site, item_contact, item_help)
            bot.send_message(message.chat.id, '⬅Назад', reply_markup=markup)
        back(message)


def user_answer(message):  # запрашиваем количество новостей для some_news, выводим, и вызываем back
    if message.text == '2️⃣':
        some_news(message, 2)
    if message.text == '3️⃣':
        some_news(message, 3)
    if message.text == '4️⃣':
        some_news(message, 4)
    if message.text == '5️⃣':
        some_news(message, 5)
    back(message)


def user_answer2(message):  # запрашиваем ключевое слово для search_news, выводим, и вызываем back
    if message.text != '⬅Назад':
        search_news(message, message.text)
    back(message)


bot.polling(none_stop=True)