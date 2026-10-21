// Interface copy (pt-BR). Every user-visible string lives here so an English
// version only needs a second file with the same shape.

export const links = {
  linkedin: "https://www.linkedin.com/in/leonardo-taschin/",
  github: null as string | null, // [SEU LINK]
  email: null as string | null, // [SEU E-MAIL]
  statsbomb: "https://github.com/statsbomb/open-data",
};

export const site = {
  name: "F.I.L",
  fullName: "Football Intelligence Lab",
  author: "Leonardo Taschin",
  attribution: "Dados: StatsBomb Open Data",
  footerLeft: "F.I.L · Football Intelligence Lab · Leonardo Taschin",
  footerRight: "Dados de eventos: StatsBomb Open Data",
  loading: "Carregando…",
  loadError: "Não foi possível carregar os dados.",
  notFoundTitle: "Página não encontrada",
  notFoundBack: "Voltar para o início",
};

export const nav = {
  label: "Principal",
  projects: "Projetos",
  campaign: "Campanha 1970",
  methodology: "Metodologia",
  about: "Sobre",
};

const COMPETITIONS: Record<string, string> = { "FIFA World Cup": "Copa do Mundo" };
export const competitionPt = (name: string) => COMPETITIONS[name] ?? name;

/** "o Brasil" / "a Itália" */
export const withArticle = (article: "o" | "a", name: string) => `${article} ${name}`;
/** "do Brasil" / "da Itália" */
export const ofTeam = (article: "o" | "a", name: string) => `${article === "o" ? "do" : "da"} ${name}`;
const capitalize = (s: string) => s.charAt(0).toUpperCase() + s.slice(1);

const COUNT: Record<number, string> = { 2: "duas", 3: "três", 4: "quatro", 5: "cinco" };

function listPt(items: string[]): string {
  return items.length <= 1 ? items.join("") : `${items.slice(0, -1).join(", ")} e ${items[items.length - 1]}`;
}

export const match = {
  breadcrumbCampaign: "Campanha 1970",
  gameLabel: (order: number, stage: string) => `Jogo ${order} · ${stage}`,
  prev: (order: number, opponent: string) => `← Jogo ${order} · ${opponent}`,
  next: (order: number, opponent: string) => `Jogo ${order} · ${opponent} →`,
  project: "F.I.L · Projeto 01",
  context: (stage: string, competition: string, date: string, stadium: string | null) =>
    [stage === "Final" ? `Final da ${competition}` : `${stage} · ${competition}`, date, stadium].filter(Boolean).join(" · "),
  finding: (p: {
    article: "o" | "a"; team: string; completed: number; diff: number;
    oppArticle: "o" | "a"; opponent: string; pair: [string, string]; pairN: number;
  }) => ({
    lead: `${capitalize(withArticle(p.article, p.team))} completou ${p.completed} passes, ${Math.abs(p.diff)} a ${
      p.diff >= 0 ? "mais" : "menos"
    } que ${withArticle(p.oppArticle, p.opponent)}, e fez o jogo girar pelo eixo `,
    pair: `${p.pair[0]} – ${p.pair[1]}`,
    tail: `: ${p.pairN} passes entre os dois. Clique em um jogador para ver para quem ele passou e de quem recebeu.`,
  }),
  minPasses: "Mínimo de passes por dupla",
  legendSize: "Tamanho = passes completos",
  legendWidth: "Espessura = passes da dupla",
  teamSummary: (completed: number, accuracy: string) => `${completed} passes completos · ${accuracy} de acerto`,
  attack: "ATAQUE →",
  pitchLabel: (article: "o" | "a", team: string) => `Rede de passes ${ofTeam(article, team)}`,
  nodeAria: (name: string, num: number | null, passes: number) =>
    `${name}${num !== null ? `, camisa ${num}` : ""}, ${passes} passes completos`,
  pairTitle: (a: string, b: string, n: number) => `${a} – ${b}: ${n} passes`,
  arrowTitle: (a: string, b: string, n: number) => `${a} → ${b}: ${n} ${n === 1 ? "passe" : "passes"}`,
  noSubs: "Sem substituições: os 11 jogadores estiveram juntos em campo os 90 minutos.",
  // "Juliano entrou no lugar de Bertini (74′) e Rivera no de Boninsegna (83′)."
  subsNote: (subs: { inName: string; outName: string; minute: number }[]) =>
    listPt(subs.map((s, i) => `${s.inName} ${i === 0 ? "entrou no lugar" : "no"} de ${s.outName} (${s.minute}′)`)) + ".",
  hint: "Selecione um jogador em qualquer um dos campos. As setas mostram a direção dos passes: na cor do time, os que ele deu; em cinza-escuro, os que recebeu.",
  hintButton: (name: string) => `Ver a rede do ${name}`,
  clear: "Limpar seleção",
  panel: {
    passes: "passes dados",
    received: "passes recebidos",
    share: "dos passes do time",
    passedTo: "Passou para",
    receivedFrom: "Recebeu de",
    subOut: (minute: number, other: string) => `Saiu aos ${minute}′ (entrou ${other})`,
    subIn: (minute: number, other: string) => `Entrou aos ${minute}′ no lugar de ${other}`,
    fromReceived: "Sem passes completos: posição estimada por onde recebeu a bola.",
  },
  topTitle: (team: string) => `Top 10 combinações · ${team}`,
  topLegend: "→ ida · ← volta",
  topSplit: (forward: number, backward: number) => `→ ${forward}  ·  ← ${backward}`,
  footer: (p: { periods: string; subsLine: string }) =>
    `Passes completos com destinatário identificado, ${p.periods}. Posição do jogador = mediana das localizações dos seus passes completos, não sua posição tática contínua.${
      p.subsLine ? ` ${p.subsLine}` : ""
    }`,
  periods: (periods: number[]) => listPt(periods.map((p) => (p <= 2 ? `${p}º tempo` : `período ${p}`))).replace(/º tempo e (\d)º tempo/, "º e $1º tempos"),
  footerSubs: (teams: { name: string; article: "o" | "a"; minutes: number[] }[]) => {
    const withSubs = teams.filter((t) => t.minutes.length > 0);
    const without = teams.filter((t) => t.minutes.length === 0);
    const parts = withSubs.map(
      (t) => `${capitalize(withArticle(t.article, t.name))} fez ${t.minutes.length === 1 ? "uma substituição" : `${COUNT[t.minutes.length] ?? t.minutes.length} substituições`} (${listPt(t.minutes.map((m) => `${m}′`))}), então sua rede inclui jogadores que não estiveram em campo ao mesmo tempo`,
    );
    const rest = without.map((t) => `${withArticle(t.article, t.name)} jogou com os mesmos 11`);
    return parts.length ? `${parts.join("; ")}${rest.length ? `; ${rest.join("; ")}` : ""}.` : "Nenhuma das equipes fez substituições.";
  },
};
