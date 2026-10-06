import { useState, type ChangeEvent } from 'react'
import {type ClientForm, type ClientUpdate, type ClientUpdateProps } from "../types";
import { useEnterArming } from '../hooks/useEnterArming';

export default function ClientEdit({client,onSaved,onCancel}: ClientUpdateProps){

    
  // -------------------UPDATE----------------------//
  const [updatedClient,setUpdatedClient] = useState<ClientForm>({
      full_name : client.full_name,
      phone :client.phone ?? "",
      afm: client.afm ?? "",
      address: client.address ?? "",
      email: client.email ?? "",
      notes: client.notes ?? "",
  });
  const [upError,setUpError] = useState<string | null>(null);
  const [isUpdating,setIsUpdating] = useState<boolean>(false);
  const url = `http://localhost:8000/clients/${client.client_id}`

  const{submitRef,handleKeyDown} = useEnterArming();


  function handleChange(event:ChangeEvent<HTMLInputElement | HTMLTextAreaElement>){
  const {name,value}=event.target;
  setUpdatedClient(prev => ({...prev,[name]:value}))
  }

  async function handleSubmit(event:React.SubmitEvent<HTMLFormElement>){
  event.preventDefault();
  setUpError(null);

  
  //clean updated client and compare for actual changes
  const payload:ClientUpdate={}
  const newName = updatedClient.full_name.trim();
  if(newName!== client.full_name) payload.full_name = newName;
  const newPhone = updatedClient.phone.trim() || null;
  if (newPhone!==client.phone) payload.phone = newPhone;
  const newafm = updatedClient.afm.trim() || null;
  if (newafm!==client.afm) payload.afm = newafm;
  const newAddress = updatedClient.address.trim() || null;
  if (newAddress!==client.address) payload.address = newAddress;
  const newEmail = updatedClient.email.trim() || null;
  if (newEmail!==client.email) payload.email = newEmail;
  const newNotes = updatedClient.notes.trim() || null;
  if (newNotes!==client.notes) payload.notes = newNotes;

  if (Object.keys(payload).length===0) {
    onCancel();
    return;
  }
  setIsUpdating(true);
  
  try{
    const response = await fetch(url,{
    method: "PATCH",
    headers: {"Content-Type": "application/json"},
    body: JSON.stringify(payload)
    })

    if (!response.ok) throw new Error('Failed PATCH!')
    
    //refresh client
    onSaved();

  }catch(err){
    setUpError('Η αποθήκευση των αλλαγών απέτυχε.')
    console.error(err)
  }finally{
    setIsUpdating(false)
  }
  }

  return(
    <div>
      <form onSubmit={handleSubmit}  onKeyDown={handleKeyDown}>
        <dl className='client-details'>
          <dt> <label htmlFor="edit-name">Ονοματεπώνυμο</label></dt>
          <dd>
            <input id='edit-name' type="text" name="full_name" value={updatedClient.full_name} onChange={handleChange} aria-describedby="edit-name-hint"/>
            <small className='field-hint' id="edit-name-hint">
              Επώνυμο, όνομα, και μετά πατρώνυμο ή άλλα ονόματα — π.χ. Παπαδόπουλος Γιώργος Νικολάου
            </small>
          </dd>
          
          <dt><label htmlFor="edit-phone">Τηλέφωνο</label></dt>
          <dd>
            <input id='edit-phone' type="text" name="phone" value={updatedClient.phone} onChange={handleChange}/>
          </dd>
          
          <dt><label htmlFor="edit-afm">ΑΦΜ</label></dt>
          <dd>
            <input id='edit-afm' type="text" name="afm" value={updatedClient.afm} onChange={handleChange}/>
          </dd>

          <dt><label htmlFor="edit-address">Διεύθυνση</label></dt>
          <dd>
            <input id='edit-address' type="text" name="address" value={updatedClient.address} onChange={handleChange}/>
          </dd>

          <dt><label htmlFor="edit-email">Email</label></dt>
          <dd>
            <input id='edit-email' type="text" name="email" value={updatedClient.email} onChange={handleChange}/>
          </dd>

          <dt><label htmlFor="edit-notes">Σημειώσεις</label></dt>
          <dd>
            <textarea id='edit-notes' name="notes" value={updatedClient.notes} onChange={handleChange}/>
          </dd>
        </dl>
        <div className='form-actions'>
          <button className='save-button' disabled={isUpdating} ref={submitRef}>Αποθήκευση</button>
          <button className='cancel-button' type='button' onClick={onCancel}>Άκυρο</button>
          {upError && <p className='error-text'>{upError}</p>}
        </div>
      </form>
    </div>    
  )
}