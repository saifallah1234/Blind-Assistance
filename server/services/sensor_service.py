from db.connection import get_db_connection

def insert_sensor_data(distance, movement, buzzer):
    conn = get_db_connection()
    cur = conn.cursor()
    query = f'INSERT INTO esp (distance, mouvment, buzzer) VALUES ({distance}, {movement}, {buzzer})'
    cur.execute(query)
    conn.commit()
    cur.close()
    conn.close()

def get_latest_data():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT id, timestamp, distance, mouvment, buzzer
        FROM esp
        ORDER BY timestamp DESC
        LIMIT 1
    """)
    row = cur.fetchone()
    cur.close()
    conn.close()
    return row

def get_all_data(limit=500):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT id, timestamp, distance, mouvment, buzzer
        FROM esp
        ORDER BY timestamp DESC
        LIMIT %s
    """, (limit,))
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return rows
