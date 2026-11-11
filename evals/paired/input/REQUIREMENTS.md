# Charge feedback repair task
This independent Godot fixture has regressions. Audit responsibilities and fix the behavior while preserving the current API.
- Charge starts at 0, trigger increases by 1, saturates at 5 and never becomes larger.
- Reset sets 0 and notifies views immediately, including when already 0.
- Pressing the native Charge button must use the same model behavior; pressing Reset must update the label without per-frame polling.
- The feedback is reusable: every trigger restarts its 0.7-second duration, including while active. It stops after that duration and must not grow the scene tree on repeated use.
- Use the existing advance(delta) interface; do not create a second Timer/Tween clock. Respect inherited scene pause behavior.
- Provide AUDIT.md with source anchors, state ownership, concrete issues and minimal decisions. Provide own tests and exact commands/results in RESULT.md. Do not claim rendering, hardware performance or human input were verified unless actually done.
- You may rearrange controls enough to prevent overlap; do not turn this task into a visual redesign.
