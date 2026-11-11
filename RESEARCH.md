# 游戏开发技能、MCP 与公开资料：首轮调研

核验日期：2026-11-10。范围：官方文档、维护者仓库、原作者资料与当前会话能力。它是一轮有重点的公开网络初筛，不是对全网的穷尽清单。

本轮没有安装候选工具、连接候选 MCP 或运行第三方脚本。表中“优先试验”表示值得下一步验证；上游声称或上游 CI 不能代替本机验证。版本与条款可能更新，采用前应重新检查精确发布版、许可证与环境。

配套成果：[项目设计草案](DESIGN.md)。

## 1. 结论与建议组合

现成资源足以作为底座。从本轮查阅看，多引擎技能集合在覆盖面上已经很广；专业执行工具更集中于具体引擎和具体工作。建议采用“现成专长 + 原创整合、项目约束与验收”的路线。

优先组合是：多引擎技能库作方法入口；Scenario 的架构/UI/Shader/VFX 家族作重点试验；一个经过比较的编辑器桥作可选操作接口；官方引擎文档作 API 依据；原创工作流串起设计、实现、验证与来源记录。

## 2. 当前会话已经提供的相关能力

以下是当前会话可发现的能力，不表示所有外部软件和账号都已安装或连接。

| 能力 | 适用任务 | 边界 |
|---|---|---|
| game-ui-ux | HUD、菜单、焦点、缩放、状态绑定 | 通用方法，需要引擎适配 |
| godot-ui-control / godot-ui-layout | Godot Control、Container、Theme 与布局检查 | Godot 专用；不等于已验证当前每张界面 |
| ui-ux-pro-max / frontend-design | 视觉方向、层级、配色、排版与界面评审 | Web 偏重部分不能直接当作原生游戏 UI |
| imagegen | 美术方向探索、概念图、位图和纹理候选 | 不是可用的三维模型、骨骼或最终资产管线 |
| brainstorming / writing-plans | 创意澄清、设计与实施组织 | 不提供引擎操作本身 |
| skill-creator / skill-installer | 自建与按项安装技能 | 安装不证明技能质量或兼容 |
| documents / spreadsheets / presentations | 规格、美术规范、数值表与项目展示 | 服务制作过程，不代替引擎内验证 |
| computer-use / 视频与字幕相关能力 | 软件操作、公开演讲学习与内容整理 | 需要具体软件、素材与操作条件 |

已读取官方可安装技能目录。本轮未发现其中有一个覆盖全部游戏开发的专门包；Figma 系、CI/代码审阅、截图等可以补充特定工作。插件目录搜索返回了 Figma 与 Product Design 等候选，没有返回匹配的专用引擎插件；这不是对所有第三方 MCP 的不存在证明。

Figma 在当前插件目录可安装，尚未确认安装或连接。它不影响本轮文档成果；若要直接操作 Figma 文件，需要完成安装/连接。候选引擎 MCP 仍以各自上游安装方式为准。

## 3. 技能发现与现成技能库

| ID / 项目 | 适合的工作与质量证据 | 许可与适配限制 | 建议 |
|---|---|---|---|
| S01 [find-skills](https://github.com/vercel-labs/skills/blob/main/skills/find-skills/SKILL.md) | 真实存在的技能搜索工作流，配合 Skills CLI；本轮已只读查阅 | [CLI 仓库](https://github.com/vercel-labs/skills) MIT；它负责发现，不提供游戏专长，也不保证命中质量 | 纳入发现入口；无需先安装才能做本轮研究 |
| S02 [openai/skills](https://github.com/openai/skills) | 官方目录、安装与技能包组织方式 | 逐技能查看 LICENSE.txt，不假定整库统一授权；不是专门游戏开发库 | 基础设施参考 |
| S03 [awesome-gamedev-agent-skills](https://github.com/gamedev-skills/awesome-gamedev-agent-skills) | 多引擎、学科、类型与路由；有校验脚本、测试和[版本支持表](https://github.com/gamedev-skills/awesome-gamedev-agent-skills/blob/main/docs/VERSION-SUPPORT.md) | Apache-2.0；版本支持表的验证属于上游声明；格式校验不等于游戏行为均已通过 | 优先作为方法底座，按需选项 |
| S04 [Scenario Godot 家族](https://github.com/scenario-labs/skills/blob/main/skills/game-engines/godot/README.md) | 架构、UI、Shader、VFX 与审计/截图等执行工具 | MIT；目标 Godot 4.7.2。完整 live procedures 主要在 macOS；Windows CI 仅部分 toolkit 验证。部分证据路径属于作者机器，不随包分发 | 工程主线强候选，先复现 |
| S05 [haxqer/godot-skill](https://github.com/haxqer/godot-skill/releases) | 场景/Resource 编辑、诊断、输入、截图、性能和导出检查 | 发布说明声明 MIT 与 Godot 4.7；发布页列 v0.5.0，页面日期年份未明确 | 执行工具候选，检查具体包与写入范围 |
| S06 [ItsYUGAMES/godot-dev](https://github.com/ItsYUGAMES/godot-dev) | Claude Code 插件，路由、引擎检查、工具测试与 evals | MIT；Godot 4.7+。上游描述会在会话启动时下载/启用项目插件；不是现成 Codex 包 | 学习验证方法，不直接启用自动 hook |
| S07 [Godot Game Dev Studio](https://github.com/bgrenat/godot-game-dev-studio) | 聚合 Godot 知识、角色、目录与工具，覆盖架构/UI/效果/叙事 | LGPL-3.0，附带资源另查 NOTICE；以 Godot 为中心，未逐技能实测 | 参考编目与角色设计，勿整包改标自有许可 |
| S08 [jwynia/agent-skills](https://github.com/jwynia/agent-skills) | 人物、世界、叙事诊断、互动小说等创作方法 | 本轮根页面未找到明确可再分发许可证，具体条目需进一步核验 | 只列参考候选 |
| S09 [game-design-director](https://github.com/ronkenx9/game-design-director) | Codex 设计技能，MDA、体验、原型范围与问题库 | 根目录未见 LICENSE；页面仅少量历史，未取得维护日期 | 参考任务划分，原创实现流程 |

上述仓库的维护日期未全部取得，未取得者不标为“活跃维护”或“已停止维护”。正式收录时需要为选中的精确技能保存版本、许可文件与变更证据。

### 直接对应当前优先需求的精确技能

| 入口 | 用途 |
|---|---|
| [scenario-godot-architecture](https://github.com/scenario-labs/skills/blob/main/skills/game-engines/godot/scenario-godot-architecture/SKILL.md) | 场景独立、资源与实例状态、依赖、组件、输入和存档；带审计工具 |
| [game-ui-ux](https://github.com/gamedev-skills/awesome-gamedev-agent-skills/blob/main/skills/disciplines/game-ui-ux/SKILL.md) | 跨引擎 HUD、菜单栈、缩放、安全区与导航；当前已有同名能力，先比较再安装 |
| [scenario-godot-ui](https://github.com/scenario-labs/skills/blob/main/skills/game-engines/godot/scenario-godot-ui/SKILL.md) | 原生布局、主题、焦点、本地化和截图复核；有 gd_ui.py 与 GDScript 工具 |
| [shader-programming](https://github.com/gamedev-skills/awesome-gamedev-agent-skills/blob/main/skills/disciplines/shader-programming/SKILL.md) | 坐标、UV、顶点/片元、GLSL/HLSL 和常见效果的通用方法 |
| [scenario-godot-shaders](https://github.com/scenario-labs/skills/blob/main/skills/game-engines/godot/scenario-godot-shaders/SKILL.md) | 编译矩阵、绘制检查、参数扫描和渲染后端截图 |
| [scenario-godot-vfx](https://github.com/scenario-labs/skills/blob/main/skills/game-engines/godot/scenario-godot-vfx/SKILL.md) | 效果构建、AABB、时间采样、渲染器回退与预算 |

## 4. 引擎与建模 MCP / 操作工具

| ID / 项目 | 能力与版本证据 | 许可 / 采用限制 |
|---|---|---|
| T01 [hybridindie/godot-mcp](https://github.com/hybridindie/godot-mcp) | 场景、脚本、运行、截图、性能和测试；[正式发布 2026.11.04](https://github.com/hybridindie/godot-mcp/releases/tag/2026.11.04)宣称最低 4.4、验证于 4.7 | MIT；服务端与 addon 锁同一版。README 稳定版文字已落后于 Releases，记录为漂移实例；优先隔离试验 |
| T02 [Beckett Lite](https://github.com/beckettlab/beckett-godot-mcp) | Godot EditorPlugin 内 MCP、树/截图/日志与节点编辑；[安装说明](https://github.com/beckettlab/beckett-godot-mcp/blob/main/INSTALL.md)声称 4.2+，CI 含 4.7.2 | Lite MIT；部分自动输入、导出与知识包属于商业 Full，不能纳入 Lite 声称；启用会配置客户端 |
| T03 [Coding-Solo/godot-mcp](https://github.com/Coding-Solo/godot-mcp) | CLI 式编辑器启动、运行日志与基础场景操作；UID 功能要求 4.4+，未找到 4.7.2 明确通过证据 | MIT；提交页可见 2026-04-16 安全修复；作为历史基线和候选，不按星数直接选默认 |
| T04 [Blender Lab MCP](https://www.blender.org/lab/mcp-server/) / [代码](https://projects.blender.org/lab/blender_mcp) | 官方实验室项目，场景/Python/渲染/文档；要求 Blender 5.1+ | GPL-3.0-or-later；Python 可实际修改项目，先在素材副本试验。官网部分抓取失败，代码站可读 |
| T05 [mcp-for-blender](https://github.com/ahujasid/mcp-for-blender) | 第三方对象、材质、Python、截图与素材服务桥；README 声称 Blender 3.0+ | MIT；已从旧包名改名；外部服务和遥测行为单独记录。默认仍有最小匿名使用记录，关闭方式见其 README |
| T06 [Unity 官方 CLI / Pipeline MCP](https://docs.unity.com/en-us/unity-cli/replace-mcp-server-unity-cli) | 官方编辑器、构建与测试通道；运行编辑器驱动要求 Unity 6.0 LTS+ | 官方 CLI 标 Experimental；未核验可再分发开源许可。旧 AI Assistant 内置 MCP 已退役，不能套旧教程 |
| T07 [CoplayDev/unity-mcp](https://github.com/CoplayDev/unity-mcp) | 第三方场景、资产、C#、构建、测试与性能；README 声称 2021.3 LTS–6.x | MIT；UPM 与服务端锁版；与官方通道对比后按项目选用 |
| T08 [Unreal 官方 MCP](https://dev.epicgames.com/documentation/en-us/unreal-engine/unreal-mcp-in-unreal-editor?application_version=5.8) | UE 5.8 Experimental；Actor、灯光、材质、Slate 和测试的编辑器 HTTP 接口 | 属 Unreal 许可体系；官方描述本地默认无认证，修改请求在游戏线程串行执行。不能当通用开源库重发 |
| T09 [Penpot 官方 MCP](https://penpot.app/ai/mcp-server) / [项目](https://github.com/penpot/penpot) | 可读取、修改、创建设计元素；支持托管与本地方式，适合 UI 原型、组件和设计 token | 主项目 MPL-2.0；可作为开源设计工具优先候选。设计数据到原生游戏 UI 仍需适配，尚未连接测试 |
| T10 [Machinations 官方 MCP](https://machinations.io/docs/mcp) | 读取/编辑经济图并模拟，用于资源循环与数值设计 | 商业服务接口；Credits/日限额及方案条款另查。Community 新图公开，默认不上传私有设计 |

推荐第一轮用同一个 Godot 小样例比较 T01 与 T02：读取树、校验脚本、节点编辑与撤回、运行截图、错误定位、停止清理。选定一个再接现有项目。Unity 和 Unreal 使用各自固定版本的官方与社区工具说明，不把操作接口当通用知识层。

## 5. UI、美术、效果、素材与调试工具

| ID / 项目 | 能怎样帮助当前工作 | 授权与验证边界 |
|---|---|---|
| A01 [Penpot](https://penpot.app/) | UI 线框、原型、组件、tokens、SVG 与可检查设计数据，且有 T09 MCP | [MPL-2.0](https://github.com/penpot/penpot)；导出的 Web 代码不是 Godot/Unity/UE 原生 UI |
| A02 [Krita](https://krita.org/en/about/license/) | 概念、美术、界面位图与纹理绘制 | 软件 GPLv3，官方明确创作作品归创作者；插件许可与工具许可单独处理 |
| A03 [Blockbench](https://github.com/JannisX11/blockbench) | 独立项目低多边形建模、贴图、动画与通用格式导出 | 软件 GPLv3，插件/主题有例外，作品归创作者；不能将软件许可套到所有素材 |
| A04 [Effekseer](https://effekseer.github.io/en/index.html) / [Godot 集成](https://github.com/effekseer/EffekseerForGodot4/releases) | 可编辑粒子效果、二维动画与三维效果；Godot 正式 1.80.5.1 明确修复 4.7，1.80.7 插件仍标预发布 | [代码 MIT](https://github.com/effekseer/Effekseer/blob/master/LICENSE)，随附效果/纹理声明 CC0，运行库另有依赖许可；仍需引擎实测 |
| A05 [RenderDoc](https://github.com/baldurk/renderdoc) | 帧捕获、绘制事件、纹理/深度/混合定位，适合 Shader 和渲染错误 | [MIT](https://github.com/baldurk/renderdoc/blob/v1.x/LICENSE.md)；兼容取决于 GPU、驱动、图形 API 和具体版本 |
| A06 [Khronos glTF Validator](https://github.com/KhronosGroup/glTF-Validator) | GLB/glTF 规范检查、JSON 问题和资产统计 | Apache-2.0；规范通过后仍要检查目标引擎中的材质、贴图、骨骼和单位 |
| A07 [glTF Transform](https://gltf-transform.dev/cli) | 先 inspect，再有针对性地去重、简化或压缩，输出新文件做对照 | [MIT](https://github.com/donmccurdy/glTF-Transform/blob/main/LICENSE.md)；默认 optimize 未必适合所有资产，压缩扩展另验导入器支持 |
| A08 [Material Maker](https://github.com/RodZill4/material-maker) | 参数化材质、节点图、PBR 导出和风格一致性 | 软件主要 MIT；[社区材质与节点](https://www.materialmaker.org/doc)按单项许可，不能整站套 MIT |
| A09 [Kenney](https://kenney.nl/support) | 风格统一的占位和原型资产，配替换计划 | 游戏资产 CC0；仍保留单包许可，品牌标识另论 |
| A10 [Poly Haven](https://polyhaven.com/license) | HDRI、材质与模型参考，记录用途和分辨率 | 资产 CC0；[API](https://github.com/Poly-Haven/Public-API)与线上服务条款单独处理 |
| A11 [Freesound](https://freesound.org/help/faq/) | 按声音职责检索，做循环/格式/响度检查与致谢 | CC0、CC BY、CC BY-NC 等逐项核验；[API 条款](https://freesound.org/docs/api/terms_of_use.html)不随音频许可自动开放 |

补充观察：[Material Maker MCP](https://github.com/graysonchalmers/Tool-MaterialMaker-MCP)作者声明 very early alpha，单机验证；作为待复现实验，暂不作为默认依赖。

Figma 可通过当前插件目录按需连接，用于设计文件与协作；Penpot 提供开源替代路径。两者都需要原生游戏 UI 实现与运行验收这一环。

## 6. 引擎官方工程与效果资料

| ID / 资料 | 建议转化的工作流 | 授权与版本记录 |
|---|---|---|
| E01 [Godot 4.7 Scene organization](https://docs.godotengine.org/en/4.7/tutorials/best_practices/scene_organization.html) | 场景边界、状态归属、依赖注入、装配与可测试性 | [文档 CC BY 3.0](https://github.com/godotengine/godot-docs/blob/master/LICENSE.txt)；固定版本路径 |
| E02 [Godot 4.7 Performance](https://docs.godotengine.org/en/4.7/tutorials/performance/index.html) | 测量→瓶颈→单项改动→复测，避免泛化优化建议 | 同上；按目标后端与平台做实测 |
| E03 [Godot 4.7 Shaders](https://docs.godotengine.org/en/4.7/tutorials/shaders/index.html) | Shader 类型、空间、颜色、深度、混合与后处理的实现与检查 | 同上；headless 解析不能代替真实渲染 |
| E04 [Godot 官方示例](https://github.com/godotengine/godot-demo-projects) | GUI、渲染、输入、网络等可复现小样例 | MIT；master 对应开发版，应按稳定分支与 commit 选择 |
| E05 [GUT](https://github.com/bitwes/Gut) | GDScript 单测、替身、参数化和 CI | MIT；上游 v9.7.1/godot_4_7 对应 4.7.x。当前项目已有回归，接入不要求换框架 |
| E06 [Unity Shader Graph 17.0](https://docs.unity3d.com/Packages/com.unity.shadergraph@17.0/manual/index.html) | 视觉目标→管线/材质→节点图→参数→运行与预算 | [包源码 Unity Companion License](https://github.com/Unity-Technologies/Graphics/blob/master/Packages/com.unity.shadergraph/LICENSE.md)，不是通用 MIT；按 Unity/URP/HDRP 版本取文档 |
| E07 [Unity VFX Graph 17.0](https://docs.unity3d.com/Packages/com.unity.visualeffectgraph@17.0/manual/index.html) | 效果事件、实例参数、停止重播、容量与多实例最坏情况 | [Unity Companion License](https://github.com/Unity-Technologies/Graphics/blob/master/Packages/com.unity.visualeffectgraph/LICENSE.md)；资料引用与软件分发分开 |
| E08 [Unreal Niagara](https://dev.epicgames.com/documentation/en-us/unreal-engine/creating-visual-effects-in-niagara-for-unreal-engine) / [Debugger](https://dev.epicgames.com/documentation/en-us/unreal-engine/niagara-debugger-for-unreal-engine) | 组织 System/Emitter/Module、接线参数，用真实游玩捕获粒子数与成本 | UE EULA；链接官方资料，不把引擎内容改标自有许可 |

## 7. 创意、机制、叙事、UI、美术、受众与公开案例

| ID / 来源 | 如何转为可执行方法或产物 | 再分发边界 |
|---|---|---|
| K01 [MDA 原论文](https://aaai.org/papers/ws04-04-001-mda-a-formal-approach-to-game-design-and-game-research/) | 期望体验→规则→预期动态→观察信号→原型问题 | 公开可读，未核验再分发授权；仅索引和原创方法说明 |
| K02 [Game Design Concepts](https://gamedesignconcepts.wordpress.com/about/) | 约束创意、纸面原型、机制拆解与迭代练习 | 作者声明 CC BY 3.0 US，使用需署名 |
| K03 [ink](https://www.inklestudios.com/ink/) | 人物目标→分支→变量→回收点→可试玩脚本 | ink/Inky/Unity 插件 MIT；Godot 桥接另核验 |
| K04 [Twine](https://twinery.org/?page=Home) | 独立叙事 HTML 原型、选择后果与回流分析 | 软件与 story format 许可分开记录，创作可商用不等于格式代码可随意复制 |
| K05 [Yarn Spinner 许可](https://www.yarnspinner.dev/license/) / [YSPL](https://yarnspinner.dev/yspl/) | 对话节点、条件/命令、变量与本地化准备 | 不能统称 MIT：多数 core/Unity MIT，Godot GDScript/Unreal 为 YSPL；首版只索引其官方说明 |
| K06 [Game Accessibility Guidelines](https://gameaccessibilityguidelines.com/full-list/) | 输入、字幕、视觉、听觉、认知检查，逐项附证据与改法 | 未核验覆盖全文的统一再分发许可，默认只链接 |
| K07 [Interface In Game](https://interfaceingame.com/about/) | 按页面任务分析导航、状态、动效与信息密度 | 截图版权不因免费参考而开放；不做截图镜像 |
| K08 [Valve Dota 2 Art Guide](https://help.steampowered.com/en/faqs/view/0688-7692-4D5A-1935) | 轮廓、明度、颜色与视觉焦点的原创检查表 | 公司公开资料；不随包收录 Dota 美术原图 |
| K09 [Riot：Gameplay Clarity](https://www.riotgames.com/en/news/valorant-shaders-and-gameplay-clarity) | 玩法信号、环境/角色分离、不同画质和预算 | 官方文章可作为出处，不改标原文与图的许可 |
| K10 [The Level Design Book](https://book.leveldesignbook.com/) / [许可](https://book.leveldesignbook.com/appendix/license) | 灰盒、动线、空间目标、遭遇节奏与试玩 | 文字主要 CC BY-NC-SA 4.0，第三方图另权；核心工作流采用原创表述并链接 |
| K11 [Game Programming Patterns](https://gameprogrammingpatterns.com/) / [许可](https://github.com/munificent/game-programming-patterns/blob/master/LICENSE) | 按变化压力比较状态机、组件、事件、对象池等方案 | 正文/网页样式 CC BY-NC-ND 4.0；代码等其他文件 MIT，不能混为一谈 |
| K12 [Steam Tags](https://partner.steamgames.com/doc/store/tags) | 核心玩法承诺、标签、同类候选与差异假设 | 官方资料链接；标签不直接证明销量或受众规模 |
| K13 [Steam Visibility](https://partner.steamgames.com/doc/marketing/visibility) | 受众假设、商店表达与试玩招募 | 平台机制资料，不是收入预测；记录日期与不确定性 |
| K14 [Ubisoft La Forge](https://www.ubisoft.com/en-us/studio/laforge) | 研究问题→适用性→复现成本→小原型→保留/放弃 | 论文、代码、模型权重分别核验 |
| K15 [Into the Breach Design Postmortem](https://www.gdcvault.com/play/1026333/-Into-the-Breach-Design) | 删减、随机性、难度与迭代决策的案例卡 | 官方免费内容；不镜像视频与幻灯片 |

Machinations 的模型与 MCP 见 T10；资产和音频资料见 A 类，避免在这里重复维护同一事实。

## 8. 现成方案的完整性判断

这是基于本轮查阅作出的判断，不是对所有项目的完整审计。

| 方案 | 主要长处 | 本轮未建立的证据 / 局限 |
|---|---|---|
| awesome-gamedev-agent-skills | 跨引擎、跨学科、游戏类型和任务路由 | 未逐技能运行；不能用格式测试证明全部生成结果正确 |
| Scenario skills | 架构/UI/Shader/VFX 的具体工具和复核流程丰富 | 需审查写入与平台条件；部分上游证据不随包；不是本机运行记录 |
| Godot Game Dev Studio | Godot 专业知识与角色聚合广 | 以 Godot 为核心，授权与第三方归属需要逐项保留 |
| 单个编辑器 MCP | 让代理能够检查与操作真实项目 | 不自动提供架构判断、视觉品味、玩法设计或玩家验证 |
| 拟议 GameDev Workbench | 可统一任务、来源、项目约束、产物与验证 | 尚未实现，必须通过实际案例证明额外价值 |

## 9. 后续收录与试验次序

1. 对比当前已有同名技能与上游精确版本，避免重复路由和相互冲突。
2. 优先试验 architecture、game-ui、shader/vfx 家族，选边界清楚的自制项目。
3. 同样例比较 Godot 编辑器桥；记录读树、写入、撤回、运行、截图和停止结果。
4. UI 设计工具在 Penpot/Figma 中按实际协作需要选用；必须继续走原生 UI 实现。
5. 用真实渲染验证效果，并以 glTF 工具和目标引擎验证资产链。
6. 将试验结果整理成原创工作流、模板与案例，登记可复现版本和失败条件。
7. 扩展其他引擎；对每种引擎分别发布支持范围，缺少本地环境时明确保留未实测状态。

后续还可继续补充音频中间件、寻路与 AI、联网、程序化内容、本地化、存档升级、手柄输入和打包发行等专项。全面性通过持续任务覆盖和验证改进，不用一次性安装数量衡量。

