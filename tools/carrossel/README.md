# Carrossel do LinkedIn

Gera as imagens de divulgação (1080×1350, desenhadas em 2×) a partir das **telas reais do site** e do post do engine.

```bash
# 1. site rodando localmente
cd site && npm run dev -- --port 5179

# 2. ambiente separado (não faz parte do engine nem do site)
python -m venv .venv-carrossel
.venv-carrossel/bin/pip install -r tools/carrossel/requirements.txt

# 3. post do engine (slide 1)
.venv/bin/python -m pnsm post --match 3888702

# 4. capturas (usa o Google Chrome instalado) e montagem
.venv-carrossel/bin/python tools/carrossel/capture.py http://localhost:5179 engine/outputs/carrossel/raw
.venv-carrossel/bin/python tools/carrossel/compose.py engine/outputs/carrossel/raw engine/.cache/fonts \
    engine/outputs/post_3888702.png engine/outputs/carrossel
```

Story do Instagram (1080×1920): título, rede de passes, movimentação com bola × sem bola e números da campanha, dentro da área que o Instagram não cobre:

```bash
.venv-carrossel/bin/python tools/carrossel/story.py engine/outputs/carrossel/raw engine/.cache/fonts \
    engine/outputs/carrossel/story_instagram.png
```

Saída em `engine/outputs/carrossel/` (fora do git): `slide_1.png` … `slide_7.png`, `mapas_da_final.png` (todos os mapas da final numa imagem) e `carrossel_PNSM.pdf` (para o post em carrossel).

Os textos dos slides em `compose.py` citam números da final e da campanha; se os dados mudarem, confira-os com o site.

## Carrossel da Etapa 2

Seis slides (finalizações, só jogo aberto, Itália até a 1ª substituição, página do jogador e chamada para o site), com o site rodando localmente como acima:

```bash
.venv-carrossel/bin/python tools/carrossel/capture_etapa2.py http://localhost:5179 engine/outputs/carrossel/raw2
.venv-carrossel/bin/python tools/carrossel/compose_etapa2.py engine/outputs/carrossel/raw2 engine/.cache/fonts engine/outputs/carrossel
```

Saída: `etapa2_slide_1.png` … `etapa2_slide_6.png` e `carrossel_PNSM_etapa2.pdf`. Os desenhos comuns aos dois carrosséis (cabeçalho, rodapé, quebra de texto) ficam em `layout.py`.

> `capture.py` (Etapa 1) supõe as duas redes lado a lado da tela antiga da Partida; desde a Etapa 2 a rede mostra uma equipe por vez, então ele precisa ser atualizado antes de regerar o carrossel da Etapa 1.

## Instagram: o xG da campanha

Carrossel de 7 slides (1080×1350) sobre os 19 gols com 14,75 de xG. Os gráficos são desenhados a partir dos JSONs do motor (`site/public/data`); o mapa de chutes da final vem da captura do site (`shots_goal.png`, gerado por `capture_etapa2.py`):

```bash
.venv-carrossel/bin/python tools/carrossel/instagram_xg.py site/public/data engine/outputs/carrossel/raw2 \
    engine/.cache/fonts engine/outputs/carrossel/instagram
```

Cores: verde `#009C3B` (gol improvável, xG < 10%) e cinza `#8A8A93` (chance mais clara), par validado para daltonismo e contraste; toda barra e todo ponto têm rótulo ou legenda.
