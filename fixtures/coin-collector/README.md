# Coin Collector

Small offline Godot 4.5.1 / GDScript fixture for the Codex studio lifecycle.
Open project.godot in Godot and run the main scene. Enter starts the game;
arrow keys move; P or Esc pauses; R restarts. Collect all three coins to win.

The game makes no network requests and needs no external assets or addons.
Gameplay values are in tuning.json. This source fixture is under the repository's
MIT license. The game is not a standalone executable distribution.

To verify logic directly with a locally installed Godot:

```sh
godot --headless --path fixtures/coin-collector --script qa.gd --quit-after 600
```

Omit --headless to render and save screenshots. For the entire isolated studio
cycle, including configuration, story updates and tested source packaging, use
[tools/run_studio_cycle.py](../../tools/run_studio_cycle.py) as described in the
[validation report](../../docs/validation/cycle-2026-11-07.md).
