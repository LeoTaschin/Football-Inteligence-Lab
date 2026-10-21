# F.I.L — Football Intelligence Lab

Especificação do produto e guia de desenvolvimento. Este arquivo fica na raiz do repositório para o Claude Code ler automaticamente.

- **Autor:** Leonardo Taschin (FIAP, São Paulo)
- **Versão:** 21/10/2026
- **Escopo atual:** Etapa 1 — colocar no ar o Projeto 01 (PNSM) com a campanha do Brasil na Copa de 1970
- **Design de referência:** canvas "F.I.L Passing Network" no Claude (https://claude.ai/artifact/Xbg6HqKREbgp8iwGkpKdNF), com as telas Home, Campanha 1970, Partida, Metodologia, Post do LinkedIn, Replay do 4º gol e Com bola × sem bola

---

## 1. O que é o F.I.L

Um portfólio público de projetos de dados aplicados ao futebol. Cada projeto:

1. parte de uma **pergunta de futebol**;
2. usa **dados reais** (principalmente StatsBomb Open Data);
3. documenta **método e limitações**;
4. termina numa **ferramenta** que um analista usaria (página interativa) e numa **peça de divulgação** (imagem para LinkedIn).

Posicionamento: Engenharia de Software + Data Science + IA + Futebol. O diferencial é o perfil de *Analytics Engineer*: o modelo vira produto.

### Projetos do F.I.L

| # | Projeto | Status |
|---|---------|--------|
| 01 | PNSM — Passing Network + Shot Map | **Em desenvolvimento (este repositório)** |
| 02 | Expected Goals (xG) | Em breve |
| 03 | Expected Threat (xT) + progressão | Em breve |
| 04 | Player Similarity & Replacement Engine | Em breve |
| 05 | Tracking + Pitch Control | Em breve |
| 06 | AI Video Football Analysis | Em breve |

O site é a casa de todos eles. Na Etapa 1 só o 01 está ativo; os outros aparecem na Home como "Em breve".

---

## 2. Princípios de engenharia

1. **Um motor, várias saídas.** O motor Python é a única fonte de verdade dos números. Ele gera os JSONs que o site desenha e as imagens dos posts. O site nunca recalcula regras de futebol.
2. **Pré-calcular tudo.** StatsBomb Open Data é estático. Não há backend na Etapa 1: o site é estático e lê JSONs prontos.
3. **Regras explícitas e testadas.** Toda regra de filtragem tem teste. Erros silenciosos (passe contado errado) são o pior bug possível.
4. **Validar antes de publicar.** O export falha se uma checagem de consistência falhar.
5. **Assumir limitações.** Toda visualização informa recorte, fonte e o que ela não mostra.
6. **Código em inglês, interface em português.** Nomes de variáveis, funções e arquivos em inglês; textos da interface em pt-BR (preparar para i18n futura em inglês).

---

## 3. Arquitetura

```text
StatsBomb Open Data (GitHub, JSON)
        │  competitions / matches / events / lineups
        ▼
engine/ (Python) ── pacote `pnsm`
  load → transform → metrics → validate → export
        │                                  │
        ▼                                  ▼
site/public/data/*.json            engine/outputs/*.png (posts)
        │
        ▼
site/ (React + TypeScript, estático)
  Home · Campanha · Partida · Metodologia
        │
        ▼
Deploy estático (Vercel ou Netlify) + GitHub Actions
```

### Estrutura do repositório

```text
fil/
├── CLAUDE.md
├── README.md
├── engine/
│   ├── pyproject.toml
│   ├── config/
│   │   └── wc1970_brazil.yaml
│   ├── src/pnsm/
│   │   ├── __init__.py
│   │   ├── __main__.py        # CLI: python -m pnsm ...
│   │   ├── load.py            # download + cache dos JSON do StatsBomb
│   │   ├── transform.py       # tabelas tipadas de passes, chutes, ações defensivas
│   │   ├── metrics.py         # nós, conexões, combinações, totais, fases
│   │   ├── sequences.py       # sequências de gols para o replay
│   │   ├── labels.py          # posicionamento automático de rótulos
│   │   ├── validate.py        # checagens de consistência
│   │   ├── export.py          # escreve os JSONs do site
│   │   ├── names.py           # nomes curtos e traduções de posição
│   │   └── report/            # imagem do post (matplotlib + mplsoccer)
│   │       ├── theme.py
│   │       ├── components.py
│   │       └── post.py
│   ├── tests/
│   └── outputs/               # PNGs gerados (gitignored)
├── site/
│   ├── package.json
│   ├── vite.config.ts
│   ├── public/data/           # gerado pelo engine (commitado ou gerado no CI)
│   └── src/
│       ├── main.tsx
│       ├── routes/
│       ├── components/
│       ├── lib/               # geometria, formatação
│       ├── styles/tokens.css
│       └── types/data.ts      # tipos espelhando o schema JSON
└── .github/workflows/
    ├── engine-tests.yml
    └── build-deploy.yml
```

### Stack

**Engine:** Python 3.11+, `pandas`, `requests` (ou `statsbombpy`), `pyyaml`, `matplotlib`, `mplsoccer`, `pytest`. Opcional: `pydantic` para validar o schema de saída.

**Site:** Vite + React + TypeScript + React Router. Campo e redes desenhados em **SVG** (não em divs como no protótipo do canvas). Sem biblioteca de gráficos na Etapa 1; barras simples em CSS. Fonte Inter (Google Fonts).

**Deploy:** Vercel (build estático), com *Root Directory* = `site` no painel e a configuração em `site/vercel.json` (Vite + rewrite das rotas para `index.html`). Os JSONs de `site/public/data` são commitados, então a Vercel não roda Python. GitHub Actions roda os testes do engine, regera os dados e faz o build.

---

## 4. Dados

### Fonte

StatsBomb Open Data: https://github.com/statsbomb/open-data (também espelhado em https://github.com/hudl/open-data).

URLs brutas:
```text
https://raw.githubusercontent.com/statsbomb/open-data/master/data/competitions.json
https://raw.githubusercontent.com/statsbomb/open-data/master/data/matches/{competition_id}/{season_id}.json
https://raw.githubusercontent.com/statsbomb/open-data/master/data/events/{match_id}.json
https://raw.githubusercontent.com/statsbomb/open-data/master/data/lineups/{match_id}.json
```

Cachear os arquivos baixados em `engine/.cache/` (gitignored). Não redistribuir os JSON brutos no repositório; distribuir apenas os dados derivados, com atribuição. **Conferir as condições de uso e de marca no repositório oficial antes de publicar.**

### Recorte da Etapa 1

Copa do Mundo de 1970: `competition_id = 43`, `season_id = 272`, equipe `Brazil`.

| Jogo | Fase | Partida | match_id |
|---|---|---|---|
| 1 | Fase de grupos | Brasil 4 × 1 Tchecoslováquia | 3888699 |
| 2 | Fase de grupos | Brasil 1 × 0 Inglaterra | 3888700 |
| 3 | Fase de grupos | Brasil 3 × 2 Romênia | 3889217 |
| 4 | Quartas de final | Brasil 4 × 2 Peru | 3889218 |
| 5 | Semifinal | Brasil 3 × 1 Uruguai | 3888701 |
| 6 | Final | Brasil 4 × 1 Itália | 3888702 |

Todas as seis têm apenas os períodos 1 e 2 (sem prorrogação). O motor deve, ainda assim, tratar períodos 3–5.

A partida tem **duas equipes**: a tela da Partida mostra as duas; a Campanha agrega apenas o Brasil.

### Sistema de coordenadas

- Campo StatsBomb: **x de 0 a 120**, **y de 0 a 80** (jardas).
- Cada equipe ataca da **esquerda para a direita** nos seus próprios eventos (x = 120 é o gol adversário).
- **y cresce para baixo**: com o time atacando para a direita, y = 0 é a lateral esquerda e y = 80 a direita (um lateral-direito tem y alto).
- Eventos de pressão/duelo do adversário estão no referencial **dele**. Nunca misturar coordenadas de equipes diferentes sem espelhar (`x' = 120 − x`, `y' = 80 − y`).
- Conversão para metros: `m = jardas × 0.9144`.

### Nomes de exibição

Usar `player_nickname` da escalação quando existir; senão, sobrenome conhecido. Manter um dicionário de exceções em `names.py`, por exemplo:

| player_name | Exibição |
|---|---|
| Édson Arantes do Nascimento | Pelé |
| Roberto Rivelino | Rivellino |
| Eduardo Gonçalves de Andrade | Tostão |
| Wilson da Silva Piazza | Piazza |
| Giancarlo De Sisti | De Sisti |

Para italianos sem apelido, usar o sobrenome (Mazzola, Cera, Albertosi, Domenghini, Bertini, Facchetti, Rosato, Boninsegna, Riva, Juliano, Burgnich, Rivera). Sempre agregar por `player_id`, nunca por nome.

Posições: traduzir `positions[0].position` (ex.: "Right Back" → "Lateral-direito", "Left Defensive Midfield" → "Volante (esq.)", "Goalkeeper" → "Goleiro").

---

## 5. Regras de negócio (PNSM)

### 5.1 Passes da rede

Um evento `type = Pass` entra na rede quando:

1. é da equipe analisada;
2. `period ∈ {1, 2}` (com acréscimos); prorrogação e pênaltis fora na v1;
3. é **completo**: o campo `pass.outcome` **não existe** (regra do schema StatsBomb);
4. tem `pass.recipient` e `location` válidos.

Laterais, faltas e escanteios entram se forem passes completos (documentar; uma versão futura terá filtro "só jogo aberto").

Registrar contagem de excluídos **por motivo** (incompleto, sem destinatário, sem localização, período).

- Os filtros são aplicados **em sequência**, nesta ordem: equipe → período → incompleto → sem destinatário → sem localização. Cada passe excluído conta em **um único motivo** (o primeiro que o derruba), então `tentados − Σ excluídos (exceto período) = completos` sempre fecha.
- Passes de outra equipe não são "excluídos": simplesmente não pertencem à tabela da equipe.
- `attempted` = passes da equipe **dentro dos períodos**; o motivo `period` é registrado à parte.
- **Localização válida** = `location` presente, com `0 ≤ x ≤ 120` e `0 ≤ y ≤ 80`.

### 5.2 Nós

- **Posição:** mediana (x, y) das `location` dos passes completos **realizados** pelo jogador.
- **Tamanho:** número de passes completos realizados.
- **Também exportar:** passes recebidos (`received`), e a posição "sem bola" (ver 5.6).
- **Jogador que só recebeu** (nenhum passe completo dado, mas destinatário de algum): o nó existe com `passes: 0`, posicionado na mediana dos `pass.end_location` dos passes que recebeu, e marcado com `positionFrom: "received"` (padrão: `"passes"`). Assim toda conexão tem os dois nós e nenhuma é escondida em silêncio.

### 5.3 Conexões

- Exportar **dirigidas**: `from → to` com contagem.
- A visualização padrão soma ida e volta numa linha (par não dirigido).
- **Mínimo padrão:** 3 passes por par (soma das direções). Configurável; a UI oferece 3+, 5+, 8+.
- Ao selecionar um jogador, mostrar as conexões dele como **setas dirigidas** (passes dados na cor do time; recebidos em cinza-escuro), respeitando o mínimo do par.

### 5.4 Top combinações

Ordenar pares não dirigidos pela soma; exibir os 10 maiores com a separação ida/volta (`→ 26 · ← 18`). A ordem do par mostra primeiro quem passou mais.

### 5.5 Substituições

A rede da partida inteira pode juntar jogadores que não estiveram juntos em campo. Exportar a lista de substituições (`minute`, `out`, `in`) e marcar nós como `subbedIn` / `subbedOut` com minuto. A UI mostra o aviso. **Pendente (Etapa 2):** opção "até a 1ª substituição".

### 5.6 Com bola × sem bola

- **Com bola:** mediana das localizações dos passes completos (mesma posição do nó).
- **Sem bola:** mediana das localizações das ações defensivas do jogador: `Pressure`, `Ball Recovery`, `Interception`, `Duel`, `Clearance`, `Block`.
- Exportar a contagem de ações defensivas por jogador (amostras pequenas devem ser sinalizadas, ex.: goleiro).
- Métricas derivadas: deslocamento por jogador (`def.x − ball.x`, em metros) e altura média do time sem o goleiro.
- Texto obrigatório: "São posições médias das ações, não a posição real sem a bola."

### 5.7 Replay de gols

Para cada gol (evento `Shot` com `shot.outcome = Goal` da equipe), reconstruir a posse (`possession`) e exportar a sequência de segmentos da bola:

- `Pass`: de `location` a `pass.end_location`, duração `duration`;
- `Carry`: de `location` a `carry.end_location`;
- `Shot`: de `location` a `shot.end_location` (x, y);
- tempo relativo ao primeiro evento com bola da posse;
- toques (`touches`): jogador e local onde recebeu a bola (`Ball Receipt*`) ou recuperou;
- passos narrados (`steps`): texto curto por passe/ação marcante, gerado a partir de templates ("Pelé → Gérson", "Clodoaldo dribla N vezes", "Carlos Alberto finaliza: gol").

Ignorar eventos do adversário na animação (estão em outro referencial). Texto obrigatório: "Os dados de eventos não registram onde os jogadores estavam sem a bola."

### 5.8 Shot Map (Etapa 2)

Regras já definidas no plano do projeto: um marcador por `Shot`, área proporcional a `shot.statsbomb_xg`, xG ausente nunca vira zero, distinguir resultados (`Goal`, `Saved`, `Off T`, `Blocked`, `Wayward`, `Post`, outros), marcar bola parada (`shot.type`). Métricas: chutes, gols, soma de xG, xG médio, cobertura de xG.

---

## 6. Schema dos JSONs

Tipos devem existir em `engine` (pydantic/dataclasses) e espelhados em `site/src/types/data.ts`.

### `data/index.json` — catálogo

```json
{
  "generatedAt": "2026-10-21T00:00:00Z",
  "source": "StatsBomb Open Data",
  "collections": [{
    "id": "wc1970-brazil",
    "title": "Campanha do Brasil · Copa de 1970",
    "competitionId": 43, "seasonId": 272, "team": "Brazil",
    "matches": [3888699, 3888700, 3889217, 3889218, 3888701, 3888702]
  }]
}
```

### `data/matches/{match_id}.json` — tela da Partida

```json
{
  "match": {
    "id": 3888702, "date": "1970-06-21", "stage": "Final",
    "competition": "FIFA World Cup", "season": "1970",
    "home": "Brazil", "away": "Italy", "score": [4, 1]
  },
  "periods": [1, 2],
  "teams": [{
    "name": "Brazil", "displayName": "Brasil",
    "colors": { "fill": "#FFD500", "line": "#009C3B", "ink": "#0A0A0B" },
    "passes": { "attempted": 471, "completed": 400,
                "excluded": { "incomplete": 71, "noRecipient": 0, "noLocation": 0 } },
    "nodes": [{
      "playerId": 397621, "num": 8, "name": "Gérson", "position": "Volante (dir.)",
      "ball": { "x": 65.7, "y": 38.6 }, "def": { "x": 37.6, "y": 41.8, "n": 23 },
      "passes": 70, "received": 77,
      "sub": null,
      "label": "below"
    }],
    "edges": [{ "from": 397621, "to": 39708, "n": 26 }],
    "substitutions": [],
    "shots": { "count": 27, "goals": 4, "xg": 2.77, "xgCoverage": [27, 27] }
  }],
  "goals": [{
    "team": "Brazil", "minute": 86, "scorer": "Carlos Alberto",
    "duration": 29.9,
    "segments": [{ "t": 0.9, "d": 1.15, "from": [39.5, 13.5], "to": [29.3, 17.1], "kind": "carry" }],
    "touches": [{ "t": 0.9, "num": 9, "name": "Tostão", "at": [39.5, 13.5], "label": "below" }],
    "steps": [{ "t": 0.9, "text": "Tostão recupera a bola no próprio campo" }]
  }],
  "validation": { "edgeSumEqualsCompleted": true, "noForeignEvents": true }
}
```

`label` ∈ `below | above | left | right`, decidido pelo motor (ver 7.4).

Campos a mais que o export gera (o exemplo acima é o mínimo; a fonte de verdade é `engine/src/pnsm/export.py`):

- `match.stadium`; `scale` = `{maxPasses, maxPair, maxDirected}` da partida (mesma escala para as duas equipes).
- Por equipe: `teamId`; `passes.excluded.period`; `pairs` = `[{a, b, forward, backward, n}]` ordenados por `n` (`a` é quem passou mais; usado nas linhas não dirigidas e no Top 10, para o site não somar nada); `phase` = `{ballHeight, defHeight, shiftMeters}` (sem o goleiro).
- Por nó: `positionFrom` (`passes` | `received`, ver 5.2); `def.lowSample` (menos de 5 ações); `shift` em metros (`def.x − ball.x`); `sub` = `{type: "in" | "out", minute, with: playerId}` ou `null`.
- Por gol: `teamId`, `scorerId`, `passes`, `players`; `touches[].playerId`. O replay começa depois do último toque do adversário com a bola na posse (o `possession` do StatsBomb nem sempre muda quando a bola troca de dono).
- Coordenadas exportadas com 2 casas; o site arredonda para exibir.

### `data/collections/wc1970-brazil.json` — tela da Campanha

```json
{
  "id": "wc1970-brazil",
  "summary": { "wins": 6, "played": 6, "goalsFor": 19, "goalsAgainst": 7,
               "completed": 2490, "attempted": 2908,
               "xgFor": 14.75, "xgAgainst": 8.53, "morePassesThanOpponent": 6 },
  "matches": [{
    "id": 3888699, "order": 1, "stage": "Fase de grupos", "opponent": "Tchecoslováquia",
    "score": [4, 1], "completed": 406, "opponentCompleted": 359,
    "xg": 3.81, "opponentXg": 2.42,
    "topPair": { "names": ["Carlos Alberto", "Clodoaldo"], "n": 30 },
    "mini": { "nodes": [], "edges": [] },
    "note": null
  }],
  "topPassers": [{ "name": "Carlos Alberto", "n": 367 }],
  "topPairs": [{ "names": ["Carlos Alberto", "Clodoaldo"], "n": 164 }]
}
```

Notas dos cartões (`note`) podem ser geradas por regras simples (ex.: "único jogo com menos xG que o adversário", "jogo com mais passes completos", "maior diferença de passes"), nunca escritas à mão.

---

## 7. Site

### 7.1 Rotas

| Rota | Tela | Fonte de dados |
|---|---|---|
| `/` | Home do F.I.L | estático + `index.json` |
| `/pnsm/1970` | Campanha 1970 | `collections/wc1970-brazil.json` |
| `/pnsm/1970/:matchId` | Partida | `matches/{id}.json` |
| `/pnsm/metodologia` | Metodologia | estático + `index.json` |

Links do post do LinkedIn apontam para `/pnsm/1970` ou direto para uma partida.

### 7.2 Telas

**Home**
- Barra de navegação: F.I.L · Projetos · Campanha 1970 · Metodologia · Sobre.
- Hero: "Dados e IA para entender como o futebol é jogado." + subtítulo + CTAs ("Ver o projeto 01", "Todos os projetos").
- Destaque do PNSM: cartão com título "Como o Brasil de 1970 trocava a bola", números (6 partidas, 2.490 passes completos, 19 gols) e mini-rede da final.
- Lista de projetos 01–06 com status.
- Sobre: bio curta + links (LinkedIn: https://br.linkedin.com/in/leonardo-taschin, GitHub: https://github.com/LeoTaschin/, e-mail **pendente**).

**Campanha 1970**
- Breadcrumb, título, achado principal (Carlos Alberto: 367 passes completos, presente nas duas duplas mais usadas).
- Faixa de resumo: 6 de 6 vitórias · 19 × 7 · 2.490 passes completos (86%) · xG 14,75 × 8,53 · 6 de 6 jogos com mais passes que o adversário.
- Grade de 6 cartões (um por jogo): fase, placar, mini-rede, passes completos × adversário, xG × adversário, dupla mais usada, nota opcional, "Ver partida →". Final com destaque (borda escura, selo "Campeão").
- "A campanha em números": quem mais passou (top 6), duplas mais usadas (top 5), passes completos por jogo Brasil × adversário.
- Chamada para a Metodologia.

**Partida** (tela principal do PNSM)
- Breadcrumb + navegação jogo anterior/seguinte.
- Cabeçalho: fase, data, estádio (quando disponível), placar, achado gerado.
- Barra de controles: mínimo de passes (3+, 5+, 8+) + legenda.
- **Abas** (Etapa 1: as três):
  1. **Rede de passes** — dois campos horizontais lado a lado (cada equipe ataca para a direita), linhas não dirigidas; clique num jogador → setas dirigidas, demais esmaecidos, painel do jogador (passes dados, recebidos, % do time, top 5 "passou para" e "recebeu de", aviso de substituição).
  2. **Com bola × sem bola** — animação entre as duas formações (ver 5.6), botões Com bola / Sem bola / Animar, linha da altura média, painel com deslocamentos.
  3. **Gols** — lista dos gols da partida; selecionar um abre o replay (ver 5.7) com play/pause, recomeçar, velocidade 0,5×/1×/2×, linha do tempo arrastável e lista de passos clicável.
- Top 10 combinações de cada equipe.
- Rodapé com metodologia resumida e atribuição.

**Metodologia**
- Índice lateral; seções: A pergunta · Dados (tabela com match_id, tentados, completos) · Quais passes entram · Como a rede é desenhada · Validação · Limitações · Reproduzir (comandos + link do GitHub) · Atribuição.

### 7.3 Componentes

```text
<AppNav/>              navegação global
<Pitch/>               campo SVG (horizontal | vertical, tamanho responsivo via viewBox 120×80)
<PassNetwork/>         nós + linhas + setas; props: team, minPasses, selectedId, onSelect
<PlayerNode/>          círculo com número, rótulo posicionado
<Arrow/>               linha dirigida com ponta, offset perpendicular
<PlayerPanel/>         painel do jogador selecionado
<CombinationTable/>    top N combinações com barras
<PhaseMorph/>          com bola × sem bola animado
<GoalReplay/>          replay de gol
<MatchCard/>           cartão da campanha com <MiniNetwork/>
<StatStrip/>           faixa de números
<BarList/>             lista de barras horizontais
<SiteFooter/>          rodapé com atribuição
```

Todo o SVG usa o sistema de coordenadas StatsBomb no `viewBox` (`0 0 120 80`), com `preserveAspectRatio="xMidYMid meet"`. Tamanhos visuais (raio, espessura) em unidades de campo calculadas a partir de px desejados ÷ escala, ou com `vector-effect: non-scaling-stroke`.

### 7.4 Regras visuais (vindas do canvas)

**Escalas**
- Raio do nó (px, campo de 560 px de largura): `r = 7 + 12 · √(passes / maxPassesDaPartida)`.
- Espessura da linha não dirigida: `w = 1 + 8 · (n / maxParDaPartida)`; opacidade `0.25 + 0.65 · n/max` (teto 0.9).
- Seta dirigida: `w = 1.5 + 6 · (n / maxDirigido)`; afastar perpendicularmente `2 + w/2` px para separar ida e volta; encurtar nas pontas pelo raio do nó; ponta com comprimento `7 + 1.2w` e meia-largura `3.5 + 0.9w`.
- Mesma escala para as duas equipes da partida (comparação justa).

**Rótulos**
- Padrão: abaixo do nó. Quando dois nós estão a menos de ~2 raios, o motor escolhe `above/left/right` para evitar sobreposição (algoritmo guloso simples por ordem de tamanho, testando as 4 posições e escolhendo a de menor sobreposição com nós e rótulos já colocados). Exportar a decisão no JSON (`label`).

**Interação**
- Clique no nó seleciona/deseleciona; botão "limpar".
- Selecionado: anel escuro; jogadores sem conexão visível com opacidade 0.3; linhas de terceiros com opacidade 0.08.
- Tooltip nas linhas/setas: "Gérson → Carlos Alberto: 26 passes".
- Teclado: nós são `<button>` com `aria-label` ("Gérson, camisa 8, 70 passes completos") e `aria-pressed`.

### 7.5 Design tokens

```css
:root {
  --bg: #FFFFFF;
  --surface: #F7F7F8;      /* campo */
  --line: #D4D4D8;         /* linhas do campo, bordas fortes */
  --border: #E4E4E7;       /* divisórias */
  --row: #F0F0F2;          /* trilho de barra, divisória fraca */
  --text: #0A0A0B;
  --text-2: #3F3F46;
  --text-muted: #6B6B73;
  --text-faint: #A1A1AA;
  --incoming: #52525B;     /* setas de passes recebidos */

  --bra-fill: #FFD500;     /* nó do Brasil */
  --bra-line: #009C3B;     /* contorno, linhas e barras do Brasil */
  --bra-ink: #0A0A0B;
  --ita-fill: #0066CC;
  --ita-line: #0066CC;
  --ita-ink: #FFFFFF;

  --radius-sm: 6px; --radius-md: 8px; --radius-lg: 12px; --radius-xl: 16px;
  --font: "Inter", system-ui, sans-serif;
}
```

- Tipografia: Inter 400–800, números com `font-variant-numeric: tabular-nums`. Títulos 800 com `letter-spacing: -0.02em`.
- Cores de seleção vêm de um mapa `teamColors` (nome da seleção → fill/line/ink); fallback neutro para times sem cor definida.
- Fundo branco. Não usar escudos nem logos de federações ou da StatsBomb sem conferir as regras de marca.
- Acessibilidade: alvos ≥ 44 px, contraste de texto ≥ 4.5:1, cores distinguíveis também por luminosidade, layout funcional em 375 px (campos com rolagem horizontal ou empilhados).

### 7.6 Post do LinkedIn (gerado pelo engine)

`python -m pnsm post --match 3888702` gera `outputs/post_3888702.png`, 1080×1350:
- cabeçalho (competição, data, estádio, placar, achado);
- dois campos horizontais lado a lado com as redes não dirigidas;
- legenda (tamanho = passes completos; espessura = passes da dupla, mín. 3);
- duas tabelas Top 10 combinações com ida/volta;
- rodapé com recorte, substituições, "Dados: StatsBomb Open Data" e "Leonardo Taschin · F.I.L".
Layout com `GridSpec`; tokens de cor iguais aos do site em `report/theme.py`.

---

## 8. Validação e testes

### Checagens automáticas (`validate.py`, executadas no export)

- Soma das conexões dirigidas = passes completos elegíveis (por equipe).
- Nenhum evento de outra equipe ou de período excluído.
- Todo `from`/`to` de conexão existe em `nodes`.
- Número de chutes exportados = eventos `Shot` incluídos; gols destacados = `shot.outcome = Goal`.
- Placar: gols de `Shot` + eventos `Own Goal For` (todos os períodos exceto o 5) = placar oficial da partida.
- Segmentos do replay em ordem temporal crescente; último segmento é o `Shot` do gol.

### Testes unitários (`engine/tests/`)

- Passe completo com `pass.outcome` ausente → entra.
- Passe com `outcome` explícito → sai (motivo "incomplete").
- Passe sem destinatário → sai.
- Coordenada ausente → sai.
- Passes A→B e B→A → duas dirigidas, um par somado.
- Partida com período 3 → período excluído.
- Chute sem xG → mantido, cobertura reduzida, nunca zero.
- Jogador substituto com poucos passes → nó presente, marcado.

### Testes de regressão com dados reais (valores conferidos)

| Verificação | Valor esperado |
|---|---|
| Final, Brasil: passes tentados / completos | 471 / 400 |
| Final, Itália: passes tentados / completos | 309 / 243 |
| Final, par mais usado do Brasil (soma) | Gérson–Carlos Alberto, 44 (26 → · ← 18) |
| Final, dirigida mais usada da Itália | Albertosi → Cera, 12 |
| Final, Brasil: chutes / xG (90 min) | 27 / 2,77 |
| Final, Itália: chutes / xG | 26 / 1,64 |
| Final, substituições do Brasil | nenhuma |
| Final, substituições da Itália | Bertini → Juliano (74′), Boninsegna → Rivera (83′) |
| Campanha: passes completos do Brasil | 2.490 de 2.908 |
| Campanha: quem mais passou | Carlos Alberto, 367 |
| Campanha: par mais usado | Carlos Alberto–Clodoaldo, 164 |
| 4º gol da final: passes na sequência | 9, com 8 jogadores, ~29 s da recuperação ao chute |

### Testes do site

- Componentes de geometria (`lib/geometry.ts`) com testes unitários (Vitest).
- Teste de renderização da Partida com o JSON da final (snapshot ou Playwright, opcional).

---

## 9. CLI do engine

```bash
pip install -e engine

python -m pnsm fetch  --competition 43 --season 272          # baixa e cacheia
python -m pnsm export --config config/wc1970_brazil.yaml     # gera site/public/data
python -m pnsm post   --match 3888702                        # gera o PNG do post
pytest engine/tests
```

`config/wc1970_brazil.yaml`:

```yaml
collection: wc1970-brazil
title: Campanha do Brasil · Copa de 1970
competition_id: 43
season_id: 272
team: Brazil
periods: [1, 2]
min_pair_passes: 3
defensive_actions: [Pressure, Ball Recovery, Interception, Duel, Clearance, Block]
output_dir: ../../site/public/data  # relative to this file
```

---

## 10. Roadmap do produto

### Etapa 1 — PNSM no ar (atual)

1. **Engine: dados e regras** — `load`, `transform`, `metrics` para uma partida; testes unitários. *Pronto quando:* os valores de regressão da final batem.
2. **Engine: export** — JSON da Partida e da Campanha, `validate`, rótulos automáticos. *Pronto quando:* os 6 jogos exportam sem falha de validação.
3. **Site: base** — Vite + React + rotas + tokens + `AppNav` + `SiteFooter`.
4. **Site: Partida** — `Pitch`, `PassNetwork`, seleção, painel, tabelas. *Pronto quando:* paridade com o design do canvas.
5. **Site: animações** — `PhaseMorph` e `GoalReplay` nas abas da Partida.
6. **Site: Campanha, Home, Metodologia.**
7. **Post** — gerador do PNG 1080×1350.
8. **Deploy** — GitHub Actions (testes → export → build) + Vercel/Netlify + domínio.

### Etapa 2 — Aprofundar
- Shot map na Partida (aba "Finalizações").
- Opção "até a 1ª substituição".
- Página do jogador na campanha.
- Filtro "só jogo aberto".

### Etapa 3 — Catálogo aberto
- Seletor competição → temporada → partida para todo o StatsBomb Open Data.
- Freeze frames 360 onde disponíveis.

### Etapa 4 — F.I.L completo
- Projetos 02–06 entram como novas seções da Home.
- Versão em inglês.

---

## 11. Pendências e decisões em aberto

- [x] Link do GitHub (https://github.com/LeoTaschin/) e repositório (https://github.com/LeoTaschin/Football-Inteligence-Lab).
- [ ] E-mail e domínio próprio (hoje: "em breve" no Sobre; deploy na Vercel).
- [ ] Conferir condições de uso/atribuição do StatsBomb Open Data para publicar dados derivados e o nome da marca.
- [ ] Datas das partidas: usar `match_date` do StatsBomb, mas conferir com fontes históricas antes de exibir (há divergência possível de um dia em jogos de 1970).
- [ ] Estádio: disponível em `matches/{c}/{s}.json` (`stadium.name`) quando houver.
- [ ] Rede "até a 1ª substituição" (Itália na final tem dois substitutos sobrepostos a titulares).
- [ ] Nós quase sobrepostos (ex.: Mazzola e Boninsegna na final): avaliar deslocamento mínimo visual sem alterar o dado exportado.
- [ ] Dados de 1970 foram registrados a partir de vídeo histórico: manter a ressalva na Metodologia.

---

## 12. Convenções para o Claude Code

- Antes de mudar uma regra de negócio (seção 5), atualizar este arquivo e os testes.
- Nunca calcular métricas no site; se faltar um número, adicioná-lo ao export.
- Não commitar JSON bruto do StatsBomb; `engine/.cache/` e `engine/outputs/` no `.gitignore`.
- Commits pequenos, mensagem no imperativo em inglês (`Add pass network export`).
- Textos de interface em pt-BR, centralizados em `site/src/content/` para facilitar a versão em inglês.
- Toda tela exibe "Dados: StatsBomb Open Data".
