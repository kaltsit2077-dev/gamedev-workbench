# unreal 适配

确认 UE 完整版本、.uproject、插件、目标平台与渲染设置；Blueprint-only 和 C++ 项目分别识别。

架构：GameMode、GameState、PlayerController、Pawn、Subsystem 的生命周期和网络权限需按实际游戏区分，UI 不直接持有跨关卡失效 Actor。UI：UMG/Slate 的锚点、DPI、Focus、InputMode 与模态返回；设计预览不证明运行导航。效果：Niagara System/Emitter/Module、User Parameters、组件池和事件接线，停播/销毁不同语义分别测试。

按项目 Automation Tests/Functional Tests 与 Unreal Insights 验证；Niagara Debugger 查活动实例、粒子和时间成本。UE5.8 官方 MCP 是 Experimental；缺版本与环境时只给适配方案。来源 T08、E08。本包未在 Unreal 本机运行。
