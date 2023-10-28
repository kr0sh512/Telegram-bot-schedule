#!/usr/bin/python3.3
import json, schedule
import schedules as bot
from datetime import datetime

path_users = "json/users.json" # Нужный путь до json файлов
path_schedule = "json/schedule.json"

def save_user(infos):
    for i in range(len(infos)):
        if type(infos[i]) == type(None):
            infos[i] = ''
        infos[i] = str(infos[i])
    infos = {
        "id" :  infos[0], 
        "first_name" :  infos[1], 
        "last_name" : infos[2], 
        "username" : infos[3],
        "group" : infos[4]
    }
    
    data = {}
    with open(path_users, 'r', encoding='utf-8') as json_file: 
        data = json.load(json_file)
        
    data[infos["id"]] = {
        "username": infos["username"],
        "first_name": infos["first_name"],
        "last_name": infos["last_name"],
        "group": infos["group"],
        "timeout": "10",
        "allow_message": "yes",
        "thread": "General"
    }

    with open(path_users, 'w', encoding='utf-8') as json_file:
        json.dump(data, json_file, ensure_ascii=False, indent=4)
    create_schedule_tasks()
    return

def change_user_param(id, key, value):
    data = {}
    with open(path_users, 'r', encoding='utf-8') as json_file: 
        data = json.load(json_file)
        
    data[id][key] = value

    with open(path_users, 'w', encoding='utf-8') as json_file:
        json.dump(data, json_file, ensure_ascii=False, indent=4)
    create_schedule_tasks()
    return

def create_schedule_tasks():
    schedule.clear()
    users = {}
    schdl = {}
    with open(path_users, 'r', encoding='utf-8') as json_file: 
        users = json.load(json_file)
    with open(path_schedule, 'r', encoding='utf-8') as json_file: 
        schdl = json.load(json_file)    
    for id, params in users.items():
        if params['allow_message'] != 'yes':
            continue
        group = params['group']
        if group == 'other':
            continue
        timeout = params['timeout']
        for day in schdl[group]:
            for i, lesson in schdl[group][day].items():
                if lesson["name"] == "": # Неправильный формат schedule
                    continue
                
                start, end = i.split("-")
                text = ''
                if len(lesson["infos"].split('|')) == 2:
                    teacher = lesson["infos"].split('|')[0]
                    room = lesson["infos"].split('|')[1]
                    text = '{}-{} | {}\
                            \n<b>{}</b>\
                            \n<i>{}</i>'.format(start, end, room, lesson["name"], teacher)
                elif len(lesson["infos"].split('|')) == 4:
                    infos = lesson["infos"].split('|')
                    text = '{}-{}\
                            \n<b>{}</b>\
                            \n({}) <i>{}</i>\
                            \n({}) <i>{}</i>'.format(start, end, lesson["name"], 
                                                   infos[1], 
                                                   infos[0], 
                                                   infos[3], 
                                                   infos[2])
                elif len(lesson["infos"].split('|')) == 1:
                    text = '{}-{}\
                            \n<b>{}</b>'.format(start, end, lesson["name"])
                else:                  #неправильный формат infos в json файле
                    print("что-то не так")
                    print(lesson["name"])
                    continue
                
                thread_id = params["thread"]
                delta = '00:' + params["timeout"]
                format = '%H:%M'
                start_task = datetime.strptime(start, format) - datetime.strptime(delta, format)
                tmp = ''
                for i in str(start_task).split(':'):
                    tmp += (('0' + i ) if len(i) < 2 else i) + ":"
                start_task = tmp[:-1]
                if day == 'mon':
                    schedule.every().monday.at(start_task).do(bot.send_message, id, text, thread_id)
                elif day == 'tue':
                    schedule.every().tuesday.at(start_task).do(bot.send_message, id, text, thread_id)
                elif day == 'wed':
                    schedule.every().wednesday.at(start_task).do(bot.send_message, id, text, thread_id)
                elif day == 'thu':
                    schedule.every().thursday.at(start_task).do(bot.send_message, id, text, thread_id)
                elif day == 'fri':
                    schedule.every().friday.at(start_task).do(bot.send_message, id, text, thread_id)
                elif day == 'sat':
                    schedule.every().saturday.at(start_task).do(bot.send_message, id, text, thread_id)
    
    bot.send_message(bot.admin_id, '🛑 Произошёл update')
    return


def check_group_in_json(number):
    schdl = {}
    with open(path_schedule, 'r', encoding='utf-8') as json_file: 
        schdl = json.load(json_file)    
        
    return str(number) in schdl.keys()

def return_infos(id):
    data = {}
    with open(path_users, 'r', encoding='utf-8') as json_file: 
        data = json.load(json_file)
    data = data[id]
    text = '<i>Выбранная группа</i>: <b>{}</b>\
        \n<i>Время напоминания до урока</i>: <b>{}</b>\
        \n<i>Разрешены ли напоминания</i>: <b>{}</b>'.format((data['group'] if data['group'] != 'other' else 'не выбрана'), 
                                                             data['timeout'], 
                                                             ('да' if data['allow_message'] == 'yes' else 'нет'))
        
    return text

def get_schedule(id):
    text = '<u>Расписание на сегодня</u>:\n\n'

    schdl_today = {}
    with open(path_schedule, 'r', encoding='utf-8') as schedule_file: 
        day = datetime.today().strftime('%A').lower()[:3]
        
        group = ''
        with open(path_users, 'r', encoding='utf-8') as user_file: 
            group = json.load(user_file)[id]['group']
        
        if (group == 'other'):
            return 'У тебя не выбрана группа для рассылки сообщений'
        
        try:
            schdl_today = json.load(schedule_file)[group][day]
        except:
            return 'Расписания твоей группы на сегодня нет'
        
    for i, lesson in schdl_today.items():
        if len(lesson["infos"].split('|')) == 2:
            teacher = lesson["infos"].split('|')[0]
            room = lesson["infos"].split('|')[1]
            text += '•{} | {}\
                    \n<b>{}</b>\
                    \n<i>{}</i>'.format(i, room, lesson["name"], teacher)
                    
        elif len(lesson["infos"].split('|')) == 4:
            infos = lesson["infos"].split('|')
            text += '•{}\
                    \n<b>{}</b>\
                    \n({}) <i>{}</i>\
                    \n({}) <i>{}</i>'.format(i, lesson["name"], 
                                            infos[1], 
                                            infos[0], 
                                            infos[3], 
                                            infos[2])
        else:
            text += '•{}\
                    \n<b>{}</b>'.format(i, lesson["name"])
        
        text += '\n\n'
        
    return text
