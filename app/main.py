import logging
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters
from database import SessionLocal
from models import Doctor
from yandex_gpt import process_query  # Импортируем вашу модель

BOT_TOKEN = "7590319507:AAHyDNMr-RK5qhArW7JfJYKv3J4x1uG0YGo"
FOLDER_ID = "b1gb9k14k5ui80g91tnp"

# Логирование
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Кнопки главного меню
def main_menu():
    keyboard = [
        [KeyboardButton("Записаться на приём")],
        [KeyboardButton("Список врачей")],
        [KeyboardButton("Спросить у Эрики")],
        [KeyboardButton("Зарегистрироваться")]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

# Команда /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Добро пожаловать в клинику Эрикмед!", reply_markup=main_menu())

# Команда для отображения списка врачей
async def list_doctors(update: Update, context: ContextTypes.DEFAULT_TYPE):
    db = SessionLocal()
    try:
        doctors = db.query(Doctor).all()
        if doctors:
            response = "\n".join([f"{doctor.doctor_id}. {doctor.full_name} ({doctor.specialty})" for doctor in doctors])
        else:
            response = "Список врачей пуст."
        await update.message.reply_text(response)
    finally:
        db.close()

# Команда для записи на приём
async def book_appointment(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Введите данные для записи в формате: 20.12.2024 14:00 к доктору Иванову.")

# Команда для общения с моделью
async def ask_erika(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_message = update.message.text
    db = SessionLocal()
    try:
        await update.message.reply_text("Эрика обрабатывает ваш запрос, пожалуйста, подождите...")
        response = process_query(user_message, FOLDER_ID, db)
        await update.message.reply_text(response)
    except Exception as e:
        logger.error(f"Ошибка работы модели: {e}")
        await update.message.reply_text("Произошла ошибка при обработке запроса. Попробуйте позже.")
    finally:
        db.close()

# Команда для регистрации
async def register(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Введите ваш логин и пароль через пробел (пример: user1 pass123):")

async def handle_registration(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        username, password = update.message.text.split()
        db = SessionLocal()
        # Проверьте уникальность пользователя
        if db.query(Client).filter(Client.username == username).first():
            await update.message.reply_text("Пользователь уже существует!")
            return

        new_user = Client(username=username, password=password)
        db.add(new_user)
        db.commit()

        await update.message.reply_text("Вы успешно зарегистрированы!")
    except Exception as e:
        await update.message.reply_text(f"Ошибка регистрации: {str(e)}")
    finally:
        db.close()

# Основной запуск бота
async def main():
    application = ApplicationBuilder().token(BOT_TOKEN).build()

    # Команды
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.Text("Список врачей"), list_doctors))
    application.add_handler(MessageHandler(filters.Text("Записаться на приём"), book_appointment))
    application.add_handler(MessageHandler(filters.Text("Спросить у Эрики"), ask_erika))
    application.add_handler(CommandHandler("register", register))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_registration))

    # Запуск polling
    await application.run_polling()

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())  # Запуск бота

def process_query(user_id: int = Form(...), query: str = Form(...)):
    """
    Выполнение SQL-запроса с логированием результата.
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(query)
        response = cursor.fetchall()
        conn.commit()
        conn.close()
        log_query(user_id, query, str(response))
        return {"data": response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
import psycopg2

# Вставка данных из API в базу данных
def insert_api_data(data):
    connection = psycopg2.connect("dbname=mydb user=myuser password=mypassword host=localhost")
    cursor = connection.cursor()

    for item in data:
        cursor.execute(
            "SELECT add_api_data(%s, %s, %s, %s, %s)",
            (item['service_name'], item['category_name'], item['price'], item['filial_name'], item['specialist_name'])
        )

    connection.commit()
    cursor.close()
    connection.close()

# Обновление статуса после обработки нейронной сетью
def update_status(api_data_id, response):
    connection = psycopg2.connect("dbname=mydb user=myuser password=mypassword host=localhost")
    cursor = connection.cursor()
    cursor.execute("SELECT update_processed_status(%s, %s)", (api_data_id, response))
    connection.commit()
    cursor.close()
    connection.close()
