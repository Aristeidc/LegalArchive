import { Link, useParams } from "react-router"
import { type ClientListProps } from "../types"
import gStar from "../assets/star-gold.png"

export default function ClientList({clients }:ClientListProps) {

    const {id}=useParams();   

    return(
        <div className='client-catalog'>
        <h2>Κατάλογος Πελατών</h2>
        {clients.length > 0 ?(
            <ul className='client-list'>
                {clients.map((client)=>{
                    const isOpen = String(client.client_id) === id;
                    return(
                        <li className="client-row" key={client.client_id} >
                            <Link 
                                to={!isOpen ?(`/clients/${client.client_id}`):("/clients")}  
                                className="client-link"
                                aria-current={isOpen ? "page" : undefined}
                            >
                                {client.full_name}
                                {client.is_favorite && <img src={gStar} alt="Αγαπημένος" className="fav-star"/>}                    
                            </Link> 
                        </li>
                    );   
                })}
            </ul>
            ):(
            <p className="empty-state">Δεν βρέθηκαν πελάτες.</p>
        )}
        </div>
    )
}