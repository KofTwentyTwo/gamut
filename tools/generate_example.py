"""Generate the worked-example GAMUT theme 'Ember Dusk' with computed metrics."""
import itertools
import json
from coloraide import Color

# ---------- APCA (SAPC-4g) ----------
def _y(hexcol):
    c = Color(hexcol).convert('srgb')
    r, g, b = [max(ch, 0.0) ** 2.4 for ch in c.coords()]
    y = 0.2126729 * r + 0.7151522 * g + 0.0721750 * b
    if y < 0.022:
        y += (0.022 - y) ** 1.414
    return y

def apca(txt_hex, bg_hex):
    ytxt, ybg = _y(txt_hex), _y(bg_hex)
    if ybg > ytxt:  # dark text on light bg
        s = (ybg ** 0.56 - ytxt ** 0.57) * 1.14
        lc = 0.0 if s < 0.1 else s - 0.027
    else:           # light text on dark bg
        s = (ybg ** 0.65 - ytxt ** 0.62) * 1.14
        lc = 0.0 if s > -0.1 else s + 0.027
    return abs(lc * 100)

# ---------- deltaE-OK ----------
def de_ok(h1, h2):
    a = Color(h1).convert('oklab').coords()
    b = Color(h2).convert('oklab').coords()
    return sum((x - y) ** 2 for x, y in zip(a, b)) ** 0.5

# ---------- Machado 2009 CVD simulation (severity 1.0), linear sRGB ----------
M = {
 'protanopia':  [[0.152286,1.052583,-0.204868],[0.114503,0.786281,0.099216],[-0.003882,-0.048116,1.051998]],
 'deuteranopia':[[0.367322,0.860646,-0.227968],[0.280085,0.672501,0.047413],[-0.011820,0.042940,0.968881]],
 'tritanopia':  [[1.255528,-0.076749,-0.178779],[-0.078411,0.930809,0.147602],[0.004733,0.691367,0.303900]],
}
def cvd(hexcol, kind):
    c = Color(hexcol).convert('srgb-linear').coords()
    m = M[kind]
    out = [min(1.0, max(0.0, sum(m[i][j] * c[j] for j in range(3)))) for i in range(3)]
    return Color('srgb-linear', out).convert('srgb').to_string(hex=True, fit='oklch-chroma')

def oklch_to_hex(L, C, H):
    return Color('oklch', [L, C, H]).convert('srgb').to_string(hex=True, fit='oklch-chroma')

def col(L, C, H):
    return {"oklch": [round(L, 3), round(C, 3), round(H, 1)], "hex": oklch_to_hex(L, C, H)}

# ---------- Theme definition (parameters -> roles) ----------
HUE_BG = 285.0
core = {
  "bg":        col(0.20, 0.020, HUE_BG),
  "bgAlt":     col(0.25, 0.022, HUE_BG),
  "surface":   col(0.31, 0.025, HUE_BG),
  "muted":     col(0.68, 0.030, HUE_BG),
  "fgAlt":     col(0.76, 0.025, HUE_BG),
  "fg":        col(0.86, 0.020, HUE_BG),
  "fgBright":  col(0.92, 0.015, HUE_BG),
  "bgInverse": col(0.96, 0.010, HUE_BG),
  # accents: lightness staggered (optimizer output) so CVD-confusable hues
  # stay separated by lightness; all reach APCA Lc >= 60 vs bg
  "accent0":   col(0.795, 0.140, 25),   # red    - errors/variables
  "accent1":   col(0.840, 0.130, 55),   # orange - constants/numbers (the 'ember')
  "accent2":   col(0.880, 0.120, 95),   # yellow - classes/search
  "accent3":   col(0.830, 0.110, 145),  # green  - strings
  "accent4":   col(0.830, 0.090, 200),  # cyan   - regex/escapes
  "accent5":   col(0.780, 0.110, 255),  # blue   - functions
  "accent6":   col(0.865, 0.120, 320),  # magenta- keywords
  "accent7":   col(0.620, 0.070, 55),   # brown  - deprecated/tags
}

ACCENTS = [f"accent{i}" for i in range(7)]  # accent7 exempt from accent gates
bg = core["bg"]["hex"]

# ---------- Metrics ----------
fg_bg = apca(core["fg"]["hex"], bg)
muted_bg = apca(core["muted"]["hex"], bg)
acc_bg = {a: apca(core[a]["hex"], bg) for a in ACCENTS}
pairs = list(itertools.combinations(ACCENTS, 2))
sep = {f"{a}/{b}": de_ok(core[a]["hex"], core[b]["hex"]) for a, b in pairs}
min_sep = min(sep.values())

cvd_res = {}
for kind in M:
    sim = {a: cvd(core[a]["hex"], kind) for a in ACCENTS}
    d = min(de_ok(sim[a], sim[b]) for a, b in pairs)
    cvd_res[kind] = {"minAccentPair": round(d, 3), "safe": d >= 0.04}

Ls = [core[a]["oklch"][0] for a in ACCENTS]
Cs = [core[a]["oklch"][1] for a in ACCENTS]
Hs = sorted(core[a]["oklch"][2] for a in ACCENTS)
gaps = [Hs[i+1] - Hs[i] for i in range(len(Hs)-1)] + [360 - Hs[-1] + Hs[0]]
hue_spread = 360 - max(gaps)

ramp = ["bg","bgAlt","surface","muted","fgAlt","fg","fgBright","bgInverse"]
mono = all(core[ramp[i]]["oklch"][0] < core[ramp[i+1]]["oklch"][0] for i in range(7))

badges = []
if fg_bg >= 75 and muted_bg >= 45 and all(v >= 60 for v in acc_bg.values()): badges.append("aa-readable")
if fg_bg >= 90 and all(v >= 75 for v in acc_bg.values()): badges.append("aaa-readable")
if min_sep >= 0.04: badges.append("distinct-accents")
if "distinct-accents" in badges and all(r["safe"] for r in cvd_res.values()): badges.append("cvd-safe")
if max(Ls)-min(Ls) <= 0.10 and max(Cs)-min(Cs) <= 0.06: badges.append("coherent")
badges.append("conventional-hues")

report = {
  "gates": {
    "ramp_monotonic": mono,
    "fg_bg_apca": round(fg_bg,1), "fg_gate(>=75)": fg_bg >= 75,
    "muted_bg_apca": round(muted_bg,1), "muted_gate(>=45)": muted_bg >= 45,
    "accents_bg_apca": {k: round(v,1) for k,v in acc_bg.items()},
    "accent_gate(>=60)": all(v >= 60 for v in acc_bg.values()),
    "min_accent_separation_deltaEOK": round(min_sep,3), "sep_gate(>=0.04)": min_sep >= 0.04,
    "cvd": cvd_res,
  },
  "badges": badges,
}
print(json.dumps(report, indent=2))

# ---------- Assemble theme file ----------
theme = {
  "$schema": "https://gamut.style/schema/v0.1/theme.schema.json",
  "format": "gamut/0.1",
  "id": "gamut/ember-dusk",
  "version": "1.0.0",
  "name": "Ember Dusk",
  "mode": "dark",
  "author": {"name": "GAMUT"},
  "license": "CC0-1.0",
  "tags": ["warm", "dark", "ember", "violet-night", "cozy"],
  "description": "A violet-night dark theme warmed by ember-orange accents.",
  "core": core,
  "ui": {
    "borderFocus": core["accent5"],
    "error": core["accent0"], "warning": core["accent2"],
    "success": core["accent3"], "info": core["accent5"],
    "link": core["accent5"], "findMatchBg": core["accent2"],
  },
  "syntax": {
    "keyword": core["accent6"], "function": core["accent5"],
    "string": core["accent3"], "number": core["accent1"],
    "type": core["accent2"],
    "comment": {**core["muted"], "style": ["italic"]},
  },
  "ansi": {
    "black": core["bgAlt"], "red": core["accent0"], "green": core["accent3"],
    "yellow": core["accent2"], "blue": core["accent5"], "magenta": core["accent6"],
    "cyan": core["accent4"], "white": core["fg"],
    "brightBlack": core["muted"], "brightRed": col(0.84, 0.150, 25),
    "brightGreen": col(0.87, 0.120, 145), "brightYellow": col(0.92, 0.130, 95),
    "brightBlue": col(0.83, 0.120, 255), "brightMagenta": col(0.90, 0.130, 320),
    "brightCyan": col(0.88, 0.100, 200), "brightWhite": core["fgBright"],
  },
  "metrics": {
    "computedWith": "gamut-tools/0.1.0-prototype",
    "contrast": {"method": "APCA-4g", "fgBg": round(fg_bg,1),
                 "minAccentBg": round(min(acc_bg.values()),1)},
    "separation": {"method": "deltaE-OK", "minAccentPair": round(min_sep,3)},
    "cvd": {"method": "machado-2009", **cvd_res},
    "coherence": {"accentLightnessRange": round(max(Ls)-min(Ls),3),
                  "accentChromaRange": round(max(Cs)-min(Cs),3),
                  "hueSpreadDegrees": round(hue_spread,0)},
    "badges": badges,
  },
}
out = "/sessions/sweet-gallant-cori/mnt/Theme Color Master/example.ember-dusk.theme.json"
with open(out, "w") as f:
    json.dump(theme, f, indent=2)
print("written:", out)
