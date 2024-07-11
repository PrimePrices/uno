from sqlite3 import connect, Row

def get_db():
    conn=connect("database.db")
    conn.row_factory=Row
    return conn

def requires_db(f):#wrapper
    def wrapper(*args, **kwargs):
        conn=connect("database.db")
        conn.row_factory=Row
        with connect("database.db") as conn:
            conn.row_factory=Row
            return f(*args, **kwargs, conn=conn)
    