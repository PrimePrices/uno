from sqlite3 import connect, Row

def get_db():
    conn=connect("database.db")
    conn.row_factory=Row
    return conn