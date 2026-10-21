import { Link } from "react-router-dom";

import { campaign as copy } from "../content/pt";
import { formatDecimal } from "../lib/format";
import type { CampaignMatch, CollectionData } from "../types/data";
import { MiniNetwork } from "./MiniNetwork";
import styles from "./MatchCard.module.css";

interface MatchCardProps {
  match: CampaignMatch;
  collection: CollectionData;
  isLast: boolean;
}

export function MatchCard({ match, collection, isLast }: MatchCardProps) {
  const [goalsFor, goalsAgainst] = match.score;
  const result = goalsFor > goalsAgainst ? "win" : goalsFor < goalsAgainst ? "loss" : "draw";
  // the final card is highlighted when it is the last match and it was won
  const champion = isLast && match.stage === "Final" && result === "win";
  const tag = champion ? copy.champion : result === "win" ? copy.win : result === "draw" ? copy.draw : copy.loss;

  return (
    <Link to={`/pnsm/1970/${match.id}`} className={`${styles.card} ${champion ? styles.highlight : ""}`}>
      <div className={styles.top}>
        <span className={styles.label}>{copy.gameLabel(match.order, match.stage)}</span>
        <span className={`${styles.tag} ${styles[champion ? "champion" : result]}`}>{tag}</span>
      </div>
      <span className={styles.score}>
        {collection.displayName} {goalsFor} <span className={styles.times}>×</span> {goalsAgainst} {match.opponent}
      </span>
      <MiniNetwork data={match.mini} colors={collection.colors} scale={collection.scale} />
      <dl className={styles.facts}>
        <div>
          <dt>{copy.cardCompleted}</dt>
          <dd>
            {match.completed} <span className={styles.opp}>× {match.opponentCompleted}</span>
          </dd>
        </div>
        <div>
          <dt>{copy.cardXg}</dt>
          <dd>
            {formatDecimal(match.xg)} <span className={styles.opp}>× {formatDecimal(match.opponentXg)}</span>
          </dd>
        </div>
        <div className={styles.wide}>
          <dt>{copy.cardPair}</dt>
          <dd className={styles.pair}>{copy.cardPairValue(match.topPair.names[0], match.topPair.names[1], match.topPair.n)}</dd>
        </div>
      </dl>
      {match.note && <span className={styles.note}>{match.note}</span>}
      <span className={styles.cta}>{copy.seeMatch}</span>
    </Link>
  );
}
