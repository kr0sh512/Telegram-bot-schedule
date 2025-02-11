#!/usr/bin/python3.3
import gspread, os, telebot
import pandas as pd
from dotenv import load_dotenv
from google.oauth2 import service_account
from sshtunnel import SSHTunnelForwarder
from psycopg2 import pool

load_dotenv()


"""
CREATE TABLE IF NOT EXISTS schedule(
    id BIGSERIAL PRIMARY KEY,
    day_of_week VARCHAR(255),
    begin_time VARCHAR(20),
    end_time VARCHAR(20),
    course VARCHAR(255),
    lector VARCHAR(255),
    is_lecture BOOLEAN DEFAULT FALSE,
    room VARCHAR(20),
    group VARCHAR(10),
    parity VARCHAR(10),
);
"""

"""
День недели	Время начала	Название	Чётность пары	Лекция?	Преподаватель	Кабинет	2-ой преподаватель	Прочие кабинеты	Остальная информация
Понедельник	8:45	Английский язык	-	FALSE	Бим Мария Моисеевна	735	Шубина Юлия Витальевна	790	
Понедельник	10:30	Практикум на ЭВМ	-	FALSE	Тюляева Вера Викторовна	МЗ-4			
Понедельник	12:15	Действительный и комплексный анализ	-	TRUE	Крицков Леонид Владимирович	П-12			
Понедельник	15:00	Физическая культура	-	FALSE					
Понедельник	16:20			FALSE					
Вторник	8:45	Теория вероятностей и математическая статистика	-	TRUE	Королёв  Виктор  Юрьевич	П-13			
Вторник	10:30	Обыкновенные дифференциальные уравнения	-	FALSE	Дмитриева Ирина Владимировна	607			
Вторник	12:15	Действительный и комплексный анализ	-	FALSE	Сычугов Дмитрий Юрьевич	613			
Вторник	14:35	Электродинамика	-	FALSE	Аксенов Владимир Николаевич	659			
Вторник	16:20		-	FALSE					
Среда	8:45	Практикум на ЭВМ	-	FALSE	Тюляева Вера Викторовна	505			
Среда	10:30	Теория вероятностей и математическая статистика	-	FALSE	Ирина Геннадьевна Шевцова	645			
Среда	12:15	Обыкновенные дифференциальные уравнения	-	TRUE	Денисов Александр Михайлович	П-13			
Среда	15:00			FALSE					
Среда	16:20			FALSE					
Четверг	9:00			FALSE					
Четверг	10:30			FALSE					
Четверг	12:15			FALSE					
Четверг	15:00			FALSE					
Четверг	16:20			FALSE					
Пятница	9:00			FALSE					
Пятница	10:30			FALSE					
Пятница	12:15			FALSE					
Пятница	15:00			FALSE					
Пятница	16:20			FALSE					
Суббота	9:00			FALSE					
Суббота	10:30			FALSE					
Суббота	12:15			FALSE					
Суббота	15:00			FALSE					
Суббота	16:20			FALSE					
				FALSE					
				FALSE					
				FALSE					
				FALSE					
				FALSE					
				FALSE					
				FALSE					
				FALSE					
				FALSE					
"""

SERVICE_ACCOUNT_FILE = "app/credentials.json"

credentials = service_account.Credentials.from_service_account_file(
    SERVICE_ACCOUNT_FILE,
    scopes=[
        "https://www.googleapis.com/auth/drive",
        "https://www.googleapis.com/auth/documents",
    ],
)

gc = gspread.authorize(credentials)

table = gc.open_by_key(os.environ.get("TABLE_ID"))

ws = table.worksheets()

bot = telebot.TeleBot(os.environ.get("TG_TEST_TOKEN"))

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


for i in ws:
    print(i.title)

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
