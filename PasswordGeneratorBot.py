from telegram.error import BadRequest
from telegram.ext import CommandHandler, \
    CallbackContext, ApplicationBuilder, \
    CallbackQueryHandler, MessageHandler
from telegram.ext.filters import TEXT
from telegram import Update, InlineKeyboardMarkup, \
    InlineKeyboardButton
import random


def generate_password(length, capital=False, digits=False, specials=False):
    if length < 4 or length > 20:
        return 'Password have low or big length'

    chars = [chr(i) for i in range (97,123)]

    if capital:
        chars.extend([chr(i) for i in range(65,91)])
    if digits:
        chars.extend([chr(i) for i in range(48, 58)])
    if specials:
        chars.extend([chr(i) for i in range(33,48)])

    psw = ''.join(random.choices(chars, k=length))
    return psw


def change_config(markup, callback_data, func, **kwargs):
    config = [
        [markup.inline_keyboard[0][0],
         change_button(markup.inline_keyboard[0][1], callback_data, func, **kwargs),
         markup.inline_keyboard[0][2]]
    ]
    for inline_buttons in markup.inline_keyboard[1:]:
        config.append([change_button(inline_buttons[0], callback_data, func, **kwargs),])

    return config


def change_button(buttom, callback_data, func , **kwargs):
    if buttom.callback_data == callback_data or buttom.callback_data == 'size':
        return InlineKeyboardButton(text=func(text=buttom.text,
                                              callback_data=callback_data,
                                              **kwargs),
                                    callback_data=buttom.callback_data)
    return buttom


def switch_text(**kwargs):
    text = kwargs['text']
    return text.replace(cross_icon, check_mark) if cross_icon in text \
        else text.replace(check_mark, cross_icon)


def change_size (**kwargs):
    size = kwargs['size']
    callback_data = kwargs.get('callback_data')
    if callback_data:
        if 'size_up' in callback_data and size < 20:
            return f'{size + 1}'
        elif 'size_down' in callback_data and size > 4:
            return f'{size - 1}'
    return f'{size}'


async def password(update: Update, context: CallbackContext):
    words = update.message.text.split()
    words.pop(0)
    if len(words) == 0 or len(words) > 4 or not words[0].isdigit():
        await update.message.reply_text(f'Unknown format! Try : <length> (Optional): <capital> <digits> <specials> ')
        return
    kwargs = {}
    for param in ['capital', 'digits', 'specials']:
        if param in words:
            kwargs[param] = True
    length = int(words[0])
    psw = generate_password(length, **kwargs)
    await update.message.reply_text(f'Your password: {psw}')


async def menu(update: Update, context: CallbackContext):
    markup = InlineKeyboardMarkup(buttons)
    await update.message.reply_text('Menu:', reply_markup=markup)

async def got_message (update: Update,context: CallbackContext):
    if waiting_for_new_size and update.message.text.isdigit():
        global callback_size
        callback_size = int(update.message.text)
        if callback_size < 4:
            await update.message.reply_text('Size is too small. Try bigger!')
            callback_size = 4
        elif callback_size > 20:
            await update.message.reply_text("Size is too big. Try smaller!")
            callback_size = 20
        else:
            await update.message.reply_text('Done! Just press size button again!')
async def Buttons_pressed(update: Update, context:CallbackContext):
    query = update.callback_query

    markup = update.callback_query.message.reply_markup

    if query.data == 'generate':
        length = 0
        params = {}
        for tuple_buttons in markup.inline_keyboard:
            if len(tuple_buttons) > 1:
                length = int(tuple_buttons[1].text)
            elif check_mark in tuple_buttons[0].text:
                key = tuple_buttons[0]. callback_data.split()[1]
                params[key] = True
        await query.message.reply_text(generate_password(length, **params))
    elif query.data == "size":
        global waiting_for_new_size
        if waiting_for_new_size is False:
            await query.message.reply_text("Type new size: ")
            waiting_for_new_size = True
        else:
            global callback_size
            markup = InlineKeyboardMarkup(inline_keyboard=change_config(markup, query.data,
                                                                        change_size, size=callback_size))
            waiting_for_new_size = False
            try:
                await query.edit_message_reply_markup(reply_markup=markup)
            except BadRequest:
                await query.message.reply_text("You didn't change size!")
    elif 'check_box' in query.data:
        markup = InlineKeyboardMarkup(inline_keyboard=change_config(markup, query.data, switch_text))
        await query.edit_message_reply_markup(reply_markup=markup)

    elif 'tune' in query.data:
        current_size = int(markup.inline_keyboard[0][1].text)
        markup = InlineKeyboardMarkup(inline_keyboard=
                                      change_config(markup, query.data, change_size, size=current_size))
        try:
            await query.edit_message_reply_markup(reply_markup=markup)
        except BadRequest:
            await query.message.reply_text("Size have been reached it's limit")


if __name__ == '__main__':

    cross_icon = u'\u274c'
    check_mark = u'\u2705'

    size_config = {
        'tune size_down': r'\/',
        'size': '12',
        'tune size_up': '/\\'
    }
    waiting_for_new_size = False
    password_config = {
        'check_box capital': f'Capitalise {cross_icon}',
        'check_box digits': f'Digits {cross_icon}',
        'check_box specials': f'Special symbols {cross_icon}',
        'generate':'Generate password'

    }

    buttons = [[InlineKeyboardButton(text=value, callback_data=key)
                for key, value in size_config.items()]]

    buttons += [[InlineKeyboardButton(text=value, callback_data=key)]
                for key, value in password_config.items()]

    BOT_TOKEN = '6553616361:AAH1OhlVHtKUj3778_2tZ8RJm-K69couI5c'
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler('password',password))
    app.add_handler(CommandHandler('menu', menu))
    app.add_handler(CallbackQueryHandler(Buttons_pressed))
    app.add_handler(MessageHandler(TEXT, got_message))
    app.run_polling()

# link:t.me/PyTelegram4409bot