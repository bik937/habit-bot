# Habit Bot

Личный Telegram-бот Эльдара для ежедневного отслеживания привычек.

## Что делает

- Утреннее напоминание с кнопками (09:00)
- Вечерний итог дня (21:00)
- Отметка привычек нажатием кнопки
- Добавление и удаление привычек через /manage
- Три типа графиков: тепловая карта, прогресс, рейтинг

## Стек

- Python 3.11
- aiogram 3.17
- APScheduler 3.11
- SQLite + aiosqlite
- matplotlib
- Деплой: Railway (Docker)

## Структура

```
habit-bot/
├── bot.py          ← точка входа
├── config.py       ← настройки и переменные окружения
├── database.py     ← работа с SQLite
├── scheduler.py    ← утренние/вечерние уведомления
├── charts.py       ← генерация графиков
├── handlers/       ← обработчики команд и кнопок
└── data/           ← SQLite база данных
```

## Переменные окружения

```
BOT_TOKEN=токен от BotFather
CHAT_ID=chat_id пользователя
DB_PATH=data/habits.db
TIMEZONE=Europe/Moscow
```

## Запуск

```bash
pip install -r requirements.txt
python bot.py
```

## Язык

Всегда отвечай на русском.
