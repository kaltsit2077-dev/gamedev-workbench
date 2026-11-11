# web 适配

确认 Phaser/PixiJS/three.js 等实际库与版本，按目标运行环境选 Canvas/WebGL/WebGPU。引擎中立工作流可用；不要把 Web 实现反向当成原生引擎 UI。

架构：update/draw、场景状态、资源加载与 DOM 生命周期分开；resize、visibility、失焦和销毁均有所有者。UI：画布坐标、CSS 尺寸和设备像素比必须区分，键盘/手柄焦点和无障碍标签要有可用路径。效果：shader 版本、alpha 与颜色空间、context loss 和资源释放。

固定依赖后用浏览器实际测试交互、缩放和渲染；自动测试截图不能替代所有设备和真人试玩。本包只提供任务映射，未运行指定 Web 游戏引擎。来源 S03。
