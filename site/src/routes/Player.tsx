import { Link, useNavigate, useParams, useSearchParams } from "react-router-dom";

import { BarList } from "../components/BarList";
import { MiniNetwork } from "../components/MiniNetwork";
import { PassNetwork } from "../components/PassNetwork";
import { Status } from "../components/Status";
import layout from "../components/SplitLayout.module.css";
import { player as copy, site } from "../content/pt";
import { useCollection, useMatch, usePlayer } from "../lib/data";
import { formatDecimal } from "../lib/format";
import { networkOf } from "../lib/network";
import type { PlayerGame, PlayerPage, PlayerRef } from "../types/data";
import styles from "./Player.module.css";

const MIN_PAIR = 3;
const INCOMING = "#52525B";
const OTHERS = 8;

export function Player() {
  const { slug } = useParams();
  const state = usePlayer(slug ?? null);
  const collection = useCollection();
  if (state.status !== "ready") return <Status state={state} />;
  const players = collection.status === "ready" ? collection.data.players : [];
  return <PlayerView key={slug} data={state.data} players={players} />;
}

/** View and game live in the URL (?visao=todos, ?jogo=6; ?partida=<matchId> from another page) so a post can link to them. */
function usePlayerParams(data: PlayerPage) {
  const [params, setParams] = useSearchParams();
  const all = params.get("visao") === "todos";
  const g = Number(params.get("jogo"));
  const byMatch = data.games.findIndex((x) => x.matchId === Number(params.get("partida")));
  const game = byMatch >= 0 ? byMatch : Number.isInteger(g) && g >= 1 && g <= data.games.length ? g - 1 : data.games.length - 1;
  const update = (changes: Record<string, string | null>) =>
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
  return {
    all,
    game,
    setAll: (on: boolean) => update({ visao: on ? "todos" : null }),
    openGame: (i: number) => update({ visao: null, partida: null, jogo: String(i + 1) }),
  };
}

function PlayerView({ data, players }: { data: PlayerPage; players: PlayerRef[] }) {
  const { all, game, setAll, openGame } = usePlayerParams(data);
  const s = data.summary;
  const g = data.games[game];
  const single = s.games === 1;
  const share = s.share === null ? null : `${formatDecimal(s.share, 1)}%`;
  const shortOf = (x: PlayerGame) => copy.gameShort(x.stage, x.order, x.opponent);
  const others = players.filter((p) => p.teamName === data.teamName && p.playerId !== data.playerId).slice(0, OTHERS);

  return (
    <div className={`container ${styles.page}`}>
      <nav aria-label="Trilha" className={styles.breadcrumb}>
        <Link to="/pnsm/1970">{copy.breadcrumb}</Link>
        <span aria-hidden="true">/</span>
        <span>{data.name}</span>
      </nav>

      <header className={styles.header}>
        <div className={styles.who}>
          <span className={styles.badge} style={{ background: data.colors.fill, color: data.colors.ink, borderColor: data.colors.line }}>
            {data.num}
          </span>
          <div className={styles.names}>
            <h1 className={styles.name}>{data.name}</h1>
            <span className={styles.sub}>{copy.sub(data.position, data.team, s.games)}</span>
          </div>
        </div>
        <p className={styles.lead}>
          {copy.lead({
            name: data.name,
            article: data.article,
            team: data.team,
            games: s.games,
            teamRank: s.teamRank,
            passes: s.passes,
            share,
            to: data.to[0] ?? null,
            from: data.from[0] ?? null,
            avgShift: s.avgShift,
            opponent: { article: data.games[0].opponentArticle, name: data.games[0].opponent },
            stage: data.games[0].stage,
            rankInGame: data.games[0].rank,
          })}
        </p>
        {single && <p className={styles.notice}>{copy.single}</p>}
      </header>

      <div className={styles.stats}>
        <Stat value={String(s.passes)} label={copy.stats.passes(s.teamRank)} />
        <Stat value={String(s.received)} label={copy.stats.received} />
        <Stat value={share ?? "–"} label={copy.stats.share(data.article, data.team)} />
        <Stat value={`${s.topPasserGames} de ${s.games}`} label={copy.stats.topPasser(s.games)} />
        <Stat value={s.avgShift === null ? "–" : copy.meters(s.avgShift)} label={copy.stats.shift} />
      </div>

      <div className={layout.body}>
        <div className={layout.main}>
          <div className={styles.gamesHead}>
            <h2 className={styles.h2}>{copy.gamesTitle}</h2>
            <div className={styles.segmented} role="group" aria-label={copy.viewLabel}>
              <button type="button" aria-pressed={!all} onClick={() => setAll(false)}>
                {copy.views.one}
              </button>
              <button type="button" aria-pressed={all} onClick={() => setAll(true)}>
                {copy.views.all}
              </button>
            </div>
          </div>
          <p className={layout.caption}>{all ? copy.viewNoteAll(data.name) : copy.viewNoteOne(data.name)}</p>

          {all ? (
            <div className={styles.grid}>
              {data.games.map((x, i) => (
                <button key={x.matchId} type="button" className={styles.card} onClick={() => openGame(i)} aria-label={copy.openGameAria(data.name, shortOf(x))}>
                  <span className={styles.cardHead}>
                    <span className="eyebrow">{copy.cardKicker(x.stage, x.order)}</span>
                    <span className={styles.cardScore}>{`${x.score[0]} × ${x.score[1]}`}</span>
                  </span>
                  <span className={styles.cardOpp}>× {x.opponent}</span>
                  <MiniNetwork data={x.mini} colors={data.colors} scale={data.scale} referenceWidth={260} highlightId={data.playerId} />
                  <span className={styles.cardStats}>
                    <Stat value={String(x.passes)} label={copy.gameStats.passes} small />
                    <Stat value={String(x.received)} label={copy.gameStats.received} small />
                    <Stat value={`${x.rank}º`} label={copy.gameStats.rank} small />
                  </span>
                  {x.partner && <span className={styles.cardPartner}>{copy.partnerShort(x.partner.name, x.partner.n)}</span>}
                </button>
              ))}
            </div>
          ) : (
            <>
              <div className={styles.pills} role="group" aria-label={copy.gameLabel}>
                {data.games.map((x, i) => (
                  <button key={x.matchId} type="button" className="pill" aria-pressed={i === game} onClick={() => openGame(i)}>
                    {shortOf(x)}
                  </button>
                ))}
              </div>
              <GameNetwork data={data} game={g} players={players} />
            </>
          )}

          <section className={styles.phases}>
            <div className={styles.gamesHead}>
              <h2 className={styles.h2}>{copy.phasesTitle}</h2>
              <span className={layout.caption}>{copy.phasesHint}</span>
            </div>
            {data.games.map((x, i) => (
              <button key={x.matchId} type="button" className={styles.phaseRow} aria-pressed={!all && i === game} onClick={() => openGame(i)}>
                <span className={styles.phaseLabel}>{shortOf(x)}</span>
                <span className={styles.phaseTrack} aria-hidden="true">
                  <span className={styles.phaseMid} />
                  {x.def && (
                    <span
                      className={styles.phaseSpan}
                      style={{
                        left: `${(Math.min(x.ball.x, x.def.x) / 120) * 100}%`,
                        width: `${(Math.abs(x.ball.x - x.def.x) / 120) * 100}%`,
                        background: data.colors.line,
                      }}
                    />
                  )}
                  {x.def && <span className={styles.phaseDef} style={{ left: `${(x.def.x / 120) * 100}%` }} />}
                  <span className={styles.phaseBall} style={{ left: `${(x.ball.x / 120) * 100}%`, background: data.colors.fill, borderColor: data.colors.line }} />
                </span>
                <span className={styles.phaseShift}>{x.shift === null ? "–" : copy.meters(x.shift)}</span>
              </button>
            ))}
            <p className={layout.caption}>{copy.phasesNote}</p>
          </section>
        </div>

        <aside className={layout.aside}>
          <section className={styles.gameCard} aria-live="polite">
            <div className={styles.gameCardHead}>
              <span className="eyebrow">{copy.gameKicker(g.stage, g.order)}</span>
              <span className={styles.gameTitle}>{copy.gameTitle(data.team, g.score, g.opponent)}</span>
            </div>
            <div className={styles.gameStats}>
              <Stat value={String(g.passes)} label={copy.gameStats.passes} />
              <Stat value={String(g.received)} label={copy.gameStats.received} />
              <Stat value={`${g.rank}º`} label={copy.gameStats.rank} />
            </div>
            {g.partner && <p className={styles.text}>{copy.partner(g.partner.name, g.partner.n)}</p>}
            {g.sub && <p className={styles.chip}>{g.sub.type === "in" ? copy.subIn(g.sub.minute) : copy.subOut(g.sub.minute)}</p>}
            <Link className={styles.button} to={`/pnsm/1970/${g.matchId}?jogador=${data.playerId}`}>
              {copy.openMatch}
            </Link>
          </section>

          <section className={styles.with}>
            <div>
              <h2 className={styles.asideTitle}>{copy.withTitle}</h2>
              <span className={layout.caption}>{copy.withNote(s.games)}</span>
            </div>
            <div className={styles.withList}>
              <h3 className={styles.listTitle}>{copy.passedTo}</h3>
              <BarList
                rows={data.to.map((p) => ({ key: p.playerId, name: p.name, n: p.n, href: `/pnsm/1970/jogador/${p.slug}` }))}
                color={data.colors.line}
                max={Math.max(data.to[0]?.n ?? 1, data.from[0]?.n ?? 1)}
              />
            </div>
            <div className={styles.withList}>
              <h3 className={styles.listTitle}>{copy.receivedFrom}</h3>
              <BarList
                rows={data.from.map((p) => ({ key: p.playerId, name: p.name, n: p.n, href: `/pnsm/1970/jogador/${p.slug}` }))}
                color={INCOMING}
                max={Math.max(data.to[0]?.n ?? 1, data.from[0]?.n ?? 1)}
              />
            </div>
          </section>

          {others.length > 0 && (
            <section className={styles.others}>
              <h2 className={styles.asideTitle}>{copy.othersTitle}</h2>
              <div className={styles.chips}>
                {others.map((p) => (
                  <Link key={p.playerId} className="pill" to={`/pnsm/1970/jogador/${p.slug}`}>
                    {p.name}
                  </Link>
                ))}
              </div>
              <span className={layout.caption}>{copy.othersNote}</span>
            </section>
          )}
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

/** The selected game's full network (from the match file), the player selected, his "sem bola" ghost. */
function GameNetwork({ data, game, players }: { data: PlayerPage; game: PlayerGame; players: PlayerRef[] }) {
  const match = useMatch(game.matchId);
  const navigate = useNavigate();
  if (match.status !== "ready") return <Status state={match} />;
  const team = match.data.teams.find((t) => t.teamId === data.teamId)!;
  const slugOf = new Map(players.map((p) => [p.playerId, p.slug]));
  const open = (pid: number) => {
    const slug = slugOf.get(pid);
    // the other player's page opens on this same match
    if (slug && pid !== data.playerId) navigate(`/pnsm/1970/jogador/${slug}?partida=${game.matchId}`);
  };
  return (
    <>
      <div className={styles.pitchScroll}>
        <div className={styles.pitchBox}>
          <PassNetwork
            team={team}
            net={networkOf(team, "full")}
            scale={match.data.scale}
            minPasses={MIN_PAIR}
            selectedId={data.playerId}
            onSelect={open}
            ghost={game.def}
          />
        </div>
      </div>
      <ul className={layout.legend} aria-label="Legenda">
        <li>
          <Arrow color={data.colors.line} />
          {copy.legendGiven}
        </li>
        <li>
          <Arrow color={INCOMING} />
          {copy.legendReceived}
        </li>
        <li>
          <span className={styles.ghostSwatch} />
          {copy.legendGhost}
        </li>
      </ul>
    </>
  );
}

function Stat({ value, label, small = false }: { value: string; label: string; small?: boolean }) {
  return (
    <span className={small ? styles.statSmall : styles.stat}>
      <span className={styles.statValue}>{value}</span>
      <span className={styles.statLabel}>{label}</span>
    </span>
  );
}

function Arrow({ color }: { color: string }) {
  return (
    <svg width="30" height="10" viewBox="0 0 30 10" aria-hidden="true">
      <path d="M1 4h20V1l8 4-8 4V6H1z" fill={color} />
    </svg>
  );
}
