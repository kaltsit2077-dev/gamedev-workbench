# unity 适配

先确认 Editor 完整版本、Packages/manifest.json、目标平台及 URP/HDRP/Built-in；Graph 包与渲染管线版本分别匹配。

架构：MonoBehaviour 生命周期/场景装配与领域状态分离，ScriptableObject 配置不能无意保存本局可变状态；退出时撤销订阅。UI：按项目选择 UI Toolkit 或 uGUI，维护 EventSystem/焦点、Canvas 缩放与输入模块，不混用不兼容方案。效果：Shader Graph/VFX Graph 的事件、实例参数与容量，停止/重启/销毁需验证。

用 Editor Test Runner 或项目既有测试入口；批处理可使用 Unity 的 -batchmode -projectPath -runTests -testResults 参数，需按当前版本核对官方用法和许可，不能假定本机可执行。官方 CLI/Pipeline MCP 先按 T06 检查，旧 AI Assistant 配置不能直接迁移。来源 E06、E07、T06、T07。本包仅提供指导，未在 Unity 本机运行。
