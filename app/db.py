#!/usr/bin/python3.3
import schedule
import schedules as bot
from datetime import datetime
import os
from dotenv import load_dotenv
from sshtunnel import SSHTunnelForwarder
from psycopg2 import pool
from typing import Optional, Dict


allow_update = True
PARITY_FIRST = 0

load_dotenv()


if os.environ.get("ENV") == "dev":
    print("DEV: Connecting to local database")
    server = SSHTunnelForwarder(
        (os.environ.get("SSH_HOST"), 22),
        ssh_private_key=os.environ.get("SSH_KEY"),
        ssh_username=os.environ.get("SSH_USER"),
        ssh_password=(
            os.environ.get("SSH_PASSWORD") if os.environ.get("SSH_PASSWORD") else None
        ),
        remote_bind_address=("localhost", int(os.environ.get("DB_PORT"))),
    )
    server.start()

db = pool.SimpleConnectionPool(
    1,
    20,
    user=os.environ.get("DB_USER"),
    password=os.environ.get("DB_PASSWORD"),
    host="localhost" if os.environ.get("ENV") == "dev" else os.environ.get("DB_HOST"),
    port=(
        server.local_bind_port
        if os.environ.get("ENV") == "dev"
        else os.environ.get("DB_PORT")
    ),
    database=os.environ.get("DB_NAME"),
)


def into_dict(data: tuple, column_name: list[tuple]) -> dict:
    cols = [desc[0] for desc in column_name]

    return dict(zip(cols, data)) if data else None


def into_list(rows: list[tuple], column_name: list[tuple]) -> list[dict]:
    cols = [desc[0] for desc in column_name]

    return [dict(zip(cols, row)) for row in rows] if rows else []


def save_user(infos):
    conn = db.getconn()
    cursor = conn.cursor()
    cursor.execute(
        'INSERT INTO users (id, first_name, last_name, username, "group") VALUES (%s, %s, %s, %s, %s) ON CONFLICT (id) DO UPDATE SET first_name = EXCLUDED.first_name, last_name = EXCLUDED.last_name, username = EXCLUDED.username, "group" = EXCLUDED."group"',
        infos,
    )

    conn.commit()
    db.putconn(conn)

    return


def change_user_param(id, key, value):
    conn = db.getconn()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE users SET {} = %s WHERE id = %s".format(key),
        (value, id),
    )
    conn.commit()
    db.putconn(conn)

    create_schedule_tasks()

    return


def parse_lesson(lesson: dict[str, str]) -> str:
    text = ""
    start, end = lesson["begin_time"], lesson["end_time"]

    if not lesson["course"]:
        return ""

    if lesson["parity"] == 0:
        lesson["course"] += " (чёт.)"

    if lesson["parity"] == 1:
        lesson["course"] += " (нечёт.)"

    if lesson["lector"]:
        if "/" not in lesson["lector"]:
            text = "{}-{} | {}\
                    \n{}<b>{}</b>\
                    \n<i>{}</i>".format(
                start,
                end,
                lesson["room"],
                "🎓 " if lesson["is_lecture"] else "",
                lesson["course"],
                lesson["lector"],
            )
        else:
            lectors = lesson["lector"].split("/")
            text = "{}-{} | {}\
                    \n<b>{}</b>\
                    \n<i>{}</i>\
                    \n<i>{}</i>".format(
                start,
                end,
                lesson["room"].replace("/", ", "),
                lesson["course"],
                lectors[0],
                lectors[1],
            )
    else:
        text = "{}-{}\
                \n{}<b>{}</b>".format(
            start,
            end,
            "🎓 " if lesson["is_lecture"] else "",
            lesson["course"],
        )

        # text += f"\n{lesson['info']}"

    return text


def create_schedule_tasks(manual=False):
    global allow_update

    if not manual:
        if not allow_update:
            return

    allow_update = True

    schedule.clear()

    def run_script():
        os.system("python3 -u upload_sql.py")

    schedule.every(6).minutes.do(run_script)

    conn = db.getconn()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users")
    data = cursor.fetchall()
    users = into_list(data, cursor.description)

    for user in users:
        if not user["allow_message"]:
            continue
        group = user["group"]
        if group == "other":
            continue

        cursor.execute('SELECT * FROM schedule WHERE "group" = %s', (group,))
        data = cursor.fetchall()
        if not data:
            continue
        schdl = into_list(data, cursor.description)

        schdl.sort(key=lambda lesson: datetime.strptime(lesson["begin_time"], "%H:%M"))

        for lesson in schdl:
            if not lesson["course"]:
                continue

            start = lesson["begin_time"]
            text = parse_lesson(lesson)

            if not text:
                continue

            thread_id = user["thread"]

            delta = "00:" + str(user["timeout"])
            format = "%H:%M"
            start_task = datetime.strptime(start, format) - datetime.strptime(
                delta, format
            )
            tmp = ""
            for i in str(start_task).split(":"):
                tmp += (("0" + i) if len(i) < 2 else i) + ":"
            start_task = tmp[:-1]

            if lesson["day_of_week"] == "mon":
                schedule.every().monday.at(start_task).do(
                    bot.send_message, user["id"], text, thread_id, lesson["parity"]
                )
            elif lesson["day_of_week"] == "tue":
                schedule.every().tuesday.at(start_task).do(
                    bot.send_message, user["id"], text, thread_id, lesson["parity"]
                )
            elif lesson["day_of_week"] == "wed":
                schedule.every().wednesday.at(start_task).do(
                    bot.send_message, user["id"], text, thread_id, lesson["parity"]
                )
            elif lesson["day_of_week"] == "thu":
                schedule.every().thursday.at(start_task).do(
                    bot.send_message, user["id"], text, thread_id, lesson["parity"]
                )
            elif lesson["day_of_week"] == "fri":
                schedule.every().friday.at(start_task).do(
                    bot.send_message, user["id"], text, thread_id, lesson["parity"]
                )
            elif lesson["day_of_week"] == "sat":
                schedule.every().saturday.at(start_task).do(
                    bot.send_message, user["id"], text, thread_id, lesson["parity"]
                )

    db.putconn(conn)

    return


def groups_in_json() -> list[str]:
    conn = db.getconn()
    cursor = conn.cursor()
    cursor.execute('SELECT DISTINCT "group" FROM schedule ORDER BY "group"')
    data = cursor.fetchall()
    groups = [row[0] for row in data]
    db.putconn(conn)

    return groups


def students_in_group(group) -> list[str]:
    group = str(group)

    conn = db.getconn()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users WHERE "group" = %s', (group,))
    data = cursor.fetchall()
    students = [row[0] for row in data]
    db.putconn(conn)

    return students


def return_infos(id) -> Optional[Dict[str, str]]:
    conn = db.getconn()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE id = %s", (id,))
    data = cursor.fetchone()
    user = into_dict(data, cursor.description)
    db.putconn(conn)

    return user


def pause_bot():
    global allow_update

    if allow_update:
        schedule.clear()

        def run_script():
            os.system("python3 -u upload_sql.py")

        schedule.every(6).minutes.do(run_script)

        allow_update = False
        bot.send_admin_message("Бот больше не отправляет расписание")
    else:
        create_schedule_tasks(True)
        allow_update = True
        bot.send_admin_message("Бот возобновил рассылку!")

    return


def get_schedule(id: str, day: str) -> str:
    id = str(id)

    if day == "sun":
        day = "mon"

    days = ["mon", "tue", "wed", "thu", "fri", "sat"]
    russian_days = ["понедельник", "вторник", "среду", "четверг", "пятницу", "субботу"]

    text = "<u>Расписание на {}</u>:\n\n".format(russian_days[days.index(day)])

    conn = db.getconn()
    cursor = conn.cursor()
    cursor.execute('SELECT "group" FROM users WHERE id = %s', (id,))
    data = cursor.fetchone()
    group = data[0]
    db.putconn(conn)

    if group == "other":
        return "У тебя не выбрана группа для рассылки сообщений"

    if group not in groups_in_json():
        return f"Такой группы нет в базе. Проверь в <a href='https://docs.google.com/spreadsheets/d/{os.environ.get('TABLE_ID')}/edit?usp=sharing'>таблице</a> существование расписания для твоей группы"

    conn = db.getconn()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM schedule WHERE "group" = %s', (group,))
    data = cursor.fetchall()
    schdl = into_list(data, cursor.description)
    db.putconn(conn)

    schdl_today = [lesson for lesson in schdl if lesson["day_of_week"] == day]

    if not schdl_today:
        return "Расписания твоей группы на {} нет".format(russian_days[days.index(day)])

    for lesson in schdl_today:
        str_lesson = parse_lesson(lesson)
        if str_lesson:
            text += "•" + str_lesson + "\n\n"

    if text == "<u>Расписание на {}</u>:\n\n".format(russian_days[days.index(day)]):
        return "Расписания твоей группы на {} нет".format(russian_days[days.index(day)])

    count_of_weeks = (datetime.now() - datetime(2024, 2, 5)).days // 7
    is_odd = (count_of_weeks + 1) % 2 == PARITY_FIRST

    text = ("(нечёт) " if is_odd else "(чёт) ") + text

    return text


if __name__ == "__main__":
    print(groups_in_json())

    pass
