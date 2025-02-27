#!/usr/bin/python3.3
from datetime import datetime
import os
from dotenv import load_dotenv
from sshtunnel import SSHTunnelForwarder
from psycopg2 import pool
import json


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

# Load users from JSON file
with open("users.json", "r", encoding="utf-8") as file:
    users = json.load(file)

# Insert users into the database
with db.getconn() as conn:
    with conn.cursor() as cursor:
        for user_id, user_data in users.items():
            cursor.execute(
                """
                INSERT INTO users (id, username, first_name, last_name, "group", timeout, allow_message, thread)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (id) DO NOTHING
                """,
                (
                    user_id,
                    user_data.get("username"),
                    user_data.get("first_name"),
                    user_data.get("last_name"),
                    user_data.get("group", "other"),
                    user_data.get("timeout", 10),
                    user_data.get("allow_message", "yes") == "yes",
                    user_data.get("thread", "General"),
                ),
            )
    conn.commit()
