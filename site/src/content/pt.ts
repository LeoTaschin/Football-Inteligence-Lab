import type { ShotFinish } from "../types/data";

// Interface copy (pt-BR). Every user-visible string lives here so an English
// version only needs a second file with the same shape.

export const links = {
  linkedin: "https://br.linkedin.com/in/leonardo-taschin",
  github: "https://github.com/LeoTaschin/" as string | null,
  repo: "https://github.com/LeoTaschin/Football-Inteligence-Lab" as string | null,
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
  ghost: "sem bola",
  playerLink: (name: string) => `Ver ${name} na campanha →`,
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
      (t) => `${withArticle(t.article, t.name)} fez ${t.minutes.length === 1 ? "uma substituição" : `${COUNT[t.minutes.length] ?? t.minutes.length} substituições`} (${listPt(t.minutes.map((m) => `${m}′`))}), então sua rede inclui jogadores que não estiveram em campo ao mesmo tempo`,
    );
    const rest = without.map((t) => `${withArticle(t.article, t.name)} jogou com os mesmos 11`);
    // only the start of the sentence is capitalized: "O Brasil fez …; o Peru fez …"
    return parts.length ? capitalize(`${parts.join("; ")}${rest.length ? `; ${rest.join("; ")}` : ""}.`) : "Nenhuma das equipes fez substituições.";
  },
};

export const tabs = {
  label: "Visualizações da partida",
  network: "Rede de passes",
  phases: "Com bola × sem bola",
  goals: "Gols",
  shots: "Finalizações",
};

export const phases = {
  title: (article: "o" | "a", team: string) => `${capitalize(withArticle(article, team))} com e sem a bola`,
  withBall: "Com bola",
  withoutBall: "Sem bola",
  animate: "Animar",
  pause: "Pausar animação",
  teamPicker: "Equipe",
  blockLine: "Altura média do time",
  attack: (article: "o" | "a", team: string) => `ATAQUE ${ofTeam(article, team).toUpperCase()} →`,
  captionWith: "Com bola: cada círculo está na mediana de onde o jogador completou passes. O tracejado mostra para onde ele vai sem a bola.",
  captionWithout: "Sem bola: cada círculo está na mediana das ações defensivas do jogador. O tracejado mostra onde ele estava com a bola.",
  bigNumber: (meters: number) => `${Math.abs(meters).toFixed(1).replace(".", ",")} m`,
  bigText: (meters: number) =>
    `é quanto o time ${meters <= 0 ? "recua" : "avança"}, em média, entre as ações com bola e as ações sem bola.`,
  shiftsTitle: "Quanto cada um se desloca",
  shift: (meters: number) => `${meters > 0 ? "+" : "−"}${Math.round(Math.abs(meters))} m`,
  mostShift: (name: string, meters: number) => ({ name, text: ` é quem mais muda: cerca de ${Math.round(Math.abs(meters))} m entre atacar e defender.` }),
  forward: (names: string[]) =>
    names.length === 1
      ? { name: names[0], text: " é o único cujas ações sem bola acontecem mais à frente que as com bola." }
      : { name: listPt(names), text: " têm ações sem bola mais à frente que as com bola." },
  lowSample: "* poucas ações defensivas (menos de 5): posição sem bola pouco confiável.",
  noDefense: (names: string[]) => `Sem ações defensivas registradas: ${listPt(names)}.`,
  method:
    "Com bola: mediana de onde o jogador completou passes. Sem bola: mediana das suas ações defensivas (pressões, recuperações, duelos, interceptações, cortes e bloqueios). São posições médias das ações, não a posição real sem a bola. Goleiro fora da altura média.",
};

export const goals = {
  listTitle: "Gols da partida",
  none: "Nenhum gol de jogada nesta partida.",
  item: (minute: number, scorer: string) => `${minute}′ · ${scorer}`,
  title: (scorer: string) => `O gol de ${scorer}, passe a passe`,
  context: (team: string, score: string, minute: number) => `${team} · ${score} · ${minute}′`,
  passes: "passes",
  players: "jogadores",
  // truncated like the replay clock (29.86 s -> "29 s", clock 0:29)
  seconds: (s: number) => `${Math.floor(s)} s`,
  duration: "do início da jogada ao gol",
  play: "Reproduzir",
  pause: "Pausar",
  restart: "Recomeçar",
  timeline: "Linha do tempo da jogada",
  speed: "Velocidade",
  speedLabel: (v: number) => `${String(v).replace(".", ",")}×`,
  stepsTitle: "A jogada",
  goal: (scorer: string) => `GOL · ${scorer}`,
  attack: "ATAQUE →",
  method:
    "Cada círculo marca onde o jogador tocou na bola; linha cheia é passe, tracejada é condução. Os dados de eventos não registram onde os jogadores estavam sem a bola.",
  ownGoalNote: "Gols contra não são chutes e não têm replay.",
};

export const campaign = {
  breadcrumbProjects: "Projetos",
  breadcrumbProject: "01 · PNSM",
  eyebrow: (competition: string, season: string, country: string | null) =>
    `${competition} de ${season}${country ? ` · ${country}` : ""}`,
  title: (article: "o" | "a", team: string, season: string) => `Como ${withArticle(article, team)} de ${season} trocava a bola`,
  // "O lateral Carlos Alberto foi quem mais passou na Copa, 367 passes completos, e está nas duas duplas mais usadas do time."
  finding: (p: { role: string | null; name: string; n: number; inTopPairs: number; matches: number }) => ({
    lead: `Redes de passes dos ${COUNT_WORDS_M[p.matches] ?? p.matches} jogos da campanha. ${p.role ? `O ${p.role.toLowerCase()} ` : ""}`,
    name: p.name,
    tail: ` foi quem mais passou, ${formatThousands(p.n)} passes completos${
      p.inTopPairs >= 2 ? `, e está nas ${COUNT_WORDS_F[p.inTopPairs] ?? p.inTopPairs} duplas mais usadas do time` : p.inTopPairs === 1 ? ", e está na dupla mais usada do time" : ""
    }.`,
  }),
  summaryLabel: "Resumo da campanha",
  wins: "vitórias",
  goals: "gols marcados e sofridos",
  passes: (accuracy: string) => `passes completos · ${accuracy} de acerto`,
  xg: "xG a favor e contra",
  morePasses: "jogos com mais passes que o adversário",
  outOf: (a: number, b: number) => `${a} de ${b}`,
  gamesTitle: (n: number) => `Os ${COUNT_WORDS_M[n] ?? n} jogos`,
  gamesHint: "Selecione um jogo para ver a rede completa",
  gameLabel: (order: number, stage: string) => `Jogo ${order} · ${stage}`,
  champion: "Campeão",
  win: "Vitória",
  draw: "Empate",
  loss: "Derrota",
  cardCompleted: "Passes completos",
  cardXg: "xG",
  cardPair: "Dupla mais usada",
  cardPairValue: (a: string, b: string, n: number) => `${a} – ${b} · ${n} passes`,
  seeMatch: "Ver partida →",
  numbersTitle: "A campanha em números",
  passersTitle: "Quem mais passou",
  passersNote: (n: number, missed: { name: string; games: string[] }[]) =>
    `Passes completos somando os ${COUNT_WORDS_M[n] ?? n} jogos.${
      missed.length ? ` ${missed.map((m, i) => `${m.name} ${i === 0 ? "não jogou contra" : "contra"} ${listPt(m.games)}`).join("; ")}.` : ""
    }`,
  pairsTitle: "Duplas mais usadas",
  pairsNote: (n: number) => `Passes completos entre os dois, nas duas direções, somando os ${COUNT_WORDS_M[n] ?? n} jogos.`,
  perGameTitle: "Passes completos por jogo",
  opponent: "Adversário",
  methodText:
    "Todos os números consideram passes completos com destinatário nos 90 minutos. Veja quais eventos entram, como a rede é construída e quais são as limitações.",
  methodLink: "Ler a metodologia",
};

const COUNT_WORDS_M: Record<number, string> = { 2: "dois", 3: "três", 4: "quatro", 5: "cinco", 6: "seis", 7: "sete" };
const COUNT_WORDS_F: Record<number, string> = { 2: "duas", 3: "três", 4: "quatro", 5: "cinco" };
const formatThousands = (n: number) => new Intl.NumberFormat("pt-BR").format(n);

export const home = {
  eyebrow: "Football Intelligence Lab · por Leonardo Taschin",
  title: "Dados e IA para entender como o futebol é jogado.",
  lead: "Uma série de projetos com dados reais de partidas: cada um parte de uma pergunta de futebol, mostra o método e termina numa ferramenta que um analista usaria.",
  ctaProject: "Ver o projeto 01",
  ctaAll: "Todos os projetos",
  featured: "Em destaque",
  live: "No ar",
  featuredKicker: "Projeto 01 · PNSM",
  featuredTitle: (article: "o" | "a", team: string, season: string) => `Como ${withArticle(article, team)} de ${season} trocava a bola`,
  featuredText: (matches: number) =>
    `Redes de passes dos ${COUNT_WORDS_M[matches] ?? matches} jogos da campanha do tri, com dados do StatsBomb Open Data. Selecione um jogador e veja para quem ele passou e de quem recebeu.`,
  statMatches: "partidas",
  statPasses: "passes completos",
  statGoals: "gols",
  explore: "Explorar a campanha →",
  projectsTitle: "Projetos",
  projectsLead:
    "Seis projetos, do event data à visão computacional. Cada um responde uma pergunta e é publicado com código, método e limitações.",
  projects: [
    { num: "01", title: "Passing Network + Shot Map", desc: "Como uma equipe conecta seus jogadores por passes e de onde vêm suas finalizações.", live: true },
    { num: "02", title: "Expected Goals (xG)", desc: "Um modelo próprio de qualidade de chance, com calibração e explicabilidade.", live: false },
    { num: "03", title: "Expected Threat (xT)", desc: "Quanto cada passe e condução aumenta a chance de gol.", live: false },
    { num: "04", title: "Player Similarity", desc: "Encontrar jogadores parecidos para recrutamento e reposição.", live: false },
    { num: "05", title: "Tracking + Pitch Control", desc: "Quem controla cada espaço do campo a cada instante.", live: false },
    { num: "06", title: "AI Video Analysis", desc: "Da transmissão às coordenadas dos jogadores com visão computacional.", live: false },
  ],
  soon: "Em breve",
  aboutTitle: "Sobre",
  about:
    "Sou Leonardo Taschin, estudante da FIAP em São Paulo. Junto engenharia de software, ciência de dados e IA para construir ferramentas de análise de futebol: não só o modelo, mas o produto que um departamento de análise usaria.",
  linkedin: "LinkedIn",
  github: "GitHub",
  email: "E-mail",
  pending: "em breve",
};

export const methodology = {
  breadcrumb: "Metodologia",
  title: "Como as redes são construídas",
  lead: "Quais dados foram usados, quais passes entram em cada rede, como os números são conferidos e o que a rede não consegue mostrar.",
  toc: "Nesta página",
  sections: {
    question: "A pergunta",
    data: "Dados",
    passes: "Quais passes entram",
    network: "Como a rede é desenhada",
    validation: "Validação",
    limits: "Limitações",
    reproduce: "Reproduzir",
    attribution: "Atribuição",
  },
  question:
    "Como uma equipe conectou seus jogadores por passes em uma partida? A rede resume os passes completos observados: quem participou mais, quais duplas mais trocaram a bola e em que regiões do campo isso aconteceu. Ela ajuda a levantar hipóteses sobre o jogo, mas não comprova sozinha a organização tática.",
  dataText: (competition: string, season: string) =>
    `Os eventos vêm do StatsBomb Open Data, que publica dados de partidas selecionadas. A ${competition} de ${season} tem `,
  dataIds: (c: number, s: number) => [`competition_id ${c}`, `season_id ${s}`] as const,
  dataTail: ". Cada partida usa dois arquivos: os eventos e as escalações.",
  tableMatch: "Partida",
  tableAttempted: (team: string) => `Passes ${team}`,
  tableCompleted: "Completos",
  tableNote: (team: string) => `Passes ${team} nos 1º e 2º tempos. "Completos" são os que entram na rede.`,
  matchName: (home: string, a: number, b: number, away: string) => `${home} ${a} × ${b} ${away}`,
  passesIntro:
    "Um evento do tipo Pass entra na rede quando cumpre todas as regras abaixo. No esquema do StatsBomb, um passe completo é aquele sem o campo pass.outcome.",
  passesRules: [
    "É da equipe analisada e aconteceu no 1º ou no 2º tempo, com acréscimos. Prorrogação e pênaltis ficam de fora.",
    "Foi completo: não tem pass.outcome.",
    "Tem destinatário identificado (pass.recipient) e localização inicial dentro do campo.",
    "Laterais, faltas e escanteios entram quando são passes completos.",
  ],
  passesOutro:
    "Os passes excluídos são contados por motivo, e cada passe conta em um único motivo, para que a diferença entre tentados e completos sempre feche.",
  networkCards: [
    ["Posição do jogador", "Mediana das localizações de onde ele completou passes. Quem só recebeu fica na mediana de onde recebeu, e isso é sinalizado."],
    ["Tamanho do círculo", "Número de passes completos que o jogador deu."],
    ["Espessura da linha", "Passes completos entre a dupla, somando as duas direções."],
    ["Setas", "Ao selecionar um jogador, cada direção vira uma seta: quem passou e quem recebeu."],
    ["Mínimo de passes", "Só duplas com pelo menos 3 passes aparecem por padrão. O limite é ajustável."],
    ["Orientação", "Cada equipe ataca da esquerda para a direita, como no padrão do StatsBomb."],
  ],
  validationIntro: "Antes de publicar, o pipeline confere automaticamente e não gera nada se alguma checagem falhar:",
  validationItems: (completed: number) => [
    `A soma de todas as conexões é igual ao número de passes completos elegíveis. Na final, ${completed} = ${completed}.`,
    "Tentados menos excluídos é igual a completos, e todo jogador de uma conexão tem um círculo.",
    "Não há eventos de outra equipe nem de períodos excluídos.",
    "Chutes e gols exportados batem com os eventos, e os gols batem com o placar.",
    "No replay, os trechos da jogada estão em ordem e o último é o chute do gol.",
  ],
  validationTests:
    "Os testes automáticos cobrem passe sem outcome, passe sem destinatário, coordenada ausente, passes da mesma dupla em direções opostas, partidas com prorrogação e chute sem xG, além de conferir os números da final e da campanha.",
  limits: [
    ["A posição não é tática.", "A mediana resume onde o jogador agiu com a bola, não onde ele ficou posicionado sem ela."],
    ["Substituições misturam formações.", "A rede da partida inteira pode juntar jogadores que nunca estiveram em campo ao mesmo tempo."],
    ["Dados históricos.", "Os eventos de 1970 foram registrados a partir de vídeo da época, então localizações e xG têm mais incerteza que em jogos modernos."],
    ["Volume não é qualidade.", "Muitos passes entre dois jogadores não significam que essa conexão criou chances. Para isso é preciso seguir a sequência dos eventos."],
    ["Sem bola é aproximação.", "A posição sem bola é a mediana das ações defensivas, não a posição real do jogador sem a bola."],
  ],
  reproduceText:
    "O mesmo motor em Python gera o JSON que o site desenha e a imagem dos posts, então os números são sempre os mesmos.",
  pipeline: ["load", "transform", "metrics", "validate", "export"],
  pipelineEnd: "site · post",
  commands: (repo: string) =>
    `git clone ${repo}\npip install -e "engine[dev]"\npython -m pnsm export --config engine/config/wc1970_brazil.yaml\npytest engine/tests`,
  repoPlaceholder: "[SEU REPOSITÓRIO]",
  codeLink: "Ver o código no GitHub",
  attribution:
    "Dados: StatsBomb Open Data, usados conforme as condições de atribuição do repositório oficial. Visualizações e análise: Leonardo Taschin.",
};

export const shots = {
  title: (article: "o" | "a", team: string) => `Finalizações ${ofTeam(article, team)}`,
  teamLabel: "Equipe",
  filterLabel: "Filtrar chutes",
  show: "Mostrar",
  filters: { all: "Todos", open: "Só jogo aberto", goals: "Só gols" },
  legendLabel: "Legenda",
  legend: { goal: "Gol", saved: "Defendido", post: "Na trave", blocked: "Bloqueado", off: "Para fora", setPiece: "Bola parada", halo: "Halo = xG (área proporcional)" },
  // badge on set-piece icons
  badge: { freeKick: "F", penalty: "P", corner: "E", kickOff: "S" } as Record<string, string>,
  attackUp: (article: "o" | "a", team: string) => `ATAQUE ${ofTeam(article, team).toUpperCase()} ↑`,
  pitchLabel: (article: "o" | "a", team: string) => `Finalizações ${ofTeam(article, team)}`,
  // StatsBomb shot.outcome → text; unknown names fall back to the result group
  outcome: {
    Goal: "Gol", Saved: "Defendido", "Saved to Post": "Defendido (na trave)", "Saved Off Target": "Defendido (para fora)",
    Post: "Na trave", Blocked: "Bloqueado", "Off T": "Para fora", Wayward: "Sem direção",
  } as Record<string, string>,
  result: { goal: "Gol", saved: "Defendido", post: "Na trave", blocked: "Bloqueado", off: "Para fora", other: "Outro" },
  body: { rightFoot: "Pé direito", leftFoot: "Pé esquerdo", head: "Cabeça", other: "Outra" },
  type: { openPlay: "Jogo aberto", freeKick: "Falta", penalty: "Pênalti", corner: "Escanteio", kickOff: "Saída de bola", other: "Outro" },
  shotAria: (minute: number, name: string, outcome: string, xg: string) => `${minute}′, ${name}, ${outcome}, xG ${xg}`,
  summaryXg: (xg: string) => `${xg} xG`,
  summary: (p: { count: number; goals: number; perShot: string | null; withXg: number }) =>
    `em ${p.count} chutes; ${p.goals} ${p.goals === 1 ? "virou" : "viraram"} gol.${p.perShot ? ` ${p.perShot} de xG por chute,` : ""} ${p.withXg}/${p.count} com xG.`,
  detail: { xg: "xG", body: "parte do corpo", type: "tipo", distance: "do gol", noXg: "sem xG" },
  meters: (m: number) => `${Math.round(m)} m`,
  // where the ball ended (engine `finish`); numbers already in metres
  finish: (f: ShotFinish, dec: (n: number) => string): string => {
    switch (f.kind) {
      case "goal": return f.height === null ? "Gol." : `Entrou a ${dec(f.height)} m do chão.`;
      case "saved": return f.height === null ? "O goleiro defendeu." : `O goleiro defendeu a ${dec(f.height)} m do chão.`;
      case "post": return "Bateu na trave.";
      case "blocked": return f.blockedAfter === null ? "Bloqueado." : `Bloqueado a ${Math.round(f.blockedAfter)} m de onde saiu o chute.`;
      case "over": return `Por cima do travessão, a ${dec(f.height)} m do chão.`;
      case "overWide": return `Por cima e ao lado: ${dec(f.wideBy)} m para fora da trave, a ${dec(f.height)} m do chão.`;
      case "wide": return `Ao lado: ${dec(f.wideBy)} m para fora da trave.`;
      case "short": return "Sem direção: a bola não chegou à linha do gol.";
      default: return "";
    }
  },
  // label at the end of the ball's path; on the goal line the detail card already says what happened
  endLabel: { goal: "", saved: "", post: "", blocked: "bloqueio", over: "", wide: "", overWide: "", short: "parou aqui", other: "" } as Record<ShotFinish["kind"], string>,
  frameCaption: "Onde a bola cruzou a linha do gol, vista de trás de quem chutou.",
  hint: "Clique num chute para ver de onde ele saiu, o caminho da bola (tracejado) e onde ela parou: na linha do gol, no bloqueio ou fora.",
  topTitle: "Maiores chances",
  noLocation: (n: number) => `${n} ${n === 1 ? "chute sem localização não aparece" : "chutes sem localização não aparecem"} no campo.`,
  footer:
    "Um ícone por chute (evento Shot), 1º e 2º tempos, no lugar de onde saiu a finalização; o ícone mostra o resultado e o halo, a chance (xG do StatsBomb, área proporcional). O tracejado liga o ponto do chute ao ponto final registrado: a linha do gol, o lugar do bloqueio ou onde a bola parou; é uma linha reta, não a curva real da bola. Chute sem xG continua no mapa, nunca vira zero. Gols contra não são chutes e não aparecem. Os eventos de 1970 vêm de vídeo da época: localização e xG têm mais incerteza.",
};

// "Só jogo aberto": what was removed, by StatsBomb pass.type, most first
const SET_PIECE: Record<string, [string, string]> = {
  "Free Kick": ["falta", "faltas"],
  "Throw-in": ["lateral", "laterais"],
  "Goal Kick": ["tiro de meta", "tiros de meta"],
  Corner: ["escanteio", "escanteios"],
  "Kick Off": ["saída de bola", "saídas de bola"],
};
function removedList(removed: Record<string, number>): string {
  return listPt(
    Object.entries(removed)
      .filter(([, n]) => n > 0)
      .sort((a, b) => b[1] - a[1])
      .map(([type, n]) => `${n} ${SET_PIECE[type]?.[n === 1 ? 0 : 1] ?? type}`),
  );
}

export const network = {
  title: (article: "o" | "a", team: string) => `A rede de passes ${ofTeam(article, team)}`,
  teamLabel: "Equipe",
  periodLabel: "Período",
  periods: { full: "Partida inteira", firstSub: "Até a 1ª substituição" },
  openPlay: "Só jogo aberto",
  summaryFull: (attempted: number, accuracy: string) => `passes completos de ${attempted} tentados (${accuracy} de acerto).`,
  summaryCut: (diff: number, full: number) =>
    diff === 0 ? "passes completos neste recorte, os mesmos da partida inteira." : `passes completos neste recorte, ${diff} a menos que na partida inteira (${full}).`,
  // notices: one per cut, from the exported facts only
  full: (subsLine: string | null) =>
    subsLine ? `A rede junta jogadores que não estiveram juntos em campo: ${subsLine}` : "Sem substituições: os 11 jogadores estiveram juntos em campo os 90 minutos.",
  firstSub: (p: { article: "o" | "a"; team: string; same: boolean; minute?: number; out?: string; n: number; full: number }) =>
    p.same
      ? `${capitalize(withArticle(p.article, p.team))} não fez substituições: a rede é a mesma da partida inteira.`
      : `Até os ${p.minute}′, quando ${p.out} saiu: ficam ${p.n} dos ${p.full} passes, só entre os jogadores que estavam juntos em campo.`,
  openPlayNotice: (removed: Record<string, number>) => {
    const total = Object.values(removed).reduce((a, b) => a + b, 0);
    return total === 0 ? "Nenhum passe de bola parada nesta partida." : `Sem bolas paradas saem ${total} passes: ${removedList(removed)}.`;
  },
  firstSubOpen: (p: { same: boolean; minute?: number; n: number; full: number; removed: number }) =>
    p.same
      ? `Sem substituições, este recorte é igual a “só jogo aberto”: saem ${p.removed} passes de bola parada.`
      : `Até os ${p.minute}′ e sem bolas paradas: ficam ${p.n} dos ${p.full} passes.`,
  shift: (name: string, meters: number) => `${name} é quem mais muda de lugar: ${Math.round(meters)} m.`,
  drop: (name: string, from: number, to: number) => `${name} é quem mais perde passes: de ${from} para ${to}.`,
  hint: "Clique num jogador para ver para quem ele passou e de quem recebeu. As setas mostram a direção: na cor do time, os passes que ele deu; em cinza-escuro, os que recebeu.",
  notInCut: (name: string) => `${name} não tem passes neste recorte.`,
  pairsTitle: "Duplas mais usadas",
  pairsLegend: "→ ida · ← volta",
  pairsAria: (a: string, b: string, n: number) => `${a} e ${b}, ${n} passes: selecionar ${a}`,
  legendGiven: "passes dados",
  legendReceived: "passes recebidos",
  captionSelected: (name: string) => `Setas: na cor do time, os passes que ${name} deu; em cinza-escuro, os que recebeu. Mesmo mínimo por dupla.`,
  captionAll: (min: number) => `Cada linha soma os passes de ida e volta da dupla; só aparecem duplas com pelo menos ${min} passes.`,
};

const STAGE_IN: Record<string, string> = {
  Final: "na final",
  Semifinal: "na semifinal",
  "Quartas de final": "nas quartas de final",
  "Fase de grupos": "na fase de grupos",
};

export const player = {
  breadcrumb: "Campanha 1970",
  sub: (position: string | null, team: string, games: number) =>
    [position, team, `${games} ${games === 1 ? "jogo" : "jogos"} na campanha`].filter(Boolean).join(" · "),
  // lead sentence from the exported numbers only
  lead: (p: {
    name: string; article: "o" | "a"; team: string; games: number; teamRank: number; passes: number; share: string | null;
    to: { name: string; n: number } | null; from: { name: string; n: number } | null; avgShift: number | null;
    opponent?: { article: "o" | "a"; name: string }; stage?: string; rankInGame?: number;
  }) => {
    const of = ofTeam(p.article, p.team);
    if (p.games === 1 && p.opponent) {
      const rank = p.rankInGame === 1 ? "o que mais passou no time" : `${p.rankInGame}º do time em passes`;
      const head = `Jogou contra ${withArticle(p.opponent.article, p.opponent.name)} ${STAGE_IN[p.stage ?? ""] ?? ""}: ${p.passes} passes completos${p.share ? `, ${p.share} dos passes ${of}` : ""}, ${rank}.`;
      return p.to ? `${head} Passou mais para ${p.to.name} (${p.to.n}).` : head;
    }
    const head =
      p.teamRank === 1
        ? `Foi quem mais passou na campanha: ${p.passes} passes completos${p.share ? `, ${p.share} dos passes ${of}` : ""}.`
        : `${p.teamRank}º ${of} em passes na campanha: ${p.passes} passes completos${p.share ? `, ${p.share} dos passes do time nos jogos em que esteve em campo` : ""}.`;
    const partners =
      p.to && p.from
        ? ` ${p.to.name} foi o destino favorito (${p.to.n} passes) e ${p.from.name} quem mais o acionou (${p.from.n}).`
        : "";
    const shift =
      p.avgShift === null || Math.round(p.avgShift) === 0
        ? ""
        : ` Entre as ações com bola e sem bola, ${p.avgShift < 0 ? "recuou" : "avançou"} em média ${Math.round(Math.abs(p.avgShift))} m.`;
    return head + partners + shift;
  },
  single: "Uma partida só: os números abaixo são dessa partida, não de uma campanha. Os dados abertos do StatsBomb trazem apenas os jogos do Brasil.",
  stats: {
    passes: (rank: number) => `passes completos · ${rank}º do time`,
    received: "passes recebidos",
    share: (article: "o" | "a", team: string) => `dos passes ${ofTeam(article, team)}`,
    topPasser: (games: number) => (games === 1 ? "jogo como quem mais passou" : "jogos como quem mais passou"),
    shift: "da posição com bola para a sem bola",
  },
  gamesTitle: "Jogo a jogo",
  viewLabel: "Visão",
  views: { one: "Um jogo", all: "Todos os jogos" },
  viewNoteOne: (name: string) => `${name} em destaque na rede da partida escolhida. Clique em outro jogador para abrir a página dele.`,
  viewNoteAll: (name: string) => `A rede de cada partida com ${name} em destaque: as linhas fortes são as duplas dele. Clique num jogo para abri-lo.`,
  gameLabel: "Partida",
  gameShort: (stage: string, order: number, opponent: string) =>
    `${stage === "Final" ? "Final" : stage === "Semifinal" ? "Semi" : stage === "Quartas de final" ? "Quartas" : `Jogo ${order}`} · ${opponent}`,
  cardKicker: (stage: string, order: number) => (stage === "Fase de grupos" ? `Jogo ${order}` : stage),
  gameKicker: (stage: string, order: number) => (stage === "Fase de grupos" ? `Jogo ${order} · Fase de grupos` : stage),
  gameTitle: (team: string, score: [number, number], opponent: string) => `${team} ${score[0]} × ${score[1]} ${opponent}`,
  gameStats: { passes: "passes dados", received: "recebidos", rank: "no time" },
  partner: (name: string, n: number) => `Dupla mais usada: ${name} (${n} passes, ida e volta).`,
  partnerShort: (name: string, n: number) => `Dupla mais usada: ${name} (${n})`,
  subIn: (minute: number) => `Entrou aos ${minute}′.`,
  subOut: (minute: number) => `Saiu aos ${minute}′.`,
  openMatch: "Ver a partida →",
  openGameAria: (name: string, game: string) => `Ver ${name} em ${game}`,
  legendGiven: "passes que ele deu",
  legendReceived: "passes que recebeu",
  legendGhost: "posição sem bola",
  phasesTitle: "Com bola × sem bola",
  phasesHint: "altura no campo, atacando para a direita",
  phasesNote:
    "Círculo cheio: mediana de onde completou passes (com bola). Tracejado: mediana das ações defensivas — pressões, recuperações, duelos, interceptações, cortes e bloqueios (sem bola). São posições médias das ações, não a posição real sem a bola.",
  withTitle: "Com quem ele jogou",
  withNote: (games: number) => (games === 1 ? "Passes completos na partida, em cada direção." : `Passes completos nos ${games} jogos, em cada direção.`),
  passedTo: "Passou para",
  receivedFrom: "Recebeu de",
  othersTitle: "Outros jogadores",
  othersNote: "Todo jogador que aparece numa rede da campanha tem página, do Brasil e dos adversários.",
  footer:
    "Passes completos com destinatário, 1º e 2º tempos, somando os jogos em que o jogador esteve em campo; a porcentagem é sobre os passes do time nesses jogos. Agregação pelo identificador do jogador no StatsBomb, não pelo nome.",
  meters: (m: number) => `${m < 0 ? "−" : "+"}${Math.round(Math.abs(m))} m`,
};
