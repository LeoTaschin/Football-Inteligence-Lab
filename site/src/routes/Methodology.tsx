import { Link } from "react-router-dom";

import { competitionPt, links, methodology as copy, ofTeam } from "../content/pt";
import { useCollection, useIndex } from "../lib/data";
import styles from "./Methodology.module.css";

const SECTIONS = ["question", "data", "passes", "network", "validation", "limits", "reproduce", "attribution"] as const;

export function Methodology() {
  const collection = useCollection();
  const index = useIndex();
  const data = collection.status === "ready" ? collection.data : null;
  const ref = index.status === "ready" ? index.data.collections[0] : null;
  const final = data?.matches[data.matches.length - 1];
  const s = copy.sections;

  return (
    <div className={`container ${styles.page}`}>
      <header className={styles.header}>
        <nav aria-label="Trilha" className={styles.breadcrumb}>
          <Link to="/pnsm/1970">01 · PNSM</Link>
          <span aria-hidden="true">/</span>
          <span>{copy.breadcrumb}</span>
        </nav>
        <h1 className={styles.title}>{copy.title}</h1>
        <p className={styles.lead}>{copy.lead}</p>
      </header>

      <div className={styles.layout}>
        <nav className={styles.toc} aria-label={copy.toc}>
          <span className={styles.tocTitle}>{copy.toc}</span>
          {SECTIONS.map((k) => (
            <a key={k} href={`#${k}`}>
              {s[k]}
            </a>
          ))}
        </nav>

        <article className={styles.article}>
          <section id="question" className={styles.section}>
            <h2>{s.question}</h2>
            <p>{copy.question}</p>
          </section>

          <section id="data" className={styles.section}>
            <h2>{s.data}</h2>
            {data && ref && (
              <p>
                {copy.dataText(competitionPt(data.competition), data.season)}
                <span className="mono">{copy.dataIds(ref.competitionId, ref.seasonId)[0]}</span> e{" "}
                <span className="mono">{copy.dataIds(ref.competitionId, ref.seasonId)[1]}</span>
                {copy.dataTail}
              </p>
            )}
            {data && (
              <>
                <div className={styles.tableWrap}>
                  <table className={styles.table}>
                    <thead>
                      <tr>
                        <th>{copy.tableMatch}</th>
                        <th>match_id</th>
                        <th className={styles.num}>{copy.tableAttempted(ofTeam(data.article, data.displayName))}</th>
                        <th className={styles.num}>{copy.tableCompleted}</th>
                      </tr>
                    </thead>
                    <tbody>
                      {data.matches.map((m) => (
                        <tr key={m.id}>
                          <td>
                            <Link to={`/pnsm/1970/${m.id}`}>{copy.matchName(data.displayName, m.score[0], m.score[1], m.opponent)}</Link>
                          </td>
                          <td className="mono">{m.id}</td>
                          <td className={styles.num}>{m.attempted}</td>
                          <td className={`${styles.num} ${styles.strong}`}>{m.completed}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
                <p className={styles.small}>{copy.tableNote(ofTeam(data.article, data.displayName))}</p>
              </>
            )}
          </section>

          <section id="passes" className={styles.section}>
            <h2>{s.passes}</h2>
            <p>{copy.passesIntro}</p>
            <ul>
              {copy.passesRules.map((r) => (
                <li key={r}>{r}</li>
              ))}
            </ul>
            <p>{copy.passesOutro}</p>
          </section>

          <section id="network" className={styles.section}>
            <h2>{s.network}</h2>
            <div className={styles.cards}>
              {copy.networkCards.map(([title, text]) => (
                <div key={title} className={styles.card}>
                  <span className={styles.cardTitle}>{title}</span>
                  <span>{text}</span>
                </div>
              ))}
            </div>
          </section>

          <section id="validation" className={styles.section}>
            <h2>{s.validation}</h2>
            <p>{copy.validationIntro}</p>
            <ul>
              {copy.validationItems(final?.completed ?? 0).map((v) => (
                <li key={v}>{v}</li>
              ))}
            </ul>
            <p>{copy.validationTests}</p>
          </section>

          <section id="limits" className={styles.section}>
            <h2>{s.limits}</h2>
            <div className={styles.limits}>
              {copy.limits.map(([title, text]) => (
                <div key={title} className={styles.limit}>
                  <strong>{title}</strong> {text}
                </div>
              ))}
            </div>
          </section>

          <section id="reproduce" className={styles.section}>
            <h2>{s.reproduce}</h2>
            <p>{copy.reproduceText}</p>
            <div className={styles.pipeline} aria-label={copy.pipeline.join(" → ")}>
              {copy.pipeline.map((step) => (
                <span key={step} className={styles.stepGroup}>
                  <span className={styles.step}>{step}</span>
                  <span aria-hidden="true" className={styles.arrow}>
                    →
                  </span>
                </span>
              ))}
              <span className={`${styles.step} ${styles.stepEnd}`}>{copy.pipelineEnd}</span>
            </div>
            <pre className={styles.code}>{copy.commands(links.github ?? copy.repoPlaceholder)}</pre>
            {links.github && (
              <a href={links.github} className="button button--secondary button--small" target="_blank" rel="noopener">
                {copy.codeLink}
              </a>
            )}
          </section>

          <section id="attribution" className={`${styles.section} ${styles.attribution}`}>
            <h2>{s.attribution}</h2>
            <p>
              {copy.attribution} <a href={links.statsbomb}>github.com/statsbomb/open-data</a>
            </p>
          </section>
        </article>
      </div>
    </div>
  );
}
