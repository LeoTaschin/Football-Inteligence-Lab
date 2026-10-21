import type { ReactNode } from "react";

import styles from "./StatStrip.module.css";

export interface Stat {
  value: ReactNode;
  label: string;
}

/** Row of big numbers between two rules (campaign summary). */
export function StatStrip({ stats, label }: { stats: Stat[]; label: string }) {
  return (
    <section aria-label={label} className={styles.strip}>
      {stats.map((s) => (
        <div key={s.label} className={styles.item}>
          <span className={styles.value}>{s.value}</span>
          <span className={styles.label}>{s.label}</span>
        </div>
      ))}
    </section>
  );
}

/** "19 × 7" with a light × */
export function Versus({ a, b }: { a: ReactNode; b: ReactNode }) {
  return (
    <>
      {a} <span className={styles.times}>×</span> {b}
    </>
  );
}
