import psycopg2
from config import DB_CONFIG

def get_connection():
    return psycopg2.connect(**DB_CONFIG)

def test_connection():
    try:
        conn = get_connection()
        conn.close()
        print("подключение к бд успешно")
        return True
    except Exception as ex:
        print(f"Ошибка подключения: {ex}")
        return False
    
if __name__ == "__main__":
    test_connection()