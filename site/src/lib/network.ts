import type { CutKey, TeamData, TeamNetwork } from "../types/data";

export type NetworkKey = "full" | CutKey;

/** Period × "só jogo aberto" → which exported network to draw (CLAUDE.md 5.9). Picks, never computes. */
export function cutKey(untilFirstSub: boolean, openPlay: boolean): NetworkKey {
  if (untilFirstSub) return openPlay ? "firstSubOpen" : "firstSub";
  return openPlay ? "openPlay" : "full";
}

export function networkOf(team: TeamData, key: NetworkKey): TeamNetwork {
  return key === "full" ? { completed: team.passes.completed, nodes: team.nodes, edges: team.edges, pairs: team.pairs } : team.cuts[key];
}
