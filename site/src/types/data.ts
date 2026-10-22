// Mirrors the JSON written by engine/src/pnsm/export.py (CLAUDE.md, section 6).
// Change both sides together.

export type LabelSide = "below" | "above" | "left" | "right";
export type Point = [number, number];

export interface TeamColors {
  fill: string;
  line: string;
  ink: string;
}

// --- index.json ---------------------------------------------------------------------

export interface CollectionRef {
  id: string;
  title: string;
  competitionId: number;
  seasonId: number;
  team: string;
  matches: number[];
}

export interface IndexData {
  generatedAt: string;
  source: string;
  collections: CollectionRef[];
}

// --- matches/{id}.json --------------------------------------------------------------

export interface MatchInfo {
  id: number;
  date: string;
  stage: string;
  competition: string;
  season: string;
  stadium: string | null;
  country: string | null;
  home: string;
  away: string;
  score: [number, number];
}

export interface SubInfo {
  type: "in" | "out";
  minute: number;
  with: number;
}

export interface NetworkNode {
  playerId: number;
  num: number | null;
  name: string;
  position: string | null;
  ball: { x: number; y: number };
  positionFrom: "passes" | "received";
  def: { x: number; y: number; n: number; lowSample: boolean } | null;
  shift: number | null;
  passes: number;
  received: number;
  sub: SubInfo | null;
  label: LabelSide;
}

export interface DirectedEdge {
  from: number;
  to: number;
  n: number;
}

export interface Pair {
  a: number; // passed more inside the pair
  b: number;
  forward: number; // a -> b
  backward: number; // b -> a
  n: number;
}

export interface Substitution {
  minute: number;
  out: number;
  in: number;
  reason: string | null;
}

/** The network drawn on the pitch: the full one or a cut. */
export interface TeamNetwork {
  completed: number;
  nodes: CutNode[];
  edges: DirectedEdge[];
  pairs: Pair[];
}

export type CutKey = "firstSub" | "openPlay" | "firstSubOpen";

/** A node of a cut: same as the full network's, without the "sem bola" fields. */
export type CutNode = Omit<NetworkNode, "def" | "shift">;

/** One of the network cuts of CLAUDE.md 5.9, compared with the full network. */
export interface NetworkCut {
  completed: number;
  sameAsFull: boolean;
  /** the team's first substitution, for the cuts "até a 1ª substituição" */
  cutAt: { minute: number; out: number; in: number } | null;
  /** set-piece passes removed by "só jogo aberto", by StatsBomb pass.type */
  removed: Record<"Corner" | "Free Kick" | "Throw-in" | "Goal Kick" | "Kick Off", number> | null;
  highlights: {
    shift: { playerId: number; meters: number } | null;
    drop: { playerId: number; from: number; to: number } | null;
  };
  nodes: CutNode[];
  edges: DirectedEdge[];
  pairs: Pair[];
}

export interface TeamData {
  teamId: number;
  name: string;
  displayName: string;
  article: "o" | "a";
  colors: TeamColors;
  passes: {
    attempted: number;
    completed: number;
    excluded: { period: number; incomplete: number; noRecipient: number; noLocation: number };
  };
  nodes: NetworkNode[];
  edges: DirectedEdge[];
  pairs: Pair[];
  cuts: Record<CutKey, NetworkCut>;
  substitutions: Substitution[];
  shots: {
    count: number;
    goals: number;
    xg: number;
    /** xG ÷ shots with xG; null when no shot has xG */
    xgPerShot: number | null;
    xgCoverage: [number, number];
    items: Shot[];
    /** indices in `items` of the highest-xG chances, best first */
    top: number[];
  };
  phase: { ballHeight: number; defHeight: number; shiftMeters: number } | null;
}

export type ShotResult = "goal" | "saved" | "post" | "blocked" | "off" | "other";

/** One shot in its team's frame (attacking towards x = 120). Missing values are null, never 0. */
export interface Shot {
  period: number;
  minute: number;
  second: number;
  playerId: number;
  name: string;
  num: number | null;
  x: number | null;
  y: number | null;
  /** metres from the centre of the goal */
  distance: number | null;
  /** end location: [x, y] or [x, y, z] */
  end: number[] | null;
  /** original StatsBomb shot.outcome */
  outcome: string;
  result: ShotResult;
  xg: number | null;
  shotType: "openPlay" | "freeKick" | "penalty" | "corner" | "kickOff" | "other";
  setPiece: boolean;
  bodyPart: "rightFoot" | "leftFoot" | "head" | "other";
}

export interface GoalSegment {
  t: number;
  d: number;
  from: Point;
  to: Point;
  kind: "pass" | "carry" | "shot";
}

export interface GoalTouch {
  t: number;
  playerId: number;
  num: number | null;
  name: string;
  at: Point;
  label: LabelSide;
}

export interface Goal {
  teamId: number;
  team: string;
  minute: number;
  scorerId: number;
  scorer: string;
  duration: number;
  passes: number;
  players: number;
  segments: GoalSegment[];
  touches: GoalTouch[];
  steps: { t: number; text: string }[];
}

export interface MatchData {
  match: MatchInfo;
  periods: number[];
  scale: {
    maxPasses: number;
    maxPair: number;
    maxDirected: number;
    /** the shot map is drawn from this x up to 120 (60 = half pitch) */
    shotsFromX: number;
  };
  teams: [TeamData, TeamData];
  goals: Goal[];
  validation: Record<string, boolean>;
}

// --- collections/{id}.json ----------------------------------------------------------

export interface MiniNetwork {
  nodes: { playerId: number; num: number | null; x: number; y: number; passes: number }[];
  edges: { a: number; b: number; n: number }[];
}

export interface CampaignMatch {
  id: number;
  order: number;
  stage: string;
  opponent: string;
  opponentName: string;
  score: [number, number];
  completed: number;
  attempted: number;
  opponentCompleted: number;
  xg: number;
  opponentXg: number;
  topPair: { ids: [number, number]; names: [string, string]; n: number };
  mini: MiniNetwork;
  note: string | null;
}

export interface CollectionData {
  id: string;
  title: string;
  competition: string;
  season: string;
  country: string | null;
  team: string;
  displayName: string;
  article: "o" | "a";
  colors: TeamColors;
  summary: {
    played: number;
    wins: number;
    draws: number;
    losses: number;
    goalsFor: number;
    goalsAgainst: number;
    completed: number;
    attempted: number;
    accuracy: number | null;
    xgFor: number;
    xgAgainst: number;
    morePassesThanOpponent: number;
  };
  scale: { maxPasses: number; maxPair: number };
  matches: CampaignMatch[];
  topPassers: { playerId: number; name: string; n: number; position: string | null; missed: string[] }[];
  topPairs: { ids: [number, number]; names: [string, string]; n: number }[];
}
