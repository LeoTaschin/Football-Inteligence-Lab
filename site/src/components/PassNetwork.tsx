import type { KeyboardEvent } from "react";

import { match as copy } from "../content/pt";
import { arrowShape, arrowWidth, labelPlacement, lineStyle, nodeRadius, polygonPoints, PX } from "../lib/geometry";
import type { CutNode, MatchData, TeamData, TeamNetwork } from "../types/data";
import { Pitch } from "./Pitch";
import styles from "./PassNetwork.module.css";

const INCOMING = "#52525B";

interface PassNetworkProps {
  team: TeamData;
  /** the network to draw (full or a cut); colors and names come from `team` */
  net: TeamNetwork;
  scale: MatchData["scale"];
  minPasses: number;
  selectedId: number | null;
  onSelect: (playerId: number) => void;
  /** the selected player's "sem bola" position (CLAUDE.md 5.6), drawn as a dashed ghost */
  ghost?: { x: number; y: number } | null;
}

export function PassNetwork({ team, net, scale, minPasses, selectedId, onSelect, ghost }: PassNetworkProps) {
  const byId = new Map(net.nodes.map((n) => [n.playerId, n]));
  const radius = (n: CutNode) => nodeRadius(n.passes, scale.maxPasses);
  const visiblePairs = net.pairs.filter((p) => p.n >= minPasses);
  const hasSel = selectedId !== null && byId.has(selectedId);

  const linked = new Set<number>();
  if (hasSel) {
    for (const p of visiblePairs) {
      if (p.a === selectedId) linked.add(p.b);
      if (p.b === selectedId) linked.add(p.a);
    }
  }

  // thin first so the thick lines are drawn on top
  const lines = visiblePairs
    .filter((p) => !hasSel || (p.a !== selectedId && p.b !== selectedId))
    .slice()
    .sort((p, q) => p.n - q.n);

  const visiblePairKeys = new Set(visiblePairs.map((p) => key(p.a, p.b)));
  const arrows = hasSel
    ? net.edges
        .filter((e) => (e.from === selectedId || e.to === selectedId) && visiblePairKeys.has(key(e.from, e.to)))
        // received first, then given on top; thin before thick
        .sort((e, f) => Number(e.from === selectedId) - Number(f.from === selectedId) || e.n - f.n)
    : [];

  const onKey = (playerId: number) => (event: KeyboardEvent) => {
    if (event.key === "Enter" || event.key === " ") {
      event.preventDefault();
      onSelect(playerId);
    }
  };

  return (
    <Pitch label={copy.pitchLabel(team.article, team.displayName)} corner={copy.attack}>
      <g>
        {lines.map((p) => {
          const a = byId.get(p.a)!;
          const b = byId.get(p.b)!;
          const style = lineStyle(p.n, scale.maxPair);
          return (
            <line
              key={key(p.a, p.b)}
              x1={a.ball.x}
              y1={a.ball.y}
              x2={b.ball.x}
              y2={b.ball.y}
              stroke={team.colors.line}
              strokeOpacity={hasSel ? 0.08 : style.opacity}
              strokeWidth={style.width * PX}
              strokeLinecap="round"
              className={styles.line}
            >
              <title>{copy.pairTitle(a.name, b.name, p.n)}</title>
            </line>
          );
        })}
      </g>

      <g>
        {arrows.map((e) => {
          const from = byId.get(e.from)!;
          const to = byId.get(e.to)!;
          const shape = arrowShape(from.ball, to.ball, radius(from), radius(to), arrowWidth(e.n, scale.maxDirected));
          if (!shape) return null;
          const out = e.from === selectedId;
          return (
            <polygon
              key={`${e.from}-${e.to}`}
              points={polygonPoints(shape.points)}
              fill={out ? team.colors.line : INCOMING}
              fillOpacity={out ? 0.95 : 0.85}
              className={styles.arrow}
            >
              <title>{copy.arrowTitle(from.name, to.name, e.n)}</title>
            </polygon>
          );
        })}
      </g>

      {hasSel && ghost && <Ghost from={byId.get(selectedId!)!.ball} at={ghost} r={radius(byId.get(selectedId!)!)} />}

      <g>
        {net.nodes.map((n) => {
          const r = radius(n);
          const isSel = n.playerId === selectedId;
          const dim = hasSel && !isSel && !linked.has(n.playerId);
          const label = labelPlacement(n.ball, r, n.label);
          return (
            <g
              key={n.playerId}
              role="button"
              tabIndex={0}
              aria-label={copy.nodeAria(n.name, n.num, n.passes)}
              aria-pressed={isSel}
              className={styles.node}
              opacity={dim ? 0.3 : 1}
              onClick={() => onSelect(n.playerId)}
              onKeyDown={onKey(n.playerId)}
            >
              {/* invisible hit area: at least 44 px on the reference pitch */}
              <circle cx={n.ball.x} cy={n.ball.y} r={Math.max(r, 22) * PX} className={styles.hit} />
              {isSel && <circle cx={n.ball.x} cy={n.ball.y} r={(r + 4) * PX} className={styles.ring} />}
              {/* pitch-colored halo separating the node from the lines behind it */}
              <circle cx={n.ball.x} cy={n.ball.y} r={(r + 2) * PX} className={styles.halo} />
              <circle
                cx={n.ball.x}
                cy={n.ball.y}
                r={r * PX}
                fill={team.colors.fill}
                stroke={team.colors.line}
                strokeWidth={2 * PX}
                className={styles.disc}
              />
              {n.num !== null && (
                <text
                  x={n.ball.x}
                  y={n.ball.y}
                  fill={team.colors.ink}
                  fontSize={(9 + r * 0.32) * PX}
                  textAnchor="middle"
                  dominantBaseline="central"
                  className={styles.num}
                >
                  {n.num}
                </text>
              )}
              <text
                x={label.x}
                y={label.y}
                fontSize={12 * PX}
                textAnchor={label.anchor}
                dominantBaseline={label.baseline}
                className={styles.label}
              >
                {n.name}
              </text>
            </g>
          );
        })}
      </g>
    </Pitch>
  );
}

/** Dashed circle at the "sem bola" position, joined to the node by a dashed line. */
function Ghost({ from, at, r }: { from: { x: number; y: number }; at: { x: number; y: number }; r: number }) {
  return (
    <g aria-hidden="true" className={styles.ghost}>
      <line x1={from.x} y1={from.y} x2={at.x} y2={at.y} />
      <circle cx={at.x} cy={at.y} r={r * PX} />
      <text x={at.x} y={at.y + (r + 3) * PX} fontSize={11 * PX} textAnchor="middle" dominantBaseline="hanging">
        {copy.ghost}
      </text>
    </g>
  );
}

function key(a: number, b: number): string {
  return a < b ? `${a}-${b}` : `${b}-${a}`;
}
