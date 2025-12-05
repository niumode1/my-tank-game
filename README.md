# 坦克大战 - 终极版

## 项目结构
tank_war/├── assets/│ ├── images/│ └── sounds/ # 音效文件夹（放置 shoot.wav, explosion.wav, hit.wav）├── src/│ ├── init.py│ ├── main.py # 主程序（整合所有功能）│ ├── game_objects.py # 基础对象类│ ├── tank.py # 坦克类（优化炮管动画）│ ├── bullet.py # 子弹类│ ├── map.py # 地图类（可破坏掩体）│ └── sound_manager.py # 音效管理器├── requirements.txt└── README.md
plaintext

## 新增功能
1. **可破坏掩体**：子弹击中绿色掩体后掩体消失
2. **音效系统**：
   - 射击音效（shoot.wav）
   - 爆炸音效（explosion.wav）
   - 击中音效（hit.wav）
   - 自动适配音效文件（无文件时不报错）
3. **优化炮管动画**：
   - 支持8方向旋转
   - 平滑角度计算
   - 更粗的炮管线条
4. **8方向移动**：WASD组合键实现斜向移动

## 音效文件说明
- 在`assets/sounds/`目录下放置以下音效文件：
  - shoot.wav：射击音效
  - explosion.wav：爆炸音效
  - hit.wav：击中音效
- 若无音效文件，游戏仍可正常运行（无音效）

## 运行说明
1. 安装依赖：`pip install -r requirements.txt`
2. 运行游戏：`python src/main.py`
3. 操作：WASD移动（支持斜向），空格键射击