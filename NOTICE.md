# NOTICE — Third-Party Attributions

CalebBible is licensed under the MIT License (see `LICENSE`).
This file consolidates third-party attributions for discoverability.

## Lineage

CalebBible is the rebranded continuation of **cys-terminal**
(https://github.com/idoforgod/cys-terminal) by the same author. Every `cys`/`CYSJavis`
identifier was renamed to `CalebBible`; the architecture, core mechanics, and pack
contents carry over unchanged. The third-party attributions below apply to both.

## Vendored code

| Component | Path | Upstream | License |
|---|---|---|---|
| portable-pty (patched) | `vendor/portable-pty/` | wezterm (Wez Furlong) | MIT — original copyright preserved in `vendor/portable-pty/LICENSE.md` |
| insane-search | `CalebBible-pack/skills/insane-search/` | fivetaku/insane-search | MIT — see `CalebBible-pack/skills/THIRD_PARTY.md` |
| skill collections (32 skills) | `CalebBible-pack/skills/` | NomaDamas/k-skill · obra/superpowers · mattpocock/skills | MIT — commit-pinned attributions in `CalebBible-pack/skills/THIRD_PARTY.md` |

## Design-only references (no code vendored)

Voicebox (MIT) and TimesFM (Apache-2.0) informed designs; no code was copied.
Clean-room reimplementation notes are embedded at the referencing sites
(`CalebBible-pack/bin/CalebBible_*.py` headers) and in `CalebBible-pack/skills/THIRD_PARTY.md`.

## Dependencies

Rust crate and npm dependencies are declared in `Cargo.toml` / `src-tauri/Cargo.toml` /
`ui/package.json`; direct dependencies are MIT or MIT/Apache-2.0 dual-licensed.
SQLite (bundled via rusqlite) is public domain.
