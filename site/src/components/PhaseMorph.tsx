import { useEffect, useState } from "react";

import { phases as copy } from "../content/pt";
import { PITCH_H } from "../lib/geometry";
import type { TeamData } from "../types/data";
import { Pitch } from "./Pitch";
import styles from "./PhaseMorph.module.css";

/** This view is drawn on an 840 px reference pitch (design "Com bola × sem bola"). */
const U = 120 / 840;
const NODE_R = 18;
const GHOST_R = 9;
const AUTO_MS = 2600;
const GOALKEEPER = "Goleiro";

type Mode = "ball" | "def";

interface PhaseMorphProps {
  teams: TeamData[];
}

export function PhaseMorph({ teams }: PhaseMorphProps) {
  const [teamIndex, setTeamIndex] = useState(0);
  const [mode, setMode] = useState<Mode>("ball");
  const [auto, setAuto] = useState(false);

  useEffect(() => {
    if (!auto) return;
    const id = window.setInterval(() => setMode((m) => (m === "ball" ? "def" : "ball")), AUTO_MS);
    return () => window.clearInterval(id);
  }, [auto]);

  const team = teams[teamIndex];
  const players = team.nodes.filter((n) => n.def !== null);
  const missing = team.nodes.filter((n) => n.def === null).map((n) => n.name);
  const outfield = players.filter((n) => n.position !== GOALKEEPER && n.shift !== null);
  const shifts = [...outfield].sort((a, b) => a.shift! - b.shift!);
  const maxShift = Math.max(1, ...shifts.map((n) => Math.abs(n.shift!)));
  const most = shifts.reduce((best, n) => (Math.abs(n.shift!) > Math.abs(best.shift!) ? n : best), shifts[0]);
  const forward = shifts.filter((n) => n.shift! > 0).map((n) => n.name);
  const hasLowSample = players.some((n) => n.def!.lowSample);
  const blockX = team.phase ? (mode === "ball" ? team.phase.ballHeight : team.phase.defHeight) : null;

  const pick = (m: Mode) => {
    setAuto(false);
    setMode(m);
  };

  return (
    <div className={styles.wrap}>
      <div className={styles.head}>
        <h2 className={styles.title}>{copy.title(team.article, team.displayName)}</h2>
        <div className={styles.controls}>
          {teams.length > 1 && (
            <div className={styles.group} role="group" aria-label={copy.teamPicker}>
              {teams.map((t, i) => (
                <button key={t.teamId} type="button" className="pill" aria-pressed={i === teamIndex} onClick={() => setTeamIndex(i)}>
                  {t.displayName}
                </button>
              ))}
            </div>
          )}
          <div className={styles.group}>
            <button type="button" className="pill" aria-pressed={mode === "ball"} onClick={() => pick("ball")}>
              {copy.withBall}
            </button>
            <button type="button" className="pill" aria-pressed={mode === "def"} onClick={() => pick("def")}>
              {copy.withoutBall}
            </button>
            <button
              type="button"
              className={`pill ${styles.auto}`}
              aria-pressed={auto}
              onClick={() => {
                if (!auto) setMode((m) => (m === "ball" ? "def" : "ball"));
                setAuto(!auto);
              }}
            >
              {auto ? copy.pause : copy.animate}
            </button>
          </div>
        </div>
      </div>

      <div className={styles.body}>
        <figure className={styles.figure}>
          <div className={styles.pitchScroll}>
            <div className={styles.pitchBox}>
              <Pitch label={`${copy.title(team.article, team.displayName)} · ${mode === "ball" ? copy.withBall : copy.withoutBall}`} unit={U} corner={copy.attack(team.article, team.displayName)}>
                {blockX !== null && (
                  <g className={styles.move} style={{ transform: `translate(${blockX}px, 0px)` }} aria-hidden="true">
                    <line x1={0} y1={0} x2={0} y2={PITCH_H} className={styles.block} />
                    <g transform={`translate(0 ${16 * U})`}>
                      <rect x={-62 * U} y={-11 * U} width={124 * U} height={22 * U} rx={6 * U} className={styles.blockTag} />
                      <text x={0} y={0} fontSize={12 * U} textAnchor="middle" dominantBaseline="central" className={styles.blockText}>
                        {copy.blockLine}
                      </text>
                    </g>
                  </g>
                )}

                {players.map((n) => {
                  const here = mode === "ball" ? n.ball : n.def!;
                  const there = mode === "ball" ? n.def! : n.ball;
                  const dx = here.x - there.x;
                  const dy = here.y - there.y;
                  const len = Math.hypot(dx, dy);
                  const trim = (NODE_R + GHOST_R) * U;
                  return (
                    <g key={`ghost-${n.playerId}`} aria-hidden="true">
                      {len > trim && (
                        <line
                          x1={there.x + (dx / len) * GHOST_R * U}
                          y1={there.y + (dy / len) * GHOST_R * U}
                          x2={here.x - (dx / len) * NODE_R * U}
                          y2={here.y - (dy / len) * NODE_R * U}
                          className={styles.ghostLine}
                        />
                      )}
                      <circle cx={there.x} cy={there.y} r={GHOST_R * U} className={styles.ghost} />
                    </g>
                  );
                })}

                {players.map((n) => {
                  const p = mode === "ball" ? n.ball : n.def!;
                  return (
                    <g key={n.playerId} className={styles.move} style={{ transform: `translate(${p.x}px, ${p.y}px)` }}>
                      <circle r={(NODE_R + 2) * U} className={styles.halo} />
                      <circle r={NODE_R * U} fill={team.colors.fill} stroke={team.colors.line} strokeWidth={2 * U} />
                      <text fontSize={14 * U} textAnchor="middle" dominantBaseline="central" fill={team.colors.ink} className={styles.num}>
                        {n.num}
                      </text>
                      <text y={(NODE_R + 3) * U} fontSize={12 * U} textAnchor="middle" dominantBaseline="hanging" className={styles.label}>
                        {n.name}
                        {n.def!.lowSample ? "*" : ""}
                      </text>
                    </g>
                  );
                })}
              </Pitch>
            </div>
          </div>
          <figcaption className={styles.caption} aria-live="polite">
            {mode === "ball" ? copy.captionWith : copy.captionWithout}
          </figcaption>
        </figure>

        <aside className={styles.side}>
          {team.phase && (
            <div className={styles.big}>
              <span className={styles.bigNumber}>{copy.bigNumber(team.phase.shiftMeters)}</span>
              <span className={styles.bigText}>{copy.bigText(team.phase.shiftMeters)}</span>
            </div>
          )}
          <div className={styles.shifts}>
            <span className={styles.sectionTitle}>{copy.shiftsTitle}</span>
            <ol className={styles.shiftList}>
              {shifts.map((n) => (
                <li key={n.playerId} className={styles.shiftRow}>
                  <span className={styles.shiftName}>{n.name}</span>
                  <span className={styles.track} aria-hidden="true">
                    <span
                      className={styles.bar}
                      style={{
                        width: `${Math.round((100 * Math.abs(n.shift!)) / maxShift)}%`,
                        background: n.shift! > 0 ? "var(--incoming)" : team.colors.line,
                      }}
                    />
                  </span>
                  <span className={styles.shiftValue}>{copy.shift(n.shift!)}</span>
                </li>
              ))}
            </ol>
          </div>
          <div className={styles.facts}>
            {most && <Fact {...copy.mostShift(most.name, most.shift!)} />}
            {forward.length > 0 && <Fact {...copy.forward(forward)} />}
            {hasLowSample && <span>{copy.lowSample}</span>}
            {missing.length > 0 && <span>{copy.noDefense(missing)}</span>}
          </div>
        </aside>
      </div>

      <p className={styles.method}>{copy.method}</p>
    </div>
  );
}

function Fact({ name, text }: { name: string; text: string }) {
  return (
    <span>
      <strong>{name}</strong>
      {text}
    </span>
  );
}
