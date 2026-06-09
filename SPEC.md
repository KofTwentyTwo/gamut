# GAMUT Theme Format — Specification v0.1 (Draft)

**GAMUT**: *GAMUT's A Massive Universe of Themes.*

A universal, machine-verifiable color theme format. One theme file serves every
consumer — terminals, code editors, web apps, GUI toolkits — through a tiered
role model with defined fallbacks.

File extension: `.theme.json`.
Media type (proposed): `application/theme+json`.

---

## 1. Design principles

1. **Layered, not flat.** Consumers read the deepest tier they understand and
   fall back upward. A terminal needs 16 colors; an IDE wants 100+. Same file.
2. **Superset of base16/base24.** Tier 1 maps losslessly onto base16 slots, so
   the entire Tinted Theming template ecosystem can consume any GAMUT theme via a
   trivial converter.
3. **Perceptual canonical space.** Colors are authored and stored in OKLCH.
   sRGB hex is included as a pre-computed convenience, never as the source of
   truth.
4. **Quality is in the file.** Every theme carries computed accessibility and
   coherence metrics. Claims like "AA readable" or "colorblind-safe" are
   machine-checkable, not marketing.
5. **Free to adopt.** Spec is open (CC-BY), themes are CC0, parsers are MIT.

---

## 2. File structure

```json
{
  "$schema": "https://gamut.style/schema/v0.1/theme.schema.json",
  "format": "gamut/0.1",
  "id": "gamut/ember-dusk",
  "version": "1.0.0",
  "name": "Ember Dusk",
  "mode": "dark",
  "author": { "name": "GAMUT", "url": "https://gamut.style" },
  "license": "CC0-1.0",
  "tags": ["warm", "low-contrast", "autumn", "cozy"],
  "description": "A warm dark theme with ember-orange accents.",

  "palette":  { ... },   // Tier 0 — raw named colors
  "core":     { ... },   // Tier 1 — base16-compatible roles
  "ui":       { ... },   // Tier 2 — interface roles
  "syntax":   { ... },   // Tier 3 — syntax/token roles
  "ansi":     { ... },   // Terminal ANSI 16 mapping

  "metrics":  { ... }    // Computed quality metadata (§7)
}
```

### Identity and versioning

- `id` — namespaced, immutable: `author-slug/theme-slug`. Lowercase kebab-case.
- `version` — semver. Color changes bump minor; role additions bump patch;
  breaking semantic changes bump major.
- A theme at `id@version` is permanent and immutable once published.

### Color value encoding

Every color value is an object:

```json
{ "oklch": [0.72, 0.11, 55], "hex": "#d99962" }
```

- `oklch` — `[L, C, H]`. L ∈ [0,1], C ≥ 0, H ∈ [0,360). Canonical.
- `hex` — sRGB, gamut-mapped from the OKLCH value (CSS Color 4 algorithm).
  MUST equal the gamut-mapped conversion; validators reject mismatches.
- Optional `alpha` ∈ [0,1], default 1.

---

## 3. Tier 0 — Palette

Free-form named colors. This is the designer's raw material; roles in higher
tiers reference palette entries by name (`"$ember"`) or define literal values.

```json
"palette": {
  "ember":  { "oklch": [0.72, 0.13, 50],  "hex": "#e0905a" },
  "night0": { "oklch": [0.22, 0.02, 280], "hex": "#1a1823" }
}
```

No semantics. Consumers MUST NOT read Tier 0 directly except for display.

## 4. Tier 1 — Core roles (base16-compatible)

Sixteen required roles with fixed semantics, structured as an 8-step
monochrome-ish ramp plus 8 accents. Designed for lossless export to base16.

| Role        | Meaning                                  | base16 |
|-------------|------------------------------------------|--------|
| `bg`        | Default background                       | base00 |
| `bgAlt`     | Lighter/darker background (status bars)  | base01 |
| `surface`   | Selection background                     | base02 |
| `muted`     | Comments, invisibles                     | base03 |
| `fgAlt`     | Dim foreground                           | base04 |
| `fg`        | Default foreground                       | base05 |
| `fgBright`  | Emphasized foreground                    | base06 |
| `bgInverse` | Brightest background (light bg in dark)  | base07 |
| `accent0`   | Red-ish — errors, variables              | base08 |
| `accent1`   | Orange-ish — constants, numbers          | base09 |
| `accent2`   | Yellow-ish — classes, search             | base0A |
| `accent3`   | Green-ish — strings, additions           | base0B |
| `accent4`   | Cyan-ish — regex, escapes                | base0C |
| `accent5`   | Blue-ish — functions, info               | base0D |
| `accent6`   | Magenta-ish — keywords                   | base0E |
| `accent7`   | Brown/deprecated — tags                  | base0F |

Constraints (validated, see §7):

- Ramp `bg → bgInverse` MUST be monotonic in OKLCH lightness.
- `fg` vs `bg` MUST reach APCA |Lc| ≥ 75.
- `muted` vs `bg` MUST reach APCA |Lc| ≥ 45.
- Accents `accent0–6` vs `bg` MUST each reach APCA |Lc| ≥ 60.
- Hue conventions above are SHOULD, not MUST (themes may subvert them but
  lose the `conventional-hues` badge).

## 5. Tier 2 — UI roles

Interface semantics beyond the core ramp. All OPTIONAL; each role has a
spec-defined fallback into Tier 1, so consumers can always resolve a value.

| Role               | Fallback     | Role             | Fallback   |
|--------------------|--------------|------------------|------------|
| `surfaceRaised`    | `bgAlt`      | `link`           | `accent5`  |
| `border`           | `surface`    | `linkVisited`    | `accent6`  |
| `borderFocus`      | `accent5`    | `error`          | `accent0`  |
| `selectionBg`      | `surface`    | `warning`        | `accent2`  |
| `selectionFg`      | `fg`         | `success`        | `accent3`  |
| `cursor`           | `fg`         | `info`           | `accent5`  |
| `cursorText`       | `bg`         | `diffAdded`      | `accent3`  |
| `findMatchBg`      | `accent2`    | `diffRemoved`    | `accent0`  |
| `hoverBg`          | `surface`    | `diffChanged`    | `accent2`  |
| `disabledFg`       | `muted`      | `badgeBg`        | `accent5`  |
| `tooltipBg`        | `surfaceRaised` | `badgeFg`     | `bg`       |
| `scrollbar`        | `surface`    | `shadow`         | `bg`       |

Resolution algorithm: `resolve(role) = theme.ui[role] ?? resolve(fallback(role))`.
Fallback chains are guaranteed acyclic and terminate in Tier 1.

## 6. Tier 3 — Syntax roles

Token-level semantics for editors and highlighters. All OPTIONAL with Tier 1
fallbacks. Aligned with the TextMate/Tree-sitter/Semantic-token vocabulary so
exporters are mechanical.

| Role         | Fallback  | Role          | Fallback  |
|--------------|-----------|---------------|-----------|
| `keyword`    | `accent6` | `string`      | `accent3` |
| `function`   | `accent5` | `stringEscape`| `accent4` |
| `type`       | `accent2` | `number`      | `accent1` |
| `class`      | `accent2` | `constant`    | `accent1` |
| `variable`   | `fg`      | `comment`     | `muted`   |
| `property`   | `accent4` | `commentDoc`  | `muted`   |
| `parameter`  | `fg`      | `operator`    | `fgAlt`   |
| `decorator`  | `accent1` | `punctuation` | `fgAlt`   |
| `tag`        | `accent0` | `regex`       | `accent4` |
| `attribute`  | `accent2` | `markupHeading` | `accent5` |
| `namespace`  | `accent2` | `markupBold`  | `fgBright` |

Optional per-role style flags: `"style": ["italic" | "bold" | "underline"]`.

## 7. `metrics` — computed quality metadata

Generated by tooling at publish time, never hand-written. Validators recompute
and reject files whose metrics don't match their colors.

```json
"metrics": {
  "computedWith": "gamut-tools/0.1.0",
  "contrast": {
    "method": "APCA-4g",
    "fgBg": 82.1,
    "minAccentBg": 63.4,
    "matrix": { "...": "optional full pairwise Lc table" }
  },
  "separation": {
    "method": "deltaE-OK",
    "minAccentPair": 0.085
  },
  "cvd": {
    "method": "machado-2009",
    "protanopia":  { "minAccentPair": 0.052, "safe": true },
    "deuteranopia":{ "minAccentPair": 0.048, "safe": true },
    "tritanopia":  { "minAccentPair": 0.061, "safe": true }
  },
  "coherence": {
    "accentLightnessRange": 0.06,
    "accentChromaRange": 0.04,
    "hueSpreadDegrees": 296
  },
  "badges": ["aa-readable", "cvd-safe", "conventional-hues"]
}
```

### Badge thresholds (v0.1)

| Badge               | Requirement                                            |
|---------------------|--------------------------------------------------------|
| `aa-readable`       | fg/bg ≥ 75 Lc; all accents/bg ≥ 60 Lc; muted/bg ≥ 45 Lc |
| `aaa-readable`      | fg/bg ≥ 90 Lc; all accents/bg ≥ 75 Lc                  |
| `distinct-accents`  | min pairwise ΔEOK between accents ≥ 0.04               |
| `cvd-safe`          | `distinct-accents` holds under all three CVD simulations |
| `coherent`          | accent lightness range ≤ 0.10 and chroma range ≤ 0.06  |
| `conventional-hues` | accent hues within spec hue windows                    |

## 8. Export mappings (normative appendices, separate docs)

Each exporter is a pure function of a resolved theme (all fallbacks applied):

- **base16/base24 YAML** — Tier 1 (+ ANSI for base24). Lossless.
- **VS Code** — `ui` → workbench colors, `syntax` → tokenColors/semantic tokens.
- **JetBrains** — `.icls` + theme JSON plugin format.
- **Terminals** — WezTerm/Alacritty/Ghostty/Kitty TOML/YAML, iTerm2 plist,
  Windows Terminal JSON (from `ansi` + core).
- **Web** — CSS custom properties, Tailwind config, W3C Design Tokens JSON.

## 9. Conformance

- **Reader**: resolves fallbacks correctly; uses `hex` or `oklch` per its
  color capability; ignores unknown fields (forward compatibility).
- **Writer**: emits valid schema, correct gamut-mapped hex, accurate metrics.
- **Validator** (reference implementation): JSON Schema + the MUST constraints
  in §4 + metric recomputation.

## 10. Open questions for v0.2

- Light/dark theme pairing (`companion` field linking two ids?).
- High-contrast variants as derivations vs. separate themes.
- ANSI bright-color derivation rules when `ansi` is omitted.
- Signed themes / integrity hashes for CDN distribution.
- Non-color tokens (font hints, blur, transparency) — likely out of scope.
