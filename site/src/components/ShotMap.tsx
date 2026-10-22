import type { KeyboardEvent } from "react";

import { shots as copy } from "../content/pt";
import { formatDecimal } from "../lib/format";
import { PITCH_H, PITCH_W, SHOT_PX, shotPoint, shotRadius } from "../lib/geometry";
import type { Shot, ShotResult, TeamData } from "../types/data";
import pitchStyles from "./Pitch.module.css";
import styles from "./ShotMap.module.css";

/** room above the goal line for icons right on it (pitch units) */
const TOP_MARGIN = 4;
/** icon size in px on the 520 px reference pitch */
const ICON_PX = 24;
const BLOCKED = "#52525B";

interface ShotIconProps {
  result: ShotResult;
  color: string;
  /** letter of the set-piece badge ("F" for a free kick), or null */
  badge: string | null;
}

/** Outcome glyph on a 24×24 grid, centred on (12, 12): ball (goal), glove (save), post, block sign, arrow out (miss). */
export function ShotIcon({ result, color, badge }: ShotIconProps) {
  return (
    <g>
      {result === "goal" ? (
        <>
          <circle cx="12" cy="12" r="10.5" fill={color} stroke="var(--text)" strokeWidth="1.5" />
          <path d="M12 7.2l4.5 3.3-1.7 5.3H8.9L7.2 10.5z" fill="#FFFFFF" />
          <path d="M12 7.2V3.6M16.5 10.5l3.4-1.2M14.8 15.8l2.1 2.9M8.9 15.8l-2.1 2.9M7.2 10.5L3.8 9.3" stroke="#FFFFFF" strokeWidth="1.2" fill="none" />
        </>
      ) : (
        <circle cx="12" cy="12" r="11" fill="#FFFFFF" stroke={result === "blocked" ? "#71717A" : color} strokeWidth="1.5" />
      )}
      {result === "saved" && (
        <path
          d="M8.2 12.6V8.4a1.1 1.1 0 0 1 2.2 0v3.4M10.4 11.6V7.1a1.1 1.1 0 0 1 2.2 0v4.5M12.6 11.6V7.6a1.1 1.1 0 0 1 2.2 0v4.3M14.8 11.2V9.4a1.1 1.1 0 0 1 2.2 0v3.8a4.6 4.6 0 0 1-4.6 4.6h-.9a4.3 4.3 0 0 1-3.6-1.9l-1.8-2.8a1 1 0 0 1 1.7-1.1l.4.6"
          fill="none"
          stroke={color}
          strokeWidth="1.5"
          strokeLinecap="round"
          strokeLinejoin="round"
        />
      )}
      {result === "post" && (
        <>
          <path d="M6 17.5V7h12v10.5" fill="none" stroke="var(--text)" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round" />
          <circle cx="16" cy="10.2" r="2.1" fill={color} />
        </>
      )}
      {result === "blocked" && (
        <>
          <circle cx="12" cy="12" r="6" fill="none" stroke={BLOCKED} strokeWidth="1.8" />
          <path d="M7.8 7.8l8.4 8.4" stroke={BLOCKED} strokeWidth="1.8" strokeLinecap="round" />
        </>
      )}
      {(result === "off" || result === "other") && (
        <path d="M8 16L16 8M10 8h6v6" fill="none" stroke={color} strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round" />
      )}
      {badge && (
        <>
          <circle cx="21" cy="3" r="6.5" fill="var(--text)" stroke="#FFFFFF" strokeWidth="1.5" />
          <text x="21" y="3" fill="#FFFFFF" fontSize="8" fontWeight="800" textAnchor="middle" dominantBaseline="central">
            {badge}
          </text>
        </>
      )}
    </g>
  );
}

/** The icon on its own, for legends and the detail card. */
export function ShotIconSvg({ size, ...icon }: ShotIconProps & { size: number }) {
  return (
    <svg width={size} height={size} viewBox="-1 -3 27 27" aria-hidden="true" className={styles.iconSvg}>
      <ShotIcon {...icon} />
    </svg>
  );
}

interface ShotMapProps {
  team: TeamData;
  /** the pitch is drawn from this x up to the goal (scale.shotsFromX) */
  fromX: number;
  selected: number | null;
  visible: (shot: Shot) => boolean;
  onSelect: (index: number) => void;
}

/** Vertical pitch, the team attacking upward: one icon per shot (outcome), a halo per shot (xG), and the selected shot's path. */
export function ShotMap({ team, fromX, selected, visible, onSelect }: ShotMapProps) {
  const depth = PITCH_W - fromX;
  const color = team.colors.line;
  const placed = team.shots.items.map((shot, i) => ({ shot, i })).filter(({ shot }) => shot.x !== null && shot.y !== null);
  // goals above the rest, the selected shot last
  const order = [...placed].sort((a, b) => rank(a.shot, a.i === selected) - rank(b.shot, b.i === selected));
  const icon = ICON_PX * SHOT_PX;

  const onKey = (i: number) => (event: KeyboardEvent) => {
    if (event.key === "Enter" || event.key === " ") {
      event.preventDefault();
      onSelect(i);
    }
  };

  const sel = selected !== null ? team.shots.items[selected] : null;

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

      <g aria-hidden="true">
        {placed.map(({ shot, i }) => {
          const p = shotPoint(shot.x!, shot.y!);
          return (
            <circle
              key={i}
              cx={p.x}
              cy={p.y}
              r={shotRadius(shot.xg) * SHOT_PX}
              fill={color}
              fillOpacity={0.14}
              stroke={color}
              strokeOpacity={0.45}
              className={styles.halo}
              opacity={visible(shot) ? 1 : 0.15}
            />
          );
        })}
      </g>

      {sel && sel.x !== null && sel.y !== null && sel.end && <BallPath shot={sel} color={color} part="line" />}

      <g>
        {order.map(({ shot, i }) => {
          const p = shotPoint(shot.x!, shot.y!);
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
              opacity={visible(shot) ? 1 : 0.15}
              onClick={() => onSelect(i)}
              onKeyDown={onKey(i)}
            >
              <title>{`${shot.minute}′ · ${shot.name} · ${outcome}`}</title>
              <circle cx={p.x} cy={p.y} r={(ICON_PX / 2 + 3) * SHOT_PX} className={isSel ? styles.ring : styles.hit} />
              <g transform={`translate(${p.x - icon / 2} ${p.y - icon / 2}) scale(${icon / 24})`}>
                <ShotIcon result={shot.result} color={color} badge={shot.setPiece ? (copy.badge[shot.shotType] ?? null) : null} />
              </g>
            </g>
          );
        })}
      </g>

      {/* the end marker and its label go over the icons */}
      {sel && sel.x !== null && sel.y !== null && sel.end && <BallPath shot={sel} color={color} part="end" />}
    </svg>
  );
}

function rank(shot: Shot, selected: boolean): number {
  return selected ? 2 : shot.result === "goal" ? 1 : 0;
}

/** Dashed straight line from the shot to its recorded end: goal line, block or where the ball stopped. */
function BallPath({ shot, color, part }: { shot: Shot; color: string; part: "line" | "end" }) {
  const from = shotPoint(shot.x!, shot.y!);
  const to = shotPoint(shot.end![0], shot.end![1]);
  const blocked = shot.finish.kind === "blocked";
  const stroke = blocked ? BLOCKED : color;
  const label = copy.endLabel[shot.finish.kind];
  const m = 7 * SHOT_PX;
  if (part === "line") {
    return <line x1={from.x} y1={from.y} x2={to.x} y2={to.y} stroke={stroke} className={styles.pathLine} aria-hidden="true" />;
  }
  return (
    <g aria-hidden="true" className={styles.path}>
      {blocked ? (
        <rect x={to.x - m / 2} y={to.y - m / 2} width={m} height={m} fill={BLOCKED} stroke="#FFFFFF" transform={`rotate(45 ${to.x} ${to.y})`} className={styles.pathEnd} />
      ) : (
        <circle cx={to.x} cy={to.y} r={m / 2} fill={color} stroke="#FFFFFF" className={styles.pathEnd} />
      )}
      {label && (
        <text x={to.x} y={to.y + 14 * SHOT_PX} fontSize={11 * SHOT_PX} textAnchor="middle" dominantBaseline="hanging" className={styles.pathLabel}>
          {label}
        </text>
      )}
    </g>
  );
}

/** Lines of the attacking end, turned so the goal is at the top (StatsBomb x → screen y = 120 − x). */
function VerticalMarkings({ depth }: { depth: number }) {
  const halfway = PITCH_W - 60; // screen y of the halfway line
  return (
    <g className={pitchStyles.lines} aria-hidden="true">
      {/* the grass goes past the goal line so icons on it are not cut */}
      <rect x={0} y={-TOP_MARGIN} width={PITCH_H} height={depth + TOP_MARGIN} className={pitchStyles.grass} />
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
