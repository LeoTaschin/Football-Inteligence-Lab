import { useState } from "react";

import { shots as copy } from "../content/pt";
import { formatDecimal } from "../lib/format";
import { SHOT_XG_REF } from "../lib/geometry";
import type { MatchData, Shot, TeamData } from "../types/data";
import { ShotIconSvg, ShotMap } from "./ShotMap";
import { TeamSwitch } from "./TeamSwitch";
import layout from "./SplitLayout.module.css";
import styles from "./ShotsPanel.module.css";

type Filter = keyof typeof copy.filters;
const FILTERS: Filter[] = ["all", "open", "goals"];
const KEEP: Record<Filter, (s: Shot) => boolean> = {
  all: () => true,
  open: (s) => !s.setPiece,
  goals: (s) => s.result === "goal",
};
const LEGEND = ["goal", "saved", "post", "blocked", "off"] as const;
const NEUTRAL = "#52525B";
const BAR_Z = 2.67; // crossbar, yards: the goal view is drawn in StatsBomb units
const dec1 = (n: number) => formatDecimal(n, 1);

interface ShotsPanelProps {
  data: MatchData;
  team: number;
  onTeam: (index: number) => void;
  /** index in the team's shots.items */
  selected: number | null;
  onSelect: (index: number) => void;
}

/** "Finalizações": one team at a time; the pitch with every shot on the left, the selected shot and the biggest chances on the right. */
export function ShotsPanel({ data, team: ti, onTeam, selected, onSelect }: ShotsPanelProps) {
  const [filter, setFilter] = useState<Filter>("all");
  const team = data.teams[ti];
  const s = team.shots;
  const shot = selected !== null ? s.items[selected] : null;
  const noLocation = s.items.filter((x) => x.x === null || x.y === null).length;
  const outcomeOf = (x: Shot) => copy.outcome[x.outcome] ?? copy.result[x.result];

  return (
    <div className={layout.tab}>
      <div className={layout.head}>
        <h2 className={layout.title}>{copy.title(team.article, team.displayName)}</h2>
        <TeamSwitch teams={data.teams} current={ti} onChange={onTeam} label={copy.teamLabel} />
      </div>

      <div className={layout.body}>
        <div className={layout.main}>
          <div className={styles.filter} role="group" aria-label={copy.filterLabel}>
            <span>{copy.show}</span>
            {FILTERS.map((f) => (
              <button key={f} type="button" className="pill" aria-pressed={f === filter} onClick={() => setFilter(f)}>
                {copy.filters[f]}
              </button>
            ))}
          </div>

          <div className={styles.pitchBox}>
            <ShotMap team={team} fromX={data.scale.shotsFromX} selected={selected} visible={KEEP[filter]} onSelect={onSelect} />
            <span className={styles.attack} aria-hidden="true">
              {copy.attackUp(team.article, team.displayName)}
            </span>
          </div>

          <ul className={layout.legend} aria-label={copy.legendLabel}>
            {LEGEND.map((r) => (
              <li key={r}>
                <ShotIconSvg size={22} result={r} color={NEUTRAL} badge={null} />
                {copy.legend[r]}
              </li>
            ))}
            <li>
              <span className={styles.badge}>F</span>
              {copy.legend.setPiece}
            </li>
            <li>
              <span className={styles.halo} />
              {copy.legend.halo}
            </li>
          </ul>
          {noLocation > 0 && <p className={layout.caption}>{copy.noLocation(noLocation)}</p>}
          <p className={layout.caption}>{copy.hint}</p>
        </div>

        <aside className={layout.aside}>
          <div className={layout.summary}>
            <span className={layout.big}>{copy.summaryXg(formatDecimal(s.xg))}</span>
            <span className={layout.summaryText}>
              {copy.summary({
                count: s.count,
                goals: s.goals,
                perShot: s.xgPerShot === null ? null : formatDecimal(s.xgPerShot),
                withXg: s.xgCoverage[0],
              })}
            </span>
          </div>

          {shot ? <ShotDetail team={team} shot={shot} outcome={outcomeOf(shot)} /> : <p className={layout.hint}>{copy.hint}</p>}

          <section className={styles.top}>
            <h3 className={styles.topTitle}>{copy.topTitle}</h3>
            {s.top.map((index) => {
              const x = s.items[index];
              return (
                <button key={index} type="button" className={styles.topRow} aria-pressed={index === selected} onClick={() => onSelect(index)}>
                  <span className={styles.minute}>{x.minute}′</span>
                  <span className={styles.who}>
                    <span className={styles.player}>{x.name}</span>
                    <span className={styles.outcome}>{outcomeOf(x)}</span>
                  </span>
                  <span className={styles.track}>
                    <span style={{ width: `${Math.min(100, (100 * (x.xg ?? 0)) / SHOT_XG_REF)}%`, background: team.colors.line }} />
                  </span>
                  <span className={styles.xg}>{formatDecimal(x.xg ?? 0)}</span>
                </button>
              );
            })}
          </section>
        </aside>
      </div>

      <p className={layout.caption}>{copy.footer}</p>
    </div>
  );
}

function ShotDetail({ team, shot, outcome }: { team: TeamData; shot: Shot; outcome: string }) {
  const f = shot.finish;
  // the goal view needs the height where the ball crossed the line
  const crossed = shot.end && shot.end.length > 2 && (f.kind === "goal" || f.kind === "saved" || f.kind === "post" || f.kind === "over" || f.kind === "wide" || f.kind === "overWide");
  return (
    <section className={styles.detail} aria-live="polite">
      <div className={styles.detailHead}>
        <ShotIconSvg size={34} result={shot.result} color={team.colors.line} badge={shot.setPiece ? (copy.badge[shot.shotType] ?? null) : null} />
        <div className={styles.detailWho}>
          <span className="eyebrow">{`${team.displayName} · ${shot.minute}′ · ${outcome}`}</span>
          <span className={styles.detailName}>{shot.name}</span>
        </div>
      </div>
      <dl className={styles.detailStats}>
        <div>
          <dt>{copy.detail.xg}</dt>
          <dd className={styles.bigStat}>{shot.xg === null ? copy.detail.noXg : formatDecimal(shot.xg)}</dd>
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
      {crossed && <GoalView y={shot.end![1]} z={shot.end![2]} goal={shot.result === "goal"} color={team.colors.line} />}
      <p className={styles.finish}>{copy.finish(f, dec1)}</p>
    </section>
  );
}

/** Front view of the goal (y 30–50, height 0–7 yd), seen from behind the shooter: where the ball crossed the line. */
function GoalView({ y, z, goal, color }: { y: number; z: number; goal: boolean; color: string }) {
  const bx = Math.min(49.4, Math.max(30.6, y));
  const bz = Math.min(6.1, Math.max(0, z));
  return (
    <figure className={styles.goalView}>
      <svg viewBox="30 -6.5 20 7" preserveAspectRatio="xMidYMid meet" aria-hidden="true">
        <line x1={30} y1={0} x2={50} y2={0} className={styles.ground} />
        <rect x={36} y={-BAR_Z} width={8} height={BAR_Z} className={styles.frame} />
        <circle cx={bx} cy={-bz} r={0.42} fill={goal ? color : "#FFFFFF"} className={styles.ball} />
      </svg>
      <figcaption>{copy.frameCaption}</figcaption>
    </figure>
  );
}
