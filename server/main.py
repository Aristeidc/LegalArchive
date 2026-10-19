from fastapi import FastAPI, HTTPException, Depends
from datetime import datetime,timezone
from database import init_db, fetch_client, get_db, CLIENT_COLUMNS
from models import Client, ClientCreate, ClientUpdate
from text_normalizer import normalizer
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import sqlite3
from typing import Annotated


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield

app = FastAPI(lifespan=lifespan) 

origins = [
    "http://localhost:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_methods=["*"],
    allow_headers=["*"],
)

DbConnection = Annotated[sqlite3.Connection, Depends(get_db)]

@app.post("/clients",response_model = Client, status_code=201)
def create_client(client: ClientCreate, conn: DbConnection):
    stripped_name = client.full_name.strip()
    if not stripped_name:
        raise HTTPException(status_code=400, detail = "full_name cannot be empty")
    normalized_name = normalizer(stripped_name)
    if not normalized_name:
        raise HTTPException(status_code=400, detail = "not valid full_name")
    created_at = datetime.now(tz=timezone.utc).isoformat()
    updated_at =  created_at
    cursor = conn.cursor()
    with conn:
        cursor.execute("INSERT INTO clients(full_name, full_name_normalized, phone, email, afm, address, notes, created_at, updated_at) " \
                        "VALUES(:full_name, :full_name_normalized, :phone, :email, :afm, :address, :notes, :created_at, :updated_at)",
                        {'full_name': stripped_name,
                         'full_name_normalized': normalized_name,
                         'phone': client.phone,
                         'email': client.email,
                         'afm' : client.afm,
                         'address' : client.address,
                         'notes' : client.notes,
                         'created_at': created_at,
                         'updated_at': updated_at
                         })
    lastId=cursor.lastrowid
    row=fetch_client(conn,lastId)
    return dict(row)

@app.get("/clients", response_model = list[Client])
def list_clients(conn: DbConnection, name:str | None = None):
    curs = conn.cursor()
    if name is None:
        curs.execute(f"SELECT {CLIENT_COLUMNS} FROM clients ORDER BY is_favorite DESC, full_name_normalized, client_id")
    else:
        normalized = normalizer(name)
        if not normalized:
            return []
        normalized = normalized.replace("\\","\\\\").replace("%","\\%").replace("_","\\_")
        pattern =f"%{normalized}%"
        curs.execute(f"SELECT {CLIENT_COLUMNS} FROM clients WHERE full_name_normalized LIKE :pattern ESCAPE '\\' ORDER BY is_favorite DESC, full_name_normalized, client_id",{'pattern':pattern})
    rows = curs.fetchall()
    return [dict(row) for row in rows]

@app.get("/clients/{client_id}",response_model = Client)
def get_client_by_id(client_id: int, conn: DbConnection):    
    row = fetch_client(conn,client_id)
    if row is None:
        raise HTTPException(status_code = 404, detail = "Client not found")

    return dict(row)

@app.delete("/clients/{client_id}", status_code=204)
def delete_client_by_id(client_id: int, conn: DbConnection):
    curs = conn.cursor()
    with conn:
        curs.execute("DELETE FROM clients WHERE client_id=:client_id",{'client_id':client_id})
    d_row = curs.rowcount
    if d_row==0:
        raise HTTPException(status_code = 404, detail = "Client not found")
        
@app.patch("/clients/{client_id}", response_model=Client)
def update_client_by_id(client: ClientUpdate, client_id: int, conn: DbConnection):
    updated_fields = client.model_dump(exclude_unset=True)
    if not updated_fields:
        raise HTTPException(status_code=400, detail = "No fields to update")
    if "full_name" in updated_fields:
        if updated_fields["full_name"] is None:
            raise HTTPException(status_code=400, detail="full_name cannot be empty")
        updated_fields["full_name"] = updated_fields["full_name"].strip()
        if not updated_fields["full_name"]:
            raise HTTPException(status_code=400, detail = "full_name cannot be empty")
        updated_fields["full_name_normalized"] = normalizer(updated_fields["full_name"])
        if not updated_fields["full_name_normalized"]:
            raise HTTPException(status_code=400, detail = "not valid full_name")    
    updated_at = datetime.now(tz=timezone.utc).isoformat()
    curs = conn.cursor()
    row = fetch_client(conn,client_id)
    if row is None:
        raise HTTPException(status_code = 404, detail = "Client not found")
    updated_parts = [f"{key}=:{key}" for key in updated_fields]
    set_clause = ", ".join(updated_parts)
   
    updated_fields["updated_at"] = updated_at
    updated_fields["client_id"] = client_id
    with conn:
        curs.execute(f"UPDATE clients SET {set_clause}, updated_at=:updated_at WHERE client_id=:client_id",
                    updated_fields)
    row = fetch_client(conn,client_id)
    return dict(row)

@app.get("/")
def read_root():
    return {"message": "it works"}


