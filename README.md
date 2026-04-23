# Habit Tracker Bot

Личный Telegram-бот для ежедневного отслеживания привычек.

## Возможности

- ✅ Отмечай привычки нажатием кнопки
- ➕ Добавляй и удаляй привычки в любое время
- ☀️ Утреннее напоминание с кнопками (09:00)
- 🌙 Вечерний итог дня (21:00)
- 📊 Три типа графиков: тепловая карта, прогресс, рейтинг

## Быстрый старт

### Шаг 1 — Создай бота в Telegram

1. Напиши @BotFather в Telegram
2. Отправь `/newbot`
3. Придумай имя и username для бота
4. Скопируй токен — он выглядит так: `1234567890:AAHdqTcvCH1vGWJxfSeofSAs0K5PALDsaw`

### Шаг 2 — Узнай свой chat_id

1. Напиши @userinfobot в Telegram
2. Он ответит твоим chat_id — число вида `123456789`

### Шаг 3 — Настрой окружение

```bash
cp .env.example .env
```

Открой `.env` и заполни:
```
BOT_TOKEN=твой_токен_от_botfather
CHAT_ID=твой_chat_id
```

### Шаг 4 — Запусти локально

```bash
pip install -r requirements.txt
python bot.py
```

Напиши `/start` своему боту в Telegram.

---

## Деплой на Railway (бесплатно)

### Шаг 1 — Загрузи код на GitHub

1. Создай репозиторий на github.com
2. Загрузи папку `habit-bot/`

### Шаг 2 — Создай проект на Railway

1. Зайди на [railway.app](https://railway.app)
2. Нажми **New Project → Deploy from GitHub repo**
3. Выбери свой репозиторий

### Шаг 3 — Добавь переменные окружения

В настройках проекта Railway → Variables:
```
BOT_TOKEN = твой_токен
CHAT_ID = твой_chat_id
DB_PATH = data/habits.db
TIMEZONE = Europe/Moscow
```

### Шаг 4 — Добавь постоянное хранилище (для базы данных)

1. В Railway → Add Service → Volume
2. Mount path: `/app/data`

Без этого база данных сбросится при перезапуске контейнера.

### Шаг 5 — Deploy

Railway автоматически соберёт Docker-образ и запустит бота.

---

## Команды бота

| Команда | Действие |
|---|---|
| `/start` | Приветствие |
| `/manage` | Добавить / удалить привычки |
| `/checkin` | Отметить привычки за сегодня |
| `/today` | Сводка за сегодня |
| `/stats` | Статистика и графики |

---

## Стек

- Python 3.11
- aiogram 3.17
- APScheduler 3.11
- SQLite + aiosqlite
- matplotlib
