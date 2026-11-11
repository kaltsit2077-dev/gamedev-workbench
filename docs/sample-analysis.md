# 工程分析阅读稿

这是文本扫描线索，需结合项目约束、源码和行为验证判断；不证明完整依赖或状态所有权。

入口：res://demo.tscn

扫描文件：8；引用线索：9；状态写入线索：29。

## 扫描范围与限制

{&quot;excluded\_directories&quot;: \[&quot;addons&quot;, &quot;build&quot;, &quot;dist&quot;, &quot;node\_modules&quot;, &quot;tests&quot;, &quot;vendor&quot;\], &quot;hidden\_and\_symlinks&quot;: &quot;excluded&quot;, &quot;max\_files&quot;: 3000, &quot;max\_bytes\_per\_file&quot;: 2000000}

- No AST/type/scope resolution; bare member matches may be shadowed by locals.
- Matching property names on different receivers do not prove shared state.
- Dynamic paths, UIDs, runtime groups and signal calls are not a complete dependency graph.
- No private file content or credentials are collected; output can still reveal project structure.

## Autoload

| 名称 | 路径 |
| --- | --- |

## 资源引用

| 来源 | 目标 | 类型 | 路径状态 |
| --- | --- | --- | --- |
| capture.gd | demo.gd | preload | exists |
| demo.gd | state.gd | preload | exists |
| demo.gd | pulse.gd | preload | exists |
| demo.tscn | demo.gd | ext-resource | exists |
| quality.gd | demo.gd | preload | exists |
| quality.gd | validation\_probe.gd | preload | exists |
| smoke.gd | state.gd | preload | exists |
| smoke.gd | pulse.gd | preload | exists |
| smoke.gd | demo.gd | preload | exists |

## 状态写入线索

| 文件 | 方法 | 目标 | 操作 | 绑定限制 |
| --- | --- | --- | --- | --- |
| capture.gd | capture | root.size | = | receiver unresolved |
| demo.gd | \_ready | panel.size\_flags\_horizontal | = | receiver unresolved |
| demo.gd | \_ready | panel.size\_flags\_stretch\_ratio | = | receiver unresolved |
| demo.gd | \_ready | title.text | = | receiver unresolved |
| demo.gd | \_ready | title.autowrap\_mode | = | receiver unresolved |
| demo.gd | \_ready | trigger\_button.text | = | receiver unresolved |
| demo.gd | \_ready | trigger\_button.custom\_minimum\_size | = | receiver unresolved |
| demo.gd | \_ready | reset\_button.text | = | receiver unresolved |
| demo.gd | \_ready | reset\_button.custom\_minimum\_size | = | receiver unresolved |
| demo.gd | \_ready | effect\_area.size\_flags\_horizontal | = | receiver unresolved |
| demo.gd | \_ready | effect\_area.custom\_minimum\_size | = | receiver unresolved |
| demo.gd | \_ready | effect\_area.mouse\_filter | = | receiver unresolved |
| demo.gd | \_ready | trigger\_button.focus\_next | = | receiver unresolved |
| demo.gd | \_ready | trigger\_button.focus\_previous | = | receiver unresolved |
| demo.gd | \_ready | reset\_button.focus\_next | = | receiver unresolved |
| demo.gd | \_ready | reset\_button.focus\_previous | = | receiver unresolved |
| demo.gd | \_layout\_effect | pulse.position | = | receiver unresolved |
| demo.gd | \_layout\_effect | pulse.scale | = | receiver unresolved |
| demo.gd | \_update\_status | status.text | = | receiver unresolved |
| pulse.gd | trigger | elapsed | = | member name match; local shadowing unresolved |
| pulse.gd | trigger | active | = | member name match; local shadowing unresolved |
| pulse.gd | advance | elapsed | = | member name match; local shadowing unresolved |
| pulse.gd | advance | active | = | member name match; local shadowing unresolved |
| quality.gd | run\_checks | root.size | = | receiver unresolved |
| quality.gd | run\_checks | root.size | = | receiver unresolved |
| state.gd | trigger | charge | = | member name match; local shadowing unresolved |
| state.gd | reset | charge | = | member name match; local shadowing unresolved |
| validation\_probe.gd | send\_action | event.action | = | receiver unresolved |
| validation\_probe.gd | send\_action | event.pressed | = | receiver unresolved |

## 循环线索


动态引用未被解析的数量：0。
未发现某条引用，不等于该依赖不存在。循环列表是扫描器发现的线索，不是全部循环的枚举。
