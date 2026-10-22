# Projeto 02 — Expected Goals (xG) próprio

**Status (22/10/2026):** não iniciado. O autor vai estudar xG antes; **nenhuma decisão foi tomada**. Este documento só reúne o ponto de partida e as perguntas a responder quando o projeto começar.

## A pergunta que motivou

No post da Etapa 2: o Brasil de 1970 fez 19 gols com 14,75 de xG (StatsBomb), e 9 dos 19 gols vieram de chances com menos de 10%. O xG mede a chance de um chute *médio* naquela situação e não sabe quem chuta. Um modelo próprio permite entender o que entra nessa estimativa e testar o que ela deixa de fora.

## O que já existe no F.I.L e pode ser reaproveitado

- **Carregamento** (`pnsm.load`): download e cache dos JSON do StatsBomb Open Data (competições, partidas, eventos, escalações).
- **Tabela de chutes** (`pnsm.transform.shots_table`): um chute por linha com local, ponto final (x, y, z), resultado, tipo (jogo aberto, falta, pênalti…), parte do corpo e o `statsbomb_xg` (que serve de referência para comparar o modelo próprio). xG ausente nunca vira zero.
- **Desfecho e distância** (`pnsm.metrics.shot_finish`, distância ao centro do gol no export).
- **Visualização:** a aba Finalizações e os ícones (`site/src/components/ShotMap.tsx`) já desenham chutes, halos de xG e o caminho da bola.
- **Processo:** regra primeiro no `CLAUDE.md`, testes, validação antes de publicar, design aprovado no canvas, uma branch por passo.

## Perguntas a decidir depois dos estudos

1. **Dados de treino:** quais competições do StatsBomb Open Data entram, e como separar treino, validação e teste (por competição? por temporada?) para não vazar informação.
2. **Escopo do chute:** pênaltis ficam fora (xG quase constante)? Faltas diretas e cabeçadas entram no mesmo modelo ou em modelos separados?
3. **Variáveis:** distância e ângulo ao gol, parte do corpo, tipo de jogada, tipo do passe anterior (cruzamento, enfiada), pressão; e os *freeze frames* 360 (posição do goleiro e dos defensores) onde existirem.
4. **Modelo:** começar por um modelo interpretável (por exemplo, regressão logística) e só depois testar algo mais complexo?
5. **Como avaliar:** métricas de probabilidade (log loss, Brier), curva de calibração e comparação direta com o `statsbomb_xg` nos mesmos chutes.
6. **"Quem chuta":** incluir o jogador (ou a qualidade de finalização dele) é parte do modelo ou uma análise à parte, como a pergunta do post?
7. **Produto:** onde o modelo aparece no site (uma página própria do Projeto 02? o xG próprio ao lado do StatsBomb na aba Finalizações?) e qual a peça de divulgação.

## Ao retomar

Ler este documento e as anotações de estudo do autor, responder às perguntas acima com ele, registrar as decisões aqui e no `CLAUDE.md` (nova seção de regras), e só então desenhar e codar.
