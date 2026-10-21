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

export interface TeamData {
  teamId: number;
  name: string;
  displayName: string;
  colors: TeamColors;
  passes: {
    attempted: number;
    completed: number;
    excluded: { period: number; incomplete: number; noRecipient: number; noLocation: number };
  };
  nodes: NetworkNode[];
  edges: DirectedEdge[];
  pairs: Pair[];
  substitutions: Substitution[];
  shots: { count: number; goals: number; xg: number; xgCoverage: [number, number] };
  phase: { ballHeight: number; defHeight: number; shiftMeters: number } | null;
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
  scale: { maxPasses: number; maxPair: number; maxDirected: number };
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
  team: string;
  displayName: string;
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
  matches: CampaignMatch[];
  topPassers: { playerId: number; name: string; n: number }[];
  topPairs: { ids: [number, number]; names: [string, string]; n: number }[];
}
