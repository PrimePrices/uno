import sqlite3

def get_db():
    print("Fact accessed")
    conn=sqlite3.connect("apps/fact/fact.db")
    cursor=conn.cursor()
    return cursor, conn
def init_db():
    cursor, conn=get_db()
    with open("apps/fact/create.sql", "r") as create:
        cursor.executescript(create.read())
    conn.close()