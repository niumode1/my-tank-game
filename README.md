# 坦克大战 - 真男人版

## 项目简介
基于Python开发的经典坦克大战复刻版，支持8方向移动、可破坏掩体、音效系统等核心功能，代码轻量易扩展，适合学习交流与二次开发。

## 许可证声明
本项目采用 **MIT许可证** 开源，版权归属如下：
Copyright (c) 2025 Xiao shouzheng, Xiong yuebing
完整许可证文本见仓库根目录 `LICENSE` 文件，使用本项目需遵守许可证相关条款。

## 项目结构
tank_war/
├── assets/
│   ├── images/       # 游戏图片资源（坦克、地图、掩体等）
│   └── sounds/       # 音效文件夹（放置 shoot.wav, explosion.wav, hit.wav）
├── src/
│   ├── __init__.py   # 游戏初始化配置
│   ├── main.py       # 主程序（整合所有功能）
│   ├── game_objects.py # 基础对象类（通用属性/方法）
│   ├── tank.py       # 坦克类（优化炮管动画）
│   ├── bullet.py     # 子弹类（碰撞检测、移动逻辑）
│   ├── map.py        # 地图类（可破坏掩体、地形生成）
│   └── sound_manager.py # 音效管理器（加载/播放音效）
├── requirements.txt  # 项目依赖
├── LICENSE           # MIT开源许可证（含完整版权声明）
└── README.md         # 项目说明文档

## 新增功能
1. **可破坏掩体**：子弹击中绿色掩体后掩体消失，碰撞检测精准
2. **音效系统**：
   - 射击音效（shoot.wav）
   - 爆炸音效（explosion.wav）
   - 击中音效（hit.wav）
   - 自动适配音效文件（无文件时不报错，游戏正常运行）
3. **优化炮管动画**：
   - 支持8方向旋转
   - 平滑角度计算
   - 更粗的炮管线条，视觉效果更清晰
4. **8方向移动**：WASD组合键实现斜向移动，操作更灵活

## 音效文件说明
- 路径：`assets/sounds/`
- 需放置文件：
  - shoot.wav：射击音效
  - explosion.wav：爆炸音效
  - hit.wav：击中音效
- 兼容说明：若无音效文件，游戏仍可正常运行（仅无音效输出）

## 运行说明
### 环境要求
- Python 3.7+
- 操作系统：Windows 10/11、macOS、Linux（兼容主流系统）
- 依赖库：见 `requirements.txt`

### 操作步骤
1. 克隆/下载项目到本地
2. 安装依赖：
   ```bash
   pip install -r requirements.txt
运行游戏：
bash
运行
python src/main.py
游戏操作：
WASD：控制坦克 8 方向移动（支持斜向）
空格键：发射子弹
关闭窗口：ESC 键 / 点击窗口关闭按钮
版权信息
Copyright (c) 2025 Xiao shouzheng, Xiong yuebing根据 MIT 许可证，允许自由使用、修改、分发本项目，但需保留原始版权声明与许可证文本。本项目仅用于学习交流，禁止未经授权的商用侵权行为。
