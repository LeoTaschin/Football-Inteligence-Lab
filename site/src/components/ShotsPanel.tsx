import { useState } from "react";

import { shots as copy } from "../content/pt";
import { formatDecimal } from "../lib/format";
import { SHOT_XG_REF, shotRadius } from "../lib/geometry";
import type { MatchData, Shot, ShotResult, TeamData } from "../types/data";
import { Marker, markerLook, ShotMap } from "./ShotMap";
import styles from "./ShotsPanel.module.css";

export interface ShotRef {
  team: number; // index in data.teams
  index: number; // index in team.shots.items
}

type Filter = keyof typeof copy.filters;
const FILTERS: Filter[] = ["all", "open", "goals"];
const KEEP: Record<Filter, (s: Shot) => boolean> = {
  all: () => true,
  open: (s) => !s.setPiece,
  goals: (s) => s.result === "goal",
};
const LEGEND = ["goal", "saved", "post", "blocked", "off"] as const;
const SIZE_LEGEND = [0.05, 0.2, 0.5];
const NEUTRAL = "#52525B";

interface ShotsPanelProps {
  data: MatchData;
  selected: ShotRef | null;
  onSelect: (ref: ShotRef) => void;
}

/** "Finalizações" tab: one vertical shot map per team, the selected shot's detail and the biggest chances. */
export function ShotsPanel({ data, selected, onSelect }: ShotsPanelProps) {
  const [filter, setFilter] = useState<Filter>("all");
  const { teams } = data;
  const outcomeOf = (s: Shot) => copy.outcome[s.outcome] ?? copy.result[s.result];

  return (
    <div className={styles.panel}>
      <p className={styles.summary}>
        {copy.summary(
          teams.map((t) => ({ article: t.article, name: t.displayName, xg: formatDecimal(t.shots.xg), count: t.shots.count, goals: t.shots.goals })),
        )}
      </p>

      <div className={styles.controls}>
        <div className={styles.filter} role="group" aria-label={copy.filterLabel}>
          <span>{copy.show}</span>
          {FILTERS.map((f) => (
            <button key={f} type="button" className="pill" aria-pressed={f === filter} onClick={() => setFilter(f)}>
              {copy.filters[f]}
            </button>
          ))}
        </div>
        <ul className={styles.legend} aria-label={copy.legendLabel}>
          {LEGEND.map((r) => (
            <li key={r}>
              <LegendIcon result={r} square={false} />
              {copy.legend[r]}
            </li>
          ))}
          <li>
            <LegendIcon result="off" square />
            {copy.legend.setPiece}
          </li>
        </ul>
      </div>

      <div className={styles.maps}>
        {teams.map((team, ti) => {
          const noLocation = team.shots.items.filter((s) => s.x === null || s.y === null).length;
          return (
            <section key={team.teamId} className={styles.team}>
              <div className={styles.teamHead}>
                <h2 className={styles.teamName}>
                  <span className={styles.teamDot} style={{ background: team.colors.fill, borderColor: team.colors.line }} />
                  {team.displayName}
                </h2>
                <span className={styles.muted}>{copy.attackUp}</span>
              </div>
              <div className={styles.pitchBox}>
                <ShotMap
                  team={team}
                  fromX={data.scale.shotsFromX}
                  selected={selected?.team === ti ? selected.index : null}
                  visible={KEEP[filter]}
                  onSelect={(index) => onSelect({ team: ti, index })}
                />
              </div>
              {noLocation > 0 && <p className={styles.muted}>{copy.noLocation(noLocation)}</p>}
              <TeamStats team={team} />
            </section>
          );
        })}
      </div>

      {selected ? (
        <ShotDetail team={teams[selected.team]} shot={teams[selected.team].shots.items[selected.index]} outcome={outcomeOf} />
      ) : (
        <p className={styles.hint}>{copy.hint}</p>
      )}

      <section className={styles.top}>
        <div className={styles.topHead}>
          <h3 className={styles.topTitle}>{copy.topTitle}</h3>
          <span className={styles.muted}>{copy.topLegend}</span>
        </div>
        <div className={styles.topLists}>
          {teams.map((team, ti) => (
            <div key={team.teamId}>
              <div className={styles.topListHead}>
                <span>{team.displayName}</span>
                <span>xG</span>
              </div>
              {team.shots.top.map((index) => {
                const s = team.shots.items[index];
                const on = selected?.team === ti && selected.index === index;
                return (
                  <button
                    key={index}
                    type="button"
                    className={styles.topRow}
                    aria-pressed={on}
                    onClick={() => onSelect({ team: ti, index })}
                  >
                    <span className={styles.muted}>{s.minute}′</span>
                    <span className={styles.player}>{s.name}</span>
                    <span className={styles.outcome}>{outcomeOf(s)}</span>
                    <span className={styles.xg}>
                      <span className={styles.track}>
                        <span
                          className={styles.fill}
                          style={{ width: `${Math.min(100, (100 * (s.xg ?? 0)) / SHOT_XG_REF)}%`, background: team.colors.line }}
                        />
                      </span>
                      <span className={styles.xgValue}>{formatDecimal(s.xg ?? 0)}</span>
                    </span>
                  </button>
                );
              })}
            </div>
          ))}
        </div>
      </section>

      <div className={styles.sizeLegend}>
        <strong>{copy.sizeTitle}</strong>
        {SIZE_LEGEND.map((xg) => {
          const r = shotRadius(xg);
          return (
            <span key={xg} className={styles.sizeItem}>
              <span className={styles.sizeDot} style={{ width: 2 * r, height: 2 * r }} />
              {formatDecimal(xg)}
            </span>
          );
        })}
        <span>{copy.sizeNote}</span>
      </div>

      <p className={styles.note}>{copy.footer}</p>
    </div>
  );
}

function TeamStats({ team }: { team: TeamData }) {
  const s = team.shots;
  const items = [
    { value: String(s.count), label: copy.stats.count },
    { value: String(s.goals), label: copy.stats.goals },
    { value: formatDecimal(s.xg), label: copy.stats.xg },
    { value: s.xgPerShot === null ? "–" : formatDecimal(s.xgPerShot), label: copy.stats.xgPerShot },
    { value: `${s.xgCoverage[0]}/${s.xgCoverage[1]}`, label: copy.stats.coverage },
  ];
  return (
    <dl className={styles.stats}>
      {items.map((it) => (
        <div key={it.label}>
          <dt>{it.label}</dt>
          <dd>{it.value}</dd>
        </div>
      ))}
    </dl>
  );
}

function ShotDetail({ team, shot, outcome }: { team: TeamData; shot: Shot; outcome: (s: Shot) => string }) {
  const r = 11;
  return (
    <section className={styles.detail} aria-live="polite">
      <svg width={2 * r + 4} height={2 * r + 4} viewBox={`${-r - 2} ${-r - 2} ${2 * r + 4} ${2 * r + 4}`} aria-hidden="true">
        <Marker cx={0} cy={0} r={r} square={shot.setPiece} look={markerLook(shot.result, team.colors.line)} unit={1} />
      </svg>
      <div className={styles.who}>
        <span className="eyebrow">{`${team.displayName} · ${shot.minute}′ · ${outcome(shot)}`}</span>
        <span className={styles.detailName}>{shot.name}</span>
      </div>
      <dl className={styles.detailStats}>
        <div>
          <dt>{copy.detail.xg}</dt>
          <dd className={styles.big}>{shot.xg === null ? copy.detail.noXg : formatDecimal(shot.xg)}</dd>
        </div>
        <div>
          <dt>{copy.detail.body}</dt>
          <dd>{copy.body[shot.bodyPart]}</dd>
        </div>
        <div>
          <dt>{copy.detail.type}</dt>
          <dd>{copy.type[shot.shotType]}</dd>
        </div>
        {shot.distance !== null && (
          <div>
            <dt>{copy.detail.distance}</dt>
            <dd>{copy.meters(shot.distance)}</dd>
          </div>
        )}
      </dl>
    </section>
  );
}

function LegendIcon({ result, square }: { result: ShotResult; square: boolean }) {
  return (
    <svg width={16} height={16} viewBox="-8 -8 16 16" aria-hidden="true">
      <Marker cx={0} cy={0} r={6.5} square={square} look={markerLook(result, NEUTRAL)} unit={1} />
    </svg>
  );
}
