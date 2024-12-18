import logging
from sqlalchemy import create_engine, Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import text  # Для правильного выполнения SQL
from faker import Faker
import random
from datetime import datetime

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# URL подключения к базе данных
SQLALCHEMY_DATABASE_URL = "postgresql://vozzy:newpassword@localhost/clinic_db"  # Замените на свои данные

# Создание объекта базы данных
Base = declarative_base()

# Создание подключения к базе данных
engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Модели базы данных

class Doctor(Base):
    __tablename__ = 'doctors'

    doctor_id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String, index=True)
    specialty = Column(String)

    appointments = relationship('Appointment', back_populates='doctor')

class Client(Base):
    __tablename__ = 'clients'

    client_id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String, index=True)
    username = Column(String, unique=True, index=True)  # Добавляем поле username для уникальности

    appointments = relationship('Appointment', back_populates='client')

class Service(Base):
    __tablename__ = 'services'

    service_id = Column(Integer, primary_key=True, index=True)
    service_name = Column(String)

    appointments = relationship('Appointment', back_populates='service')

class Appointment(Base):
    __tablename__ = 'appointments'

    appointment_id = Column(Integer, primary_key=True, index=True)
    client_id = Column(Integer, ForeignKey('clients.client_id'))
    doctor_id = Column(Integer, ForeignKey('doctors.doctor_id'))
    service_id = Column(Integer, ForeignKey('services.service_id'))
    appointment_time = Column(DateTime)

    client = relationship('Client', back_populates='appointments')
    doctor = relationship('Doctor', back_populates='appointments')
    service = relationship('Service', back_populates='appointments')
