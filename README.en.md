# GameDev Workbench

A portable Agent Skill and offline Python toolbox for independent game developers. Focus: architecture, native game UI, gameplay features and visual effects. Includes design, narrative, audience, asset and validation guidance.

Python 3.11+, no third-party packages. Run `python tools/gdw.py --help`. Copy the entire `skills/gamedev-workbench` directory into your client's skill directory, or use install-plan/install with an explicit destination. No overwrite, remote installer, MCP connection or engine modification is performed.

Release: 0.4.0-preview. Includes bounded read-only Godot project analysis, readable Markdown reports, conservative snapshot comparison, UI/effect checks and paired evaluation tooling. The original sample passed 60 checks across five viewport sizes with 20 OpenGL captures. Both arms passed the first executable repair pilot; no productivity gain was established. That pilot used the 0.2 skill. External integrations, Unity/Unreal execution, physical input and performance remain unverified. See [capabilities](docs/CAPABILITIES.md), [validation](docs/VALIDATION.md), [tools](docs/EXECUTION-TOOLS.md) and [paired results](docs/PAIRED-EVALUATION.md). Original material is Apache-2.0; indexed external content retains its own license. Primary documentation and workflows are in Chinese.

[Repository](https://github.com/kaltsit2077-dev/gamedev-workbench) · [Preview downloads](https://github.com/kaltsit2077-dev/gamedev-workbench/releases) · [Roadmap](docs/ROADMAP.md). CI checks Python 3.11/3.14 on Windows/Linux/macOS; engine execution remains a separate validation dimension. Rebuild archives with `python tools/package.py --output-dir dist`.
