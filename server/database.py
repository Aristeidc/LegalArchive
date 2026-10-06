import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent/ "LegalArchive.db"

def get_connection():
    connection = sqlite3.connect(DB_PATH)
    connection.row_factory=sqlite3.Row
    return connection

def init_db():
    connection = get_connection()
    connection.execute("""CREATE TABLE IF NOT EXISTS 
        clients(
            client_id               INTEGER     PRIMARY KEY,
            full_name               TEXT        NOT NULL,
            full_name_normalized    TEXT        NOT NULL,
            is_favorite             INTEGER     NOT NULL DEFAULT 0,
            phone                   TEXT,
            email                   TEXT,
            afm                     TEXT,
            address                 TEXT,
            notes                   TEXT,
            created_at              TEXT        NOT NULL,
            updated_at              TEXT        NOT NULL
        )""")
    connection.commit()
    connection.close()

CLIENT_COLUMNS = "client_id, full_name, is_favorite, phone, email, afm, address, notes, created_at, updated_at"

def fetch_client(connection,client_id):
    curs = connection.cursor()
    curs.execute(f"SELECT {CLIENT_COLUMNS} FROM clients WHERE client_id=:client_id",{'client_id':client_id})
    row = curs.fetchone()
    return row
