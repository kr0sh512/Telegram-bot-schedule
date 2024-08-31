#!/usr/bin/python3.3
import json, schedule
import schedules as bot
from datetime import datetime

path_users = "json/users.json"  # Нужный путь до json файлов
path_schedule = "json/schedule_3sem.json"
path_students = "json/students.json"

allow_update = True


def save_user(infos):
    for i in range(len(infos)):
        if type(infos[i]) == type(None):
            infos[i] = ""
        infos[i] = str(infos[i])

    infos = {
        "id": infos[0],
        "first_name": infos[1],
        "last_name": infos[2],
        "username": infos[3],
        "group": infos[4],
    }

    data = {}
    with open(path_users, "r", encoding="utf-8") as json_file:
        data = json.load(json_file)

    data[infos["id"]] = {
        "username": infos["username"],
        "first_name": infos["first_name"],
        "last_name": infos["last_name"],
        "group": infos["group"],
        "timeout": "10",
        "allow_message": "yes",
        "thread": "General",
    }

    with open(path_users, "w", encoding="utf-8") as json_file:
        json.dump(data, json_file, ensure_ascii=False, indent=4)

    create_schedule_tasks()

    return


def change_user_param(id, key, value):
    id = str(id)
    data = {}
    with open(path_users, "r", encoding="utf-8") as json_file:
        data = json.load(json_file)

    data[id][key] = value

    with open(path_users, "w", encoding="utf-8") as json_file:
        json.dump(data, json_file, ensure_ascii=False, indent=4)
    create_schedule_tasks()
    bot.send_admin_message(
        "Изменения:\
                          \n<i>user:</i> @{}\
                          \n<i>id:</i> <code>{}</code>\
                          \n<i>key:</i> <code>{}</code>\
                          \n<i>value:</i> <code>{}</code>".format(
            data[id]["username"], id, key, value
        )
    )
    return


def parse_lesson(time, lesson):
    text = ""
    start, end = time.split("-")

    if len(lesson["infos"].split("|")) == 2:
        teacher = lesson["infos"].split("|")[0]
        room = lesson["infos"].split("|")[1]
        text = "{}-{} | {}\
                \n<b>{}</b>\
                \n<i>{}</i>".format(
            start, end, room, lesson["name"], teacher
        )
    elif len(lesson["infos"].split("|")) == 4:
        infos = lesson["infos"].split("|")
        text = "{}-{}\
                \n<b>{}</b>\
                \n({}) <i>{}</i>\
                \n({}) <i>{}</i>".format(
            start, end, lesson["name"], infos[1], infos[0], infos[3], infos[2]
        )
    elif len(lesson["infos"].split("|")) == 1:
        text = "{}-{}\
                \n<b>{}</b>".format(
            start, end, lesson["name"]
        )
    else:
        print("что-то не так")
        print(lesson["name"])

    return text


def create_schedule_tasks(manual=False):
    global allow_update

    if not manual:
        if not allow_update:
            return

        bot.send_admin_message("Произошёл auto-update")

    allow_update = True

    schedule.clear()
    users = {}
    schdl = {}
    with open(path_users, "r", encoding="utf-8") as json_file:
        users = json.load(json_file)
    with open(path_schedule, "r", encoding="utf-8") as json_file:
        schdl = json.load(json_file)
    for id, params in users.items():
        if params["allow_message"] != "yes":
            continue
        group = params["group"]
        if group == "other":
            continue
        timeout = params["timeout"]
        for day in schdl[group]:
            for i, lesson in schdl[group][day].items():
                if lesson["name"] == "":  # Неправильный формат schedule
                    continue

                start = i.split("-")[0]
                text = parse_lesson(i, lesson)

                if text == "":
                    continue

                thread_id = params["thread"]

                delta = "00:" + params["timeout"]
                format = "%H:%M"
                start_task = datetime.strptime(start, format) - datetime.strptime(
                    delta, format
                )
                tmp = ""
                for i in str(start_task).split(":"):
                    tmp += (("0" + i) if len(i) < 2 else i) + ":"
                start_task = tmp[:-1]

                if day == "mon":
                    schedule.every().monday.at(start_task).do(
                        bot.send_message, id, text, thread_id, True
                    )
                elif day == "tue":
                    schedule.every().tuesday.at(start_task).do(
                        bot.send_message, id, text, thread_id, True
                    )
                elif day == "wed":
                    schedule.every().wednesday.at(start_task).do(
                        bot.send_message, id, text, thread_id, True
                    )
                elif day == "thu":
                    schedule.every().thursday.at(start_task).do(
                        bot.send_message, id, text, thread_id, True
                    )
                elif day == "fri":
                    schedule.every().friday.at(start_task).do(
                        bot.send_message, id, text, thread_id, True
                    )
                elif day == "sat":
                    schedule.every().saturday.at(start_task).do(
                        bot.send_message, id, text, thread_id, True
                    )

    return


def groups_in_json():
    schdl = {}
    with open(path_schedule, "r", encoding="utf-8") as json_file:
        schdl = json.load(json_file)

    return schdl.keys()


def students_in_group(group):
    group = str(group)

    data = {}
    with open(path_users, "r", encoding="utf-8") as json_file:
        data = json.load(json_file)

    students = []

    for i in data.keys():
        if data[i]["group"] == group:
            students.append(i)

    return students


def students_in_json(id="", key=""):
    id = str(id)

    group = {}
    with open(path_users, "r", encoding="utf-8") as json_file:
        group = json.load(json_file)
    group = group[id]["group"]

    stud = {}
    with open(path_students, "r", encoding="utf-8") as json_file:
        stud = json.load(json_file)
    stud = stud.get(group)

    if stud == None:
        return None

    if key == "":
        return list(stud.keys())

    return stud[key]


def return_infos(id):
    id = str(id)
    data = {}
    with open(path_users, "r", encoding="utf-8") as json_file:
        data = json.load(json_file)
    data = data.get(id)

    return data


def pause_bot():
    global allow_update

    if allow_update:
        schedule.clear()
        allow_update = False
        bot.send_admin_message("Бот больше не отправляет расписание")
    else:
        create_schedule_tasks(True)
        allow_update = True
        bot.send_admin_message("Бот возобновил рассылку!")

    return


def get_schedule(id, day):
    id = str(id)
    if day == "sun":
        day = "mon"
    days = ["mon", "tue", "wed", "thu", "fri", "sat"]
    russian_days = ["понедельник", "вторник", "среду", "четверг", "пятницу", "субботу"]

    text = "<u>Расписание на {}</u>:\n\n".format(russian_days[days.index(day)])

    schdl_today = {}
    with open(path_schedule, "r", encoding="utf-8") as schedule_file:
        group = ""
        with open(path_users, "r", encoding="utf-8") as user_file:
            group = json.load(user_file)[id]["group"]

        if group == "other":
            return "У тебя не выбрана группа для рассылки сообщений"

        try:
            schdl_today = json.load(schedule_file)[group][day]
        except:
            return "Расписания твоей группы на {} нет".format(
                russian_days[days.index(day)]
            )

    for i, lesson in schdl_today.items():
        text += "•" + parse_lesson(i, lesson) + "\n\n"

    return text
