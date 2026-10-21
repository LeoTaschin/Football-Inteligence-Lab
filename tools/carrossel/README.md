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
