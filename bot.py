import requests
from bs4 import BeautifulSoup
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import logging

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# Замените на ваш токен от BotFather
BOT_TOKEN = "8284502910:AAHnnvmdQh5xq1Lh8owHwgis88WRoCDLUh8"

def get_schedule(group_name: str) -> str:
    """Парсит расписание с сайта для указанной группы."""
    url = "https://edu.tgpi.ru/schedule/"  # Обратите внимание: протокол должен быть https
    
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
    except requests.RequestException as e:
        return f"Ошибка при запросе к сайту: {e}"
    
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Пример поиска группы — нужно адаптировать под реальную структуру сайта
    group_element = soup.find('div', {'class': 'group', 'data-name': group_name})
    
    if not group_element:
        return f"❌ Группа '{group_name}' не найдена на сайте. Проверьте написание."
    
    schedule_data = []
    days = group_element.find_all('div', class_='day')
    
    for day in days:
        day_name = day.find('h3').text.strip()
        lessons = day.find_all('div', class_='lesson')
        
        day_schedule = f"\n📅 {day_name}:\n"
        for lesson in lessons:
            time = lesson.find('span', class_='time').text.strip()
            subject = lesson.find('span', class_='subject').text.strip()
            room = lesson.find('span', class_='room').text.strip()
            day_schedule += f"  ⏰ {time} — 📚 {subject} (🏫 {room})\n"
        schedule_data.append(day_schedule)
    
    return ''.join(schedule_data) if schedule_data else "Расписание на неделю не найдено."

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /start."""
    await update.message.reply_text(
        "👋 Привет! Я бот для получения расписания ТГПИ.\n\n"
        "📝 Введите название группы (например, ИСТ-101), чтобы получить расписание на неделю."
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик текстовых сообщений с названием группы."""
    group_name = update.message.text.strip()
    
    if len(group_name) < 2:
        await update.message.reply_text("❌ Название группы слишком короткое. Попробуйте ещё раз.")
        return
    
    await update.message.reply_text("🔄 Ищу расписание...")
    
    schedule = get_schedule(group_name)
    await update.message.reply_text(schedule)

def main():
    """Запуск бота."""
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    print("🚀 Бот запущен и готов к работе!")
    app.run_polling()

if __name__ == "__main__":
    main()
