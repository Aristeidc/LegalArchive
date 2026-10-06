//custom hook for arming save buttons instead of saving outright

import { useRef, type KeyboardEvent } from "react";

export function useEnterArming(){

    const submitRef = useRef<HTMLButtonElement>(null);

    function handleKeyDown(event:KeyboardEvent<HTMLFormElement>){
        
        if(event.key==="Enter"){
            if (event.target === submitRef.current) return;
            if (event.target instanceof HTMLTextAreaElement) return;
            event.preventDefault();
            submitRef.current?.focus();
        }
    }
    return{submitRef,handleKeyDown};
}   
