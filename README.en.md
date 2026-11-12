# GameDev Workbench

A skill and offline toolbox for AI-assisted small and medium game development: architecture, integrated features, debugging, team Git work, native UI/VFX and creative design.

[中文](README.md) · [Download](https://github.com/kaltsit2077-dev/gamedev-workbench/releases/tag/v0.10.0-preview) · [Practical cases](docs/CASE-STUDIES.md) · [Usage](docs/QUICKSTART.md)

The skill guides project-specific decisions and implementation. Tools provide bounded evidence: Godot references/UIDs/named inheritance and module rules; read-only Git inspection; explicit project tests; native UI/VFX fixtures; narrative/economy/asset checks. They do not automatically operate an editor or build a complete game.

Observed changes:

- In an unchanged existing 497-file game snapshot, 33 previously labeled named-inheritance edges went from 0 matched to 33 matched. Private source and index stayed unchanged; this is a positive subset, not whole-project accuracy.
- An original architecture case compiles despite domain state inheriting a view class. Version 0.9 missed it; the new checker reports the dependency. Removing that parent changes the same native acceptance from 3/4 to 4/4 while preserving the three functional checks. The defect is deliberately introduced, not a claimed production bug.
- The existing native menu/effect case records 121 graphical checks and 40 frames across five viewports, including large text, focus recovery and repeated-use cleanup. These are historical fixture records, not new rendering or an aesthetic score.

No general productivity or cost improvement is established. [Raw evidence and reproducible commands](docs/CASE-STUDIES.md).

Python 3.11+, standard library only:

```text
python tools/gdw.py validate
python tools/gdw.py analyze-project "your Godot project" --output analysis.json
python tools/gdw.py review-git "repository root" --output git-review.json
python tools/gdw.py install --dest "client skills directory"
```

Ask `$gamedev-workbench` to review architecture, reproduce/fix a bug, integrate changes or build native UI/VFX. Project rules and authorization take priority. Thirteen task modes load references on demand. Outputs refuse overwrite; installation does not replace an existing skill.

Native architecture demonstration, using official Godot 4.7.2 in isolated writable copies:

```text
python tools/run_architecture_case.py --engine "Godot executable" --scratch "new writable projects directory" --output-dir "new writable evidence directory"
```

The before case intentionally fails one acceptance check. No user game is modified. Godot has actual Windows native evidence; Unity/Unreal editor execution, browser rendering, physical input and performance have separate unverified limits. Python CI does not run native engines.

[Apache-2.0](LICENSE) for original work. The small official-demo evaluation subset retains its MIT license. [Validation](docs/VALIDATION.md) · [Third-party notices](THIRD_PARTY_NOTICES.md).
