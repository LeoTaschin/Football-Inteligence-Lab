import { Link } from "react-router-dom";

import { MiniNetwork } from "../components/MiniNetwork";
import { home as copy, links } from "../content/pt";
import { useCollection } from "../lib/data";
import { formatInt } from "../lib/format";
import styles from "./Home.module.css";

export function Home() {
  const collection = useCollection();
  const data = collection.status === "ready" ? collection.data : null;
  const featured = data ? data.matches[data.matches.length - 1] : null;

  return (
    <div className={`container ${styles.page}`}>
      <header className={styles.hero}>
        <span className="eyebrow">{copy.eyebrow}</span>
        <h1 className={styles.title}>{copy.title}</h1>
        <p className={styles.lead}>{copy.lead}</p>
        <div className={styles.ctas}>
          <Link to="/pnsm/1970" className="button button--primary">
            {copy.ctaProject}
          </Link>
          <a href="#projetos" className="button button--secondary">
            {copy.ctaAll}
          </a>
        </div>
      </header>

      <section className={styles.section}>
        <div className={styles.featuredHead}>
          <h2 className="eyebrow">{copy.featured}</h2>
          <span className={styles.live}>
            <span className={styles.liveDot} />
            {copy.live}
          </span>
        </div>
        <Link to="/pnsm/1970" className={styles.featured}>
          <div className={styles.featuredText}>
            <span className={styles.kicker}>{copy.featuredKicker}</span>
            <span className={styles.featuredTitle}>
              {data ? copy.featuredTitle(data.article, data.displayName, data.season) : copy.featuredKicker}
            </span>
            <span className={styles.featuredLead}>{copy.featuredText(data?.summary.played ?? 6)}</span>
            {data && (
              <div className={styles.featuredStats}>
                <Stat value={String(data.summary.played)} label={copy.statMatches} />
                <Stat value={formatInt(data.summary.completed)} label={copy.statPasses} />
                <Stat value={String(data.summary.goalsFor)} label={copy.statGoals} />
              </div>
            )}
            <span className={styles.explore}>{copy.explore}</span>
          </div>
          <div className={styles.featuredPitch}>
            {data && featured && (
              <MiniNetwork data={featured.mini} colors={data.colors} scale={data.scale} referenceWidth={420} showNumbers />
            )}
          </div>
        </Link>
      </section>

      <section id="projetos" className={styles.section}>
        <div className={styles.sectionIntro}>
          <h2 className={styles.h2}>{copy.projectsTitle}</h2>
          <p className={styles.sectionLead}>{copy.projectsLead}</p>
        </div>
        <ol className={styles.projects}>
          {copy.projects.map((p) => (
            <li key={p.num} className={styles.project}>
              <span className={styles.projectNum}>{p.num}</span>
              <div className={styles.projectText}>
                {p.live ? (
                  <Link to="/pnsm/1970" className={styles.projectTitle}>
                    {p.title}
                  </Link>
                ) : (
                  <span className={styles.projectTitle}>{p.title}</span>
                )}
                <span className={styles.projectDesc}>{p.desc}</span>
              </div>
              <span className={`${styles.status} ${p.live ? styles.statusLive : ""}`}>{p.live ? copy.live : copy.soon}</span>
            </li>
          ))}
        </ol>
      </section>

      <section id="sobre" className={styles.about}>
        <h2 className={styles.h2}>{copy.aboutTitle}</h2>
        <div className={styles.aboutBody}>
          <p>{copy.about}</p>
          <div className={styles.aboutLinks}>
            <a href={links.linkedin} className="button button--secondary button--small" rel="me noopener" target="_blank">
              {copy.linkedin}
            </a>
            {links.github ? (
              <a href={links.github} className="button button--secondary button--small" rel="me noopener" target="_blank">
                {copy.github}
              </a>
            ) : (
              <span className={styles.pending}>
                {copy.github} · {copy.pending}
              </span>
            )}
            {links.email ? (
              <a href={`mailto:${links.email}`} className="button button--secondary button--small">
                {copy.email}
              </a>
            ) : (
              <span className={styles.pending}>
                {copy.email} · {copy.pending}
              </span>
            )}
          </div>
        </div>
      </section>
    </div>
  );
}

function Stat({ value, label }: { value: string; label: string }) {
  return (
    <div className={styles.stat}>
      <span className={styles.statValue}>{value}</span>
      <span className={styles.statLabel}>{label}</span>
    </div>
  );
}
