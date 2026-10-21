import { match as copy } from "../content/pt";
import { formatPercent } from "../lib/format";
import type { TeamData } from "../types/data";
import { BarList } from "./BarList";
import styles from "./PlayerPanel.module.css";

const TOP = 5;

interface PlayerPanelProps {
  team: TeamData;
  playerId: number;
  onClear: () => void;
}

export function PlayerPanel({ team, playerId, onClear }: PlayerPanelProps) {
  const byId = new Map(team.nodes.map((n) => [n.playerId, n]));
  const node = byId.get(playerId);
  if (!node) return null;

  // edges come sorted by n (most used first) from the engine
  const out = team.edges.filter((e) => e.from === playerId).slice(0, TOP);
  const inc = team.edges.filter((e) => e.to === playerId).slice(0, TOP);
  const subText = node.sub
    ? node.sub.type === "out"
      ? copy.panel.subOut(node.sub.minute, byId.get(node.sub.with)?.name ?? "")
      : copy.panel.subIn(node.sub.minute, byId.get(node.sub.with)?.name ?? "")
    : null;

  return (
    <section className={styles.panel} aria-live="polite">
      <div className={styles.identity}>
        <div className={styles.head}>
          <div className={styles.who}>
            <span
              className={styles.badge}
              style={{ background: team.colors.fill, color: team.colors.ink, borderColor: team.colors.line }}
            >
              {node.num}
            </span>
            <div className={styles.names}>
              <h2 className={styles.name}>{node.name}</h2>
              <span className={styles.position}>
                {[node.position, team.displayName].filter(Boolean).join(" · ")}
              </span>
            </div>
          </div>
          <button type="button" className={styles.close} onClick={onClear} aria-label={copy.clear}>
            <svg width="16" height="16" viewBox="0 0 16 16" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" aria-hidden="true">
              <path d="M3 3l10 10M13 3L3 13" />
            </svg>
          </button>
        </div>
        <div className={styles.stats}>
          <Stat value={node.passes} label={copy.panel.passes} />
          <Stat value={node.received} label={copy.panel.received} />
          <Stat value={formatPercent(node.passes, team.passes.completed)} label={copy.panel.share} />
        </div>
        {subText && <span className={styles.note}>{subText}</span>}
        {node.positionFrom === "received" && <span className={styles.note}>{copy.panel.fromReceived}</span>}
      </div>

      <div className={styles.list}>
        <span className={styles.listTitle}>
          <span className={styles.swatch} style={{ background: team.colors.line }} />
          {copy.panel.passedTo}
        </span>
        <BarList rows={out.map((e) => ({ key: e.to, name: byId.get(e.to)?.name ?? "", n: e.n }))} color={team.colors.line} />
      </div>

      <div className={styles.list}>
        <span className={styles.listTitle}>
          <span className={styles.swatch} style={{ background: "var(--incoming)" }} />
          {copy.panel.receivedFrom}
        </span>
        <BarList rows={inc.map((e) => ({ key: e.from, name: byId.get(e.from)?.name ?? "", n: e.n }))} color="var(--incoming)" />
      </div>
    </section>
  );
}

function Stat({ value, label }: { value: number | string; label: string }) {
  return (
    <div className={styles.stat}>
      <span className={styles.statValue}>{value}</span>
      <span className={styles.statLabel}>{label}</span>
    </div>
  );
}
