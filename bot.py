import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import logging

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# Токен бота (замените на ваш)
BOT_TOKEN = "8284502910:AAHnnvmdQh5xq1Lh8owHwgis88WRoCDLUh8"

# Базовый URL для расписания группы
BASE_URL = "https://edu.tgpi.ru/schedule/group/13493/"

def get_schedule_for_date(date_str: str) -> str:
    """
    Получает расписание для указанной даты.
    date_str должен быть в формате YYYY-MM-DD
    """
    try:
        url = f"{BASE_URL}{date_str}"
        response = requests.get(url, timeout=10)
        
        if response.status_code != 200:
            return f"❌ Ошибка: сайт вернул статус {response.status_code}"
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Ищем расписание для указанной даты
        schedule_element = soup.find('div', {'data-date': date_str})
        if not schedule_element:
            return "❌ Расписание на эту дату не найдено."
        
        # Извлекаем уроки
        lessons = schedule_element.find_all('div', class_='lesson')
        if not lessons:
            return "На эту дату занятий нет."
        
        schedule_text = f"Расписание на {date_str}:\n\n"
        for i, lesson in enumerate(lessons, 1):
            time_elem = lesson.find('span', class_='time')
            subject_elem = lesson.find('span', class_='subject')
            room_elem = lesson.find('span', class_='room')
            
            time = time_elem.text.strip() if time_elem else "Время не указано"
            subject = subject_elem.text.strip() if subject_elem else "Предмет не указан"
            room = room_elem.text.strip() if room_elem else "Аудитория не указана"
            
            schedule_text += f"{i}. {time} — {subject} ({room})\n"
        return schedule_text
    except Exception as e:
        return f"❌ Ошибка при получении расписания: {e}"

def get_date_from_command(command: str) -> str:
    """
    Преобразует команду в дату в формате YYYY-MM-DD.
    """
    today = datetime.now().date()
    if command == 'завтра':
        target_date = today + timedelta(days=1)
    elif command == 'послезавтра':
        target_date = today + timedelta(days=2)
    elif command == 'неделя':
        target_date = today + timedelta(weeks=1)
    else:
        return None
    return target_date.strftime('%Y-%m-%d')

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /start."""
    welcome_text = """
📅 Бот расписания группы

Используйте команды:
/tomorrow — расписание на завтра
/day_after_tomorrow — расписание послезавтра
/week — расписание через неделю

Или просто напишите:
- завтра
- послезавтра
- неделя
    """
    await update.message.reply_text(welcome_text)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик текстовых сообщений."""
    user_text = update.message.text.lower().strip()
    
    # Определяем команду
    if user_text in ['завтра', 'послезавтра', 'неделя']:
        date_str = get_date_from_command(user_text)
        if date_str:
            schedule = get_schedule_for_date(date_str)
            await update.message.reply_text(schedule)
        else:
            await update.message.reply_text("Неизвестная команда. Используйте: завтра, послезавтра или неделя.")
    else:
        await update.message.reply_text("Используйте: завтра, послезавтра или неделя")

async def tomorrow(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /tomorrow."""
    date_str = get_date_from_command('завтра')
    schedule = get_schedule_for_date(date_str)
    await update.message.reply_text(schedule)

async def day_after_tomorrow(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /day_after_tomorrow."""
    date_str = get_date_from_command('послезавтра')
    schedule = get_schedule_for_date(date_str)
    await update.message.reply_text(schedule)

async def week(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /week."""
    date_str = get_date_from_command('неделя')
    schedule = get_schedule_for_date(date_str)
    await update.message.reply_text(schedule)

def main():
    """Запуск бота."""
    app = Application.builder().token(BOT_TOKEN).build()
    # Добавляем обработчики
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("tomorrow", tomorrow))
    app.add_handler(CommandHandler("day_after_tomorrow", day_after_tomorrow))
    app.add_handler(CommandHandler("week", week))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    print("🚀 Бот запущен и готов к работе!")
    app.run_polling()

if __name__ == "__main__":
    main()
