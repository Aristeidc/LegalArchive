from pydantic import BaseModel

class ClientCreate(BaseModel):
    full_name: str
    phone: str | None = None
    email: str | None = None
    afm: str | None = None
    address: str | None = None
    notes: str | None = None

class Client(BaseModel):
    client_id: int
    full_name: str
    is_favorite: bool
    phone: str | None = None
    email: str | None = None
    afm: str | None = None
    address: str | None = None
    notes: str | None = None
    created_at: str
    updated_at: str

class ClientUpdate(BaseModel):
    full_name: str  | None = None
    is_favorite: bool = False
    phone: str | None = None
    email: str | None = None
    afm: str | None = None
    address: str | None = None
    notes: str | None = None

# is_favorite: bool = False :
# Default is never written: exclude_unset drops unsent fields.
# No "| None": an explicit null gets a 422 instead of hitting NOT NULL.