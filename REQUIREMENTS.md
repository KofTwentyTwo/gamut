# GAMUT — Product Requirements v0.1

**GAMUT**: *GAMUT's A Massive Universe of Themes.*

A website that generates, curates, and distributes color themes built on color
science, exportable to every major application format, backed by an open theme
format (see SPEC.md) positioned to become a cross-application standard.

Priorities: P0 = launch-blocking, P1 = fast-follow, P2 = later.

---

## 1. Goals

1. The largest catalog of *objectively verified* themes (target: 1,000+ at
   launch, all passing hard quality gates).
2. The easiest place to preview, filter, and export a theme to your app.
3. An open format + free CDN that apps can adopt directly, making the site
   the de facto theme registry.

Non-goals (v1): user accounts, user-submitted themes, paid features, image
"extract a theme from a photo" tools.

## 2. Generation pipeline (P0)

The catalog is produced by a deterministic, reproducible pipeline:

1. **Parameter sampling.** Theme = parameter vector:
   `{mode, bg_lightness, bg_hue_tint, base_hue, hue_scheme, chroma_level,
   contrast_target, accent_lightness, seed}`. Grid + stratified random
   sampling → ~50k candidates.
2. **Expansion.** Deterministic function expands parameters into a full GAMUT
   theme in OKLCH (Tier 0–3 + ANSI), then gamut-maps to sRGB hex.
3. **Hard gates** (reject): every MUST constraint in SPEC.md §4 — APCA
   contrast floors, monotonic ramp, min ΔEOK accent separation, CVD-simulated
   separation.
4. **Scoring** (rank): contrast headroom, hue spread entropy, chroma/lightness
   coherence, proximity to learned "aesthetic envelopes" fitted from ~50
   popular reference themes (Gruvbox, Nord, Catppuccin, Dracula, Tokyo Night,
   Solarized, Rosé Pine, ...).
5. **Diversity selection.** Farthest-point sampling over a theme-distance
   metric (weighted ΔEOK across resolved roles) to pick the final 1,000 —
   maximally distinct, all above the quality bar.
6. **Naming & tagging.** LLM pass generates a unique memorable name, a
   one-line description, and mood/style tags from the theme's measurable
   properties (hue family, warmth, contrast, chroma). Names checked for
   uniqueness and trademark collisions against existing famous themes.

Requirements:

- Fully reproducible from `(pipeline_version, seed)`.
- Pipeline outputs themes + metrics; metrics embedded per SPEC §7.
- Seeded ports: faithful conversions of ~50 famous open-licensed themes into
  GAMUT (license-permitting), clearly labeled as ports. (P0 — people search for
  what they know.)

## 3. Catalog & browsing (P0)

- **Filter** by: mode (dark/light), hue family, warmth, contrast level
  (badges: aa/aaa), chroma (muted ↔ vibrant), CVD-safe, tags, name.
- **Sort** by: quality score, popularity (downloads), newest, "vibe match".
- **Similarity**: "more like this" from theme-distance metric (P1: text→theme
  semantic search, "cozy autumn forest").
- **Theme page**: live previews, full palette with OKLCH/hex values, metric
  report (contrast matrix, CVD simulation toggle), all export options,
  permanent versioned URL.

## 4. Preview (P0)

Quality of preview decides conversion. Per theme, client-side rendered:

- Code samples in 5+ languages (TS, Python, Rust, Go, HTML/CSS) with
  realistic token coverage.
- Terminal session mock (ANSI 16 exercise: ls colors, git diff, htop-style).
- UI mock (sidebar/editor/statusbar — VS Code-like chrome).
- CVD simulation toggle (protanopia/deuteranopia/tritanopia) on all previews.
- Light-speed switching: previews re-skin via CSS custom properties, no reload.

## 5. Export (P0) and distribution (P0/P1)

Formats, in priority order:

| Priority | Target | Notes |
|----------|--------|-------|
| P0 | GAMUT JSON (canonical) | the format itself |
| P0 | VS Code theme JSON / VSIX | largest audience |
| P0 | base16 + base24 YAML | unlocks Tinted Theming's hundreds of app templates |
| P0 | CSS custom properties | web devs; zero-friction |
| P0 | WezTerm, Alacritty, Ghostty, Kitty | active terminal communities |
| P1 | JetBrains .icls/theme plugin | big audience, fiddlier format |
| P1 | iTerm2, Windows Terminal | |
| P1 | Tailwind config, W3C Design Tokens | design-system buyers |
| P2 | Sublime, Zed, Helix, Emacs, Xcode | long tail |

Distribution requirements:

- **CDN**: every theme at `cdn.gamut.style/{author}/{slug}@{version}.theme.json` —
  permanent, immutable, CORS-open, no auth. Plus `@latest` alias. (P0)
- **REST API**: search/filter endpoint mirroring catalog filters; export
  endpoint `/{id}/export/{format}`. Rate-limited, no key for reads. (P1)
- **Reference libraries**: `@gamut-themes/core` (JS/TS) and `gamut-theme` (Python) —
  parse, resolve fallbacks, validate, convert. MIT. (P1; JS one is P0 since
  the site itself uses it.)
- **Importers**: VS Code JSON → GAMUT, base16 YAML → GAMUT. (P1 — migration path.)

## 6. Standardization track (P1, strategic)

- Spec repo public on GitHub from day one; versioned; issues open.
- Validator CLI + GitHub Action ("validate my theme").
- One killer integration owned by us: VS Code extension that browses/installs
  any catalog theme live from the CDN. (P1)
- Interop pitch to Tinted Theming: GAMUT→base16 converter contributed to their
  org; GAMUT positioned as a superset, not a rival.
- Success metric: first third-party app consuming GAMUT natively.

## 7. Site engineering requirements

- Static-first: catalog is build-time generated JSON; site works as a static
  deploy + CDN (cheap, fast, cacheable). API can come later as functions.
- Theme pages SSR/SSG with OpenGraph palette preview images (social sharing
  is the growth loop; generate PNG cards at build time).
- Search/filter client-side over a compact index (1,000 themes ≈ small).
- Analytics on: filter usage, export format counts, download per theme
  (feeds popularity sort and tells us which exporters matter).
- Performance: theme page interactive < 1s on mid-range mobile; preview
  switch < 16ms (CSS variables only).
- Accessibility of the site itself: WCAG 2.2 AA — non-negotiable given the
  positioning.

## 8. Quality verification (P0)

- CI recomputes metrics for every published theme; publish fails on mismatch.
- Golden tests per exporter: GAMUT fixture → expected VS Code/base16/etc output.
- Round-trip tests: export→import→compare within ΔE tolerance.
- Visual regression snapshots of previews for N sample themes.

## 9. Risks

| Risk | Mitigation |
|------|------------|
| Chicken-and-egg on standard adoption | Site is valuable standalone; standard rides along |
| Generated themes feel samey/soulless | Aesthetic envelopes from loved themes; farthest-point diversity; strong naming |
| Big-name themes dominate search demand | Seed catalog with labeled ports of famous themes |
| Format wars / Tinted Theming friction | Strict superset + contributed converter, cooperative posture |
| Exporter format drift (apps change) | Golden tests + versioned exporters; community fixes via GitHub |

## 10. Open questions

- Monetization (later): API keys for high-volume reads? Team/brand palettes?
- User submissions: curation bar and validation pipeline for community themes.
- Trademark review process for generated names.
- Whether to publish the generator itself as open source (catalog
  reproducibility vs. moat).
