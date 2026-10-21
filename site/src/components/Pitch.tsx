import type { ReactNode } from "react";

import { PITCH_H, PITCH_W, PX } from "../lib/geometry";
import styles from "./Pitch.module.css";

interface PitchProps {
  label: string;
  children?: ReactNode;
  /** text in the bottom-right corner, e.g. "ATAQUE →" */
  corner?: string;
  className?: string;
  /** one design px in pitch units; defaults to the 560 px reference pitch */
  unit?: number;
  /** draw the goal mouth on the right (replay) */
  goal?: boolean;
}

/** Horizontal StatsBomb pitch (viewBox 0 0 120 80), attack to the right. */
export function Pitch({ label, children, corner, className, unit = PX, goal = false }: PitchProps) {
  return (
    <svg
      className={`${styles.pitch} ${className ?? ""}`}
      viewBox={`0 0 ${PITCH_W} ${PITCH_H}`}
      preserveAspectRatio="xMidYMid meet"
      role="group"
      aria-label={label}
    >
      <PitchMarkings />
      {goal && <rect x={PITCH_W - 5 * unit} y={36} width={5 * unit} height={8} className={styles.goal} aria-hidden="true" />}
      {corner && (
        <text x={PITCH_W - 10 * unit} y={PITCH_H - 8 * unit} className={styles.corner} fontSize={11 * unit} textAnchor="end" aria-hidden="true">
          {corner}
        </text>
      )}
      {children}
    </svg>
  );
}

function PitchMarkings() {
  return (
    <g className={styles.lines} aria-hidden="true">
      <rect x={0} y={0} width={PITCH_W} height={PITCH_H} className={styles.grass} />
      <line x1={60} y1={0} x2={60} y2={80} />
      <circle cx={60} cy={40} r={10} />
      {/* penalty areas and six-yard boxes */}
      <rect x={0} y={18} width={18} height={44} />
      <rect x={0} y={30} width={6} height={20} />
      <rect x={102} y={18} width={18} height={44} />
      <rect x={114} y={30} width={6} height={20} />
      <rect x={0} y={0} width={PITCH_W} height={PITCH_H} />
    </g>
  );
}
