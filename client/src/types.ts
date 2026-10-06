export type Client = {
    client_id: number
    full_name: string
    is_favorite: boolean 
    phone: string | null
    email: string | null
    afm: string | null
    address: string | null
    notes: string | null
    created_at: string
    updated_at: string 
}

export interface ClientListProps {
  clients: Client[];
}

export interface ClientSearchProps{
  onSearch:(name:string)=> void;
}

export type ClientForm ={
  full_name: string 
  phone: string 
  email: string 
  afm: string 
  address: string 
  notes: string 
}

export type ClientUpdate ={
  full_name?: string
  is_favorite?: boolean
  phone?: string | null
  email?: string | null
  afm?: string | null
  address?: string | null
  notes?: string | null
}

export interface ClientUpdateProps{
  client: Client
  onSaved: () => void
  onCancel: () => void
}

export type ClientCreate = {
  full_name: string
  phone: string | null
  email: string | null
  afm: string | null
  address: string | null
  notes: string | null
}