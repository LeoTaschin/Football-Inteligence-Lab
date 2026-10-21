import { match as copy } from "../content/pt";
import type { TeamData } from "../types/data";
import { BarList } from "./BarList";
import styles from "./CombinationTable.module.css";

interface CombinationTableProps {
  team: TeamData;
  maxPair: number;
  top?: number;
}

/** Top N undirected pairs; the engine already orders them and puts first who passed more. */
export function CombinationTable({ team, maxPair, top = 10 }: CombinationTableProps) {
  const name = new Map(team.nodes.map((n) => [n.playerId, n.name]));
  const rows = team.pairs.slice(0, top).map((p, i) => ({
    key: `${p.a}-${p.b}`,
    rank: i + 1,
    name: `${name.get(p.a)} – ${name.get(p.b)}`,
    detail: copy.topSplit(p.forward, p.backward),
    n: p.n,
  }));
  return (
    <section className={styles.section}>
      <div className={styles.head}>
        <h3 className={styles.title}>{copy.topTitle(team.displayName)}</h3>
        <span className={styles.legend}>{copy.topLegend}</span>
      </div>
      <BarList rows={rows} color={team.colors.line} max={maxPair} variant="table" />
    </section>
  );
}
