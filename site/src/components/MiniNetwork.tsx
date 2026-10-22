import { lineStyle } from "../lib/geometry";
import type { MiniNetwork as MiniData, TeamColors } from "../types/data";
import { Pitch } from "./Pitch";

interface MiniNetworkProps {
  data: MiniData;
  colors: TeamColors;
  /** maxima shared by every mini network on the page */
  scale: { maxPasses: number; maxPair: number };
  /** px width the sizes are designed for (cards ≈ 340 px, home ≈ 420 px) */
  referenceWidth?: number;
  showNumbers?: boolean;
  /** one player in focus: his pairs strong, everyone else faded */
  highlightId?: number;
}

/** Small non-interactive pass network (campaign cards, home highlight). */
export function MiniNetwork({ data, colors, scale, referenceWidth = 340, showNumbers = false, highlightId }: MiniNetworkProps) {
  const u = 120 / referenceWidth;
  const byId = new Map(data.nodes.map((n) => [n.playerId, n]));
  const radius = (passes: number) =>
    (showNumbers ? 5 + 9 * Math.sqrt(passes / scale.maxPasses) : 3 + 5 * Math.sqrt(passes / scale.maxPasses)) * u;
  const focus = highlightId !== undefined;
  const mine = (e: { a: number; b: number }) => e.a === highlightId || e.b === highlightId;
  // thin first; with a focus, his pairs on top
  const edges = [...data.edges].sort((a, b) => Number(focus && mine(a)) - Number(focus && mine(b)) || a.n - b.n);

  return (
    <div aria-hidden="true" style={{ border: "1px solid var(--line)" }}>
      <Pitch label="" unit={u}>
        {edges.map((e) => {
          const a = byId.get(e.a)!;
          const b = byId.get(e.b)!;
          const style = lineStyle(e.n, scale.maxPair);
          return (
            <line
              key={`${e.a}-${e.b}`}
              x1={a.x}
              y1={a.y}
              x2={b.x}
              y2={b.y}
              stroke={colors.line}
              strokeOpacity={focus ? (mine(e) ? Math.min(0.9, style.opacity + 0.1) : 0.1) : style.opacity}
              // mini: 1 + 4·n/max px instead of 1 + 8·n/max
              strokeWidth={(1 + (4 * e.n) / scale.maxPair) * u}
              strokeLinecap="round"
            />
          );
        })}
        {data.nodes.map((n) => {
          const r = radius(n.passes);
          const isFocus = n.playerId === highlightId;
          return (
            <g key={n.playerId} opacity={focus && !isFocus ? 0.35 : 1}>
              {isFocus && <circle cx={n.x} cy={n.y} r={r + 3.5 * u} fill="none" stroke="var(--text)" strokeWidth={1.5 * u} />}
              <circle cx={n.x} cy={n.y} r={r + 1.5 * u} fill="var(--surface)" />
              <circle cx={n.x} cy={n.y} r={r} fill={colors.fill} stroke={colors.line} strokeWidth={2 * u} />
              {showNumbers && n.num !== null && (
                <text
                  x={n.x}
                  y={n.y}
                  fontSize={(7 + (r / u) * 0.3) * u}
                  fontWeight={800}
                  textAnchor="middle"
                  dominantBaseline="central"
                  fill={colors.ink}
                >
                  {n.num}
                </text>
              )}
            </g>
          );
        })}
      </Pitch>
    </div>
  );
}
