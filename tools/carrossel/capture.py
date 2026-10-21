"""Capture site views (2x) for the LinkedIn post. Usage: capture.py <base_url> <out_dir>"""

import sys
from pathlib import Path

from playwright.sync_api import sync_playwright

BASE, OUT = sys.argv[1].rstrip("/"), Path(sys.argv[2])
OUT.mkdir(parents=True, exist_ok=True)
FINAL = "/pnsm/1970/3888702"


def union(page, locators, pad=12):
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


with sync_playwright() as p:
    browser = p.chromium.launch(channel="chrome")
    page = browser.new_page(viewport={"width": 1280, "height": 1000}, device_scale_factor=2)

    # 1. both networks (pitch only) + whole team sections
    open_page(page, FINAL)
    pitches = page.locator("main svg[role=group]")
    pitches.nth(0).screenshot(path=OUT / "net_bra.png")
    pitches.nth(1).screenshot(path=OUT / "net_ita.png")
    teams = page.locator("main section", has=page.locator("h2"))
    page.screenshot(path=OUT / "networks_full.png", full_page=True,
                    clip=union(page, [page.locator("main header").first, teams.nth(0), teams.nth(1)]))
    tops = page.locator("main section", has=page.locator("h3", has_text="Top 10"))
    page.screenshot(path=OUT / "top10.png", full_page=True, clip=union(page, [tops.nth(0), tops.nth(1)]))

    # 2. Gérson selected: arrows + panel
    open_page(page, FINAL + "?jogador=397621")
    panel = page.locator("main section", has=page.locator("text=Passou para"))
    page.screenshot(path=OUT / "selected.png", full_page=True,
                    clip=union(page, [teams.nth(0), teams.nth(1), panel]))
    page.locator("main svg[role=group]").nth(0).screenshot(path=OUT / "net_gerson.png")

    # 3. with / without ball (shows the "sem bola" state after the transition)
    open_page(page, FINAL + "?aba=fases")
    panelf = page.locator("[role=tabpanel]")
    page.screenshot(path=OUT / "phases_full.png", full_page=True, clip=union(page, [panelf]))
    page.locator("[role=tabpanel] svg[role=group]").screenshot(path=OUT / "phases_ball.png")
    page.get_by_role("button", name="Sem bola").click()
    page.wait_for_timeout(1500)
    page.locator("[role=tabpanel] svg[role=group]").screenshot(path=OUT / "phases_def.png")

    # 4. 4th goal replay, full play shown
    open_page(page, FINAL + "?aba=gols&gol=5")
    page.screenshot(path=OUT / "replay_full.png", full_page=True, clip=union(page, [page.locator("[role=tabpanel]")]))
    page.locator("[role=tabpanel] svg[role=group]").screenshot(path=OUT / "replay_pitch.png")

    # 5. campaign
    open_page(page, "/pnsm/1970")
    strip = page.locator("section[aria-label='Resumo da campanha']")
    games = page.locator("main section", has=page.locator("h2", has_text="jogos"))
    page.screenshot(path=OUT / "campaign.png", full_page=True,
                    clip=union(page, [strip, games]))

    browser.close()
print("ok", sorted(f.name for f in OUT.iterdir()))
