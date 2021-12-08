import psycopg2

def getConnection():
    try:
        conn = psycopg2.connect(
            host='localhost',
            database='fbd',
            user='postgres',
            password='1234'
        )
    except psycopg2.OperationalError as e:
        print("Erro ao conectador o banco de dados")


    return conn