# F.I.L — Football Intelligence Lab

[![CI](https://github.com/LeoTaschin/Football-Inteligence-Lab/actions/workflows/ci.yml/badge.svg)](https://github.com/LeoTaschin/Football-Inteligence-Lab/actions/workflows/ci.yml)

Projetos de dados aplicados ao futebol, por [Leonardo Taschin](https://br.linkedin.com/in/leonardo-taschin). Cada projeto parte de uma pergunta de futebol, usa dados reais, documenta método e limitações e termina numa ferramenta interativa.

**Projeto 01 · PNSM (Passing Network + Shot Map):** como o Brasil de 1970 trocava a bola. Redes de passes dos seis jogos da campanha do tri, com seleção de jogador, posições com e sem bola e replay dos gols.

> *EN: A football analytics portfolio. Project 01 builds interactive pass networks, on/off-ball shapes and goal replays for Brazil's 1970 World Cup run from StatsBomb Open Data.*

## Como funciona

```text
StatsBomb Open Data ──► engine/ (Python, pacote pnsm) ──► site/public/data/*.json ──► site/ (React + TypeScript, estático)
                        load → transform → metrics → validate → export
```

- O **engine** é a única fonte dos números: aplica as regras (passes completos, nós pela mediana, conexões dirigidas), valida tudo e só então escreve os JSONs. Se uma checagem falhar, nada é exportado.
- O **site** apenas desenha os JSONs prontos; não recalcula nenhuma regra.
- O **CI** (GitHub Actions) roda em todo PR: testes do engine, `pnsm check` (dados do site em dia com as regras) e testes + build do site. A Vercel publica a `main`.

A especificação completa (regras, schema, decisões) está em [`CLAUDE.md`](CLAUDE.md).

## Reproduzir

```bash
python -m venv .venv && source .venv/bin/activate
pip install -e "engine[dev,report]"
python -m pnsm fetch  --competition 43 --season 272 --team Brazil   # baixa e cacheia em engine/.cache
python -m pnsm export --config engine/config/wc1970_brazil.yaml     # valida e gera site/public/data
python -m pnsm check  --config engine/config/wc1970_brazil.yaml     # confere se os JSONs commitados estão em dia
python -m pnsm post   --match 3888702                               # PNG 1080×1350 do post (engine[report])
pytest engine/tests

cd site && npm ci && npm run dev    # http://localhost:5173
npm test                            # testes de geometria e formatação
```

## Dados e atribuição

Dados de eventos: [StatsBomb Open Data](https://github.com/statsbomb/open-data). O repositório distribui apenas dados derivados (`site/public/data`); os JSON brutos ficam em cache local e não são versionados. Os eventos de 1970 foram registrados a partir de vídeo histórico, então localizações e xG têm mais incerteza que em jogos modernos.
