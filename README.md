# GAMUT

**GAMUT**: *GAMUT's A Massive Universe of Themes.*

An open-source project to generate, verify, and distribute color themes using
color science — and a universal theme format any application can consume.

🌐 [gamut.style](https://gamut.style) *(coming soon)*

## What is this?

Most color themes are hand-made and unverified. GAMUT generates themes in
perceptually uniform color space (OKLCH) and subjects every one to hard,
machine-checkable quality gates:

- **Readability** — APCA contrast minimums for every foreground/background pair
- **Distinguishability** — minimum ΔE-OK separation between all accent colors
- **Colorblind safety** — accent separation verified under simulated
  protanopia, deuteranopia, and tritanopia (Machado 2009)
- **Coherence** — monotonic lightness ramps, bounded accent lightness/chroma

Themes that pass earn badges (`aa-readable`, `cvd-safe`, `coherent`, ...)
embedded in the theme file itself — verifiable by anyone, not marketing claims.

One GAMUT theme file exports to many targets: VS Code, base16/base24
(Tinted Theming), WezTerm, Alacritty, Ghostty, Kitty, CSS custom properties,
and more.

## Repository contents

| File | Purpose |
|------|---------|
| [SPEC.md](SPEC.md) | The GAMUT theme format specification (v0.1 draft) |
| [REQUIREMENTS.md](REQUIREMENTS.md) | Product requirements for the site & pipeline |
| [theme.schema.json](theme.schema.json) | JSON Schema for `.theme.json` files |
| [example.ember-dusk.theme.json](example.ember-dusk.theme.json) | Worked example theme, generated and verified |
| [tools/generate_example.py](tools/generate_example.py) | Prototype generator: OKLCH expansion, APCA, ΔE-OK, CVD simulation |

## Quick start

```bash
pip install coloraide
python3 tools/generate_example.py   # regenerates the example theme + gate report
```

## Status

Early design phase. The format spec, schema, and generator prototype work;
the generation pipeline at scale, site, and exporters are next.

Roadmap (short version): scale the generator → ~100 themes → preview page at
gamut.style → exporters → 1,000-theme catalog → public API/CDN.

## Architecture (planned)

Frontend application + [QQQ](https://github.com/Kingsrook/qqq) backend,
deployed on Kubernetes. Theme catalog generated offline by the Python
pipeline; themes served as immutable JSON from `cdn.gamut.style`.

## Licensing

- Code: [MIT](LICENSE)
- Theme format specification: CC-BY-4.0
- Published themes: CC0-1.0 (public domain)
