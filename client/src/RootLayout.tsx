import { Outlet } from "react-router";


export default function RootLayout(){

    return(
        <div className="app-shell">
            <h1 className="site-header">Δικηγορικό Γραφείο</h1>
            <Outlet/>
        </div>
    )
}