#!/usr/bin/python3.3
import gspread, os, telebot
import pandas as pd
from dotenv import load_dotenv
from google.oauth2 import service_account
from sshtunnel import SSHTunnelForwarder
from psycopg2 import pool
from datetime import datetime

load_dotenv()

bot = telebot.TeleBot(os.environ.get("TG_TEST_TOKEN"))

SERVICE_ACCOUNT_FILE = "credentials.json"

credentials = service_account.Credentials.from_service_account_file(
    SERVICE_ACCOUNT_FILE,
    scopes=[
        "https://www.googleapis.com/auth/drive",
        "https://www.googleapis.com/auth/documents",
    ],
)

gc = gspread.authorize(credentials)

table = gc.open_by_key(os.environ.get("TABLE_ID"))

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


def f():
    ws = table.worksheets()

    for i in ws:
        # print(i.title)

        if not (i.title == "Пример" or i.title == "main") and i.title.isdigit():
            df = pd.DataFrame(i.get_all_records())
            if not df.empty:
                with db.getconn() as conn:
                    with conn.cursor() as cursor:
                        cursor.execute(
                            'DELETE FROM schedule WHERE "group" = %s', (str(i.title),)
                        )
                        conn.commit()
                        for index, row in df.iterrows():
                            day_of_week_map = {
                                "Понедельник": "mon",
                                "Вторник": "tue",
                                "Среда": "wed",
                                "Четверг": "thu",
                                "Пятница": "fri",
                                "Суббота": "sat",
                                "Воскресенье": "sun",
                            }
                            row["День недели"] = day_of_week_map.get(
                                row["День недели"], row["День недели"]
                            )
                            if row["Название"] == "":
                                continue
                            end_time = (
                                pd.to_datetime(row["Время начала"], format="%H:%M")
                                + pd.Timedelta(hours=1, minutes=35)
                            ).strftime("%H:%M")
                            cursor.execute(
                                """
                                INSERT INTO schedule (day_of_week, begin_time, end_time, course, lector, is_lecture, room, "group", parity)
                                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                                """,
                                (
                                    row["День недели"],
                                    row["Время начала"],
                                    end_time,
                                    row["Название"],
                                    f'{row["Преподаватель"]}{"/" + str(row["2-ой преподаватель"]) if row["2-ой преподаватель"] else ""}',
                                    row["Лекция?"],
                                    f'{row["Кабинет"]}{"/" + str(row["Прочие кабинеты"]) if row["Прочие кабинеты"] else ""}',
                                    i.title,
                                    row["Чётность пары"],
                                ),
                            )
                        conn.commit()

    text = f"Last tg-bot update was at: {datetime.now().astimezone().strftime('%Y-%m-%d %H:%M %Z')}"
    table.get_worksheet(0).update_acell("A25", text)

    return


if __name__ == "__main__":
    try:
        f()
    except Exception as e:
        print(e)

        bot.send_message(int(os.environ.get("ADMIN_ID")), "Check logs! upload error.")
        bot.send_message(int(os.environ.get("ADMIN_ID")), e)

    exit(0)
