import { useCallback, useEffect, useState } from 'react'
import { type Client } from './types'
import ClientList  from './components/ClientList';
import ClientSearch from './components/ClientSearch';
import { Outlet, Link } from 'react-router';

export default function ClientsPage() {
  
  const [clients, setClients] = useState<Client[]>([]);
  const [error,setError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [nameSearch,setNameSearch] = useState<string>("");

  const onSearch = (name:string )=>{
    setNameSearch(name)
  }

  const fetchClients = useCallback(async (signal?: AbortSignal) =>{
    setIsLoading(true)
    setError(null)
    try{
      let url=`http://localhost:8000/clients`

      if (nameSearch){
        const params = new URLSearchParams({name:nameSearch});
        url += `?${params}`;
      }
      const response = await fetch(url, {signal});

      if (!response.ok) throw new Error ('Failed to fetch!');

      const data = await response.json(); 

      setClients(data);
      setIsLoading(false)
    }catch (err){
      if (err instanceof DOMException && err.name === "AbortError") return;
      setError('Η φόρτωση των πελατών απέτυχε.')
      setIsLoading(false)
      console.error(err)
    }
  },[nameSearch]);

  useEffect(()=>{
    const controller = new AbortController();
    fetchClients(controller.signal);
    return()=> controller.abort();
  },[fetchClients]);
  
  return (
    <div className="client-page">
      <main className='clients-layout'>
        <div className='clients-column'>
          <ClientSearch onSearch={onSearch}/>
          {isLoading && clients.length===0 && <p>Φόρτωση…</p>}
          {error && <p className='error-text'>{error}</p>}
          {!error &&(
            <div className='list-wrapper'>
              <ClientList clients={clients} />
            </div>
          )}
          <Link to="/clients/new" className="new-client-button link-button">Νέος Πελάτης</Link>
        </div>
        <aside className='client-panel'>
          <Outlet context={fetchClients}/>
        </aside>
      </main>
    </div>
  )
}


