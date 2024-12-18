import requests
import psycopg2
import logging
LOGIN_URL = "https://dev.back.matrixcrm.ru/api/v1/Auth/login"
API_URL = "https://dev.back.matrixcrm.ru/api/v1/AI/servicesByFilters"
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

LOGIN_PAYLOAD = {
    "Email": "xzolenr6@gmail.com",
    "Password": "Ericman2004",
    "DeviceId": "1234",
    "TenantId": "1234",
}

def get_db_connection():
    try:
        conn = psycopg2.connect(
            dbname="clinic_db",
            user="vozzy",
            password="newpassword",
            host="localhost"
        )
        return conn
    except Exception as e:
        logger.error(f"Ошибка подключения к базе данных: {e}")
        return None

def get_auth_token():
    response = requests.post(LOGIN_URL, json=LOGIN_PAYLOAD)
    if response.status_code == 200:
        token = response.json().get("Token")
        logger.info("Авторизация прошла успешно, получен токен.")
        return token
    else:
        logger.error("Ошибка авторизации.")
        return None

def get_services(token):
    headers = {
        "Authorization": f"Bearer {token}"
    }
    response = requests.get(API_URL, headers=headers)

    if response.status_code == 200:
        logger.info("Данные успешно получены с API.")
        return response.json()
    else:
        logger.error(f"Ошибка при получении данных с API: {response.status_code}")
        return None

def insert_services_and_doctors(data):
    conn = get_db_connection()
    if conn:
        try:
            cursor = conn.cursor()
            for item in data['data']['items']:
                service_name = item.get("serviceName", "Неизвестная услуга")
                doctor_name = item.get("employeeFullName", "Неизвестный врач")
                price = item.get("price", 0)

                cursor.execute("""
                    INSERT INTO services (service_name, price)
                    VALUES (%s, %s)
                    ON CONFLICT (service_name) DO NOTHING;
                """, (service_name, price))
                
                cursor.execute("""
                    INSERT INTO doctors (full_name)
                    VALUES (%s)
                    ON CONFLICT (full_name) DO NOTHING;
                """, (doctor_name,))
                
            conn.commit()
            logger.info("Данные успешно записаны в базу данных.")
        except Exception as e:
            logger.error(f"Ошибка записи данных в базу данных: {e}")
            conn.rollback()
        finally:
            cursor.close()
            conn.close()

def main():
    token = get_auth_token()
    if token:
        services_data = get_services(token)
        if services_data:
            insert_services_and_doctors(services_data)

if __name__ == "__main__":
    main()
