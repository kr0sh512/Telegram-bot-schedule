# Telegram Bot Schedule
This project is a Telegram bot designed to manage and display schedules. The bot can help users keep track of their daily activities, appointments, and events.

A working version of the [bot for cmc msu](https://t.me/vmk_schedule_bot) students

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

- `/start` - use to change the group number.
- `/schedule` - use to get today's schedule.
- `/random` - create a queue of people.
- `/info` - use to find out your bot settings.
- `/pause` - use to stop receiving messages from the bot.
- `/thread` - use in the desired channel chat so that the bot sends messages there.
- `/timeout` - set the time when the bot will send you a message.
- `/request` - use to send a request to the developer.
- `/source` - Bot's page on Github.
- `/restart` - restart the bot (admin only).
- `/update` - update schedule tasks (admin only).
- `/stats` - get statistics (admin only).
- `/json` - get the users and schedule file (admin only).
- `/info` <i>user_id</i> - find out the user's settings (admin only).
- `/spam` - send a broadcast message (admin only).
- `/pause_all` - pause the bot for everyone (holidays/weekends) (admin only).
- `/stop` <i>user_id</i> - stop sending messages to the user (admin only).

## Contributing

Contributions are welcome! Please fork the repository and create a pull request with your changes.

## Contact

For any questions or suggestions, please open an issue or contact the project maintainer at gudovdo@my.msu.ru.

## Target Audience

This bot is particularly useful for students to track their lessons and manage their academic schedules effectively.

## Limitations

- Cannot create or edit schedule entities directly
- Only works with preloaded schedules and groups










