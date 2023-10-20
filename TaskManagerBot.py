import telebot
import os
import json

TOKEN = '6553616361:AAH1OhlVHtKUj3778_2tZ8RJm-K69couI5c'

bot = telebot.TeleBot(TOKEN)

data_folder = "data"
task_file = os.path.join(data_folder, "task.json")

def load_data_from_json(file_path):
    if not os.path.exists(file_path):
        default_data = {}
        with open(file_path, 'w') as file:
            json.dump(default_data, file)
        return default_data

    with open(file_path, 'r') as file:
        return json.load(file)

def save_data_to_json(data, file_path):
    with open(file_path, 'w') as file:
        json.dump(data, file, ensure_ascii=False, indent=4)

tasks = load_data_from_json(task_file)

def save_tasks_to_json():
    save_data_to_json(tasks, task_file)

def log_task_creation(task_text, assignees):
    global tasks
    tasks[task_text] = {
        "assignees": assignees,
        "status": "Назначена"
    }
    save_tasks_to_json()

@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, "Привет! Этот бот поможет вам управлять задачами.")

@bot.message_handler(commands=['create_task'])
def create_task(message):
    chat_id = message.chat.id
    user_id = message.from_user.id
    if is_user_admin(user_id):
        bot.send_message(chat_id, "Пожалуйста, напишите задачу:")
        bot.register_next_step_handler(message, save_task)
    else:
        bot.send_message(chat_id, "Извините, у вас нет прав на создание задач.")

def save_task(message):
    chat_id = message.chat.id
    task_text = message.text

    bot.send_message(chat_id, "Укажите исполнителей (через запятую):")
    bot.register_next_step_handler(message, lambda m: save_task_assignees(m, task_text))

def save_task_assignees(message, task_text):
    chat_id = message.chat.id
    assignees = message.text.split(',')

    for assignee in assignees:
        try:
            bot.send_message(assignee, f"Вам назначена новая задача: '{task_text}'")
            send_task_with_keyboard(assignee, task_text)  # Отправляем задачу с клавиатурой
        except telebot.apihelper.ApiTelegramException as e:
            print(f"Ошибка при отправке сообщения в чат {assignee}: {e}")

    log_task_creation(task_text, assignees)
    bot.send_message(chat_id, f"Задача '{task_text}' создана и назначена исполнителям: {', '.join(assignees)}")

def send_task_with_keyboard(chat_id, task_text):
    keyboard = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.row("Выполнено", "Отмена")
    bot.send_message(chat_id, f"Задача: {task_text}\nСтатус: Назначена", reply_markup=keyboard)


@bot.callback_query_handler(func=lambda call: call.data == 'Выполнено')
def mark_task_done(call):
    chat_id = call.message.chat.id
    task_text = call.message.text.split('\n')[0].replace("Задача: ", "")
    if task_text in tasks:
        tasks[task_text]["status"] = "Выполнено"
        save_tasks_to_json()
        bot.send_message(chat_id, f"Задача '{task_text}' помечена как выполненная.")


@bot.message_handler(commands=['completed_tasks'])
def get_completed_tasks(message):
    chat_id = message.chat.id
    completed_tasks = [task for task, info in tasks.items() if info["status"] == "Выполнено"]
    if completed_tasks:
        bot.send_message(chat_id, "Выполненные задачи:")
        for task_text in completed_tasks:
            bot.send_message(chat_id, f"Задача: {task_text}\nСтатус: Выполнено")
    else:
        bot.send_message(chat_id, "Нет выполненных задач.")

def notify_admin_about_completed_task(chat_id, task_text):

    admin_id = 1572286222
    if admin_id:
        bot.send_message(admin_id, f"Задача '{task_text}' выполнена.")

def is_user_admin(user_id):
    users_data = load_data_from_json("users.json")
    for user in users_data["users"]:
        if user["id"] == user_id:
            return user["is_admin"]
    return False  # Если пользователя не найдено, считаем его не администратором

if __name__ == "__main__":
    bot.polling()







# import telebot
# import os
# import json
#
# TOKEN = '6553616361:AAH1OhlVHtKUj3778_2tZ8RJm-K69couI5c'  # Замените на свой токен Telegram
#
# bot = telebot.TeleBot(TOKEN)
#
# data_folder = "data"
# task_file = os.path.join(data_folder, "task.json")
#
# def load_data_from_json(file_path):
#     if not os.path.exists(file_path):
#         # Если файл не существует, создаем пустой JSON файл
#         default_data = {}
#         with open(file_path, 'w') as file:
#             json.dump(default_data, file)
#         return default_data
#
#     with open(file_path, 'r') as file:
#         return json.load(file)
#
# def save_data_to_json(data, file_path):
#     with open(file_path, 'w') as file:
#         json.dump(data, file, ensure_ascii=False, indent=4)
#
# tasks = load_data_from_json(task_file)
#
# def save_tasks_to_json():
#     save_data_to_json(tasks, task_file)
#
# def log_task_creation(task_text, assignees):
#     global tasks
#     tasks[task_text] = {
#         "assignees": assignees,
#         "status": "Назначена"
#     }
#     save_tasks_to_json()
#
# @bot.message_handler(commands=['start'])
# def start(message):
#     bot.reply_to(message, "Привет! Этот бот поможет вам управлять задачами.")
#
# @bot.message_handler(commands=['create_task'])
# def create_task(message):
#     chat_id = message.chat.id
#     user_id = message.from_user.id
#     if is_user_admin(user_id):
#         bot.send_message(chat_id, "Пожалуйста, напишите задачу:")
#         bot.register_next_step_handler(message, save_task)
#     else:
#         bot.send_message(chat_id, "Извините, у вас нет прав на создание задач.")
#
# def save_task(message):
#     chat_id = message.chat.id
#     task_text = message.text
#
#     bot.send_message(chat_id, "Укажите исполнителей (через запятую):")
#     bot.register_next_step_handler(message, lambda m: save_task_assignees(m, task_text))
#
# def save_task_assignees(message, task_text):
#     chat_id = message.chat.id
#     assignees = message.text.split(',')
#
#     for assignee in assignees:
#         try:
#             bot.send_message(assignee, f"Вам назначена новая задача: '{task_text}'")
#             send_task_with_keyboard(assignee, task_text)
#         except telebot.apihelper.ApiTelegramException as e:
#             print(f"Ошибка при отправке сообщения в чат {assignee}: {e}")
#
#     log_task_creation(task_text, assignees)
#     bot.send_message(chat_id, f"Задача '{task_text}' создана и назначена исполнителям: {', '.join(assignees)}")
#
# def send_task_with_keyboard(chat_id, task_text):
#     keyboard = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
#     keyboard.row("Выполнено", "Отмена")
#     bot.send_message(chat_id, f"Задача: {task_text}\nСтатус: Назначена", reply_markup=keyboard)
#
#
#
# @bot.callback_query_handler(func=lambda call: call.data == 'done')
# def mark_task_done(call):
#     chat_id = call.message.chat.id
#     task_text = call.message.text.split('\n')[0].replace("Задача: ", "")
#     if task_text in tasks:
#         tasks[task_text]["status"] = "Выполнено"
#         save_tasks_to_json()
#
#         # Отправляем уведомление об выполнении администратору
#         notify_admin_about_completed_task(chat_id, task_text)
#
#
# @bot.message_handler(commands=['completed_tasks'])
# def get_completed_tasks(message):
#     chat_id = message.chat.id
#     completed_tasks = [task for task, info in tasks.items() if info["status"] == "Выполнено"]
#     if completed_tasks:
#         bot.send_message(chat_id, "Выполненные задачи:")
#         for task_text in completed_tasks:
#             bot.send_message(chat_id, f"Задача: {task_text}\nСтатус: Выполнено")
#     else:
#         bot.send_message(chat_id, "Нет выполненных задач.")
#
#
# def notify_admin_about_completed_task(chat_id, task_text):
#     # Здесь вы можете указать ID администратора или другой способ определения администратора
#     admin_id = 1572286222
#     if admin_id:
#         bot.send_message(admin_id, f"Задача '{task_text}' выполнена.")
#
#
# def is_user_admin(user_id):
#     # Загрузка информации о пользователях из файла users.json
#     users_data = load_data_from_json("users.json")
#     for user in users_data["users"]:
#         if user["id"] == user_id:
#             return user["is_admin"]
#     return False
#
# if __name__ == "__main__":
#     bot.polling()
