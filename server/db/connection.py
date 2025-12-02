import psycopg2
def get_db_connection():
    return psycopg2.connect(
        dbname="esp",
        user="postgres",
        password="admin",
        host="localhost",
        port=5432
    )