#!/usr/bin/env python3
"""Rendu des visuels Instagram Avialog (1080x1350, PNG) à partir d'un fichier JSON.

Usage : python3 render.py post.json sortie_dir/
Le JSON décrit une liste de "slides" (1 = post simple, 2-10 = carrousel).

Champs d'une slide (tous optionnels sauf title) :
  eyebrow  : petit label orange en capitales (ex. "PILOTE", "ATELIER PART-CAO")
  title    : titre principal ; entourer un mot de *astérisques* pour le passer en orange
  body     : paragraphe court (2-3 lignes max)
  stat     : gros chiffre (ex. "215€") ; stat_label : légende du chiffre
  terminal : liste de lignes façon console (sans "$" devant)
  items    : liste de 2 à 4 cartes {"k": "titre court", "v": "description"}
  choices  : 2 à 4 réponses fermées pour un post question (A/B/C/D)
  cta      : phrase d'appel à l'action en bas (ex. "Essai gratuit sur avialog.fr")

Règles de marque appliquées : orange #F97316, fond #080a12, Barlow Condensed + Space Mono,
pas de numéro de slide, pas de chevrons, pas de "$" devant les commandes.
"""
import json, sys, html, re, pathlib, os

os.environ.setdefault("PLAYWRIGHT_BROWSERS_PATH", "/opt/pw-browsers")
HERE = pathlib.Path(__file__).resolve().parent
FONTS = HERE.parent / "fonts"
ORANGE = "#F97316"
BG = "#080a12"


def fmt_title(t):
    t = html.escape(t)
    return re.sub(r"\*(.+?)\*", r'<span class="o">\1</span>', t)


def slide_html(s, is_cover, total):
    parts = []
    if s.get("eyebrow"):
        parts.append(f'<div class="eyebrow">{html.escape(s["eyebrow"])}</div>')
    if s.get("stat"):
        parts.append(f'<div class="stat">{html.escape(s["stat"])}</div>')
        if s.get("stat_label"):
            parts.append(f'<div class="statlabel">{html.escape(s["stat_label"])}</div>')
    size = "xl" if is_cover and len(s.get("title", "")) < 48 else ("l" if len(s.get("title", "")) < 70 else "m")
    parts.append(f'<h1 class="{size}">{fmt_title(s.get("title",""))}</h1>')
    if s.get("body"):
        parts.append(f'<p class="body">{html.escape(s["body"])}</p>')
    if s.get("terminal"):
        lines = "".join(f'<div class="tl">{html.escape(l)}</div>' for l in s["terminal"])
        parts.append(f'<div class="term"><div class="tbar"><i></i><i></i><i></i><span>avialog</span></div>{lines}</div>')
    if s.get("items"):
        cards = "".join(
            f'<div class="card"><div class="ck">{html.escape(i["k"])}</div><div class="cv">{html.escape(i.get("v",""))}</div></div>'
            for i in s["items"][:4])
        parts.append(f'<div class="cards">{cards}</div>')
    if s.get("choices"):
        ch = "".join(
            f'<div class="choice"><span class="letter">{"ABCD"[n]}</span>{html.escape(c)}</div>'
            for n, c in enumerate(s["choices"][:4]))
        parts.append(f'<div class="choices">{ch}</div>')
    cta = f'<div class="cta">{html.escape(s["cta"])}</div>' if s.get("cta") else ""
    swipe = '<div class="swipe">GLISSE POUR LA SUITE</div>' if (is_cover and total > 1) else ""
    return f"""<!doctype html><html><head><meta charset="utf-8"><style>
@font-face{{font-family:BC;src:url('file://{FONTS}/BarlowCondensed-ExtraBold.ttf');font-weight:800}}
@font-face{{font-family:BC;src:url('file://{FONTS}/BarlowCondensed-Bold.ttf');font-weight:700}}
@font-face{{font-family:BC;src:url('file://{FONTS}/BarlowCondensed-SemiBold.ttf');font-weight:600}}
@font-face{{font-family:BC;src:url('file://{FONTS}/BarlowCondensed-Medium.ttf');font-weight:500}}
@font-face{{font-family:SM;src:url('file://{FONTS}/SpaceMono-Regular.ttf');font-weight:400}}
@font-face{{font-family:SM;src:url('file://{FONTS}/SpaceMono-Bold.ttf');font-weight:700}}
*{{margin:0;padding:0;box-sizing:border-box}}
html,body{{width:1080px;height:1350px;background:{BG};color:#f4f4f5;overflow:hidden}}
body{{position:relative;font-family:BC,sans-serif}}
.grid{{position:absolute;inset:0;background-image:linear-gradient(rgba(255,255,255,.035) 1px,transparent 1px),linear-gradient(90deg,rgba(255,255,255,.035) 1px,transparent 1px);background-size:54px 54px}}
.glow{{position:absolute;width:900px;height:900px;right:-380px;top:-380px;background:radial-gradient(circle,rgba(249,115,22,.16),transparent 62%)}}
.stripes{{position:absolute;left:0;right:0;bottom:0;height:14px;background:repeating-linear-gradient(-45deg,{ORANGE} 0 18px,transparent 18px 36px);opacity:.85}}
.br{{position:absolute;width:64px;height:64px;border-color:{ORANGE};border-style:solid;opacity:.9}}
.br.tl{{left:48px;top:48px;border-width:5px 0 0 5px}}.br.tr{{right:48px;top:48px;border-width:5px 5px 0 0}}
.br.bl{{left:48px;bottom:62px;border-width:0 0 5px 5px}}.br.brr{{right:48px;bottom:62px;border-width:0 5px 5px 0}}
.wrap{{position:absolute;left:104px;right:104px;top:150px;bottom:190px;display:flex;flex-direction:column;justify-content:center;gap:34px}}
.eyebrow{{font-family:SM;font-weight:700;font-size:26px;letter-spacing:6px;color:{ORANGE};text-transform:uppercase}}
h1{{font-weight:800;text-transform:uppercase;line-height:.95;letter-spacing:-1px}}
h1.xl{{font-size:134px}}h1.l{{font-size:104px}}h1.m{{font-size:80px}}
.o{{color:{ORANGE}}}
.body{{font-family:BC;font-weight:500;font-size:44px;line-height:1.22;color:#d4d4d8;max-width:860px}}
.stat{{font-weight:800;font-size:250px;line-height:.85;color:{ORANGE};letter-spacing:-4px}}
.statlabel{{font-family:SM;font-size:28px;color:#a1a1aa;letter-spacing:2px;text-transform:uppercase;margin-top:-10px}}
.term{{background:#0f121c;border:2px solid rgba(249,115,22,.35);border-radius:14px;padding:0 0 26px;font-family:SM;font-size:30px;overflow:hidden}}
.tbar{{display:flex;gap:12px;align-items:center;padding:18px 24px;border-bottom:1px solid rgba(255,255,255,.08);margin-bottom:18px}}
.tbar i{{width:16px;height:16px;border-radius:50%;background:#3f3f46}}.tbar i:first-child{{background:{ORANGE}}}
.tbar span{{margin-left:auto;font-size:22px;color:#71717a}}
.tl{{padding:4px 30px;color:#e4e4e7;white-space:pre-wrap}}.tl:first-of-type{{color:{ORANGE}}}
.cards{{display:grid;grid-template-columns:1fr 1fr;gap:22px}}
.card{{border:2px solid rgba(249,115,22,.28);background:rgba(249,115,22,.06);border-radius:14px;padding:28px 28px 30px}}
.ck{{font-weight:700;font-size:44px;text-transform:uppercase;color:#fafafa;line-height:1}}
.cv{{font-family:SM;font-size:22px;color:{ORANGE};margin-top:14px;line-height:1.4}}
.choices{{display:flex;flex-direction:column;gap:18px}}
.choice{{display:flex;align-items:center;gap:26px;border:2px solid rgba(255,255,255,.14);border-radius:14px;padding:22px 28px;font-weight:600;font-size:48px;text-transform:uppercase}}
.letter{{font-family:SM;font-weight:700;font-size:30px;color:{BG};background:{ORANGE};width:58px;height:58px;border-radius:10px;display:flex;align-items:center;justify-content:center;flex:none}}
.cta{{position:absolute;left:104px;right:104px;bottom:200px;font-family:SM;font-weight:700;font-size:28px;color:{BG};background:{ORANGE};padding:22px 30px;border-radius:12px;text-align:center;letter-spacing:1px}}
.foot{{position:absolute;left:104px;right:104px;bottom:92px;display:flex;justify-content:space-between;align-items:flex-end}}
.mark{{font-weight:800;font-size:56px;letter-spacing:1px;line-height:1}}.mark b{{color:{ORANGE}}}
.url{{font-family:SM;font-size:24px;color:#a1a1aa}}
.swipe{{position:absolute;right:104px;top:92px;font-family:SM;font-size:20px;letter-spacing:4px;color:#a1a1aa}}
</style></head><body>
<div class="grid"></div><div class="glow"></div>
<div class="br tl"></div><div class="br tr"></div><div class="br bl"></div><div class="br brr"></div>
{swipe}
<div class="wrap">{''.join(parts)}</div>
{cta}
<div class="foot"><div class="mark">avia<b>log</b></div><div class="url">avialog.fr</div></div>
<div class="stripes"></div>
</body></html>"""


def main():
    spec = json.loads(pathlib.Path(sys.argv[1]).read_text())
    out = pathlib.Path(sys.argv[2]).resolve(); out.mkdir(parents=True, exist_ok=True)
    slides = spec["slides"]
    from playwright.sync_api import sync_playwright
    paths = []
    with sync_playwright() as p:
        b = p.chromium.launch()
        pg = b.new_page(viewport={"width": 1080, "height": 1350})
        for i, s in enumerate(slides):
            hp = out / f"slide{i+1}.html"
            hp.write_text(slide_html(s, i == 0, len(slides)))
            pg.goto(hp.as_uri()); pg.wait_for_timeout(250)
            png = out / f"slide{i+1}.png"
            pg.screenshot(path=str(png)); paths.append(str(png))
        b.close()
    print("\n".join(paths))


if __name__ == "__main__":
    main()
