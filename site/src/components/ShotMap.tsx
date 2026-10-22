import type { KeyboardEvent } from "react";

import { shots as copy } from "../content/pt";
import { formatDecimal } from "../lib/format";
import { PITCH_H, PITCH_W, SHOT_PX, shotPoint, shotRadius } from "../lib/geometry";
import type { Shot, ShotResult, TeamData } from "../types/data";
import pitchStyles from "./Pitch.module.css";
import styles from "./ShotMap.module.css";

/** room above the goal line for markers right on it (pitch units) */
const TOP_MARGIN = 4;
const BLOCKED_FILL = "rgba(161, 161, 170, 0.55)";
const BLOCKED_LINE = "#71717A";

interface MarkerLook {
  fill: string;
  fillOpacity: number;
  stroke: string;
  strokeWidth: number; // px
  dashed: boolean;
}

/** Marker look per result (design "Finalizações"): filled goal, tinted save, dashed post, grey block, hollow miss. */
export function markerLook(result: ShotResult, color: string): MarkerLook {
  switch (result) {
    case "goal":
      return { fill: color, fillOpacity: 1, stroke: "var(--text)", strokeWidth: 2, dashed: false };
    case "saved":
      return { fill: color, fillOpacity: 0.3, stroke: color, strokeWidth: 2, dashed: false };
    case "post":
      return { fill: "#FFFFFF", fillOpacity: 1, stroke: color, strokeWidth: 2, dashed: true };
    case "blocked":
      return { fill: BLOCKED_FILL, fillOpacity: 1, stroke: BLOCKED_LINE, strokeWidth: 1.5, dashed: false };
    default:
      return { fill: "#FFFFFF", fillOpacity: 0.85, stroke: color, strokeWidth: 2, dashed: false };
  }
}

interface MarkerProps {
  cx: number;
  cy: number;
  /** radius in pitch units */
  r: number;
  square: boolean;
  look: MarkerLook;
  /** one design px in the current units */
  unit: number;
}

/** Circle for open play, rounded square for set pieces. */
export function Marker({ cx, cy, r, square, look, unit }: MarkerProps) {
  const common = {
    fill: look.fill,
    fillOpacity: look.fillOpacity,
    stroke: look.stroke,
    strokeWidth: look.strokeWidth * unit,
    strokeDasharray: look.dashed ? `${3 * unit} ${2 * unit}` : undefined,
  };
  return square ? (
    <rect x={cx - r} y={cy - r} width={2 * r} height={2 * r} rx={3 * unit} {...common} />
  ) : (
    <circle cx={cx} cy={cy} r={r} {...common} />
  );
}

interface ShotMapProps {
  team: TeamData;
  /** the pitch is drawn from this x up to the goal (scale.shotsFromX) */
  fromX: number;
  selected: number | null;
  /** index in team.shots.items → shown at full opacity */
  visible: (shot: Shot) => boolean;
  onSelect: (index: number) => void;
}

/** Vertical pitch from `fromX` to the goal, the team attacking upward; one marker per shot, area ∝ xG. */
export function ShotMap({ team, fromX, selected, visible, onSelect }: ShotMapProps) {
  const depth = PITCH_W - fromX;
  const color = team.colors.line;
  // big markers first so the small ones on top stay clickable; the selected one last
  const order = team.shots.items
    .map((shot, i) => ({ shot, i }))
    .filter(({ shot }) => shot.x !== null && shot.y !== null)
    .sort((a, b) => (a.i === selected ? 1 : b.i === selected ? -1 : shotRadius(b.shot.xg) - shotRadius(a.shot.xg)));

  const onKey = (i: number) => (event: KeyboardEvent) => {
    if (event.key === "Enter" || event.key === " ") {
      event.preventDefault();
      onSelect(i);
    }
  };

  return (
    <svg
      className={`${pitchStyles.pitch} ${styles.map}`}
      viewBox={`0 ${-TOP_MARGIN} ${PITCH_H} ${depth + TOP_MARGIN}`}
      preserveAspectRatio="xMidYMid meet"
      role="group"
      aria-label={copy.pitchLabel(team.article, team.displayName)}
    >
      <VerticalMarkings depth={depth} />
      <g aria-hidden="true">
        <circle cx={40} cy={12} r={0.35} className={styles.spot} />
        <rect x={36} y={-5 * SHOT_PX} width={8} height={5 * SHOT_PX} className={styles.goal} />
      </g>
      <g>
        {order.map(({ shot, i }) => {
          const p = shotPoint(shot.x!, shot.y!);
          const r = shotRadius(shot.xg) * SHOT_PX;
          const isSel = i === selected;
          const outcome = copy.outcome[shot.outcome] ?? copy.result[shot.result];
          return (
            <g
              key={i}
              role="button"
              tabIndex={0}
              aria-label={copy.shotAria(shot.minute, shot.name, outcome, shot.xg === null ? copy.detail.noXg : formatDecimal(shot.xg))}
              aria-pressed={isSel}
              className={styles.shot}
              opacity={visible(shot) ? 1 : 0.12}
              onClick={() => onSelect(i)}
              onKeyDown={onKey(i)}
            >
              <title>{`${shot.minute}′ · ${shot.name} · ${outcome}`}</title>
              <circle cx={p.x} cy={p.y} r={Math.max(r, 8 * SHOT_PX)} className={styles.hit} />
              {isSel && <circle cx={p.x} cy={p.y} r={r + 4 * SHOT_PX} className={styles.ring} />}
              <Marker cx={p.x} cy={p.y} r={r} square={shot.setPiece} look={markerLook(shot.result, color)} unit={SHOT_PX} />
            </g>
          );
        })}
      </g>
    </svg>
  );
}

/** Lines of the attacking end, turned so the goal is at the top (StatsBomb x → screen y = 120 − x). */
function VerticalMarkings({ depth }: { depth: number }) {
  const halfway = PITCH_W - 60; // screen y of the halfway line
  return (
    <g className={pitchStyles.lines} aria-hidden="true">
      {/* the grass goes past the goal line so markers on it are not cut */}
      <rect x={0} y={-TOP_MARGIN} width={PITCH_H} height={depth + TOP_MARGIN} className={pitchStyles.grass} />
      {/* penalty area, six-yard box, spot and arc */}
      <rect x={18} y={0} width={44} height={18} />
      <rect x={30} y={0} width={20} height={6} />
      <path d="M 32 18 A 10 10 0 0 0 48 18" className={styles.arc} />
      {depth >= halfway && (
        <>
          <line x1={0} y1={halfway} x2={PITCH_H} y2={halfway} />
          <circle cx={40} cy={halfway} r={10} />
        </>
      )}
      <rect x={0} y={0} width={PITCH_H} height={depth} />
    </g>
  );
}
