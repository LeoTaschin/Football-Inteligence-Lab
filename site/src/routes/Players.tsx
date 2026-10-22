import { Link, useSearchParams } from "react-router-dom";

import { Status } from "../components/Status";
import layout from "../components/SplitLayout.module.css";
import { playersList as copy, site } from "../content/pt";
import { useCollection } from "../lib/data";
import { formatDecimal, formatInt, urlName } from "../lib/format";
import type { CollectionData, PlayerRef, PlayerTeam } from "../types/data";
import styles from "./Players.module.css";

type Sort = "passes" | "received" | "name";
const SORTS: Record<string, Sort> = { passes: "passes", recebidos: "received", nome: "name" };
const SORT_PARAM: Record<Sort, string | null> = { passes: null, received: "recebidos", name: "nome" };

export function Players() {
  const state = useCollection();
  if (state.status !== "ready") return <Status state={state} />;
  return <PlayersView data={state.data} />;
}

function PlayersView({ data }: { data: CollectionData }) {
  const [params, setParams] = useSearchParams();
  const teams = data.playerTeams;
  const ti = Math.max(0, teams.findIndex((t) => urlName(t.team) === params.get("equipe")));
  const sort = SORTS[params.get("ordem") ?? "passes"] ?? "passes";
  const team = teams[ti];
  const rows = sorted(data.players.filter((p) => p.teamName === team.teamName), sort);
  const max = Math.max(1, ...rows.map((r) => r.passes));
  const own = teams[0];

  const set = (changes: Record<string, string | null>) =>
    setParams(
      (prev) => {
        const next = new URLSearchParams(prev);
        for (const [k, v] of Object.entries(changes)) {
          if (v === null) next.delete(k);
          else next.set(k, v);
        }
        return next;
      },
      { replace: true, preventScrollReset: true },
    );

  return (
    <div className={`container ${styles.page}`}>
      <nav aria-label="Trilha" className={styles.breadcrumb}>
        <Link to="/pnsm/1970">{copy.breadcrumb}</Link>
        <span aria-hidden="true">/</span>
        <span>{copy.title}</span>
      </nav>

      <header className={styles.header}>
        <h1 className={styles.title}>{copy.title}</h1>
        <p className={styles.lead}>{copy.lead(data.players.length, own.players, own.article, own.team)}</p>
      </header>

      <div className={styles.teams} role="group" aria-label={copy.teamLabel}>
        {teams.map((t, i) => (
          <button
            key={t.teamName}
            type="button"
            className={`pill ${styles.teamPill}`}
            aria-pressed={i === ti}
            onClick={() => set({ equipe: i === 0 ? null : urlName(t.team) })}
          >
            <span className={styles.dot} style={{ background: t.colors.fill, borderColor: t.colors.line }} />
            {t.team}
          </button>
        ))}
      </div>

      <div className={layout.body}>
        <div className={layout.main}>
          <div className={styles.tableScroll}>
            <table className={styles.table}>
              <thead>
                <tr>
                  <th aria-hidden="true" />
                  <th>
                    <SortButton label={copy.columns.player} active={sort === "name"} arrow="↑" onClick={() => set({ ordem: SORT_PARAM.name })} />
                  </th>
                  <th className={styles.num}>{copy.columns.games}</th>
                  <th>
                    <SortButton label={copy.columns.passes} active={sort === "passes"} arrow="↓" onClick={() => set({ ordem: SORT_PARAM.passes })} />
                  </th>
                  <th className={styles.num}>
                    <SortButton label={copy.columns.received} active={sort === "received"} arrow="↓" onClick={() => set({ ordem: SORT_PARAM.received })} />
                  </th>
                  <th className={styles.num}>{copy.columns.share}</th>
                </tr>
              </thead>
              <tbody>
                {rows.map((p) => (
                  <tr key={p.playerId}>
                    <td>
                      <span className={styles.badge} style={{ background: team.colors.fill, color: team.colors.ink, borderColor: team.colors.line }}>
                        {p.num}
                      </span>
                    </td>
                    <td>
                      <Link className={styles.player} to={`/pnsm/1970/jogador/${p.slug}`} aria-label={copy.rowAria(p.name, p.passes)}>
                        <span className={styles.nameLine}>
                          <span className={styles.name}>{p.name}</span>
                          {p.substitute && <span className={styles.sub}>{copy.substitute}</span>}
                        </span>
                        <span className={styles.position}>{p.position}</span>
                      </Link>
                    </td>
                    <td className={styles.num}>{p.games}</td>
                    <td>
                      <span className={styles.barCell}>
                        <span className={styles.track} aria-hidden="true">
                          <span style={{ width: `${(100 * p.passes) / max}%`, background: team.colors.line }} />
                        </span>
                        <span className={styles.value}>{p.passes}</span>
                      </span>
                    </td>
                    <td className={styles.num}>{p.received}</td>
                    <td className={`${styles.num} ${styles.muted}`}>{p.share === null ? "–" : `${formatDecimal(p.share, 1)}%`}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          <p className={layout.caption}>{ti === 0 ? copy.noteOwn : copy.noteOpponent}</p>
        </div>

        <aside className={layout.aside}>
          <TeamSummary team={team} own={own} played={data.summary.played} players={rows} />
        </aside>
      </div>

      <footer className={styles.footer}>
        <p>{copy.footer}</p>
        <p className={styles.credit}>
          {site.attribution}
          <br />
          {site.author} · {site.name}
        </p>
      </footer>
    </div>
  );
}

function TeamSummary({ team, own, played, players }: { team: PlayerTeam; own: PlayerTeam; played: number; players: PlayerRef[] }) {
  const byId = new Map(players.map((p) => [p.playerId, p]));
  const passer = byId.get(team.topPasser)!;
  const receiver = byId.get(team.topReceiver)!;
  return (
    <>
      <div className={styles.summary}>
        <span className="eyebrow">{team.match ? copy.matchKicker(team.match.stage, team.match.order) : copy.ownKicker}</span>
        <span className={styles.summaryTitle}>
          {team.match ? copy.matchTitle(own.team, team.match.score, team.team) : copy.ownTitle(team.team, played)}
        </span>
        <span className={layout.summaryText}>
          {team.match
            ? copy.matchText(team.players, team.article, team.team, team.completed)
            : copy.ownText(team.players, formatInt(team.completed))}
        </span>
      </div>
      <div className={styles.highlights}>
        <Highlight team={team} label={copy.topPasser} player={passer} value={passer.passes} />
        <Highlight team={team} label={copy.topReceiver} player={receiver} value={receiver.received} />
        {team.allGames !== null && (
          <div className={styles.highlight}>
            <span className={styles.badge}>{played}</span>
            <span className={styles.hlText}>
              <span className={styles.hlLabel}>{copy.allGames(played)}</span>
              <span className={styles.hlName}>{copy.allGamesValue(team.allGames)}</span>
            </span>
          </div>
        )}
      </div>
      {team.match && (
        <Link className={styles.button} to={`/pnsm/1970/${team.match.id}?equipe=2`}>
          {copy.openMatch}
        </Link>
      )}
    </>
  );
}

function Highlight({ team, label, player, value }: { team: PlayerTeam; label: string; player: PlayerRef; value: number }) {
  return (
    <Link className={styles.highlight} to={`/pnsm/1970/jogador/${player.slug}`}>
      <span className={styles.badge} style={{ background: team.colors.fill, color: team.colors.ink, borderColor: team.colors.line }}>
        {player.num}
      </span>
      <span className={styles.hlText}>
        <span className={styles.hlLabel}>{label}</span>
        <span className={styles.hlName}>{player.name}</span>
      </span>
      <span className={styles.hlValue}>{value}</span>
    </Link>
  );
}

function SortButton({ label, active, arrow, onClick }: { label: string; active: boolean; arrow: string; onClick: () => void }) {
  return (
    <button type="button" className={styles.sort} aria-pressed={active} onClick={onClick}>
      {label}
      {active ? ` ${arrow}` : ""}
    </button>
  );
}

function sorted(rows: PlayerRef[], sort: Sort): PlayerRef[] {
  const out = [...rows];
  if (sort === "name") out.sort((a, b) => a.name.localeCompare(b.name, "pt"));
  else if (sort === "received") out.sort((a, b) => b.received - a.received || a.playerId - b.playerId);
  // "passes": the engine already sends them most passes first
  return out;
}
