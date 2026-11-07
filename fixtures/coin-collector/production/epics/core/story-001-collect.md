# STORY-001: Collect, win and restart

Status: Ready
Last Updated: 2026-11-07
Type: Integration
Layer: Core
GDD: N/A - minimal workflow uses design/game-brief.md
ADR: N/A - minimal local scene and external tuning
Depends on: None

## Acceptance Criteria

- [ ] Title appears; Enter starts the playable scene.
- [ ] Held arrow input moves the player; arena boundaries contain the player.
- [ ] P pauses and resumes; movement is frozen during pause.
- [ ] Collecting all three coins changes the counter and shows victory.
- [ ] R resets the score, coin positions and playable state.
- [ ] Losing application focus pauses the game.
- [ ] Title, pause, victory and restarted states have retained screenshots.

## Files

- project.godot
- main.tscn
- src/game.gd
- tuning.json
- qa.gd

## Test Evidence

production/qa/evidence/story-001-collect/
Run result: NOT VERIFIED - initial regression seed; runner writes actual results.
