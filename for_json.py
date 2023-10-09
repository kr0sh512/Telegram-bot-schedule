#!/usr/bin/python3.3
import json, schedule
import schedules as bot
from datetime import datetime

path = "users.json" # Нужный путь до json файлов
path_schedule = "schedule.json"

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
    with open(path, 'r', encoding='utf-8') as json_file: 
        data = json.load(json_file)
        
    data[infos["id"]] = {
        "username": infos["username"],
        "first_name": infos["first_name"],
        "last_name": infos["last_name"],
        "group": infos["group"],
        "timeout": "10",
        "allow_message": "yes"
    }

    with open(path, 'w', encoding='utf-8') as json_file:
        json.dump(data, json_file, ensure_ascii=False, indent=4)
    create_schedule_tasks()

def change_user_param(id, key, value):
    data = {}
    with open(path, 'r', encoding='utf-8') as json_file: 
        data = json.load(json_file)
        
    data[id][key] = value

    with open(path, 'w', encoding='utf-8') as json_file:
        json.dump(data, json_file, ensure_ascii=False, indent=4)
    create_schedule_tasks()

def create_schedule_tasks():
    schedule.clear()
    users = {}
    schdl = {}
    with open(path, 'r', encoding='utf-8') as json_file: 
        users = json.load(json_file)
    with open(path_schedule, 'r', encoding='utf-8') as json_file: 
        schdl = json.load(json_file)    
    for id, params in users.items():
        # print(id, '=>', params)
        if params['allow_message'] != 'yes':
            continue
        group = params['group']
        if group == 'other':
            continue
        timeout = params['timeout']
        for day in schdl[group]:
            for i, lesson in schdl[group][day].items():
                if lesson["name"] == "": #проверка на лоха
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
                    infos = lesson["infos"].split('|');
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
                
                delta = '00:' + params["timeout"]
                format = '%H:%M'
                start_task = datetime.strptime(start, format) - datetime.strptime(delta, format)
                tmp = ''
                for i in str(start_task).split(':'):
                    tmp += (('0' + i ) if len(i) < 2 else i) + ":"
                start_task = tmp[:-1]
                if day == 'mon':
                    schedule.every().monday.at(start_task).do(bot.send_message, id, text)
                elif day == 'tue':
                    schedule.every().tuesday.at(start_task).do(bot.send_message, id, text)
                elif day == 'wed':
                    schedule.every().wednesday.at(start_task).do(bot.send_message, id, text)
                elif day == 'thu':
                    schedule.every().thursday.at(start_task).do(bot.send_message, id, text)
                elif day == 'fri':
                    schedule.every().friday.at(start_task).do(bot.send_message, id, text)
                elif day == 'sat':
                    schedule.every().saturday.at(start_task).do(bot.send_message, id, text)
    
    bot.send_message(bot.krosh, '🛑 Произошёл update')


def check_group_in_json(number):
    schdl = {}
    with open(path_schedule, 'r', encoding='utf-8') as json_file: 
        schdl = json.load(json_file)    
    return str(number) in schdl.keys()

def return_infos(id):
    data = {}
    with open(path, 'r', encoding='utf-8') as json_file: 
        data = json.load(json_file)
    data = data[id]
    text = '<i>Выбранная группа</i>: <b>{}</b>\
        \n<i>Время напоминания до урока</i>: <b>{}</b>\
        \n<i>Разрешены ли напоминания</i>: <b>{}</b>'.format(data['group'], data['timeout'], ('да' if data['allow_message'] == 'yes' else 'нет'))
    return text