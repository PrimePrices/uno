from .db import get_db
from datetime import date
def get_today():
    cursor, conn = get_db()
    year, month, day = date.today().year, date.today().month, date.today().day
    cursor.execute(f"SELECT text, tags, sources FROM facts WHERE year={year} AND month={month} AND day={day}")
    fact = cursor.fetchone()
    conn.close()
    return fact