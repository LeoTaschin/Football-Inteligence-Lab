import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import { createBrowserRouter, RouterProvider } from "react-router-dom";

import { Layout } from "./components/Layout";
import { NotFound } from "./components/Status";
import { Campaign } from "./routes/Campaign";
import { Home } from "./routes/Home";
import { Match } from "./routes/Match";
import { Methodology } from "./routes/Methodology";
import { Player } from "./routes/Player";
import { Players } from "./routes/Players";
import "./styles/global.css";

const router = createBrowserRouter([
  {
    element: <Layout />,
    children: [
      { path: "/", element: <Home /> },
      { path: "/pnsm/1970", element: <Campaign /> },
      { path: "/pnsm/1970/:matchId", element: <Match /> },
      { path: "/pnsm/1970/jogadores", element: <Players /> },
      { path: "/pnsm/1970/jogador/:slug", element: <Player /> },
      { path: "/pnsm/metodologia", element: <Methodology /> },
      { path: "*", element: <NotFound /> },
    ],
  },
]);

createRoot(document.getElementById("root")!).render(
  <StrictMode>
    <RouterProvider router={router} />
  </StrictMode>,
);
