import { Link, useLocation } from "react-router-dom";

import { nav, site } from "../content/pt";
import styles from "./AppNav.module.css";

const ITEMS = [
  { to: "/#projetos", label: nav.projects, match: null },
  { to: "/pnsm/1970", label: nav.campaign, match: "/pnsm/1970" },
  { to: "/pnsm/metodologia", label: nav.methodology, match: "/pnsm/metodologia" },
  { to: "/#sobre", label: nav.about, match: null },
];

export function AppNav() {
  const { pathname } = useLocation();
  return (
    <nav className={styles.nav} aria-label={nav.label}>
      <div className={`container ${styles.inner}`}>
        <Link to="/" className={styles.brand}>
          {site.name}
        </Link>
        <div className={styles.links}>
          {ITEMS.map((item) => {
            const current = item.match !== null && pathname.startsWith(item.match);
            return (
              <Link key={item.to} to={item.to} aria-current={current ? "page" : undefined}>
                {item.label}
              </Link>
            );
          })}
        </div>
      </div>
    </nav>
  );
}
