import { Link } from "react-router-dom";

import { BarList } from "../components/BarList";
import { MatchCard } from "../components/MatchCard";
import { StatStrip, Versus } from "../components/StatStrip";
import { Status } from "../components/Status";
import { campaign as copy, competitionPt, playersList } from "../content/pt";
import { useCollection } from "../lib/data";
import { formatDecimal, formatInt, formatPercent } from "../lib/format";
import type { CollectionData } from "../types/data";
import styles from "./Campaign.module.css";

export function Campaign() {
  const state = useCollection();
  if (state.status !== "ready") return <Status state={state} />;
  return <CampaignView data={state.data} />;
}

function CampaignView({ data }: { data: CollectionData }) {
  const s = data.summary;
  const n = data.matches.length;
  const top = data.topPassers[0];
  const inTopPairs = data.topPairs.slice(0, 2).filter((p) => p.ids.includes(top.playerId)).length;
  // "Lateral-direito" -> "lateral-direito"; "Volante (dir.)" -> "volante"
  const role = top.position ? top.position.replace(/\s*\(.*\)$/, "") : null;
  const finding = copy.finding({ role, name: top.name, n: top.n, inTopPairs, matches: n });
  const maxPerGame = Math.max(...data.matches.flatMap((m) => [m.completed, m.opponentCompleted]));

  return (
    <div className={`container ${styles.page}`}>
      <header className={styles.header}>
        <nav aria-label="Trilha" className={styles.breadcrumb}>
          <Link to="/#projetos">{copy.breadcrumbProjects}</Link>
          <span aria-hidden="true">/</span>
          <span>{copy.breadcrumbProject}</span>
        </nav>
        <span className="eyebrow">{copy.eyebrow(competitionPt(data.competition), data.season, data.country)}</span>
        <h1 className={styles.title}>{copy.title(data.article, data.displayName, data.season)}</h1>
        <p className={styles.lead}>
          {finding.lead}
          <strong>{finding.name}</strong>
          {finding.tail}
        </p>
      </header>

      <StatStrip
        label={copy.summaryLabel}
        stats={[
          { value: copy.outOf(s.wins, s.played), label: copy.wins },
          { value: <Versus a={s.goalsFor} b={s.goalsAgainst} />, label: copy.goals },
          { value: formatInt(s.completed), label: copy.passes(formatPercent(s.completed, s.attempted)) },
          { value: <Versus a={formatDecimal(s.xgFor)} b={formatDecimal(s.xgAgainst)} />, label: copy.xg },
          { value: copy.outOf(s.morePassesThanOpponent, s.played), label: copy.morePasses },
        ]}
      />

      <section className={styles.section}>
        <div className={styles.sectionHead}>
          <h2 className={styles.h2}>{copy.gamesTitle(n)}</h2>
          <span className={styles.hint}>{copy.gamesHint}</span>
        </div>
        <div className={styles.cards}>
          {data.matches.map((m, i) => (
            <MatchCard key={m.id} match={m} collection={data} isLast={i === n - 1} />
          ))}
        </div>
      </section>

      <section className={styles.section}>
        <h2 className={styles.h2}>{copy.numbersTitle}</h2>
        <div className={styles.numbers}>
          <div className={styles.block}>
            <h3 className={styles.h3}>{copy.passersTitle}</h3>
            <BarList
              rows={data.topPassers.map((p) => ({ key: p.playerId, name: p.name, n: p.n, href: `/pnsm/1970/jogador/${p.slug}` }))}
              color={data.colors.line}
            />
            <p className={styles.note}>
              {copy.passersNote(
                n,
                data.topPassers.filter((p) => p.missed.length > 0).map((p) => ({ name: p.name, games: p.missed })),
              )}
            </p>
            <Link className={styles.more} to="/pnsm/1970/jogadores">
              {playersList.seeAll}
            </Link>
          </div>
          <div className={styles.block}>
            <h3 className={styles.h3}>{copy.pairsTitle}</h3>
            <BarList
              rows={data.topPairs.map((p) => ({ key: p.ids.join("-"), name: `${p.names[0]} – ${p.names[1]}`, n: p.n }))}
              color={data.colors.line}
            />
            <p className={styles.note}>{copy.pairsNote(n)}</p>
          </div>

          <div className={`${styles.block} ${styles.wide}`}>
            <div className={styles.perGameHead}>
              <h3 className={styles.h3}>{copy.perGameTitle}</h3>
              <div className={styles.legend}>
                <span>
                  <span className={styles.swatch} style={{ background: data.colors.line }} />
                  {data.displayName}
                </span>
                <span>
                  <span className={styles.swatch} style={{ background: "var(--text-faint)" }} />
                  {copy.opponent}
                </span>
              </div>
            </div>
            <ul className={styles.perGame}>
              {data.matches.map((m) => (
                <li key={m.id} className={styles.perGameRow}>
                  <span className={styles.perGameName}>{m.opponent}</span>
                  <div className={styles.perGameBars}>
                    <div className={styles.barLine}>
                      <span className={styles.bar} style={{ width: `${(80 * m.completed) / maxPerGame}%`, background: data.colors.line }} />
                      <span className={styles.barValue}>{m.completed}</span>
                    </div>
                    <div className={styles.barLine}>
                      <span className={styles.bar} style={{ width: `${(80 * m.opponentCompleted) / maxPerGame}%`, background: "var(--text-faint)" }} />
                      <span className={styles.barValueOpp}>{m.opponentCompleted}</span>
                    </div>
                  </div>
                </li>
              ))}
            </ul>
          </div>
        </div>
      </section>

      <section className={styles.method}>
        <p>{copy.methodText}</p>
        <Link to="/pnsm/metodologia" className="button button--secondary button--small">
          {copy.methodLink}
        </Link>
      </section>
    </div>
  );
}
