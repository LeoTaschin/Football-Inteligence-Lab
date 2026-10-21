import { useEffect } from "react";
import { Outlet, ScrollRestoration, useLocation } from "react-router-dom";

import { AppNav } from "./AppNav";
import { SiteFooter } from "./SiteFooter";

/** Scrolls to `#id` after navigation (router links like "/#projetos"). */
function ScrollToHash() {
  const { hash, pathname } = useLocation();
  useEffect(() => {
    if (!hash) return;
    document.getElementById(decodeURIComponent(hash.slice(1)))?.scrollIntoView();
  }, [hash, pathname]);
  return null;
}

export function Layout() {
  return (
    <>
      <AppNav />
      <main>
        <Outlet />
      </main>
      <SiteFooter />
      <ScrollRestoration />
      <ScrollToHash />
    </>
  );
}
