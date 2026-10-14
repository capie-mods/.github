<picture>
  <source media="(prefers-color-scheme: dark)" srcset="assets/banner-dark.svg">
  <source media="(prefers-color-scheme: light)" srcset="assets/banner-light.svg">
  <img src="assets/banner-light.svg" alt="CAPIE (Cyprian's API Extender), and the Hearts of Iron IV mods built on it." width="880">
</picture>

<img src="assets/status.svg" alt="HOI4: 1.19.3.0 only. Status: beta. Multiplayer: not tested. Source: open on release." width="637">

We make CAPIE (Cyprian's API Extender), a small native library for Hearts of Iron IV, and the
mods that use it. CAPIE gives mods things HOI4 script cannot do alone: typing into the game's own
text field, custom country and faction names on the map, and custom flags. The first mod built on
it is Rename Anything.

<img src="assets/rename-anything-hero.jpg" alt="Hearts of Iron IV diplomacy screen with a subject renamed to Province of Rizzia, its leader Rizzler King and its Rizz Party; the map shows the new name across Canada." width="880">

## Repositories

| Repository | What is in it |
|---|---|
| [rename-anything](https://github.com/capie-mods/rename-anything) | The mod for players. Rename your country, its leader, parties, states and cities in the panel that shows the name. |
| [capie](https://github.com/capie-mods/capie) | The native library, its launcher and installer, and `CONTRACT.md`, the API that mods code against. |
| [capie-script-sdk](https://github.com/capie-mods/capie-script-sdk) | Plain HOI4 script that lets any mod use CAPIE text fields without writing native code. It ships as its own Workshop item. |
| [capie-design](https://github.com/capie-mods/capie-design) | The design system both products share: colours sampled from the game, marks, diagrams and the docs theme. |

## Status

Beta, and nothing is on the Steam Workshop yet. What the repositories mark "Works today" was checked in the
game, in single player, on HOI4 1.19.3.0 with development builds. Nobody has tested multiplayer
with two players, so we make no claim that it works. On any other game version CAPIE stays off
and the scripts keep working.

## Getting started

Players: start with [Rename Anything](https://github.com/capie-mods/rename-anything). CAPIE
will install with one PowerShell line or an installer from GitHub Releases. Both are in
preparation, and there is no release to install yet.

Modders: read `CONTRACT.md` in [capie](https://github.com/capie-mods/capie) to see what the
library offers at each API level. Then look at
[capie-script-sdk](https://github.com/capie-mods/capie-script-sdk), which wraps the contract in
ordinary scripted effects and comes with a small demo mod.

<img src="assets/capie-native-field.jpg" alt="Two Rename Anything editors built on CAPIE: a leader name in the Politics panel and a subject's name and adjective, each in the game's own text field with Apply and Cancel." width="880">

## How we build it

- The source is open from the first public release. Until then the repositories are private.
  The intended licence is MIT.
- The DLLs have no network code. CAPIE, its launcher and the proxy loader open no network
  connections. Only the installer goes online, and only when you ask it to install or update.
- CAPIE fails closed. It checks the SHA-256 of `hoi4.exe` and of the code it hooks. If anything
  differs, CAPIE does not start and the game runs without it. Bad input is rejected and nothing
  changes.
- We never edit the game's own files. The launcher adds nothing
  to the game folder. The optional proxy loader adds one `version.dll` and its uninstall removes
  only that file, after checking its hash.
