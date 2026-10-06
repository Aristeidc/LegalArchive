from fastapi import FastAPI, HTTPException
from datetime import datetime,timezone
from database import get_connection,init_db, fetch_client, CLIENT_COLUMNS
from models import Client, ClientCreate, ClientUpdate
from text_normalizer import normalizer
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager


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



@app.post("/clients",response_model = Client)
def create_client(client: ClientCreate):
    stripped_name = client.full_name.strip()
    if not stripped_name:
        raise HTTPException(status_code=400, detail = "full_name cannot be empty")
    created_at = datetime.now(tz=timezone.utc).isoformat()
    updated_at =  created_at
    connection = get_connection()
    cursor = connection.cursor()
    with connection:
        cursor.execute("INSERT INTO clients(full_name, full_name_normalized, phone, email, afm, address, notes, created_at, updated_at) " \
                        "VALUES(:full_name, :full_name_normalized, :phone, :email, :afm, :address, :notes, :created_at, :updated_at)",
                        {'full_name': stripped_name,
                         'full_name_normalized': normalizer(stripped_name),
                         'phone': client.phone,
                         'email': client.email,
                         'afm' : client.afm,
                         'address' : client.address,
                         'notes' : client.notes,
                         'created_at': created_at,
                         'updated_at': updated_at
                         })
    lastId=cursor.lastrowid
    row=fetch_client(connection,lastId)
    return dict(row)

@app.get("/clients", response_model = list[Client])
def get_client(name:str | None = None):
    conn = get_connection()
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
def get_client_by_id(client_id: int):
    conn = get_connection()    
    row = fetch_client(conn,client_id)
    if row is None:
        raise HTTPException(status_code = 404, detail = "Item not found")

    return dict(row)

@app.delete("/clients/{client_id}", status_code=204)
def delete_client_by_id(client_id: int):
    conn = get_connection()
    curs = conn.cursor()
    with conn:
        curs.execute("DELETE FROM clients WHERE client_id=:client_id",{'client_id':client_id})
    d_row = curs.rowcount
    if d_row==0:
        raise HTTPException(status_code = 404, detail = "Item not found")
        
@app.patch("/clients/{client_id}", response_model=Client)
def update_client_by_id(client: ClientUpdate, client_id: int):
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
    updated_at = datetime.now(tz=timezone.utc).isoformat()
    conn = get_connection()
    curs = conn.cursor()
    row = fetch_client(conn,client_id)
    if row is None:
        raise HTTPException(status_code = 404, detail = "Item not found")
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





