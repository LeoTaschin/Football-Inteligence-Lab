import { Link, useParams, useSearchParams } from "react-router-dom";

import { CombinationTable } from "../components/CombinationTable";
import { GoalReplay } from "../components/GoalReplay";
import { NetworkTab } from "../components/NetworkTab";
import { PhaseMorph } from "../components/PhaseMorph";
import { ShotsPanel, type ShotRef } from "../components/ShotsPanel";
import { NotFound, Status } from "../components/Status";
import { TabPanel, Tabs } from "../components/Tabs";
import { competitionPt, match as copy, goals as goalsCopy, site, tabs as tabsCopy } from "../content/pt";
import { useCollection, useMatch } from "../lib/data";
import { formatDate } from "../lib/format";
import type { CampaignMatch, MatchData, TeamData } from "../types/data";
import styles from "./Match.module.css";

const MIN_OPTIONS = [3, 5, 8];
const TABS = [
  { key: "rede", label: tabsCopy.network },
  { key: "fases", label: tabsCopy.phases },
  { key: "gols", label: tabsCopy.goals },
  { key: "finalizacoes", label: tabsCopy.shots },
] as const;
type TabKey = (typeof TABS)[number]["key"];

export function Match() {
  const { matchId } = useParams();
  const id = Number(matchId);
  const valid = Number.isInteger(id) && id > 0;
  const state = useMatch(valid ? id : null);
  const collection = useCollection();

  if (!valid) return <NotFound />;
  if (state.status !== "ready") return <Status state={state} />;
  const campaign = collection.status === "ready" ? collection.data.matches : [];
  return <MatchView key={id} data={state.data} campaign={campaign} />;
}

/** Tab, team, cut, selection, filter, goal and shot live in the URL (?aba=gols&gol=4, ?equipe=2&periodo=1sub&aberto=1,
 *  ?jogador=397621&min=5, ?aba=finalizacoes&chute=1-27) so a post can link straight to them. */
function useMatchParams(data: MatchData) {
  const [params, setParams] = useSearchParams();
  const min = Number(params.get("min"));
  const minPasses = MIN_OPTIONS.includes(min) ? min : MIN_OPTIONS[0];
  const pid = Number(params.get("jogador"));
  const playerTeam = data.teams.findIndex((t) => t.nodes.some((n) => n.playerId === pid));
  const teamParam = Number(params.get("equipe")) - 1;
  // ?equipe wins; without it, the team of ?jogador; else the analysed team
  const team = teamParam === 0 || teamParam === 1 ? teamParam : Math.max(playerTeam, 0);
  const selectedId = playerTeam === team ? pid : null;
  const untilFirstSub = params.get("periodo") === "1sub";
  const openPlay = params.get("aberto") === "1";
  const tabParam = params.get("aba");
  const tab: TabKey = TABS.some((t) => t.key === tabParam) ? (tabParam as TabKey) : "rede";
  const goalParam = Number(params.get("gol"));
  const goal = Number.isInteger(goalParam) && goalParam >= 1 && goalParam <= data.goals.length ? goalParam - 1 : 0;
  const shot = parseShot(params.get("chute"), data) ?? defaultShot(data);

  const update = (changes: Record<string, string | null>) =>
    setParams(
      (prev) => {
        const next = new URLSearchParams(prev);
        for (const [k, v] of Object.entries(changes)) {
          if (v === null) next.delete(k);
          else next.set(k, v);
        }
        return next;
      },
      { replace: true, preventScrollReset: true },
    );

  return {
    minPasses,
    setMinPasses: (m: number) => update({ min: m === MIN_OPTIONS[0] ? null : String(m) }),
    team,
    setTeam: (i: number) => update({ equipe: i === 0 ? null : String(i + 1), jogador: null }),
    untilFirstSub,
    setUntilFirstSub: (on: boolean) => update({ periodo: on ? "1sub" : null }),
    openPlay,
    setOpenPlay: (on: boolean) => update({ aberto: on ? "1" : null }),
    selectedId,
    toggle: (playerId: number) => update({ jogador: selectedId === playerId ? null : String(playerId) }),
    clear: () => update({ jogador: null }),
    tab,
    setTab: (k: TabKey) => update({ aba: k === "rede" ? null : k }),
    goal,
    setGoal: (i: number) => update({ gol: String(i + 1) }),
    shot,
    setShot: (ref: ShotRef) => update({ chute: `${ref.team + 1}-${ref.index + 1}` }),
  };
}

function MatchView({ data, campaign }: { data: MatchData; campaign: CampaignMatch[] }) {
  const params = useMatchParams(data);
  const { tab, setTab, goal, setGoal, shot, setShot } = params;
  const { match, teams } = data;

  const pos = campaign.findIndex((m) => m.id === match.id);
  const current = pos >= 0 ? campaign[pos] : null;
  const prev = pos > 0 ? campaign[pos - 1] : null;
  const next = pos >= 0 && pos < campaign.length - 1 ? campaign[pos + 1] : null;

  const [home, away] = teams;
  const focus = home; // the analysed team is listed first in the collection
  const topPair = focus.pairs[0];
  const nameOf = (team: TeamData, pid: number) => team.nodes.find((n) => n.playerId === pid)?.name ?? "";
  const finding = topPair
    ? copy.finding({
        article: focus.article,
        team: focus.displayName,
        completed: focus.passes.completed,
        diff: focus.passes.completed - away.passes.completed,
        oppArticle: away.article,
        opponent: away.displayName,
        pair: [nameOf(focus, topPair.a), nameOf(focus, topPair.b)],
        pairN: topPair.n,
      })
    : null;

  return (
    <div className={`container ${styles.page}`}>
      <div className={styles.crumbs}>
        <nav aria-label="Trilha" className={styles.breadcrumb}>
          <Link to="/pnsm/1970">{copy.breadcrumbCampaign}</Link>
          <span aria-hidden="true">/</span>
          <span>{current ? copy.gameLabel(current.order, current.stage) : match.stage}</span>
        </nav>
        <div className={styles.pager}>
          {prev && (
            <Link className="button button--secondary button--small" to={`/pnsm/1970/${prev.id}`}>
              {copy.prev(prev.order, prev.opponent)}
            </Link>
          )}
          {next && (
            <Link className="button button--secondary button--small" to={`/pnsm/1970/${next.id}`}>
              {copy.next(next.order, next.opponent)}
            </Link>
          )}
        </div>
      </div>

      <header className={styles.header}>
        <div className={`eyebrow ${styles.eyebrowRow}`}>
          <span>{copy.context(match.stage, competitionPt(match.competition), formatDate(match.date), match.stadium)}</span>
          <span className={styles.project}>{copy.project}</span>
        </div>
        <h1 className={styles.title}>
          {home.displayName} <span style={{ color: home.colors.line }}>{match.score[0]}</span>{" "}
          <span className={styles.times}>×</span> <span style={{ color: away.colors.line }}>{match.score[1]}</span>{" "}
          {away.displayName}
        </h1>
        {finding && (
          <p className={styles.finding}>
            {finding.lead}
            <strong>{finding.pair}</strong>
            {finding.tail}
          </p>
        )}
      </header>

      <Tabs items={[...TABS]} current={tab} onChange={setTab} label={tabsCopy.label} idPrefix="partida" />

      {tab === "rede" && (
        <TabPanel idPrefix="partida" tab="rede">
          <NetworkTab
            data={data}
            team={params.team}
            onTeam={params.setTeam}
            untilFirstSub={params.untilFirstSub}
            onUntilFirstSub={params.setUntilFirstSub}
            openPlay={params.openPlay}
            onOpenPlay={params.setOpenPlay}
            minPasses={params.minPasses}
            onMinPasses={params.setMinPasses}
            selectedId={params.selectedId}
            onSelect={params.toggle}
            onClear={params.clear}
          />
        </TabPanel>
      )}

      {tab === "fases" && (
        <TabPanel idPrefix="partida" tab="fases">
          <PhaseMorph teams={teams} />
        </TabPanel>
      )}

      {tab === "gols" && (
        <TabPanel idPrefix="partida" tab="gols">
          {data.goals.length === 0 ? (
            <p className={styles.empty}>{goalsCopy.none}</p>
          ) : (
            <>
              <div className={styles.goalList} role="group" aria-label={goalsCopy.listTitle}>
                {data.goals.map((g, i) => {
                  const t = teams.find((x) => x.teamId === g.teamId)!;
                  return (
                    <button key={`${g.minute}-${g.scorerId}`} type="button" className="pill" aria-pressed={i === goal} onClick={() => setGoal(i)}>
                      <span className={styles.goalDot} style={{ background: t.colors.fill, borderColor: t.colors.line }} />
                      {goalsCopy.item(g.minute, g.scorer)}
                    </button>
                  );
                })}
              </div>
              <GoalReplay
                key={goal}
                goal={data.goals[goal]}
                team={teams.find((x) => x.teamId === data.goals[goal].teamId)!}
                context={`${match.stage} · ${home.displayName} ${match.score[0]} × ${match.score[1]} ${away.displayName} · ${data.goals[goal].minute}′`}
              />
            </>
          )}
        </TabPanel>
      )}

      {tab === "finalizacoes" && (
        <TabPanel idPrefix="partida" tab="finalizacoes">
          <ShotsPanel data={data} selected={shot} onSelect={setShot} />
        </TabPanel>
      )}

      <div className={styles.tables}>
        {teams.map((team) => (
          <CombinationTable key={team.teamId} team={team} maxPair={data.scale.maxPair} />
        ))}
      </div>

      <footer className={styles.footer}>
        <p>
          {copy.footer({
            periods: copy.periods(data.periods),
            subsLine: copy.footerSubs(
              teams.map((t) => ({ name: t.displayName, article: t.article, minutes: t.substitutions.map((s) => s.minute) })),
            ),
          })}
        </p>
        <p className={styles.credit}>
          {site.attribution}
          <br />
          {site.author} · {site.name}
        </p>
      </footer>
    </div>
  );
}

/** "1-27" → first team, 27th shot (both 1-based in the URL). */
function parseShot(param: string | null, data: MatchData): ShotRef | null {
  const m = /^(\d+)-(\d+)$/.exec(param ?? "");
  if (!m) return null;
  const team = Number(m[1]) - 1;
  const index = Number(m[2]) - 1;
  return data.teams[team]?.shots.items[index] ? { team, index } : null;
}

/** Without ?chute: the analysed team's last goal, else its biggest chance. */
function defaultShot(data: MatchData): ShotRef | null {
  const items = data.teams[0].shots.items;
  for (let i = items.length - 1; i >= 0; i--) if (items[i].result === "goal") return { team: 0, index: i };
  const best = data.teams[0].shots.top[0];
  return best === undefined ? null : { team: 0, index: best };
}
