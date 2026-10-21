import { useEffect, useRef, useState } from "react";

import { goals as copy } from "../content/pt";
import { formatClock } from "../lib/format";
import { labelPlacement, lerp } from "../lib/geometry";
import type { Goal, TeamData } from "../types/data";
import { Pitch } from "./Pitch";
import styles from "./GoalReplay.module.css";

/** Drawn on an 840 px reference pitch, like the replay in the design. */
const U = 120 / 840;
const TOUCH_R = 15;
const SPEEDS = [0.5, 1, 2];

interface GoalReplayProps {
  goal: Goal;
  team: TeamData;
  context: string;
}

export function GoalReplay({ goal, team, context }: GoalReplayProps) {
  const end = goal.duration;
  const [t, setTState] = useState(end); // start showing the whole play, paused
  const [playing, setPlaying] = useState(false);
  const [speed, setSpeed] = useState(1);
  const tRef = useRef(end); // the animation loop reads the time without waiting for a render
  const setT = (value: number) => {
    tRef.current = value;
    setTState(value);
  };

  useEffect(() => {
    if (!playing) return;
    let frame = 0;
    let last: number | null = null;
    const tick = (now: number) => {
      const dt = last === null ? 0 : (now - last) / 1000;
      last = now;
      const next = tRef.current + dt * speed;
      if (next >= end) {
        setT(end);
        setPlaying(false);
        return;
      }
      setT(next);
      frame = requestAnimationFrame(tick);
    };
    frame = requestAnimationFrame(tick);
    return () => cancelAnimationFrame(frame);
  }, [playing, speed, end]);

  const toggle = () => {
    if (playing) setPlaying(false);
    else {
      if (tRef.current >= end - 0.05) setT(0);
      setPlaying(true);
    }
  };
  const restart = () => {
    setT(0);
    setPlaying(true);
  };
  const seek = (value: number) => {
    setPlaying(false);
    setT(Math.min(end, Math.max(0, value)));
  };

  // ball: end of the last segment already started
  const first = goal.segments[0];
  let ball = { x: first.from[0], y: first.from[1] };
  const trail = goal.segments
    .filter((s) => t >= s.t)
    .map((s) => {
      const a = { x: s.from[0], y: s.from[1] };
      const b = lerp(a, { x: s.to[0], y: s.to[1] }, s.d > 0 ? (t - s.t) / s.d : 1);
      ball = b;
      return { s, a, b };
    });

  const lastTouch = goal.touches.reduce((acc, tc, i) => (t >= tc.t ? i : acc), -1);
  const currentStep = goal.steps.reduce((acc, st, i) => (t >= st.t ? i : acc), -1);
  const isGoal = t >= end - 0.05;

  return (
    <div className={styles.wrap}>
      <header className={styles.head}>
        <div className={styles.titles}>
          <span className="eyebrow">{context}</span>
          <h2 className={styles.title}>{copy.title(goal.scorer)}</h2>
        </div>
        <div className={styles.stats}>
          <Stat value={String(goal.passes)} label={copy.passes} />
          <Stat value={String(goal.players)} label={copy.players} />
          <Stat value={copy.seconds(goal.duration)} label={copy.duration} />
        </div>
      </header>

      <div className={styles.body}>
        <div className={styles.stage}>
          <div className={styles.pitchScroll}>
            <div className={styles.pitchBox}>
              <Pitch label={copy.title(goal.scorer)} unit={U} goal corner={copy.attack}>
                <g aria-hidden="true">
                  {trail.map(({ s, a, b }) => (
                    <line
                      key={`${s.t}-${s.kind}`}
                      x1={a.x}
                      y1={a.y}
                      x2={b.x}
                      y2={b.y}
                      stroke={s.kind === "shot" ? "var(--text)" : team.colors.line}
                      strokeOpacity={s.kind === "carry" ? 0.75 : 0.9}
                      className={s.kind === "carry" ? styles.carry : styles.pass}
                    />
                  ))}
                </g>

                <g aria-hidden="true">
                  {goal.touches.map((tc, i) => {
                    const on = t >= tc.t;
                    const current = i === lastTouch && !isGoal;
                    const label = labelPlacement({ x: tc.at[0], y: tc.at[1] }, TOUCH_R, tc.label, U);
                    return (
                      <g key={`${tc.t}-${tc.playerId}`} className={styles.touch} style={{ opacity: on ? 1 : 0 }}>
                        <g
                          className={styles.touchDot}
                          style={{ transform: `translate(${tc.at[0]}px, ${tc.at[1]}px) scale(${on ? (current ? 1.15 : 1) : 0.6})` }}
                        >
                          {current && <circle r={(TOUCH_R + 5) * U} className={styles.ring} />}
                          <circle r={TOUCH_R * U} fill={team.colors.fill} stroke={team.colors.line} strokeWidth={2 * U} />
                          <text fontSize={12 * U} textAnchor="middle" dominantBaseline="central" fill={team.colors.ink} className={styles.num}>
                            {tc.num}
                          </text>
                        </g>
                        <text
                          x={label.x}
                          y={label.y}
                          fontSize={12 * U}
                          textAnchor={label.anchor}
                          dominantBaseline={label.baseline}
                          className={styles.label}
                        >
                          {tc.name}
                        </text>
                      </g>
                    );
                  })}
                </g>

                <circle cx={ball.x} cy={ball.y} r={6 * U} className={styles.ball} aria-hidden="true" />
              </Pitch>
            </div>
          </div>
          {isGoal && <div className={styles.goalBadge}>{copy.goal(goal.scorer)}</div>}

          <div className={styles.controls}>
            <button type="button" className={styles.play} onClick={toggle} aria-label={playing ? copy.pause : copy.play}>
              {playing ? (
                <svg width="16" height="16" viewBox="0 0 16 16" fill="currentColor" aria-hidden="true">
                  <rect x="3" y="2" width="3.5" height="12" rx="1" />
                  <rect x="9.5" y="2" width="3.5" height="12" rx="1" />
                </svg>
              ) : (
                <svg width="16" height="16" viewBox="0 0 16 16" fill="currentColor" aria-hidden="true">
                  <path d="M4 2.5v11l9.5-5.5z" />
                </svg>
              )}
            </button>
            <button type="button" className={styles.restart} onClick={restart} aria-label={copy.restart}>
              <svg width="16" height="16" viewBox="0 0 16 16" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
                <path d="M2.5 8a5.5 5.5 0 1 0 1.6-3.9" />
                <path d="M2.5 2.5v3h3" />
              </svg>
            </button>
            <label className={styles.range}>
              <span className="visually-hidden">{copy.timeline}</span>
              <input type="range" min={0} max={end} step={0.05} value={t} onChange={(e) => seek(Number(e.target.value))} />
            </label>
            <span className={styles.clock}>{formatClock(t)}</span>
            <div className={styles.speeds} role="group" aria-label={copy.speed}>
              {SPEEDS.map((v) => (
                <button key={v} type="button" className={`pill ${styles.speed}`} aria-pressed={v === speed} onClick={() => setSpeed(v)}>
                  {copy.speedLabel(v)}
                </button>
              ))}
            </div>
          </div>
        </div>

        <aside className={styles.steps}>
          <span className={styles.stepsTitle}>{copy.stepsTitle}</span>
          <ol className={styles.stepList}>
            {goal.steps.map((st, i) => (
              <li key={`${st.t}-${i}`}>
                <button
                  type="button"
                  className={styles.step}
                  data-state={i === currentStep ? "current" : i < currentStep ? "done" : "next"}
                  aria-current={i === currentStep ? "step" : undefined}
                  onClick={() => seek(st.t + 0.01)}
                >
                  <span className={styles.stepTime}>{formatClock(st.t)}</span>
                  <span className={styles.stepText}>{st.text}</span>
                </button>
              </li>
            ))}
          </ol>
        </aside>
      </div>

      <p className={styles.method}>{copy.method}</p>
    </div>
  );
}

function Stat({ value, label }: { value: string; label: string }) {
  return (
    <div className={styles.stat}>
      <span className={styles.statValue}>{value}</span>
      <span className={styles.statLabel}>{label}</span>
    </div>
  );
}

