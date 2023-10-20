from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackContext
from requests import get
from bs4 import BeautifulSoup
import json
import time


BOT_TOKEN = '6553616361:AAH1OhlVHtKUj3778_2tZ8RJm-K69couI5c'


def get_code_by_city(city_name: str) -> str:
    with open('cities.json', 'r', encoding='utf-8') as f:
        cities = json.load(f)
    return cities[city_name.capitalize()]


def get_key_by_value(dictionary: dict, value):
    for key, val in dictionary.items():
        if value == val:
            return key
    raise KeyError


async def set_city(update: Update, context: CallbackContext):
    text = update.message.text.split()

    if len(text) < 2:
        await update.message.reply_text('Для этой команды нужно указать город через пробел. Например:\n'
                                        '/set_city Москва')
        return
    elif len(text) > 2:
        text = [text[0], ' '.join(text[1:])]
    try:
        city_code = get_code_by_city(text[1])
    except KeyError:
        await update.message.reply_text(f'Город {text[1]} не найден!')
        return
    with open('users.json', 'r+') as f:
        try:
            users = json.load(f)
        except json.JSONDecodeError as e:
            users = {}
        users[str(context._chat_id)] = city_code
        f.seek(0)
        json.dump(users, f)
        await update.message.reply_text(f'Город {text[1]} успешно установлен!')


async def popular_films(update: Update, context: CallbackContext):
    with open('users.json', 'r') as f:
        try:
            cities = json.load(f)
            city = cities[str(context._chat_id)]
        except json.JSONDecodeError:
            city = 'msk'
        except KeyError:
            city = 'msk'

    city_name = get_key_by_value(cities, city)
    get_url = f'https://www.afisha.ru/{city}/cinema'
    films_url = 'https://www.afisha.ru'

    categories = None
    while not categories:
        response = get(get_url)
        text = response.text
        text_soup = BeautifulSoup(text, 'html.parser')
        categories = text_soup.find_all('div', class_='_7TFDu')
        time.sleep(0.3)

    brand_new_films = categories[0].find_all_next('div', class_='wsXlA pZeTF SUiYd')
    buttons = []
    for film in brand_new_films[:4]:
        a_href = film.find_next('a', class_='vcSoT dcsqk atqQM')
        div_film_name = film.find_next('div', class_='mQ7Bh')
        film_name = div_film_name.text
        link = a_href.get('href')
        buttons.append([InlineKeyboardButton(text=f'{film_name}', url=f'{films_url}{link}', callback_data='film')])
    await update.message.reply_text(f'Кинопремьеры вашего города: {city_name}',
                                    reply_markup=InlineKeyboardMarkup(buttons))


if __name__ == '__main__':
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler('films', popular_films))
    app.add_handler(CommandHandler('set_city', set_city))

    app.run_polling()
