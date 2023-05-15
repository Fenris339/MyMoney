import psycopg2

def DB_connect(DB_name,DB_user,DB_password,DB_host,DB_port):
    try:
        DB = psycopg2.connect(
            database = DB_name,
            user = DB_user,
            password = DB_password,
            host = DB_host,
            port = DB_port
            )
        print('Успешное подключение к БД')
    except:
        print('Ошибка подключения к БД')
