import { useRouteError, isRouteErrorResponse, Link } from "react-router";


export default function ClientError(){

    const error = useRouteError();

    const notFound = isRouteErrorResponse(error) && error.status === 404;
    
    return(
        <div className="client-card">
            <div className="card-top">
                <Link to="/clients" className="link-button close-button icon-button"
                    aria-label="Κλείσιμο" title="Κλείσιμο">&#10006;</Link>
            </div>
            <p className="empty-state">
                {notFound ? "Ο πελάτης δεν βρέθηκε." : "Η φόρτωση του πελάτη απέτυχε."}
            </p>
        </div>
    )
}