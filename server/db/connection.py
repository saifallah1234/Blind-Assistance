import psycopg2
def get_db_connection():
    return psycopg2.connect(
        dbname="iot",
        user="postgres",
        password="saif12",
        host="localhost",
        port=5432
    )