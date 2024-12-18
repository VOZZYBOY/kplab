import time
import subprocess
import threading
from sqlalchemy.orm import Session
from yandex_chain import YandexLLM, YandexEmbeddings, YandexGPTModel
from langchain_community.vectorstores import InMemoryVectorStore
from langchain.prompts import ChatPromptTemplate
from langchain.schema.output_parser import StrOutputParser
from langchain.schema.runnable import RunnablePassthrough
from models import Doctor, Client, Service, Appointment
from database import SessionLocal
import logging
import os
import sys

# Добавляем корневую директорию проекта в PYTHONPATHа
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + "/..")

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Переменная для хранения текущего токена
IAM_TOKEN = None


def update_iam_token():
    """Создает новый IAM токен и сохраняет его в глобальную переменную."""
    global IAM_TOKEN
    try:
        result = subprocess.run(["yc", "iam", "create-token"], capture_output=True, text=True, check=True)
        IAM_TOKEN = result.stdout.strip()
        logger.info("IAM токен успешно обновлен.")
    except subprocess.CalledProcessError as e:
        logger.error(f"Ошибка при обновлении IAM токена: {e.stderr}")
        IAM_TOKEN = None


def get_iam_token():
    """Возвращает текущий токен. Если токена нет, обновляет его."""
    global IAM_TOKEN
    if not IAM_TOKEN:
        update_iam_token()
    return IAM_TOKEN


def start_token_updater():
    """Запускает процесс обновления IAM токена каждые 12 часов."""
    def updater():
        while True:
            update_iam_token()
            time.sleep(12 * 60 * 60)  # Обновление токена каждые 12 часов

    thread = threading.Thread(target=updater, daemon=True)
    thread.start()


def is_slot_available(db: Session, doctor_id: int, appointment_time: str) -> bool:
    """Проверяет, свободен ли временной слот для указанного доктора."""
    conflicting_appointment = db.query(Appointment).filter(
        Appointment.doctor_id == doctor_id,
        Appointment.appointment_time == appointment_time
    ).first()
    return conflicting_appointment is None


def get_context_from_db(db: Session):
    """Извлекает данные из базы данных и формирует текстовый контекст для векторного хранилища."""
    try:
        logger.info("Извлечение данных из базы...")
        doctors = db.query(Doctor).all()
        services = db.query(Service).all()
        appointments = db.query(Appointment).all()

        docs = []
        for doctor in doctors:
            docs.append(f"Доктор {doctor.full_name} специализируется на {doctor.specialty}.")
        for service in services:
            docs.append(f"Услуга: {service.service_name}.")
        for appointment in appointments:
            docs.append(
                f"Запись ID {appointment.appointment_id} клиента ID {appointment.client_id} "
                f"к доктору ID {appointment.doctor_id} на услугу ID {appointment.service_id} "
                f"в {appointment.appointment_time}."
            )
        logger.info("Контекст из базы данных успешно получен.")
        return docs
    except Exception as e:
        logger.error(f"Ошибка при получении данных из базы: {e}")
        return []


def process_query(query, folder_id, db: Session):
    global IAM_TOKEN
    try:
        logger.info("Начинается обработка запроса...")
        get_iam_token()

        embeddings = YandexEmbeddings(folder_id=folder_id, iam_token=IAM_TOKEN)
        llm = YandexLLM(folder_id=folder_id, iam_token=IAM_TOKEN, model=YandexGPTModel.ProRC)

        logger.info("Модель и эмбеддинги успешно инициализированы.")

        docs = get_context_from_db(db)
        if not docs:
            return "Не удалось получить контекст из базы данных."

        vectorstore = InMemoryVectorStore.from_texts(docs, embedding=embeddings)
        retriever = vectorstore.as_retriever()

        # Формируем шаблон для запроса
        template = """Тебя зовут Эрика, ты консультант клиники Эрикмед. Твоя задача:
поддерживать с клиентами диалог, записывать их на прием, отменять запись, рассказывать про наши услуги.
Если клиент пытается записаться к доктору и временной слот занят, обязательно сообщи об этом в ответе
При запросе о услугах пользователя перечисляй чистка лица,массаж спины,увлаэнение кожи,ботокс,жиросжигание,и тому подобное.:
{context}

Вопрос: {question}
"""
        prompt = ChatPromptTemplate.from_template(template)

        chain = (
            {"context": retriever, "question": RunnablePassthrough()}
            | prompt
            | llm
            | StrOutputParser()
        )

        logger.info("Цепочка успешно сформирована. Выполняется запрос к модели...")
        response = chain.invoke(query)

        logger.info(f"Ответ от YandexGPT: {response}")
        return response

    except Exception as e:
        logger.error(f"Ошибка при обработке запроса: {e}")
        return "Произошла ошибка при обработке запроса."


if __name__ == "__main__":
    folder_id = "b1gb9k14k5ui80g91tnp"
    start_token_updater()

    logger.info("Ожидание обновления токена...")
    time.sleep(2)

    db = SessionLocal()
    try:
        user_query = input("Введите ваш запрос: ")
        response = process_query(user_query, folder_id, db)
        print("Ответ:", response)
    finally:
        db.close()
