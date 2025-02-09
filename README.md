# Telegram Bot Schedule

This project is a Telegram bot designed to manage and display schedules. The bot helps users keep track of their daily activities, appointments, and events.

A working version of the [bot for CMC MSU](t.me/vmk_schedule_bot) students.

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
3. Create schedule files for groups.
4. Run the bot:
   ```sh
   python bot.py
   ```

## Commands

- `/start` - Change the group number.
- `/schedule` - Get today's schedule.
- `/info` - Find out your bot settings.
- `/pause` - Stop receiving messages from the bot.
- `/thread` - Use in the desired channel chat to send messages there.
- `/timeout` - Set the time when the bot will send you a message.
- `/request` - Send a request to the developer.
- `/source` - Bot's page on GitHub.
- `/restart` - Restart the bot (admin only).
- `/update` - Update schedule tasks (admin only).
- `/stats` - Get statistics (admin only).
- `/json` - Get the users and schedule file (admin only).
- `/info <user_id>` - Find out the user's settings (admin only).
- `/spam` - Send a broadcast message (admin only).
- `/pause_all` - Pause the bot for everyone (holidays/weekends) (admin only).
- `/stop <user_id>` - Stop sending messages to the user (admin only).

## Contributing

Contributions are welcome! Please fork the repository and create a pull request with your changes.

## Contact

For any questions or suggestions, please open an issue or contact the project maintainer at gudovdo@my.msu.ru.

## Target Audience

This bot is particularly useful for students to track their lessons and manage their academic schedules effectively.

## Limitations

- Cannot create or edit schedule entities directly
- Only works with preloaded schedules and groups
