# Telegram Bot Schedule
This project is a Telegram bot designed to manage and display schedules. The bot can help users keep track of their daily activities, appointments, and events.

## Features

- View preloaded schedules
- Group schedules for better organization
- Receive reminders for upcoming events
- User-friendly commands and interface

## Installation

1. Clone the repository:
    ```sh
    git clone https://github.com/yourusername/Telegram-bot-schedule.git
    ```
2. Navigate to the project directory:
    ```sh
    cd Telegram-bot-schedule
    ```
3. Install the required dependencies:
    ```sh
    pip install -r requirements.txt
    ```

## Usage

1. Create a new bot on Telegram and get the API token.
2. Set the API token in the environment variables or in a configuration file.
3. You need to create schedules files for groups.
4. Run the bot:
    ```sh
    python bot.py
    ```

## Commands

- `/start` - используй, чтобы сменить номер группы.
- `/schedule` - используй, чтобы получить расписание на сегодня.
- `/random` - сделай очередь из людей
- `/info` - используй, чтобы узнать твои настройки бота
- `/pause` - используй, чтобы прекратить получать сообщения от бота
- `/thread` - используй в нужном чате канала, чтобы бот отправлял сообщения именно туда
- `/timeout` - настрой время, когда бот будет присылать тебе сообщение
- `/request` - используй, чтобы отправить разработчику какой-то запрос
- `/source` - Страница бота на Github
- `/restart` - перезапуск бота (admin only).
- `/update` - обновление schedule задач (admin only)
- `/stats` - получание статистики (admin only)
- `/json` - получить файл пользователей и расписания (admin only)
- `/info` <i>id_пользователя</i> - узнать настройки пользователя (admin only)
- `/spam` - сделать рассылку (admin only)
- `/pause_all` - приостановить бота для всех (каникулы/выходные) (admin only)
- `/stop` <i>id_пользователя</i> - приостановить отправку сообщений для пользователя (admin only)

## Contributing

Contributions are welcome! Please fork the repository and create a pull request with your changes.

## Contact

For any questions or suggestions, please open an issue or contact the project maintainer at [gudovdo@my.msu.ru].

## Target Audience

This bot is particularly useful for students to track their lessons and manage their academic schedules effectively.

## Limitations

- Cannot create or edit schedule entities directly
- Only works with preloaded schedules and groups










