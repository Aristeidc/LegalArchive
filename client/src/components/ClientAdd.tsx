import { useState, type ChangeEvent, useRef } from "react"
import { type ClientForm, type ClientCreate} from "../types"
import { useOutletContext, Link } from "react-router";
import { useEnterArming } from "../hooks/useEnterArming";

const EMPTY_FORM: ClientForm ={
        full_name: "",
        phone: "",
        email: "",
        afm: "",
        address: "",
        notes: "",
};

export default function ClientAdd(){

    const [newClient,setNewClient] = useState(EMPTY_FORM);
    const [error,setError] = useState<string | null>(null);
    const [isSubmitting, setIsSubmitting] = useState<boolean>(false);
    const nameInputRef = useRef<HTMLInputElement>(null);
    const [success, setSuccess] = useState<boolean>(false);
    const refreshList = useOutletContext<() => void>();
    const {submitRef,handleKeyDown} = useEnterArming();

    function handleChange(event:ChangeEvent<HTMLInputElement | HTMLTextAreaElement>){
        const {name, value} = event.target;
        setNewClient(prev => ({...prev, [name]:value}))
        setSuccess(false);
    }

    async function handleSubmit(event:React.SubmitEvent<HTMLFormElement>){
        event.preventDefault()
        setIsSubmitting(true)
        setError(null)

        const cleaned= Object.fromEntries(
            Object.entries(newClient).map(([key,value]) => [key, value.trim() || null])
        )
        const payload = {...cleaned, full_name: newClient.full_name.trim()} as ClientCreate

        const url = 'http://localhost:8000/clients'
        try{
            const response = await fetch(url,{
                method: "POST",
                headers: {"Content-Type": "application/json"},
                body: JSON.stringify(payload)
            })
            
            if (!response.ok){
                throw new Error ('Failed to Post!'); 
            }
            
            setNewClient(EMPTY_FORM);
            // After a successful create, move keyboard focus back to the name field
            // so the next client can be typed straight away (supports bulk entry).
            nameInputRef.current?.focus();
            setSuccess(true);
            refreshList();
            
        }catch (err){
        setError('Η προσθήκη του πελάτη απέτυχε.')
        console.error(err)
        }finally{
            setIsSubmitting(false)
        }    
    }

    return(
        <div className="client-card">
            <div className="card-top">
                <Link to="/clients" className='close-button link-button icon-button' aria-label="Κλείσιμο" title="Κλείσιμο">&#10006;</Link>
            </div>
            <form onSubmit={handleSubmit} onKeyDown={handleKeyDown} className="add-form">
                <div className="form-field">   
                    <label htmlFor="full_name">Ονοματεπώνυμο:</label>
                    <input ref={nameInputRef} id="full_name" type="text" name="full_name" value={newClient.full_name} onChange={handleChange} required pattern=".*\S.*" aria-describedby="add-name-hint"/>
                    <small className='field-hint' id="add-name-hint">
                        Επώνυμο, όνομα, και μετά πατρώνυμο ή άλλα ονόματα — π.χ. Παπαδόπουλος Γιώργος Νικολάου
                    </small>
                </div>
                <div className="form-field">
                    <label htmlFor="phone">Τηλέφωνο:</label>
                    <input id="phone" type="text" name="phone" value={newClient.phone} onChange={handleChange}/>
                </div>
                <div className="form-field">                          
                    <label htmlFor="afm">ΑΦΜ:</label>
                    <input id="afm" type="text" name="afm" value={newClient.afm} onChange={handleChange}/>
                </div>
                <div className="form-field">    
                    <label htmlFor="address">Διεύθυνση:</label>
                    <input id="address" type="text" name="address" value={newClient.address} onChange={handleChange}/>
                </div>
                <div className="form-field">    
                    <label htmlFor="email">Email:</label>
                    <input id="email" type="text" name="email" value={newClient.email} onChange={handleChange}/>
                </div>
                <div className="form-field">    
                    <label htmlFor="notes">Σημειώσεις:</label>
                    <textarea id="notes" name="notes" value={newClient.notes} onChange={handleChange}/>
                </div>
                <div className="form-actions">    
                    <button disabled={isSubmitting} ref={submitRef}>Προσθήκη</button>
                    {error && <p className='error-text'>{error}</p> }
                    {success && <p>Ο πελάτης προστέθηκε</p>}
                </div>
            </form>
            
        </div>
    )
}