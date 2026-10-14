<picture>
  <source media="(prefers-color-scheme: dark)" srcset="assets/banner-dark.svg">
  <source media="(prefers-color-scheme: light)" srcset="assets/banner-light.svg">
  <img src="assets/banner-light.svg" alt="CAPIE (Cyprian's API Extender), and the Hearts of Iron IV mods built on it." width="880">
</picture>

<img src="assets/status.svg" alt="HOI4: 1.19.3.0 only. Status: beta. Multiplayer: not tested. Source: open on release." width="637">

Hearts of Iron IV lets you name a division anything you like, but your own country, its leader
and its party keep whatever name the game hands them. We wanted to fix that, and HOI4 script
alone could not do it. So we wrote CAPIE (Cyprian's API Extender), a small native library that
gives mods a few things the scripting language lacks: typing into the game's own text field,
custom country and faction names on the map, and custom flags. Rename Anything is the first mod
built on it.

<img src="assets/rename-anything-hero.jpg" alt="Hearts of Iron IV diplomacy screen with a subject renamed to Province of Rizzia, its leader Rizzler King and its Rizz Party; the map shows the new name across Canada." width="880">

## Repositories

| Repository | What is in it |
|---|---|
| [rename-anything](https://github.com/capie-mods/rename-anything) | The mod for players. You rename your country, its leader, parties, states and cities in the panel that shows the name. |
| [capie](https://github.com/capie-mods/capie) | The native library, its launcher and installer, and `CONTRACT.md`, the API that mods code against. |
| [capie-script-sdk](https://github.com/capie-mods/capie-script-sdk) | Plain HOI4 script, so a mod can use CAPIE text fields without any native code. It ships as its own Workshop item. |
| [capie-design](https://github.com/capie-mods/capie-design) | The design system both products share: colours sampled from the game, marks, diagrams and the docs theme. |

## Where things stand

We are in beta and nothing is on the Steam Workshop yet. Anything the repositories mark "Works
today" was checked in the game, in single player, on HOI4 1.19.3.0 with development builds.
Nobody has tried multiplayer with two players, so we make no claim that it works. On any other
game version CAPIE stays off and the scripts keep working.

## Getting started

If you play, start with [Rename Anything](https://github.com/capie-mods/rename-anything). CAPIE
will install with one PowerShell line or with an installer from GitHub Releases. Both are still
in preparation, and there is no release to install yet.

If you make mods, read `CONTRACT.md` in [capie](https://github.com/capie-mods/capie). It lists
what the library offers at each API level. Then have a look at
[capie-script-sdk](https://github.com/capie-mods/capie-script-sdk): it wraps the contract in
ordinary scripted effects and comes with a small demo mod.

<img src="assets/capie-native-field.jpg" alt="Two Rename Anything editors built on CAPIE: a leader name in the Politics panel and a subject's name and adjective, each in the game's own text field with Apply and Cancel." width="880">

## Ground rules

- The source opens with the first public release. Until then the repositories are private. We
  intend to use the MIT licence.
- There is no network code in the DLLs. CAPIE, its launcher and the proxy loader never open a
  connection. The installer goes online only when you ask it to install or update.
- CAPIE fails closed. It checks the SHA-256 of `hoi4.exe` and of the code it hooks, and if
  anything differs it does not start; the game then runs without it. Bad input is rejected and
  nothing changes.
- We never edit the game's own files. The launcher adds nothing to the game folder. The
  optional proxy loader adds one `version.dll`, and its uninstall removes only that file after
  checking its hash.
