# game-reference

**English** · [한국어](README.ko.md)

**Whatever game you're building, start here.** One page that tells you where every reference lives.
Written by a person and an AI team (Lumi, Sunsu, Sage, Blitz, Scout) together. Working rules: [`AGENTS.md`](AGENTS.md).

> The documents inside the folders are currently written in Korean; this index and the code (simulations, GDScript, Luau) are language-neutral.

## Two halves

| | Folder | What | Nature |
|---|---|---|---|
| **① Main** | [`reference/`](reference/README.md) | Popular games per genre · core loops · numbers · primary sources · open source · platform rules | Things that stay true over time. Each carries a **verified-on date**, not a creation date |
| ② Ours | [`our_games/`](our_games/README.md) | Snapshots of the games we've made, work in progress | Things that change. Used only as an index of "what we've already tried" |

## Starting point: what are you making?

| Genre | Folder | What's inside |
|---|---|---|
| Strategy (RTS · 4X · mobile SLG · card strategy · auto-battler · tower defense) | [`reference/genres/strategy/`](reference/genres/strategy/README.md) | Key titles · loops · TD numbers · lockstep sources |
| Shooter (FPS · TPS · battle royale · hero shooter · Roblox shooter) | [`reference/genres/shooter/`](reference/genres/shooter/README.md) | Key titles · TTK · netcode sources |
| MOBA | [`reference/genres/moba/`](reference/genres/moba/README.md) | Key titles · 3-lane economy · match length |
| Casual (hyper · hybrid · puzzle · sort/jam · merge · Roblox casual) | [`reference/genres/casual/`](reference/genres/casual/README.md) | Key titles · level generation · market numbers |
| RPG · idle (action · gacha · idle · survivor-likes · roguelite · Roblox simulator) | [`reference/genres/rpg/`](reference/genres/rpg/README.md) | Key titles · progression curves · pity |
| Horror · judgment (anomaly · checkpoint · shift work) | [`reference/genres/horror/`](reference/genres/horror/README.md) | Key titles · judgment-design sources · Roblox horror ratings |
| Arcade · Roblox formats (obby · runner · tycoon · .io · round-based party) | [`reference/genres/arcade/`](reference/genres/arcade/README.md) | Key titles · loop per format · maze/physics material |

Every genre folder has `README.md` (what sells and why) · `logic.md` (**base logic**: the implementation skeleton) · `sim/` (a Python rules simulation, checked with `--test`).

Genre-independent systems (game loop, FSM, RNG, economy, saving, anti-cheat) live in [`reference/systems/`](reference/systems/core_systems.md);
engine rules and tested pattern code in [`reference/platforms/godot/`](reference/platforms/godot/RULES.md) · [`reference/platforms/roblox/`](reference/platforms/roblox/RULES.md);
real numbers from other games in [`reference/data/`](reference/data/README.md); primary sources and learning material in [`reference/sources.md`](reference/sources.md).

## Layout

```
game-reference/
├─ README.md                  ← this file (English) · README.ko.md = Korean. Start here
├─ AGENTS.md                  ← AI team rules
├─ reference/                 ← ① Main: things that stay true
│  ├─ README.md               ← genre × platform index + fill status
│  ├─ genres/                 ← one folder per genre (same template)
│  │  ├─ strategy/  shooter/  moba/  casual/  rpg/  horror/  arcade/
│  │  │   ├─ README.md        ← key titles · loops · numbers · sources · traps · how we apply it
│  │  │   ├─ logic.md         ← base logic (MVP · state machine · data model · systems · tick · trust boundary · dials · platform mapping)
│  │  │   └─ sim/             ← Python rules simulation (python3 -I <genre>_sim.py --test)
│  │  └─ _template.md
│  ├─ systems/                ← engine-independent systems (core_systems.md · genres.md one-page summary)
│  ├─ platforms/godot/        ← Godot 4 rules · structure · libraries · tested GDScript patterns (+ headless tests)
│  ├─ platforms/roblox/       ← Roblox rules · structure · libraries · Luau patterns
│  ├─ data/                   ← numbers from reference games (every row has source:)
│  └─ sources.md              ← primary sources: books · articles · open source · curated lists
└─ our_games/                 ← ② Ours: game list snapshot · work in progress (anomaly_shop/ …)
```

## Core principles
1. **The server (the authority) decides.** The client only asks.
2. **Saves are versioned and idempotent.** Data never tangles, and a purchase is never granted twice.
3. **Numbers live in data.** Balancing should never need a code change.
4. **Check the license before reuse.** Code with no license, or GPL code, is used for its structure only.
5. **No number without a source.** Anything not confirmed is marked `unverified`.

## Status
- 2026-10-17: split the repo into `reference/` (main) and `our_games/` (ours) and set up the 7 genre folders. Fill status is in the table in [`reference/README.md`](reference/README.md).
- External repository facts (license, archived or not) were checked directly on each GitHub page as of each document's **verified-on date**.
- The GDScript in `reference/platforms/godot/patterns/` **passes 22 Godot 4.7.1 headless test items** (`godot --headless --path reference/platforms/godot`). Not yet tested on a real mobile device.
- The Luau in `reference/platforms/roblox/patterns/` has **only passed a syntax check** with `luau-compile`. Not yet run in Roblox Studio.
