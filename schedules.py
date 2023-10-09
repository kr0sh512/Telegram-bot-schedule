#!/usr/bin/python3.3
import threading, telebot, schedule, time
import os, sys
from telebot import types
from telegram.constants import ParseMode
import for_json

bot = telebot.TeleBot("API_TOKEN")
admin_id = 'ADMIN_ID'

start_txt = 'Привет! Это бот, который будет кидать тебе сообщения перед нужной парой с номером кабинета/фамилией препода\
\n\nCreated by: @Kr0sH\_512'

@bot.message_handler(commands=['update'])
def update_schedules(message):
    if (str(message.from_user.id) != admin_id):
        bot.send_message(message.from_user.id, 'Команда доступна только администратору', parse_mode='Markdown')
    else:
        for_json.create_schedule_tasks()

    
@bot.message_handler(commands=['restart'])
def restart_bot(message):
    if (str(message.from_user.id) != admin_id):
        bot.send_message(message.from_user.id, 'Команда доступна только администратору', parse_mode='Markdown')
    else:
        bot.send_message(admin_id, '🛑 bye', parse_mode=ParseMode.HTML)
        os.execv(sys.executable, ['python'] + sys.argv)
        
@bot.message_handler(commands=['json'])
def send_json(message):
    if (str(message.from_user.id) != admin_id):
        bot.send_message(message.from_user.id, 'Команда доступна только администратору', parse_mode='Markdown')
    else:
        with open(for_json.path, 'rb') as json_file: 
            bot.send_document(admin_id, json_file)
        with open(for_json.path_schedule, 'rb') as json_file: 
            bot.send_document(admin_id, json_file)
        

@bot.message_handler(commands=['start'])
def start(message):
    if message.chat.type == "supergroup":
        print(message.text)
        print(message.chat.id)
        print(message.text.split(' '))
        if len(message.text.split(' ')) != 2:
            bot.send_message(message.chat.id, start_txt, parse_mode='Markdown')
            bot.send_message(message.chat.id, 'Похоже, что этот бот добавлен в группу. Чтобы он присылал расписание в чат, \
            запустите его заново, указав вместе с /start@vmk_schedule_bot номер\_своей\_группы.\
                \nПример:\n/start@vmk_schedule_bot 102', parse_mode='Markdown')
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
                if for_json.check_group_in_json(temp):
                    bot.send_message(message.chat.id, 'Отлично! Теперь я буду присылать вам расписание {} группы'.format(temp), parse_mode='Markdown')
                else:
                    bot.send_message(message.chat.id, 'Похоже, что расписания для этой группы ещё не существует. \
                        \nРазработчик уже пинается, но можете дополнительно написать ему: @Kr0sH\_512', parse_mode='Markdown')
                    send_message(admin_id, '🛑 В группе {} был запрос на {} группу.\
                        \nid: {}'.format(message.chat.title, temp, message.chat.id))
                    temp = 'other'
                for_json.save_user(infos)
            else:
                bot.send_message(message.chat.id, 'Введено не число. Попробуйте снова.\
                    \nПример:\n/start@vmk_schedule_bot 102', parse_mode='Markdown')

        return
    bot.send_message(message.chat.id, start_txt, parse_mode='Markdown')
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton(text="102", callback_data="102"))
    markup.add(types.InlineKeyboardButton(text="103", callback_data="103"))
    markup.add(types.InlineKeyboardButton(text="105", callback_data="105"))
    markup.add(types.InlineKeyboardButton(text="Моей группы нет в этом списке", callback_data="other"))
    bot.send_message(message.chat.id, 'Пожалуйста, выбери свою группу', parse_mode='Markdown', reply_markup=markup)

@bot.callback_query_handler(func=lambda call: True)
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
                              parse_mode='Markdown')
    else:
        bot.edit_message_text(chat_id=call.message.chat.id,
                              message_id=call.message.message_id, 
                              text='Отлично, теперь тебе будут приходить сообщения!', 
                              parse_mode='Markdown')
        
        

@bot.message_handler(commands=['help', 'faq'])
def help(message):
    help_msg = 'Мои команды:\
            \n/start - используй, чтобы сменить номер группы.\
            \n/info - используй, чтобы узнать твои настройки бота\
            \n/pause - используй, чтобы прекратить получать сообщения от бота\
            \n/timeout - настрой время, когда бот будет присылать тебе сообщение\
            \n/request - используй, чтобы отправить разработчику какой-то запрос\
            \n\nИли же можно всегда написать напрямую: @Kr0sH\_512'
    bot.send_message(message.chat.id, help_msg, parse_mode='Markdown')
    if str(message.from_user.id) == admin_id and message.from_user.id == message.chat.id:
        help_msg = '🛑 И команды только для админа:\
            \n/restart - перезапуск бота.\
            \n/update - обновление schedule задач\
            \n/json - получить файл пользователей и расписания\
            \n/info id\_пользователя - узнать настройки пользователя'
        bot.send_message(message.from_user.id, help_msg, parse_mode='Markdown')
    
@bot.message_handler(commands=['request'])
def request(message):
    bot.send_message(message.from_user.id, 'Отправь мне сообщение и я перешлю его разработчику\
        \n(или напиши stop, чтобы отменить отправку)', parse_mode='Markdown')
    bot.register_next_step_handler(message, send_request)
    
def send_request(message):
    if message.text == "stop" or message.text == "стоп" or message.text[0] == '/':
        bot.send_message(message.from_user.id, 'Отмена отпраки', parse_mode='Markdown')
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
        if '_' in str(infos[i]):
            infos[i] = str(infos[i]).replace('_', '\_')
    
    text = '🛑 Сообщение от {} {} (@{}):\n\n{}\nid: {}'.format(infos[1], infos[2], infos[3], infos[4], infos[0])
    bot.send_message(admin_id, text, parse_mode='Markdown')
    bot.send_message(message.from_user.id, 'Ваше сообщение успешно доставлено!', parse_mode='Markdown')


    
@bot.message_handler(commands=['schedule']) ### На доработке
def send_schedule(message):
    # команда для отправки всего расписания
    bot.send_message(message.chat.id, 'Пожалуйста, притворись, что ты получил сейчас своё расписание на неделю\
        \n\n(Функция в разработке)', parse_mode='Markdown')
    
@bot.message_handler(commands=['timeout'])
def set_timeout(message):
    bot.send_message(message.chat.id, 'Пришли мне число от 1 до 60. \
        \nЭто будет количество минут, за которое я буду присылать тебе напоминание о уроке (По умолчанию: 10)', parse_mode='Markdown')
    bot.register_next_step_handler(message, save_timeout)

def save_timeout(message):
    if message.text[0] == '/':
        return
    if str(message.text).isdigit() and int(message.text) <= 60 and int(message.text) >= 1:
        for_json.change_user_param(str(message.chat.id), 'timeout', str(message.text))
        bot.send_message(message.chat.id, 'Хорошо, теперь ты будешь получать напоминания за {} минут до урока'.format(str(message.text)), parse_mode='Markdown')
    else:
        bot.send_message(message.chat.id, 'Пожалуйста, пришли число от 1 до 60. \nПо умолчанию: 10', parse_mode='Markdown')
        bot.register_next_step_handler(message, save_timeout)
    
@bot.message_handler(commands=['info'])
def send_info(message):
    if len(message.text.split(' ')) == 2 and str(message.from_user.id) == admin_id:
        bot.send_message(message.chat.id, '🛑 Окей, держи', parse_mode='Markdown')
        text = for_json.return_infos(message.text.split(' ')[1])
        bot.send_message(message.chat.id, text, parse_mode=ParseMode.HTML)
        return
    bot.send_message(message.chat.id, 'Хорошо, вот твои настройки:', parse_mode='Markdown')
    text = for_json.return_infos(str(message.chat.id))
    bot.send_message(message.chat.id, text, parse_mode=ParseMode.HTML)
    
@bot.message_handler(commands=['pause'])
def pause_schedule(message):
    for_json.change_user_param(str(message.chat.id), 'allow_message', 'no')
    bot.send_message(message.chat.id, 'Рассылка сообщений преращена. \
        \nДля возобновления воспользуйтесь командой\n/start', parse_mode='Markdown')
    
@bot.message_handler(content_types=['text'])
def text_message(message):
    if message.chat.type == "supergroup":
        return
    bot.send_message(message.from_user.id, 'К сожалению, я ещё не умею обрабатывать сообщения.\
    \nИспользуй команды из меню или напиши /help.', parse_mode='Markdown')

def send_message(id, text):
    bot.send_message(id, text, parse_mode=ParseMode.HTML)

if __name__ == '__main__':
    for_json.create_schedule_tasks()
    send_message(admin_id, '🛑 я перезапустился!')
    print("-------------------------")
    
    threading.Thread(target=bot.infinity_polling, name='bot_infinity_polling', daemon=True).start()

    while True:
        schedule.run_pending()
        time.sleep(5)
