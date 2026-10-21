import { Link } from "react-router-dom";

import { site } from "../content/pt";
import type { Loadable } from "../lib/data";

/** Loading / error placeholder for a page that waits on a JSON file. */
export function Status({ state }: { state: Exclude<Loadable<unknown>, { status: "ready" }> }) {
  return (
    <div className="container" style={{ padding: "64px var(--gutter)", minHeight: "50vh" }} role="status">
      {state.status === "loading" ? (
        <p style={{ color: "var(--text-muted)" }}>{site.loading}</p>
      ) : (
        <p>
          {site.loadError} <Link to="/">{site.notFoundBack}</Link>
        </p>
      )}
    </div>
  );
}

export function NotFound() {
  return (
    <div className="container" style={{ padding: "88px var(--gutter)", minHeight: "50vh", display: "grid", gap: 16 }}>
      <h1 style={{ fontSize: 40, fontWeight: 800, letterSpacing: "-0.02em" }}>{site.notFoundTitle}</h1>
      <Link to="/">{site.notFoundBack}</Link>
    </div>
  );
}
