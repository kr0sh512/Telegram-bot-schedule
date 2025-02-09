#!/usr/bin/python3.3
import threading, telebot, schedule, time, random
from datetime import datetime
import os, sys
from telebot import types
from telegram.constants import ParseMode
import db
from admin import admin_command, is_admin, send_admin_message, send_admin_document
from dotenv import load_dotenv

load_dotenv()

bot = telebot.TeleBot(os.environ.get("TG_TEST_TOKEN"))

PARITY_FIRST = 0


@bot.message_handler(commands=["help", "faq"])
def help(message):
    help_msg = "Мои команды:\
            \n/start - используй, чтобы сменить номер группы.\
            \n/schedule - используй, чтобы получить расписание на сегодня.\
            \n/random - сделай очередь из людей\
            \n/info - используй, чтобы узнать твои настройки бота\
            \n/pause - используй, чтобы прекратить получать сообщения от бота\
            \n/thread - используй в нужном чате канала, чтобы бот отправлял сообщения именно туда\
            \n/timeout - настрой время, когда бот будет присылать тебе сообщение\
            \n/request - используй, чтобы отправить разработчику какой-то запрос\
            \n/source - Страница бота на Github\
            \n\nИли же можно всегда написать напрямую: @Kr0sH_512"

    send_message(message.chat.id, help_msg)

    if is_admin(message):
        admin_help_msg = "И команды только для админа:\
            \n/restart - перезапуск бота.\
            \n/update - обновление schedule задач\
            \n/stats - получание статистики\
            \n/info <i>id_пользователя</i> - узнать настройки пользователя\
            \n/spam - сделать рассылку\
            \n/pause_all - приостановить бота для всех (каникулы/выходные)\
            \n/stop <i>id_пользователя</i> - приостановить отправку сообщений для пользователя"
        send_admin_message(admin_help_msg)

    return


### --//--


@bot.message_handler(commands=["restart", "r"])
@admin_command
def restart_bot(message):
    send_admin_message("bye")
    os.execv(sys.executable, ["python3", "-u"] + sys.argv)


@bot.message_handler(commands=["update"])
@admin_command
def update_schedules(message):
    db.create_schedule_tasks(manual=True)
    send_admin_message("Произошёл update")

    return


@bot.message_handler(commands=["stats"])
@admin_command
def send_stat(message):
    text = "<u>Статистика:</u>\
        \n(группа: всего/откл. увед./беседы)"

    sum_users = 0
    sum_dis_not = 0
    sum_chats = 0

    groups = list(db.groups_in_json())
    groups.append("other")

    for i in groups:
        users = db.students_in_group(i)
        sum_users += len(users)

        dis_not = len(
            [
                i
                for i, x in enumerate(users)
                if db.return_infos(x)["allow_message"] == "no"
            ]
        )
        sum_dis_not += dis_not

        chats = len([i for i, x in enumerate(users) if x[0] == "-"])
        sum_chats += chats

        text += "\n{}: {} / {} / {}".format(i, len(users), dis_not, chats)

    text += "\n\nВсего: {} / {} / {}".format(sum_users, sum_dis_not, sum_chats)

    send_admin_message(text)

    return


# info user_id


@bot.message_handler(commands=["spam"])
@admin_command
def spam(message):
    send_admin_message(
        "Пришли мне id, номер группы или <i>all</i> для рассылки сообщения этим пользователям"
    )

    bot.register_next_step_handler(message, spam_msg)

    return


def spam_msg(message):
    if message.text == "stop" or message.text == "стоп" or message.text[0] == "/":
        send_admin_message("Отмена отправки")
        return

    send_admin_message("Пришли мне текст для рассылки сообщения этим пользователям")

    bot.register_next_step_handler(message, spam_cnf, message.text)

    return


def spam_cnf(message, data):
    if message.text == "stop" or message.text == "стоп" or message.text[0] == "/":
        send_admin_message("Отмена отправки")
        return

    global text_spam
    text_spam = message.text

    text = "Пожалуйста, проверь итоговое сообщение и подтверди отправку:\
        \n\nКому: "

    if data == "all":
        text += "<u>всем</u>"
    elif data in db.groups_in_json():
        text += "{} группе".format(data)
    elif db.return_infos(data) != None:
        text += "пользователю @{}".format(db.return_infos(data)["username"])
    else:
        send_admin_message("Ошибка при выборе пользователей")
        return

    text += "\n\nСообщение: {}".format(message.text)

    markup = types.InlineKeyboardMarkup()

    markup.add(
        types.InlineKeyboardButton(text="✅", callback_data="spam#{}".format(data)),
        types.InlineKeyboardButton(text="❌", callback_data="spam_no"),
    )

    bot.send_message(
        message.from_user.id, text, parse_mode=ParseMode.HTML, reply_markup=markup
    )

    return


@bot.callback_query_handler(func=lambda call: "spam" in call.data)
def spam_send(call):
    if call.data == "spam_no":
        send_admin_message("Отмена отправки")
        return

    tmp, data = call.data.split("#")

    global text_spam
    text = text_spam

    users = []

    if data == "all":
        groups = db.groups_in_json()
        for group in groups:
            users += db.students_in_group(group)
        users += db.students_in_group("other")
    elif data in db.groups_in_json():
        users = db.students_in_group(data)
    elif db.return_infos(data) != None:
        users = [data]

    for i in users:
        send_message(i, text)

    bot.edit_message_text(
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        text="Успешно!",
        parse_mode=ParseMode.HTML,
    )

    return


@bot.message_handler(commands=["pause_all"])
@admin_command
def pause_bot(message):
    db.pause_bot()

    return


@bot.message_handler(commands=["stop"])
@admin_command
def stop_msg(message):
    if len(str(message.text).split(" ")) != 2:
        send_admin_message("Эта команда вида /stop <i>id_пользователя</i>")
        return

    db.change_user_param(str(message.text).split(" ")[1], "allow_message", "no")
    send_admin_message("Успешно")

    return


### --//--


@bot.message_handler(commands=["start"])
def start(message):
    start_txt = "Привет! Это бот, который будет кидать тебе сообщения перед нужной парой с номером кабинета/фамилией препода\
    \n\nТы можешь настроить отправку сообщений в лс или добавить меня в группу, куда я буду присылать расписание\
\n\nCreated by: @Kr0sH_512"
    if message.chat.type == "supergroup":
        if len(message.text.split(" ")) != 2:
            send_message(message.chat.id, start_txt)
            send_message(
                message.chat.id,
                "Похоже, что этот бот добавлен в группу. Чтобы он присылал расписание в чат, \
            укажите вместе с /start@vmk_schedule_bot номер своей группы.\
                \nПример:\n/start@vmk_schedule_bot 102",
            )
        else:
            temp = message.text.split(" ")[1]

            if temp.isdigit():
                infos = [
                    message.chat.id,
                    message.chat.title,
                    "",
                    message.from_user.username,
                    temp,
                ]

                if temp in db.groups_in_json():
                    send_message(
                        message.chat.id,
                        "Отлично! Теперь я буду присылать вам расписание {} группы".format(
                            temp
                        ),
                    )
                else:
                    send_message(
                        message.chat.id,
                        "Похоже, что расписания для этой группы ещё не существует. \
                        \nРазработчик уже пинается, но можете дополнительно написать ему: @Kr0sH_512",
                    )

                    send_admin_message(
                        "В группе {} был запрос на {} группу.\
                        \nid: {}".format(
                            message.chat.title, temp, message.chat.id
                        )
                    )
                    temp = "other"
                db.save_user(infos)
            else:
                send_message(
                    message.chat.id,
                    "Введено не число. Попробуйте снова.\
                    \nПример:\n/start@vmk_schedule_bot 102",
                )

        return

    send_message(message.chat.id, start_txt)

    markup = types.InlineKeyboardMarkup()
    # for i in db.groups_in_json():
    #     markup.add(types.InlineKeyboardButton(text=i, callback_data=i))
    markup.add(types.InlineKeyboardButton(text="1 курс", callback_data="1course"))
    markup.add(types.InlineKeyboardButton(text="2 курс", callback_data="2course"))

    bot.send_message(
        message.chat.id,
        "Пожалуйста, выбери свой курс",
        parse_mode=ParseMode.HTML,
        reply_markup=markup,
    )

    return


@bot.callback_query_handler(
    func=lambda call: call.data in db.groups_in_json()
    or call.data in ["other", "1course", "2course"]
)
def callback_inline(call):
    if "course" in call.data:
        course = call.data[0]

        markup = types.InlineKeyboardMarkup()
        for i in [i for i in db.groups_in_json() if i[0] == course]:
            markup.add(types.InlineKeyboardButton(text=i, callback_data=i))

        markup.add(
            types.InlineKeyboardButton(
                text="Моей группы нет в этом списке", callback_data="other"
            )
        )

        bot.edit_message_text(
            text="Пожалуйста, выбери свою группу",
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            reply_markup=markup,
        )

        # bot.edit_message_reply_markup(
        #     call.message.chat.id, call.message.message_id, reply_markup=markup
        # )

        return

    infos = [
        call.from_user.id,
        call.from_user.first_name,
        call.from_user.last_name,
        call.from_user.username,
        call.data,
    ]

    db.save_user(infos)

    if call.data == "other":
        bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            text="Используй команду /request и напиши номер группы, которую хочешь добавить\
                                  \nПосле создания расписания для твоей группы, я пришлю тебе сообщение",
            parse_mode=ParseMode.HTML,
        )
    else:
        bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            text="Отлично, теперь тебе будут приходить сообщения!",
            parse_mode=ParseMode.HTML,
        )

    return


@bot.message_handler(commands=["schedule"])
def send_schedule(message):
    text = (
        "К сожалению, бот не может отправить тебе расписание твоей группы на сегодня :("
    )
    try:
        day = datetime.today().strftime("%A").lower()[:3]  # mon tue ...
        text = db.get_schedule(message.chat.id, day)
    except Exception as e:
        # send_admin_message(
        #     "Schedule error from: {} \n\n {}".format(message.chat.id, str(e))
        # )
        bot.send_message(
            message.chat.id,
            "Пожалуйста, проверь, что ты зарегестрировался с помощью команды /start",
            ParseMode.HTML,
            message_thread_id=message.message_thread_id,
        )

    markup = types.InlineKeyboardMarkup()
    markup.add(
        types.InlineKeyboardButton(text="◀️", callback_data="left"),
        types.InlineKeyboardButton(text="▶️", callback_data="right"),
    )
    bot.send_message(
        message.chat.id,
        text,
        ParseMode.HTML,
        reply_markup=markup,
        message_thread_id=message.message_thread_id,
    )

    return


@bot.callback_query_handler(func=lambda call: call.data in ["left", "right"])
def change_schedule(call):
    days = ["mon", "tue", "wed", "thu", "fri", "sat"]
    russian_days = ["понедельник", "вторник", "среду", "четверг", "пятницу", "субботу"]
    i = 6  # выходной
    for day in russian_days:
        if day in call.message.text:
            i = russian_days.index(day)
            break

    delta = (1) if (call.data == "right") else (-1)
    ind = ((i + delta) % 6) if (i + delta > 0) else (i + delta)

    text = db.get_schedule(call.message.chat.id, days[ind])

    markup = types.InlineKeyboardMarkup()
    markup.add(
        types.InlineKeyboardButton(text="◀️", callback_data="left"),
        types.InlineKeyboardButton(text="▶️", callback_data="right"),
    )

    bot.edit_message_text(
        text,
        call.message.chat.id,
        call.message.message_id,
        parse_mode=ParseMode.HTML,
        reply_markup=markup,
    )

    return


@bot.message_handler(commands=["info"])
def send_info(message):
    if len(message.text.split(" ")) == 2 and is_admin(message):
        send_admin_message(
            "Окей, держи настройки <code>{}</code>".format(message.text.split(" ")[1])
        )
        infos = db.return_infos(message.text.split(" ")[1])
        text = "<i>Никнейм</i>: <b>@{}</b>\
        \n<i>Имя</i>: <b>{} {}</b>\
        \n<i>Выбранная группа</i>: <b>{}</b>\
        \n<i>Время напоминания до урока</i>: <b>{}</b>\
        \n<i>Разрешены ли напоминания</i>: <b>{}</b>".format(
            infos["username"],
            infos["first_name"],
            infos["last_name"],
            (infos["group"] if infos["group"] != "other" else "не выбрана"),
            infos["timeout"],
            ("да" if infos["allow_message"] == "yes" else "нет"),
        )
        send_admin_message(text)
        return

    send_message(message.chat.id, "Хорошо, вот твои настройки:")
    infos = db.return_infos(message.chat.id)
    text = "<i>Выбранная группа</i>: <b>{}</b>\
        \n<i>Время напоминания до урока</i>: <b>{}</b>\
        \n<i>Разрешены ли напоминания</i>: <b>{}</b>".format(
        (infos["group"] if infos["group"] != "other" else "не выбрана"),
        infos["timeout"],
        ("да" if infos["allow_message"] == "yes" else "нет"),
    )
    send_message(message.chat.id, text)

    return


@bot.message_handler(commands=["pause"])
def pause_schedule(message):
    infos = db.return_infos(message.chat.id)["allow_message"]

    if infos == "yes":
        db.change_user_param(str(message.chat.id), "allow_message", "no")
        send_message(
            message.chat.id,
            "Рассылка сообщений прекращена. \
            \nДля возобновления воспользуйтесь командой\n/pause",
        )
    else:
        db.change_user_param(str(message.chat.id), "allow_message", "yes")
        send_message(message.chat.id, "Рассылка сообщений возоблена!")

    return


@bot.message_handler(commands=["thread"])
def change_thread(message):
    thread_id = ""

    try:
        thread_id = message.reply_to_message.message_thread_id
    except AttributeError:
        thread_id = "General"

    db.change_user_param(str(message.chat.id), "thread", thread_id)

    send_message(
        message.chat.id,
        "Хорошо, теперь я буду отправлять сообщения в этот чат",
        thread_id,
    )

    return


@bot.message_handler(commands=["timeout"])
def set_timeout(message):
    send_message(
        message.chat.id,
        "Пришли мне число от 1 до 59. \
        \nЭто будет количество минут, за которое я буду присылать тебе напоминание о паре (По умолчанию: 10)",
    )
    bot.register_next_step_handler(message, save_timeout)

    return


def save_timeout(message):
    if (
        str(message.text).isdigit()
        and int(message.text) <= 59
        and int(message.text) >= 1
    ):
        db.change_user_param(message.chat.id, "timeout", str(message.text))
        send_message(
            message.chat.id,
            "Хорошо, теперь ты будешь получать напоминания за {} минут до урока".format(
                str(message.text)
            ),
        )
    else:
        send_message(
            message.chat.id,
            "Пожалуйста, пришли <u>число</u> от 1 до 59. \
                        \nПо умолчанию: 10",
        )
        send_message(message.chat.id, "Изменения не были внесены")

    return


@bot.message_handler(commands=["request"])
def request(message):
    send_message(
        message.from_user.id,
        "Отправь мне сообщение и я перешлю его разработчику\
        \n(или напиши stop, чтобы отменить отправку)",
    )
    bot.register_next_step_handler(message, send_request)

    return


def send_request(message):
    if message.text == "stop" or message.text == "стоп" or message.text[0] == "/":
        send_message(message.from_user.id, "Отмена отправки")
        return

    infos = [
        message.from_user.id,
        message.from_user.first_name,
        message.from_user.last_name,
        message.from_user.username,
        message.text,
    ]

    for i in range(len(infos)):
        if type(infos[i]) == type(None):
            infos[i] = ""

    admin_text = "Сообщение от {} {} (@{}):\n\n{}\nid: <code>{}</code>".format(
        infos[1], infos[2], infos[3], infos[4], infos[0]
    )
    send_admin_message(admin_text)

    send_message(message.from_user.id, "Ваше сообщение успешно доставлено!")

    return


@bot.message_handler(commands=["source"])
def send_source(message):
    bot.send_message(
        message.chat.id,
        "https://github.com/kr0sh512/Telegram-bot-schedule",
        parse_mode=ParseMode.HTML,
    )

    return


@bot.message_handler(content_types=["text"])
def text_message(message):
    if message.chat.type == "supergroup" or is_admin(message):
        return
    send_message(
        message.from_user.id,
        "К сожалению, я ещё не умею обрабатывать сообщения.\
    \nИспользуй команды из меню или напиши /help.",
    )

    return


def send_message(id, text, thread_id="General", parity=None):
    if thread_id == "General":
        thread_id = None

    if parity != None:
        parity = int(parity)
        count_of_weeks = (datetime.now() - datetime(2024, 2, 5)).days // 7
        is_odd = (count_of_weeks + 1) % 2 == PARITY_FIRST

        if is_odd != bool(parity):
            return

    try:
        bot.send_message(
            chat_id=id,
            text=text,
            parse_mode=ParseMode.HTML,
            message_thread_id=thread_id,
            disable_web_page_preview=True,
        )
    except Exception as e:
        time.sleep(5)
        try:
            bot.send_message(
                chat_id=id,
                text=text,
                parse_mode=ParseMode.HTML,
                message_thread_id=thread_id,
                disable_web_page_preview=True,
            )
        except Exception as e:
            text_error = "Error from user: @{} <code>{}</code>\n{}".format(
                db.return_infos(id)["username"], id, str(e)
            )
            # send_admin_message(text_error)
            print(f"--- {text_error} ---")

    return


def send_document(id, file, text=""):
    try:
        bot.send_document(id, file, caption=text)
    except Exception as e:
        time.sleep(5)
        try:
            bot.send_document(id, file, caption=text)
        except Exception as e:
            text_error = "Error from user: <code>{}</code>\n{}".format(id, str(e))
            send_admin_message(text_error)
            print(id, e)

    return


if __name__ == "__main__":
    db.create_schedule_tasks(True)

    send_admin_message("Я перезапустился!")
    print("-------------------------")

    threading.Thread(
        target=bot.infinity_polling, name="bot_infinity_polling", daemon=True
    ).start()

    while True:
        try:
            schedule.run_pending()
            time.sleep(5)
        except Exception as e:
            print(e)
            time.sleep(10)
