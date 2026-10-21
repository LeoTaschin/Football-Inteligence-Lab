import styles from "./BarList.module.css";

export interface BarRow {
  key: string | number;
  name: string;
  n: number;
  /** optional second line under the name */
  detail?: string;
  rank?: number;
}

interface BarListProps {
  rows: BarRow[];
  color: string;
  /** value that fills the whole bar; defaults to the largest row */
  max?: number;
  variant?: "compact" | "table";
}

/** Horizontal bars in CSS (no chart library in Etapa 1). */
export function BarList({ rows, color, max, variant = "compact" }: BarListProps) {
  const top = max ?? Math.max(1, ...rows.map((r) => r.n));
  return (
    <ol className={`${styles.list} ${styles[variant]}`}>
      {rows.map((r) => (
        <li key={r.key} className={styles.row}>
          {r.rank !== undefined && <span className={styles.rank}>{r.rank}</span>}
          <span className={styles.names}>
            <span className={styles.name}>{r.name}</span>
            {r.detail && <span className={styles.detail}>{r.detail}</span>}
          </span>
          <span className={styles.track} aria-hidden="true">
            <span className={styles.bar} style={{ width: `${Math.round((100 * r.n) / top)}%`, background: color }} />
          </span>
          <span className={styles.value}>{r.n}</span>
        </li>
      ))}
    </ol>
  );
}
