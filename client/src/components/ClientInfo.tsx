import { useEffect, useState } from 'react'
import { type Client } from "../types";
import { Link, useNavigate, useParams, useOutletContext, useLoaderData, useRevalidator } from "react-router";
import pencil from "../assets/pencil.png"
import ClientEdit from './ClientEdit';
import gStar from "../assets/star-gold.png"
import eStar from "../assets/star.png"

export default function ClientInfo(){

  const client = useLoaderData() as Client
  const { id } = useParams();
  const url = `http://localhost:8000/clients/${id}`
  const refreshList = useOutletContext<() => void>();
  const revalidator = useRevalidator();

  // -------------------UPDATE----------------------//
  const [isEditing, setIsEditing] = useState<boolean>(false);
  const onSaved = () =>{
    revalidator.revalidate();
    refreshList();
    setIsEditing(false)
  }
  const onCancel = ()=>{
    setIsEditing(false)
  }
  
  //delete Client
  const [confirmDelete,setConfirmDelete] = useState<boolean>(false);
  const [deleteError,setDeleteError] = useState<string | null>(null);
  const [isDeleting, setIsDeleting] = useState<boolean>(false);
  const navigate = useNavigate(); //leave the file

  async function handleDelete() {
    setDeleteError(null)
    setIsDeleting(true)
  
    try{
      const response = await fetch(url,{
        method: "DELETE"
      })

      if (!response.ok) throw new Error("Failed to Delete Client")
      navigate("/clients");
      refreshList();

    }catch (err){
      setDeleteError('Η διαγραφή του πελάτη απέτυχε.')
      console.error(err)
    }finally{
      setIsDeleting(false);
      setConfirmDelete(false);      
    }
  }

  //Favorites
  const [favError,setFavError] = useState<string | null>(null);
  const [isTogglingFav,setIsTogglingFav] = useState<boolean>(false);

  async function handleFavorite() {
    setFavError(null);
    setIsTogglingFav(true);

    const payload = !client.is_favorite
    try{
      const response = await fetch(url,{
        method: "PATCH",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({is_favorite: payload})
      })

      if (!response.ok) throw new Error('Failed PATCH!')

      revalidator.revalidate();
      refreshList();
      
    }catch(err){
      setFavError('Η ενημέρωση των αγαπημένων απέτυχε.')
      console.error(err)
    }finally{
      setIsTogglingFav(false)
    }
  }

  //reset UI state when switching clients
  useEffect(()=>{
    setIsEditing(false);
    setConfirmDelete(false);
    setDeleteError(null);
    setFavError(null);
  },[id])

  return(
    <div className='client-card'>
      <div className='card-top'>
        {!isEditing &&(
          <button className='fav-button icon-button' title={client.is_favorite ? "Αφαίρεση από αγαπημένα" : "Προσθήκη στα αγαπημένα"} type="button" aria-pressed={client.is_favorite} onClick={handleFavorite} disabled={isTogglingFav}>
            <img src={client.is_favorite? gStar:eStar} alt="Αγαπημένος" className="fav-star"/>
          </button>
        )}
        <Link to="/clients" className='close-button link-button icon-button' aria-label="Κλείσιμο" title="Κλείσιμο">&#10006;</Link>
      </div>
      {!isEditing?
        <div>
          <dl className='client-details client-view'>
            <dt>Ονοματεπώνυμο</dt>
            <dd>{client.full_name}</dd>
            
            <dt>Τηλέφωνο</dt>
            <dd>{client.phone || "—"}</dd>
            
            <dt>ΑΦΜ</dt>
            <dd>{client.afm || "—"}</dd>

            <dt>Διεύθυνση</dt>
            <dd>{client.address || "—"}</dd>

            <dt>Email</dt>
            <dd>{client.email || "—"}</dd>

            <dt>Σημειώσεις</dt>
            <dd>{client.notes || "—"}</dd>                          
          </dl>
          <div className='card-bottom'>
            <button className='edit-button icon-button' title='Επεξεργασία' onClick={() => setIsEditing(true)} type='button'>
              <img className='edit-icon' src={pencil} alt='Επεξεργασία'/>
            </button>
            {!confirmDelete ?( 
              <button className='delete-button danger-button' onClick={()=>setConfirmDelete(true)} type='button'>Διαγραφή</button>):
              (<div className='delete-option'>
                <h4>Διαγραφή {client.full_name};</h4>
                <span className='delete-actions'>
                  <button className='danger-button' disabled={isDeleting} type='button' onClick={handleDelete}>ΝΑΙ</button>
                  <button disabled={isDeleting} type='button' onClick={()=>setConfirmDelete(false)}>ΟΧΙ</button>
                </span>
              </div>)}
          </div>
          {deleteError && <p  className='error-text'>{deleteError}</p>}
          {favError && <p  className='error-text'>{favError}</p>}
        </div>:
        <ClientEdit client={client} onSaved={onSaved} onCancel={onCancel}/>                
      }
    </div>
  )
}