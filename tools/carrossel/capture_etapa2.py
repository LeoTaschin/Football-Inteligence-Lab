"""Capture the Etapa 2 views (2x) for the LinkedIn carousel. Usage: capture_etapa2.py <base_url> <out_dir>"""

import sys
from pathlib import Path

from playwright.sync_api import sync_playwright

BASE, OUT = sys.argv[1].rstrip("/"), Path(sys.argv[2])
OUT.mkdir(parents=True, exist_ok=True)
FINAL = "/pnsm/1970/3888702"
RIVELLINO = 397630  # player_id
PELE_46 = "1-11"  # Brazil's 11th shot: Pelé, 46', xG 0.79


def union(locators, pad=12):
    boxes = [loc.bounding_box() for loc in locators]
    x0 = min(b["x"] for b in boxes) - pad
    y0 = min(b["y"] for b in boxes) - pad
    x1 = max(b["x"] + b["width"] for b in boxes) + pad
    y1 = max(b["y"] + b["height"] for b in boxes) + pad
    return {"x": max(0, x0), "y": max(0, y0), "width": x1 - max(0, x0), "height": y1 - max(0, y0)}


def open_page(page, path):
    page.goto(BASE + path, wait_until="networkidle")
    page.evaluate("document.fonts.ready")
    page.wait_for_timeout(600)


def tab(page, path, name):
    """Title, pitch and side panel of a one-team tab; the pitch alone as <name>_pitch.png."""
    open_page(page, path)
    panel = page.locator("[role=tabpanel]")
    pitch = panel.locator("svg[role=group]").first
    page.screenshot(path=OUT / f"{name}.png", full_page=True,
                    clip=union([panel.locator("h2").first, pitch, panel.locator("aside")]))
    pitch.screenshot(path=OUT / f"{name}_pitch.png")


with sync_playwright() as p:
    browser = p.chromium.launch(channel="chrome")
    page = browser.new_page(viewport={"width": 1280, "height": 1000}, device_scale_factor=2)

    tab(page, f"{FINAL}?aba=finalizacoes&chute={PELE_46}", "shots")
    tab(page, f"{FINAL}?aberto=1&jogador={RIVELLINO}", "open_play")
    tab(page, f"{FINAL}?equipe=2&periodo=1sub", "italy_first_sub")

    open_page(page, "/pnsm/1970/jogador/carlos-alberto?visao=todos")
    # "Outros jogadores" sits right under the crop's bottom edge: hide it so it is not cut in half
    page.locator("main aside section", has=page.locator("h2", has_text="Outros jogadores")).evaluate("el => el.style.display = 'none'")
    cards = page.locator("main button[aria-label^='Ver Carlos Alberto em']")
    page.screenshot(path=OUT / "player.png", full_page=True,
                    clip=union([page.locator("main header").first, cards.first, cards.last]))

    open_page(page, "/pnsm/1970/jogadores")
    page.screenshot(path=OUT / "players_list.png", full_page=True,
                    clip=union([page.locator("main [role=group][aria-label=Equipe]"), page.locator("main table"), page.locator("main aside")]))

    browser.close()
print("ok", sorted(f.name for f in OUT.iterdir()))
