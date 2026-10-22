# Etapa 2 — Aprofundar (em andamento)

**Status (22/10/2026):** retomada. As 4 decisões foram tomadas (ver [Decisões](#decisões-22102026)); a implementação começa pela branch `engine/shot-map`.

## Decisões (22/10/2026)

1. **Recortes: filtro combinável.** Período (*partida inteira* / *até a 1ª substituição*) × *só jogo aberto* (liga/desliga) = **4 redes por equipe** em cada partida. O design de 3 botões exclusivos precisa ser ajustado para um seletor + um interruptor.
2. **Finalizações: meio campo vertical por equipe**, como no design.
3. **Página do jogador: Brasil e adversários.** Todo jogador com nó em alguma partida da coleção ganha página; adversários terão um único jogo (a página mostra só o que existe, com aviso de amostra pequena).
4. **Post: sem imagem do shot map por enquanto.**

## Design

Canvas "F.I.L Passing Network": https://claude.ai/artifact/Xbg6HqKREbgp8iwGkpKdNF — área **"PNSM · Etapa 2 — Aprofundar (proposta)"**, à direita das telas da Etapa 1.

| Artboard | Item | O que mostra |
|---|---|---|
| `Recortes.dc.html` (+ `-mobile`) | 1ª substituição + só jogo aberto | Seletor *Partida inteira / Até a 1ª substituição / Só jogo aberto*, aviso explicando cada recorte com números, tabela "O que muda neste recorte", painel do jogador com link para a página dele |
| `Finalizacoes.dc.html` (+ `-mobile`) | Shot map | Nova aba "Finalizações": meio campo vertical por equipe, área ∝ xG, marcador por resultado (gol, defendido, trave, bloqueado, para fora), falta = quadrado; filtros, detalhe do chute, números por equipe, "Maiores chances" |
| `Jogador.dc.html` (+ `-mobile`) | Página do jogador | Carlos Alberto como exemplo: resumo, jogo a jogo com mini-redes, "Com quem ele jogou", com bola × sem bola por jogo, outros jogadores |

Todos os números do design vêm do engine (dados reais), nenhum foi escrito à mão.

## Achados que o design já usa (valores conferidos)

**Recortes (final):**
- Itália até a 1ª substituição (Bertini, 74′): **193** dos 243 passes. Brasil não substituiu: 400 nos dois recortes.
- Só jogo aberto: Brasil **357** (saem 43: 14 faltas, 13 laterais, 12 tiros de meta, 2 escanteios, 2 saídas de bola); Itália **189** (saem 54: 17 tiros de meta, 14 laterais, 14 faltas, 5 saídas de bola, 4 escanteios).
- Sem bolas paradas, Rivellino recua ~11 m (faltas e escanteios puxavam a mediana); Albertosi cai de 32 para 12 passes (tiros de meta).

**Finalizações (final):**
- Brasil 27 chutes, 4 gols, xG 2,77; Itália 26 chutes, 1 gol, xG 1,64; cobertura de xG 100%.
- 3 dos 4 gols do Brasil vieram de xG < 0,07 (Pelé 0,058, Gérson 0,069, Carlos Alberto 0,028); Jairzinho 0,719.
- Maior chance do jogo: Pelé, 46′, xG 0,794, para fora. Todos os chutes saíram de x ≥ 80 (meio campo basta).

**Jogador (Carlos Alberto, campanha):**
- 367 passes (1º), 361 recebidos, 14,7% dos passes do Brasil, quem mais passou em 3 dos 6 jogos.
- Passou mais para Jairzinho (108); recebeu mais de Clodoaldo (82).
- Recuo médio com bola → sem bola: 26 m; na final, 34 m.

## Decisões em aberto

Nenhuma: resolvidas em 22/10/2026 (ver topo).

## Notas técnicas para a implementação

- **Só jogo aberto:** tirar passes com `pass.type` em `{Corner, Free Kick, Throw-in, Goal Kick, Kick Off}`. `Recovery` e `Interception` também aparecem em `pass.type`, mas são jogo aberto e ficam.
- **Até a 1ª substituição:** cortar pelo `index` do evento `Substitution` (não pelo minuto). Equipe sem substituição: rede igual à partida inteira, com aviso. Substituição muito cedo: avisar amostra pequena.
- **Shot map:** `transform.shots_table` e `metrics.shot_summary` já existem; falta exportar a lista de chutes (minuto, jogador, x, y, resultado, xG, tipo, parte do corpo) e as regras da seção 5.8 (xG ausente nunca vira zero).
- **Jogador:** agregar por `player_id` entre as partidas da coleção; nova rota `/pnsm/1970/jogador/:slug`; link a partir do painel da Partida e de "Quem mais passou" na Campanha.
- **Regras de negócio novas entram primeiro no `CLAUDE.md` (seção 5) e nos testes**, como sempre.
- Ordem sugerida de branches: ~~`engine/shot-map`~~ (PR #12) → ~~`site/finalizacoes`~~ (PR #13) → ~~`engine/recortes`~~ (PR #14) → ~~`site/recortes`~~ (rede com uma seleção, PR #15) → ~~`site/finalizacoes-v2`~~ (PR #16) → `engine/jogador` → `site/jogador`.

## Outras pendências que podem entrar junto

- Nós quase sobrepostos (Pelé/Tostão, Mazzola/Boninsegna).
- Conferir as datas de 1970 com fontes históricas.
- Ler as condições de uso e de marca do StatsBomb Open Data antes de divulgar mais.
- Apagar o projeto duplicado na Vercel (`football-inteligence-lab-6lhg`).
