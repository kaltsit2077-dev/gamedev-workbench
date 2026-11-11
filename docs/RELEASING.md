# 发布流程

发行保持 preview 标识，通过公开仓库与 GitHub Releases 提供源码、完整包、独立技能包和校验和；实际版本以远端记录为准。

1. 复核名称、维护者归属、版本与 LICENSE；索引来源不继承本项目许可。
2. 运行目录检查、工具测试、技能验证和便携安装测试。
3. 更新 VALIDATION，分别登记 Python、各引擎、渲染、性能与真人试玩状态。缺少本机证据时保留 preview。
4. 运行 `python tools/release_audit.py` 与 `python tools/package.py --output-dir dist`。选入范围声明于 tools/release_layout.py；禁止将私有分析放进公开源码区域。打包排除本地配置/缓存/日志，拒绝符号链接；检查仅为有限检测，还需人工核对实际文件。
5. 保存 ZIP 的 SHA256。安装说明须给预览、复制、拒绝覆盖和卸载方式。
6. 确认公开授权后提交到独立仓库，观察工具 CI；创建与 VERSION 一致的标签及 prerelease，上传两个 ZIP 和 SHA256SUMS.txt。包的根目录恒为 gamedev-workbench，与克隆目录名称无关。

0.3 内置 Godot 样例已完成五种视口、二十帧捕获及六十项检查；工程分析和首轮配对工具也已运行。发布包可以包含原创缺陷夹具、共同验收、脱敏产物和样例截图，不能带入私有工程分析或原始评估日志。完整项目含配对评估工具；单独技能包不含 evals 与 tools/paired_eval.py。

首个稳定版本仍需不同任务的完整案例、物理输入与独立用户试用；Unity/Unreal 本地测试独立安排。首轮有无技能均通过，没有证明提效；支持矩阵与宣传不得把新增工具验收等同于生产力提升。计划见 USAGE-AND-VALUE.md，首轮限制见 PAIRED-EVALUATION.md。

0.5 增加菜单/分层效果、有限 UID/常量解析、领域工具与跨引擎案例；源案例、模拟单测、实际引擎和实体输入分别验收。打包在相同 Python/zlib 环境与相同字节输入下固定 ZIP 元数据；不同压缩库版本的字节一致性不作保证。
