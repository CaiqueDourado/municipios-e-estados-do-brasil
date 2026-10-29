"""Screenshot-style image of one state in JSON (docs/img/state-json.png), for the README and Kaggle.

    python scripts/make_json_image.py

Takes docs/example-state.json (written by make_json.py), keeps the main fields of the state, shows the capital in
detail and the next two municipalities in one line each, highlights it and screenshots it with Playwright.
Needs pygments and playwright (with Chromium: python -m playwright install chromium).
"""

from __future__ import annotations

import json
from pathlib import Path

from playwright.sync_api import sync_playwright
from pygments import highlight
from pygments.formatters import HtmlFormatter
from pygments.lexers import JsonLexer

ROOT = Path(__file__).resolve().parents[1]
KEEP = ("ibge_code", "uf", "name", "region", "capital", "timezone", "municipality_count", "grammar", "census_2022", "hydrography")
KEEP_CITY = ("ibge_code", "name", "slug", "is_capital", "ddd", "siafi_code", "timezone", "utc_offset", "elevation_m",
             "regional_division", "census_2022", "hydrography")
KEEP_SHORT = ("ibge_code", "name", "slug", "ddd")
TRIM = {"grammar": ("article", "name_with_em", "name_with_de"),
        "regional_division": ("immediate_region", "intermediate_region"),
        "hydrography": ("hydro_springs", "hydro_rivers_km", "hydro_water_bodies")}
CUT = 90


def fmt(o, ind: int = 0) -> str:
    """JSON with small flat objects on one line, like a person would write it."""
    sp = "  " * ind
    if isinstance(o, dict):
        flat = json.dumps(o, ensure_ascii=False)
        if all(not isinstance(v, (dict, list)) for v in o.values()) and len(o) <= 4 and len(flat) <= 115:
            return flat
        return "{\n" + ",\n".join(f'{sp}  "{k}": {fmt(v, ind + 1)}' for k, v in o.items()) + f"\n{sp}}}"
    if isinstance(o, list):
        if all(not isinstance(v, (dict, list)) for v in o) and len(json.dumps(o, ensure_ascii=False)) <= 100:
            return json.dumps(o, ensure_ascii=False)
        return "[\n" + ",\n".join(f"{sp}  {fmt(v, ind + 1)}" for v in o) + f"\n{sp}]"
    return json.dumps(o, ensure_ascii=False)


CSS = """
body { margin: 0; background: #fdfdfc; font-family: Inter, 'DejaVu Sans', sans-serif; }
.win { margin: 28px; border-radius: 12px; overflow: hidden; display: inline-block;
       box-shadow: 0 10px 30px rgba(17,17,17,.12), 0 0 0 1px #d9dde3; background: #ffffff; }
.bar { height: 38px; background: #f3f4f6; border-bottom: 1px solid #e5e7eb; display: flex; align-items: center;
       padding: 0 14px; gap: 8px; }
.dot { width: 12px; height: 12px; border-radius: 50%; }
.title { margin-left: 14px; font: 13px 'DejaVu Sans Mono', monospace; color: #555555; }
.code { padding: 16px 26px 20px 0; display: flex; }
.ln { color: #b8bec7; text-align: right; padding: 0 16px 0 18px; user-select: none; }
pre { margin: 0; font: 14px/1.5 'DejaVu Sans Mono', monospace; }
.highlight { background: transparent; }
.highlight .nt { color: #2a78d6; }               /* keys */
.highlight .s2 { color: #b4531f; }               /* strings */
.highlight .mi, .highlight .mf { color: #12895f; } /* numbers */
.highlight .kc { color: #8250df; font-weight: bold; } /* true false null */
.highlight .p { color: #555555; }
"""


def render(text: str, title: str, out: Path) -> None:
    json.loads(text)  # still valid JSON
    code = highlight(text, JsonLexer(), HtmlFormatter(nowrap=True))
    lines = "\n".join(str(i) for i in range(1, text.count("\n") + 2))
    html = f"""<!doctype html><html><head><meta charset="utf-8"><style>{CSS}</style></head><body>
<div class="win" id="win"><div class="bar"><span class="dot" style="background:#ff5f57"></span>
<span class="dot" style="background:#febc2e"></span><span class="dot" style="background:#28c840"></span>
<span class="title">{title}</span></div>
<div class="code"><pre class="ln">{lines}</pre><pre class="highlight">{code}</pre></div></div></body></html>"""
    with sync_playwright() as pw:
        browser = pw.chromium.launch()
        page = browser.new_page(device_scale_factor=2, viewport={"width": 1100, "height": 800})
        page.set_content(html)
        page.locator("#win").screenshot(path=str(out))
        browser.close()
    print(out)


def cut(v):
    if isinstance(v, str):
        v = " ".join(v.split())
        return v if len(v) <= CUT else v[:CUT].rstrip() + "…"
    if isinstance(v, list):
        return v[:5]
    return v


def pick(row: dict, keys: tuple[str, ...]) -> dict:
    out = {}
    for k in keys:
        v = row.get(k)
        if isinstance(v, dict):
            v = {c: x for c, x in v.items() if c in TRIM.get(k, v)}
        if v is not None:
            out[k] = cut(v)
    return out


def main() -> None:
    docs = ROOT / "docs"
    state = json.loads((docs / "example-state.json").read_text(encoding="utf-8"))
    rec = pick(state, KEEP)
    cities = state["municipios"]
    rec["municipios"] = [pick(cities[0], KEEP_CITY)] + [pick(c, KEEP_SHORT) for c in cities[1:3]]
    render(fmt(rec), f"docs/example-state.json · {state['name']} and 3 of its {len(cities)} municipalities, trimmed",
           docs / "img" / "state-json.png")


if __name__ == "__main__":
    main()
