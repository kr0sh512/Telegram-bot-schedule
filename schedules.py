#!/usr/bin/python3.3
import threading, telebot, schedule, time, re
from datetime import datetime
import os, sys
from telebot import types
from telegram.constants import ParseMode
import for_json
from admin import admin_command, is_admin, send_admin_message, send_admin_document

bot = telebot.TeleBot("TELEBOT_API")

start_txt = 'Привет! Это бот, который будет кидать тебе сообщения перед нужной парой с номером кабинета/фамилией препода\
    \n\nТы можешь настроить отправку сообщений в лс или добавить меня в группу, куда я буду присылать расписание\
\n\nCreated by: @Kr0sH_512'

@bot.message_handler(commands=['test'])
@admin_command
def update_schedules(message):
    text = '<b>Жирный текст</b>\
        \n<i>Курсивный текст</i>\
        \n<s>Перечёркнутый текст</s>\
        \n<a href="google.com">Ссылка</a>\
        \n<code>Моноширинный текст</code>\
        \n<pre>Форматированный с сохранением     пробелов</pre>\
        \n<blockquote>Цитата</blockquote>'
    send_admin_message(text)

    return

@bot.message_handler(commands=['update'])
@admin_command
def update_schedules(message):
    for_json.create_schedule_tasks(manual=True)
    send_admin_message('Произошёл update')

    return

@bot.message_handler(commands=['restart'])
@admin_command
def restart_bot(message):
    send_admin_message('bye')
    os.execv(sys.executable, ['python'] + sys.argv)
            
@bot.message_handler(commands=['json'])
@admin_command
def send_json(message):
    with open(for_json.path_users, 'rb') as json_file: 
        send_admin_document(json_file)
    with open(for_json.path_schedule, 'rb') as json_file: 
        send_admin_document(json_file)
            
    return

@bot.message_handler(commands=['pause_all'])
@admin_command
def pause_bot(message):
    for_json.pause_bot()
    send_admin_message('Бот больше не отправляет расписание')
    
    return

@bot.message_handler(commands=['stop'])
@admin_command
def pause_bot(message):
    if len(str(message.text).split(' ')) != 2:
        send_admin_message('Эта команда вида /stop <i>id_пользователя</i>')
        return
    for_json.change_user_param(str(message.text).split(' ')[1], 'allow_message', 'no')
    send_admin_message('Успешно')
    return
        

@bot.message_handler(commands=['start'])
def start(message):
    if message.chat.type == "supergroup":        
        if len(message.text.split(' ')) != 2:
            send_message(message.chat.id, start_txt)
            send_message(message.chat.id, 'Похоже, что этот бот добавлен в группу. Чтобы он присылал расписание в чат, \
            укажите вместе с /start@vmk_schedule_bot номер своей группы.\
                \nПример:\n/start@vmk_schedule_bot 102')
        else:
            temp = message.text.split(' ')[1]
            
            if temp.isdigit():
                infos = [
                    message.chat.id, 
                    message.chat.title, 
                    '', 
                    message.from_user.username,
                    temp
                ]
                
                if temp in for_json.groups_in_json():
                    send_message(message.chat.id,
                        'Отлично! Теперь я буду присылать вам расписание {} группы'.format(temp))
                else:
                    send_message(message.chat.id, 'Похоже, что расписания для этой группы ещё не существует. \
                        \nРазработчик уже пинается, но можете дополнительно написать ему: @Kr0sH_512')
                    
                    send_admin_message('В группе {} был запрос на {} группу.\
                        \nid: {}'.format(message.chat.title, temp, message.chat.id))
                    temp = 'other'
                for_json.save_user(infos)
            else:
                send_message(message.chat.id, 'Введено не число. Попробуйте снова.\
                    \nПример:\n/start@vmk_schedule_bot 102')

        return
    
    send_message(message.chat.id, start_txt)
    
    markup = types.InlineKeyboardMarkup()
    for i in for_json.groups_in_json():
        markup.add(types.InlineKeyboardButton(text=i, callback_data=i))
    markup.add(types.InlineKeyboardButton(text="Моей группы нет в этом списке", callback_data="other"))
    bot.send_message(message.chat.id, 'Пожалуйста, выбери свою группу', parse_mode=ParseMode.HTML, reply_markup=markup)
    
    return

# @bot.callback_query_handler(func=lambda call: True)
@bot.callback_query_handler(func=lambda call: not(call.data in ['left', 'right']))
def callback_inline(call):
    infos = [
            call.from_user.id, 
            call.from_user.first_name, 
            call.from_user.last_name, 
            call.from_user.username,
            call.data
        ]
    
    for_json.save_user(infos)
    
    if call.data == 'other':
        bot.edit_message_text(chat_id=call.message.chat.id,
                              message_id=call.message.message_id, 
                              text='Используй команду /request \
                                  и напиши номер группы, которую хочешь добавить\
                                  \nПосле создания расписания для твоей группы, я пришлю тебе сообщение', 
                              parse_mode=ParseMode.HTML)
    else:
        bot.edit_message_text(chat_id=call.message.chat.id,
                              message_id=call.message.message_id, 
                              text='Отлично, теперь тебе будут приходить сообщения!', 
                              parse_mode=ParseMode.HTML)
        
    return

@bot.message_handler(commands=['help', 'faq'])
def help(message):
    help_msg = 'Мои команды:\
            \n/start - используй, чтобы сменить номер группы.\
            \n/schedule - используй, чтобы получить расписание на сегодня.\
            \n/info - используй, чтобы узнать твои настройки бота\
            \n/pause - используй, чтобы прекратить получать сообщения от бота\
            \n/thread - используй в нужном чате канала, чтобы бот отправлял сообщения именно туда\
            \n/timeout - настрой время, когда бот будет присылать тебе сообщение\
            \n/request - используй, чтобы отправить разработчику какой-то запрос\
            \n/source - Страница бота на Github\
            \n\nИли же можно всегда написать напрямую: @Kr0sH_512'
            
    send_message(message.chat.id, help_msg)
    
    if is_admin(message):
        admin_help_msg = 'И команды только для админа:\
            \n/restart - перезапуск бота.\
            \n/update - обновление schedule задач\
            \n/json - получить файл пользователей и расписания\
            \n/info <i>id_пользователя</i> - узнать настройки пользователя\
            \n/pause_all - приостановить бота для всех (каникулы/выходные)\
            \n/stop <i>id_пользователя</i> - приостановить отправку сообщений для пользователя'
        send_admin_message(admin_help_msg)
        
    return
    
@bot.message_handler(commands=['request'])
def request(message):
    send_message(message.from_user.id, 'Отправь мне сообщение и я перешлю его разработчику\
        \n(или напиши stop, чтобы отменить отправку)')
    bot.register_next_step_handler(message, send_request)
    
    return
    
def send_request(message):
    if message.text == "stop" or message.text == "стоп" or message.text[0] == '/':
        send_message(message.from_user.id, 'Отмена отпраки')
        return
    
    infos = [
        message.from_user.id, 
        message.from_user.first_name, 
        message.from_user.last_name, 
        message.from_user.username,
        message.text
    ]
    
    for i in range(len(infos)):
        if type(infos[i]) == type(None):
            infos[i] = ''
    
    admin_text = 'Сообщение от {} {} (@{}):\n\n{}\nid: {}'.format(infos[1], infos[2], infos[3], infos[4], infos[0])
    send_admin_message(admin_text)
    
    send_message(message.from_user.id, 'Ваше сообщение успешно доставлено!')
    
    return
    
@bot.message_handler(commands=['schedule'])
def send_schedule(message):
    text = 'К сожалению, бот не может отправить тебе расписание твоей группы на сегодня :('
    try:
        day = datetime.today().strftime('%A').lower()[:3] # mon tue ...
        text = for_json.get_schedule(message.chat.id, day)
    except Exception as e:
        send_admin_message('Schedule error from: {} \n\n {}'.format(message.chat.id, e))
    
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton(text="◀️", callback_data="left"),
               types.InlineKeyboardButton(text="▶️", callback_data="right"))
    bot.send_message(message.chat.id, text, ParseMode.HTML, reply_markup=markup)
    
    return
    
@bot.callback_query_handler(func=lambda call: call.data in ['left', 'right'])
def change_schedule(call):
    days = ['mon', 'tue', 'wed', 'thu', 'fri', 'sat']
    russian_days = ['понедельник', 'вторник', 'среду', 'четверг', 'пятницу', 'субботу']
    i = 6 # выходной
    for day in russian_days:
        if day in call.message.text:
            i = russian_days.index(day)
            break
    
    delta = (1) if (call.data == 'right') else (-1)
    ind = ((i + delta) % 6) if (i + delta > 0) else (i + delta)
    
    text = for_json.get_schedule(call.message.chat.id, days[ind])
    
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton(text="◀️", callback_data="left"),
               types.InlineKeyboardButton(text="▶️", callback_data="right"))
    
    bot.edit_message_text(text, call.message.chat.id, call.message.message_id, 
                              parse_mode=ParseMode.HTML, reply_markup=markup)
    
    return
    
@bot.message_handler(commands=['timeout'])
def set_timeout(message):
    send_message(message.chat.id, 'Пришли мне число от 1 до 60. \
        \nЭто будет количество минут, за которое я буду присылать тебе напоминание о уроке (По умолчанию: 10)')
    bot.register_next_step_handler(message, save_timeout)
    
    return

def save_timeout(message):
    if str(message.text).isdigit() and int(message.text) <= 60 and int(message.text) >= 1:
        for_json.change_user_param(message.chat.id, 'timeout', str(message.text))
        send_message(message.chat.id, 
                         'Хорошо, теперь ты будешь получать напоминания за {} минут до урока'.format(str(message.text)))
    else:
        send_message(message.chat.id, 
                         'Пожалуйста, пришли <u>число</u> от 1 до 60. \
                        \nПо умолчанию: 10')
        send_message(message.chat.id, 'Изменения не были внесены')
        
    return
    
@bot.message_handler(commands=['info'])
def send_info(message):
    if len(message.text.split(' ')) == 2 and is_admin(message):
        send_admin_message('Окей, держи настройки <code>{}</code>'.format(message.text.split(' ')[1]))
        infos = for_json.return_infos(message.text.split(' ')[1])
        text = '<i>Никнейм</i>: <b>@{}</b>\
        \n<i>Имя</i>: <b>{} {}</b>\
        \n<i>Выбранная группа</i>: <b>{}</b>\
        \n<i>Время напоминания до урока</i>: <b>{}</b>\
        \n<i>Разрешены ли напоминания</i>: <b>{}</b>'.format(infos['username'], infos['first_name'], infos['last_name'],
            (infos['group'] if infos['group'] != 'other' else 'не выбрана'), 
                                                             infos['timeout'], 
                                                             ('да' if infos['allow_message'] == 'yes' else 'нет'))
        send_admin_message(text)
        return
    
    send_message(message.chat.id, 'Хорошо, вот твои настройки:')
    infos = for_json.return_infos(message.chat.id)
    text = '<i>Выбранная группа</i>: <b>{}</b>\
        \n<i>Время напоминания до урока</i>: <b>{}</b>\
        \n<i>Разрешены ли напоминания</i>: <b>{}</b>'.format((infos['group'] if infos['group'] != 'other' else 'не выбрана'), 
                                                             infos['timeout'], 
                                                             ('да' if infos['allow_message'] == 'yes' else 'нет'))
    send_message(message.chat.id, text)
    
    return
    
@bot.message_handler(commands=['source'])
def send_source(message):
    bot.send_message(message.chat.id, 'https://github.com/kr0sh512/Telegram-bot-schedule', parse_mode=ParseMode.HTML)
    
    return
    
@bot.message_handler(commands=['thread'])
def change_thread(message):
    thread_id = ''
    
    try:
        thread_id = message.reply_to_message.message_thread_id
    except AttributeError:
        thread_id = "General"
        
    for_json.change_user_param(str(message.chat.id), 'thread', thread_id)
    
    send_message(message.chat.id, 'Хорошо, теперь я буду отправлять сообщения в этот чат', thread_id)
    
    return
    
@bot.message_handler(commands=['pause'])
def pause_schedule(message):
    for_json.change_user_param(str(message.chat.id), 'allow_message', 'no')
    
    send_message(message.chat.id, 'Рассылка сообщений преращена. \
        \nДля возобновления воспользуйтесь командой\n/start')
    
    return
    
@bot.message_handler(content_types=['text'])
def text_message(message):
    if message.chat.type == "supergroup":
        return
    send_message(message.from_user.id, 'К сожалению, я ещё не умею обрабатывать сообщения.\
    \nИспользуй команды из меню или напиши /help.')
    
    return

def send_message(id, text, thread_id='General'):
    if thread_id == 'General':
        thread_id = None
        
    try:
        bot.send_message(chat_id=id, text=text, parse_mode=ParseMode.HTML, message_thread_id=thread_id,disable_web_page_preview=True)
    except Exception as e:
        time.sleep(5)
        try:
            bot.send_message(chat_id=id, text=text, parse_mode=ParseMode.HTML, message_thread_id=thread_id,disable_web_page_preview=True)
        except Exception as e:
            text_error = 'Error from user: <code>{}</code>\n{}'.format(id, str(e))
            send_admin_message(text_error)
            print(id, e)
    
    return

def send_document(id, file, text = ''):   
    try:
        bot.send_document(id, file, caption=text)
    except Exception as e:
        time.sleep(5)
        try:
            bot.send_document(id, file, caption=text)
        except Exception as e:
            text_error = 'Error from user: <code>{}</code>\n{}'.format(id, str(e))
            send_admin_message(text_error)
            print(id, e)
    
    return

if __name__ == '__main__':
    for_json.create_schedule_tasks()

    send_admin_message('Я перезапустился!')
    print("-------------------------")
    
    threading.Thread(target=bot.infinity_polling, name='bot_infinity_polling', daemon=True).start()
    
    while True:
        try:
            schedule.run_pending()
            time.sleep(5)
        except Exception as e:
            print(e)
            time.sleep(10)
            