import { type ClientSearchProps } from "../types"
import { useState, type ChangeEvent } from "react"
import React from "react"
export default function ClientSearch({onSearch}:ClientSearchProps){

    const [newSearch,setNewSearch] = useState<string >("")

    function handleChange(event:ChangeEvent<HTMLInputElement>){
        setNewSearch(event.target.value)
    }

    function handleSubmit(event:React.SubmitEvent<HTMLFormElement>){
        event.preventDefault()
        const trimmed= newSearch.trim()
        onSearch(trimmed)
    }

    return(
        <div>
            <form className="search-form" onSubmit={handleSubmit}>     
                <input className="search-input" type="text" placeholder="Αναζήτηση..." value={newSearch} onChange={handleChange}/>
                <button >Αναζήτηση</button>
                <button className="clear-search" type="button" onClick={()=>{setNewSearch(""); onSearch("");}}>Καθαρισμός</button>
            </form>
        </div>
    )
}