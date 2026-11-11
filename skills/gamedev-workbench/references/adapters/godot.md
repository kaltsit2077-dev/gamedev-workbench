# godot 适配

读取 project.godot 的入口/自动加载和项目自己的引擎约定；config/features 的 minor 不能证明 patch 正确。用实际可执行文件 --version 核对。

架构：节点场景负责组合，Resource 定义与实例状态分开，信号连接和唯一状态写者明确；复用现有装配根。UI：Control/Container/Theme，focus_neighbor 和输入消费需实际走通。效果：canvas_item/spatial/particles 与目标 renderer 匹配，屏幕读取、深度与 source_color 分别检查。

解析/行为示例：`<godot> --headless --path <isolated-project> --script res://smoke.gd`。真实渲染另跑，禁止把 dummy renderer 通过写成画面通过。当前游戏应使用其 AGENTS 指定版本与回归，不改成此包示例测试。CLI doctor 只检查用户明确传入的引擎，不扫描磁盘或改缓存。来源 E01–E05、T01–T03。
