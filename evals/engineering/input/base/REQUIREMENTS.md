# Settings integration repair

Two collaborators added reduced-motion and master-volume settings on separate branches; the merge is currently unresolved in settings_state.gd. Both features must survive integration. Users also report repeated updates after opening settings multiple times, updates arriving after closing the panel, and UI/state disagreeing with persisted data after a save failure.

Keep the existing module boundaries and public APIs. SettingsState owns settings and emits changed snapshots. SettingsPanel observes a selected state while open. HUD is an independent consumer. Preserve the public smoke test and the other consumer.

Required behavior:
- Defaults are font_size=20, reduced_motion=false, master_volume=1.0. Font sizes 20/24/28/32 are valid; volume 0..1 is accepted. Invalid values do not save or notify. Both collaborators' setters remain available.
- Save callback success is exactly boolean true. Failure must not commit a new runtime state or notify consumers. An unchanged value is a silent accepted no-op. External snapshot/save references cannot mutate active state.
- Opening a panel displays current settings. Re-opening the same already-open binding is a no-op. Switching to another state detaches the previous binding. Close is idempotent, stops updates and does not mute HUD or other consumers; reopen shows the latest state.
- After repeated open/close cycles, one accepted state change produces one panel update and one HUD update. Keep source validation and unrelated state fields.
- Resolve the conflict according to both feature intents and stage the resolution, without committing. The final working tree must parse and the public smoke test must pass.

Deliver the modified scripts and concise NOTES.md: diagnosis, what changed, tests actually run and any remaining unknowns. Do not claim physical input, rendering or a full game was verified. This is an original bounded integration task, not a production project.
