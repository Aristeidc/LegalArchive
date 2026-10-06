import {createBrowserRouter, Navigate, type LoaderFunctionArgs } from "react-router";
import RootLayout from "./RootLayout";
import ClientsPage from "./ClientsPage";
import ClientInfo from "./components/ClientInfo";
import ClientAdd from "./components/ClientAdd";
import EmptyPanel from "./components/EmptyPanel";
import ClientError from "./components/ClientError";

export const router = createBrowserRouter([
    {
        path: "/",
        Component: RootLayout,
        HydrateFallback: () => <p>Φόρτωση…</p>,
        children: [
            {
                path: "clients",
                Component:ClientsPage,
                children:[
                    {
                        path: ":id",
                        Component: ClientInfo,
                        loader: clientLoader,
                        ErrorBoundary:ClientError
                    },
                    {
                        path: "new",
                        Component: ClientAdd,
                    },
                    {
                        index: true,
                        Component: EmptyPanel
                    }
                ]
            },
            {
                index:true,
                element: <Navigate to="/clients" replace />
            }
        ]
    }
])

async function clientLoader({params, request}:LoaderFunctionArgs) {
    const url= `http://localhost:8000/clients/${params.id}`

    const response = await fetch(url,{signal:request.signal});

    if(!response.ok) throw new Response("Not Found", {status:response.status});

    return response.json();
}
