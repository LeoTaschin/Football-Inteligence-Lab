import { network as copy, match as matchCopy } from "../content/pt";
import { formatPercent } from "../lib/format";
import { cutKey, networkOf } from "../lib/network";
import type { MatchData, TeamData } from "../types/data";
import { PassNetwork } from "./PassNetwork";
import { PlayerPanel } from "./PlayerPanel";
import { TeamSwitch } from "./TeamSwitch";
import layout from "./SplitLayout.module.css";
import styles from "./NetworkTab.module.css";

const MIN_OPTIONS = [3, 5, 8];
const TOP_PAIRS = 5;
const INCOMING = "#52525B";

interface NetworkTabProps {
  data: MatchData;
  team: number;
  onTeam: (index: number) => void;
  untilFirstSub: boolean;
  onUntilFirstSub: (on: boolean) => void;
  openPlay: boolean;
  onOpenPlay: (on: boolean) => void;
  minPasses: number;
  onMinPasses: (n: number) => void;
  selectedId: number | null;
  onSelect: (playerId: number) => void;
  onClear: () => void;
}

/** "Rede de passes": one team at a time, pitch on the left, the network's story on the right. */
export function NetworkTab(p: NetworkTabProps) {
  const team = p.data.teams[p.team];
  const key = cutKey(p.untilFirstSub, p.openPlay);
  const net = networkOf(team, key);
  const nameOf = (pid: number) => team.nodes.find((n) => n.playerId === pid)?.name ?? "";
  const selected = p.selectedId !== null && net.nodes.some((n) => n.playerId === p.selectedId) ? p.selectedId : null;
  const missing = p.selectedId !== null && selected === null ? nameOf(p.selectedId) : null;

  return (
    <div className={layout.tab}>
      <div className={layout.head}>
        <h2 className={layout.title}>{copy.title(team.article, team.displayName)}</h2>
        <TeamSwitch teams={p.data.teams} current={p.team} onChange={p.onTeam} label={copy.teamLabel} />
      </div>

      <div className={layout.body}>
        <div className={layout.main}>
          <div className={styles.controls}>
            <div className={styles.group} role="group" aria-label={copy.periodLabel}>
              {([false, true] as const).map((until) => (
                <button key={String(until)} type="button" className="pill" aria-pressed={p.untilFirstSub === until} onClick={() => p.onUntilFirstSub(until)}>
                  {until ? copy.periods.firstSub : copy.periods.full}
                </button>
              ))}
            </div>
            <button type="button" className={`pill ${styles.toggle}`} aria-pressed={p.openPlay} onClick={() => p.onOpenPlay(!p.openPlay)}>
              <span className={styles.track} aria-hidden="true">
                <span className={styles.knob} />
              </span>
              {copy.openPlay}
            </button>
            <div className={styles.group} role="group" aria-label={matchCopy.minPasses}>
              <span className={styles.groupLabel}>{matchCopy.minPasses}</span>
              {MIN_OPTIONS.map((m) => (
                <button key={m} type="button" className="pill" aria-pressed={m === p.minPasses} onClick={() => p.onMinPasses(m)}>
                  {m}+
                </button>
              ))}
            </div>
          </div>

          <div className={styles.pitchScroll}>
            <div className={styles.pitchBox}>
              <PassNetwork team={team} net={net} scale={p.data.scale} minPasses={p.minPasses} selectedId={selected} onSelect={p.onSelect} />
            </div>
          </div>

          <ul className={layout.legend} aria-label="Legenda">
            <li>
              <span className={styles.dotBig} />
              <span className={styles.dotSmall} />
              {matchCopy.legendSize}
            </li>
            <li>
              <span className={styles.bar} />
              {matchCopy.legendWidth}
            </li>
            <li>
              <Arrow color={team.colors.line} />
              {copy.legendGiven}
            </li>
            <li>
              <Arrow color={INCOMING} />
              {copy.legendReceived}
            </li>
          </ul>
          <p className={layout.caption}>{selected !== null ? copy.captionSelected(nameOf(selected)) : copy.captionAll(p.minPasses)}</p>
        </div>

        <aside className={layout.aside}>
          <div className={layout.summary}>
            <span className={layout.big}>{net.completed}</span>
            <span className={layout.summaryText}>
              {key === "full"
                ? copy.summaryFull(team.passes.attempted, formatPercent(team.passes.completed, team.passes.attempted))
                : copy.summaryCut(team.passes.completed - net.completed, team.passes.completed)}
            </span>
          </div>

          <div className={styles.notice}>
            <svg width="18" height="18" viewBox="0 0 18 18" fill="none" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" aria-hidden="true">
              <circle cx="9" cy="9" r="7.2" />
              <path d="M9 8.2v4.6M9 5.4v.1" />
            </svg>
            <p>{notice(team, key, nameOf)}</p>
          </div>

          {selected !== null ? (
            <PlayerPanel team={team} net={net} playerId={selected} onClear={p.onClear} />
          ) : (
            <p className={layout.hint}>{missing ? `${copy.notInCut(missing)} ${copy.hint}` : copy.hint}</p>
          )}

          <section className={styles.pairs}>
            <div className={styles.pairsHead}>
              <h3>{copy.pairsTitle}</h3>
              <span>{copy.pairsLegend}</span>
            </div>
            {net.pairs.slice(0, TOP_PAIRS).map((pair) => {
              const a = nameOf(pair.a);
              const b = nameOf(pair.b);
              return (
                <button
                  key={`${pair.a}-${pair.b}`}
                  type="button"
                  className={styles.pairRow}
                  aria-label={copy.pairsAria(a, b, pair.n)}
                  onClick={() => p.onSelect(pair.a)}
                >
                  <span className={styles.pairNames}>
                    <span>{`${a} – ${b}`}</span>
                    <span className={styles.pairSplit}>{matchCopy.topSplit(pair.forward, pair.backward)}</span>
                  </span>
                  <span className={styles.track2}>
                    <span style={{ width: `${(100 * pair.n) / p.data.scale.maxPair}%`, background: team.colors.line }} />
                  </span>
                  <span className={styles.pairN}>{pair.n}</span>
                </button>
              );
            })}
          </section>
        </aside>
      </div>
    </div>
  );
}

/** The cut's notice, built only from exported facts (CLAUDE.md 5.9). */
function notice(team: TeamData, key: ReturnType<typeof cutKey>, nameOf: (pid: number) => string): string {
  if (key === "full") {
    if (team.substitutions.length === 0) return copy.full(null);
    return copy.full(matchCopy.subsNote(team.substitutions.map((s) => ({ inName: nameOf(s.in), outName: nameOf(s.out), minute: s.minute }))));
  }
  const cut = team.cuts[key];
  const full = team.passes.completed;
  const removedTotal = Object.values(cut.removed ?? {}).reduce((a, b) => a + b, 0);
  const head =
    key === "firstSub"
      ? copy.firstSub({ article: team.article, team: team.displayName, same: cut.sameAsFull, minute: cut.cutAt?.minute, out: cut.cutAt ? nameOf(cut.cutAt.out) : undefined, n: cut.completed, full })
      : key === "openPlay"
        ? copy.openPlayNotice(cut.removed ?? {})
        : copy.firstSubOpen({ same: team.cuts.firstSub.sameAsFull, minute: cut.cutAt?.minute, n: cut.completed, full, removed: removedTotal });
  const { shift, drop } = cut.highlights;
  const extra = [
    shift ? copy.shift(nameOf(shift.playerId), shift.meters) : null,
    drop ? copy.drop(nameOf(drop.playerId), drop.from, drop.to) : null,
  ].filter(Boolean);
  return [head, ...extra].join(" ");
}

function Arrow({ color }: { color: string }) {
  return (
    <svg width="30" height="10" viewBox="0 0 30 10" aria-hidden="true">
      <path d="M1 4h20V1l8 4-8 4V6H1z" fill={color} />
    </svg>
  );
}
