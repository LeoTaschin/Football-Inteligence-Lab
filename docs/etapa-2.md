# Etapa 2 — Aprofundar (concluída)

**Status (22/10/2026):** concluída e no ar. PRs #12 a #22. Próximo passo do F.I.L: Projeto 02 (`docs/projeto-02-xg.md`).

## Decisões (22/10/2026)

1. **Recortes: filtro combinável.** Período (*partida inteira* / *até a 1ª substituição*) × *só jogo aberto* (liga/desliga) = 4 redes por equipe.
2. **Finalizações: meio campo vertical por equipe.**
3. **Página do jogador: Brasil e adversários.** Adversários têm um jogo só, com aviso.
4. **Post: sem imagem do shot map** no gerador do engine (a divulgação usou capturas do site).

## O que mudou no caminho

- **Padrão "uma seleção"** (pedido depois da primeira versão das Finalizações): Rede de passes, Finalizações, Jogador e Jogadores mostram uma equipe por vez, campo à esquerda e painel à direita, como "Com bola × sem bola". Cada tela foi redesenhada e aprovada no canvas antes do código.
- **Finalizações v2:** ícone por resultado (bola de futebol no gol, luva, trave, bloqueio, seta), traço fino, xG como halo de área proporcional, tracejado do ponto do chute ao ponto final, vista frontal do gol e a frase do desfecho (`finish`, gerada pelo motor). Rótulo na ponta só para "bloqueio" e "parou aqui".
- **Jogador:** duas visões, "Um jogo" (rede completa, setas e posição sem bola) e "Todos os jogos" (grade de mini-redes).
- **Lista de jogadores:** inicialmente adiada, entrou no PR #20.

## Entregas

| PR | Entrega |
|---|---|
| #12 | Motor: lista de chutes (`shots.items`), regras de 5.8 |
| #13 | Site: aba Finalizações (v1) |
| #14 | Motor: os 4 recortes da rede (5.9) |
| #15 | Site: Rede de passes com uma seleção e os recortes |
| #16 | Motor: desfecho do chute (`finish`); site: Finalizações v2 |
| #17 | Ícones mais limpos, bola de futebol no gol |
| #18 | Motor: páginas de jogador (5.10) |
| #19 | Site: página do jogador |
| #20 | Motor + site: lista de jogadores |
| #21 | Carrossel do LinkedIn da Etapa 2 |
| #22 | Carrossel do Instagram sobre o xG da campanha |

## Design

Canvas de design (privado) "F.I.L Passing Network" — área **"PNSM · Etapa 2"**: `Recortes.dc.html` (rede de passes, uma seleção), `Finalizacoes.dc.html`, `Jogador.dc.html`, `Jogadores.dc.html`, cada um com a versão `-mobile`.

## Achados (valores conferidos nos testes de regressão)

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

**Campanha (finalizações, usados nos posts):**
- 19 gols com 14,75 de xG em 151 chutes (+4,25 acima do esperado); 9 dos 19 gols com xG < 0,10, 8 deles chutados a 15 m ou mais.
- Jairzinho: 7 gols, um em cada jogo, xG médio 45%, 9 m do gol em média. Os 9 improváveis: xG médio 5,8%, 18 m.
- Inglaterra: único jogo com menos xG que o adversário (0,87 × 1,54), vitória por 1 × 0.

## Divulgação

- **LinkedIn** (publicado): post sobre o xG da campanha, "Pela estatística, o Brasil de 1970 deveria ter feito 15 gols. Fez 19." Carrossel da Etapa 2 em `tools/carrossel/compose_etapa2.py`.
- **Instagram:** carrossel de 7 slides com a mesma história (`tools/carrossel/instagram_xg.py`) e legenda curta com "link na bio".

## Pendências que ficaram

- Metodologia do site ainda descreve só as regras da Etapa 1.
- Versão celular das Finalizações e da página do jogador conferida só no desktop.
- Nós quase sobrepostos (Pelé/Tostão, Mazzola/Boninsegna, Rivellino/Everaldo).
- Conferir as datas de 1970 com fontes históricas.
- Ler as condições de uso e de marca do StatsBomb Open Data.
- Apagar o projeto duplicado na Vercel (`football-intelligence-lab-6lhg`).
- `tools/carrossel/capture.py` (Etapa 1) desatualizado para a rede de uma seleção.
