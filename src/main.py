import pygame
import math
import os
import traceback
import random
import sys
from tank import Tank
from map import Map
from sound_manager import SoundManager

# ========== 核心修复：添加动态路径获取函数 ==========
def get_resource_path(relative_path):
    """
    获取资源文件的绝对路径（兼容开发模式和PyInstaller打包模式）
    :param relative_path: 相对于项目根目录的路径，如 "assets/maps"
    :return: 绝对路径
    """
    try:
        # 打包后：sys._MEIPASS 是PyInstaller解压后的临时目录
        base_path = sys._MEIPASS
    except Exception:
        # 开发模式：获取src目录的上级目录（项目根目录）
        base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    # 拼接最终路径（自动处理跨平台分隔符）
    return os.path.join(base_path, relative_path)


# 初始化pygame
pygame.init()
pygame.font.init()

# 游戏配置
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60
WHITE = (240, 240, 240)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
SELECTED_COLOR = (0, 0, 255)  # 选中项颜色

# 无尽模式配置
GAME_MODES = ["CLASSIC", "ENDLESS"]  # 游戏模式
current_mode = "CLASSIC"  # 当前模式
current_wave = 1  # 当前波次
player_level = 1  # 玩家等级
player_exp = 0  # 玩家经验
boss_tank = None  # BOSS坦克变量

# 创建游戏窗口
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("坦克大战 - 真男人版")

# 字体设置（修复跨平台兼容）
try:
    small_font = pygame.font.SysFont(["SimHei", "WenQuanYi Micro Hei", "Heiti SC", "Arial"], 24)
    medium_font = pygame.font.SysFont(["SimHei", "WenQuanYi Micro Hei", "Heiti SC", "Arial"], 36)
    large_font = pygame.font.SysFont(["SimHei", "WenQuanYi Micro Hei", "Heiti SC", "Arial"], 72)
    title_font = pygame.font.SysFont(["SimHei", "WenQuanYi Micro Hei", "Heiti SC", "Arial"], 50)
except Exception as e:
    print(f"加载字体失败: {e}")
    small_font = pygame.font.Font(None, 24)
    medium_font = pygame.font.Font(None, 36)
    large_font = pygame.font.Font(None, 72)
    title_font = pygame.font.Font(None, 50)

# 时钟和音效管理器
clock = pygame.time.Clock()
try:
    sound_manager = SoundManager()
except Exception as e:
    print(f"音效管理器初始化失败: {e}")
    class DummySoundManager:
        def __getattr__(self, name):
            return lambda *args, **kwargs: None
    sound_manager = DummySoundManager()

# 游戏状态
GAME_STATE = "MENU"  # MENU, MAP_SELECT, PLAYING, GAME_OVER
winner_text = ""
selected_map_index = 0
available_maps = []
scroll_offset = 0  # 地图列表滚动偏移量

# 加载可用地图（修复打包后路径问题）
def load_available_maps():
    """加载所有可用的地图文件并打印调试信息"""
    try:
        # ========== 修复：使用动态路径 ==========
        maps_dir = get_resource_path("assets/maps")  # 替换原有的硬编码路径
        
        print(f"[调试] 当前脚本目录: {os.path.dirname(os.path.abspath(__file__))}")
        print(f"[调试] 地图目录: {maps_dir} {'(存在)' if os.path.exists(maps_dir) else '(不存在)'}")
        
        # 如果目录不存在则创建
        if not os.path.exists(maps_dir):
            os.makedirs(maps_dir, exist_ok=True)
            print(f"[调试] 创建地图目录: {maps_dir}")
            return []
        
        # 读取JSON地图文件
        map_files = []
        for file in os.listdir(maps_dir):
            if file.endswith(".json"):
                map_path = get_resource_path(f"assets/maps/{file}")  # 修复：用动态路径
                map_files.append(map_path)
                print(f"[调试] 找到地图文件: {map_path}")
        
        print(f"[调试] 共找到 {len(map_files)} 个地图文件")
        return map_files
    except Exception as e:
        print(f"加载地图列表失败: {e}")
        traceback.print_exc()
        return []

# 强制重新加载地图并打印结果
available_maps = load_available_maps()
print(f"最终可用地图列表: {[os.path.basename(p) for p in available_maps]}")

# 初始化游戏对象
try:
    game_map = Map()
except Exception as e:
    print(f"地图初始化失败: {e}")
    class DummyMap:
        name = "默认地图"
        destroyable_obstacles = []
        obstacles = []
        def __getattr__(self, name):
            if name == 'draw':
                return lambda screen: None
            elif name == 'check_bullet_collision':
                return lambda bullet: False
            return lambda *args, **kwargs: False
    game_map = DummyMap()

# 坦克初始化
try:
    player_tank = Tank(100, 100, (0, 0, 255), is_player=True)
    enemy_tank1 = Tank(600, 100, (255, 0, 0))
    enemy_tank2 = Tank(100, 400, (0, 255, 0))
    enemy_tank3 = Tank(600, 400, (255, 255, 0))
    tanks = [player_tank, enemy_tank1, enemy_tank2, enemy_tank3]
except Exception as e:
    print(f"坦克初始化失败: {e}")
    tanks = []

def reset_game(selected_map=None, mode="CLASSIC"):
    """重置游戏状态"""
    global game_map, player_tank, enemy_tank1, enemy_tank2, enemy_tank3, tanks, GAME_STATE, winner_text
    global current_mode, current_wave, player_level, player_exp, boss_tank
    
    current_mode = mode
    current_wave = 1 if mode == "ENDLESS" else current_wave
    # 重置玩家等级和经验（如果是新游戏）
    if mode == "ENDLESS":
        player_level = 1
        player_exp = 0
    
    try:
        if selected_map is not None and available_maps and 0 <= selected_map < len(available_maps):
            try:
                game_map = Map(available_maps[selected_map])
                print(f"加载选中地图: {os.path.basename(available_maps[selected_map])}")
            except Exception as e:
                print(f"加载选中地图失败: {e}")
                game_map = Map()
        else:
            game_map = Map()
            print("使用默认地图")
        
        # 初始化坦克（无尽模式初始敌人更少）
        player_tank = Tank(100, 100, (0, 0, 255), is_player=True)
        if mode == "ENDLESS":
            tanks = [player_tank] + [Tank(random.randint(100, 700), random.randint(100, 500), (255, 0, 0))]
            spawn_wave()  # 生成第一波敌人
        else:
            enemy_tank1 = Tank(600, 100, (255, 0, 0))
            enemy_tank2 = Tank(100, 400, (0, 255, 0))
            enemy_tank3 = Tank(600, 400, (255, 255, 0))
            tanks = [player_tank, enemy_tank1, enemy_tank2, enemy_tank3]
        
        boss_tank = None
        
        # 检查并移除与坦克重叠的掩体
        if hasattr(game_map, 'obstacles') and hasattr(game_map, 'destroyable_obstacles'):
            # 定义碰撞检测函数
            def is_overlapping_tank(obstacle):
                for tank in tanks:
                    if hasattr(tank, 'rect') and hasattr(obstacle, 'rect'):
                        if obstacle.rect.colliderect(tank.rect):
                            return True
                return False
            
            # 过滤与坦克重叠的掩体
            original_obstacles = len(game_map.obstacles)
            game_map.obstacles = [obs for obs in game_map.obstacles if not is_overlapping_tank(obs)]
            removed_obstacles = original_obstacles - len(game_map.obstacles)
            
            original_destroyable = len(game_map.destroyable_obstacles)
            game_map.destroyable_obstacles = [obs for obs in game_map.destroyable_obstacles if not is_overlapping_tank(obs)]
            removed_destroyable = original_destroyable - len(game_map.destroyable_obstacles)
            
            if removed_obstacles > 0 or removed_destroyable > 0:
                print(f"移除与坦克重叠的掩体: 不可破坏{removed_obstacles}个, 可破坏{removed_destroyable}个")
        
        winner_text = ""
        GAME_STATE = "PLAYING"
    except Exception as e:
        print(f"重置游戏失败: {e}")
        traceback.print_exc()
        GAME_STATE = "MENU"

def spawn_wave():
    """生成敌人波次"""
    global tanks, current_wave, boss_tank
    
    # 计算当前波次要生成的敌人数量（1-10个）
    enemy_count = min(1 + current_wave // 2, 10)
    is_boss_wave = current_wave % 5 == 0
    
    # 清除现有敌人（保留玩家）
    tanks = [tank for tank in tanks if tank.is_player]
    
    if is_boss_wave:
        # 生成BOSS坦克和2个小弟
        boss_tank = Tank(400, 100, (128, 0, 128), is_boss=True)  # 紫色BOSS坦克
        boss_tank.max_health = 10 + (current_wave // 5) * 2
        boss_tank.health = boss_tank.max_health
        boss_tank.speed = 3  # BOSS速度稍快
        tanks.append(boss_tank)
        
        # 添加2个小弟
        for _ in range(2):
            x = random.randint(100, 700)
            y = random.randint(100, 500)
            minion = Tank(x, y, (255, 165, 0))  # 橙色小弟
            minion.speed = 2.5
            minion.max_health = 5
            minion.health = minion.max_health
            tanks.append(minion)
    else:
        # 生成普通敌人
        for i in range(enemy_count):
            x = random.randint(100, 700)
            y = random.randint(100, 500)
            enemy = Tank(x, y, (255, 0, 0))
            # 敌人随波次增强
            enemy.max_health = 3 + (current_wave // 3)
            enemy.health = enemy.max_health
            enemy.speed = 2 + (current_wave // 5) * 0.5
            enemy.ai_difficulty = 1 + (current_wave // 5)  # AI难度提升
            tanks.append(enemy)
    
    print(f"第 {current_wave} 波敌人生成，共 {len(tanks)-1} 个敌人")

def level_up_player():
    """玩家升级"""
    global player_level, player_tank
    player_level += 1
    player_tank.max_health += 1
    player_tank.health = player_tank.max_health  # 升级满血
    player_tank.speed += 0.3  # 提升移速
    print(f"玩家升级到 {player_level} 级！速度: {player_tank.speed:.1f}, 最大生命值: {player_tank.max_health}")
    sound_manager.play_levelup_sound()

# 游戏主循环
running = True
try:
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                try:
                    if GAME_STATE == "MENU":
                        if event.key == pygame.K_1:
                            GAME_STATE = "MAP_SELECT"
                            current_mode = "CLASSIC"
                            print("选择经典模式")
                        elif event.key == pygame.K_2:
                            reset_game(mode="ENDLESS")
                            print("选择无尽模式")
                    elif GAME_STATE == "MAP_SELECT":
                        if available_maps:
                            if event.key == pygame.K_UP:
                                selected_map_index = (selected_map_index - 1) % len(available_maps)
                                print(f"选中地图索引: {selected_map_index}")
                            elif event.key == pygame.K_DOWN:
                                selected_map_index = (selected_map_index + 1) % len(available_maps)
                                print(f"选中地图索引: {selected_map_index}")
                            elif event.key == pygame.K_SPACE:
                                reset_game(selected_map_index, current_mode)
                        if event.key == pygame.K_ESCAPE:
                            GAME_STATE = "MENU"
                            print("返回主菜单")
                    elif GAME_STATE == "GAME_OVER":
                        if event.key == pygame.K_r:
                            if current_mode == "ENDLESS":
                                reset_game(mode="ENDLESS")
                            else:
                                reset_game(selected_map_index if (available_maps and selected_map_index < len(available_maps)) else None)
                        elif event.key == pygame.K_ESCAPE:
                            GAME_STATE = "MENU"
                        # 开发者复活功能
                        elif event.key == pygame.K_KP_MULTIPLY or event.key == pygame.K_asterisk:
                            if current_mode == "ENDLESS":
                                player_tank.health = player_tank.max_health
                                player_tank.alive = True
                                GAME_STATE = "PLAYING"
                                print("开发者复活")
                except Exception as e:
                    print(f"事件处理错误: {e}")
                    traceback.print_exc()

        if GAME_STATE == "MENU":
            try:
                screen.fill(WHITE)
                title = title_font.render("坦克大战-真男人版", True, BLACK)
                screen.blit(title, (SCREEN_WIDTH//2 - title.get_width()//2, 150))
                
                features = [
                    "Ctrl+空格键切换至英文",
                    "可破坏掩体",
                    "8方向移动与瞄准",
                    "生命值显示",
                    "无尽模式与BOSS战",
                    "玩家升级系统"
                ]
                for i, feature in enumerate(features):
                    feature_text = small_font.render(f"• {feature}", True, BLACK)
                    screen.blit(feature_text, (250, 250 + i * 40))
                
                mode_text = medium_font.render("按1选择经典模式，按2选择无尽模式", True, BLACK)
                screen.blit(mode_text, (SCREEN_WIDTH//2 - mode_text.get_width()//2, 500))
            except Exception as e:
                print(f"菜单渲染错误: {e}")

        elif GAME_STATE == "MAP_SELECT":
            try:
                screen.fill(WHITE)
                title = title_font.render("选择地图", True, BLACK)
                screen.blit(title, (SCREEN_WIDTH//2 - title.get_width()//2, 50))
                
                if not available_maps:
                    no_map_text = medium_font.render("未找到地图文件，按ESC返回", True, RED)
                    screen.blit(no_map_text, (SCREEN_WIDTH//2 - no_map_text.get_width()//2, 250))
                    
                    hint_text = small_font.render("请在assets/maps 目录下放置JSON地图文件", True, BLACK)
                    screen.blit(hint_text, (SCREEN_WIDTH//2 - hint_text.get_width()//2, 320))
                else:
                    # 计算滚动偏移量，确保选中的地图在可视区域内
                    visible_count = 8  # 一次显示8个地图
                    scroll_offset = max(0, min(selected_map_index - visible_count // 2, 
                                              len(available_maps) - visible_count))
                    
                    # 绘制地图列表
                    for i in range(scroll_offset, min(scroll_offset + visible_count, len(available_maps))):
                        map_path = available_maps[i]
                        map_name = os.path.basename(map_path).replace(".json", "")
                        color = SELECTED_COLOR if i == selected_map_index else BLACK
                        map_text = medium_font.render(map_name, True, color)
                        y_pos = 120 + (i - scroll_offset) * 50
                        screen.blit(map_text, (SCREEN_WIDTH//2 - map_text.get_width()//2, y_pos))
                    
                    # 绘制滚动提示（当地图数量超过可视数量时）
                    if len(available_maps) > visible_count:
                        scroll_hint = small_font.render("↑↓ 键滚动查看更多地图", True, BLACK)
                        screen.blit(scroll_hint, (20, SCREEN_HEIGHT - 30))
                    
                    hint_text = small_font.render("空格键确认选择 | ESC返回菜单", True, BLACK)
                    screen.blit(hint_text, (SCREEN_WIDTH//2 - hint_text.get_width()//2, 550))
            except Exception as e:
                print(f"地图选择界面渲染错误: {e}")
                traceback.print_exc()
                GAME_STATE = "MENU"

        elif GAME_STATE == "PLAYING":
            try:
                # 更新玩家坦克
                if tanks and len(tanks) > 0:
                    keys = pygame.key.get_pressed()
                    tanks[0].update(keys, game_map, None, sound_manager)

                # 更新AI坦克
                if tanks and len(tanks) > 1:
                    for tank in tanks[1:]:
                        if hasattr(tank, 'health') and tank.health > 0:
                            tank.update(None, game_map, tanks[0] if tanks else None, sound_manager)

                # 改进的子弹碰撞检测系统
                if tanks:
                    for tank in tanks:
                        if hasattr(tank, 'bullets') and hasattr(tank, 'health') and tank.health > 0:
                            # 遍历子弹副本进行安全操作
                            for bullet in tank.bullets[:]:
                                if bullet.active:
                                    # 更新子弹位置
                                    bullet.update()
                                    
                                    # 首先检测子弹与地图障碍物的碰撞（包括灰色和绿色掩体）
                                    if game_map.check_bullet_collision(bullet):
                                        bullet.active = False
                                        # 如果是可破坏掩体被击中，需要处理掩体销毁
                                        if hasattr(game_map, 'destroyable_obstacles'):
                                            for obstacle in game_map.destroyable_obstacles[:]:
                                                if hasattr(obstacle, 'rect') and bullet.rect.colliderect(obstacle.rect):
                                                    game_map.destroyable_obstacles.remove(obstacle)
                                                    break
                                        continue
                                    
                                    # 然后检测子弹与其他坦克的碰撞
                                    hit_target = False
                                    for target in tanks:
                                        if target != tank and hasattr(target, 'health') and target.health > 0:
                                            if hasattr(target, 'rect') and bullet.rect.colliderect(target.rect):
                                                target.health -= 1
                                                bullet.active = False
                                                sound_manager.play_hit_sound()
                                                if target.health <= 0:
                                                    sound_manager.play_explosion_sound()
                                                    # 敌人死亡时掉落血包
                                                    if hasattr(target, 'drop_health'):
                                                        target.drop_health()
                                                hit_target = True
                                                break
                                    
                                    # 移除失效子弹
                                    if not bullet.active and bullet in tank.bullets:
                                        tank.bullets.remove(bullet)

                # 检查游戏结束条件
                alive_enemies = []
                if tanks and len(tanks) > 1:
                    alive_enemies = [tank for tank in tanks[1:] if hasattr(tank, 'health') and tank.health > 0]
                
                if tanks and len(tanks) > 0 and hasattr(tanks[0], 'health') and tanks[0].health <= 0:
                    if current_mode == "ENDLESS":
                        winner_text = f"无尽模式结束！波次: {current_wave} | 等级: {player_level}"
                    else:
                        winner_text = "AI胜利!"
                    GAME_STATE = "GAME_OVER"
                    sound_manager.play_game_over_sound()
                elif len(alive_enemies) == 0 and tanks and len(tanks) > 1:
                    if current_mode == "ENDLESS":
                        # 无尽模式下波次完成
                        current_wave += 1
                        spawn_wave()
                        # 玩家获得波次奖励
                        player_exp += 100 * current_wave
                        # 检查是否升级
                        if player_exp >= player_level * 200:
                            player_exp -= player_level * 200
                            level_up_player()
                    else:
                        winner_text = "玩家胜利!"
                        GAME_STATE = "GAME_OVER"
                        sound_manager.play_victory_sound()

                # 绘制游戏画面
                screen.fill(WHITE)
                game_map.draw(screen)
                
                if tanks:
                    for tank in tanks:
                        if hasattr(tank, 'health') and tank.health > 0:
                            tank.draw(screen)
                
                # 绘制血包
                health_packs = []
                for tank in tanks:
                    if hasattr(tank, 'health') and tank.health <= 0 and hasattr(tank, 'health_pack') and tank.health_pack:
                        health_packs.append(tank.health_pack)
                        pygame.draw.rect(screen, (255, 0, 255), tank.health_pack.rect)
                
                # 检测玩家拾取血包
                if tanks and len(tanks) > 0 and hasattr(tanks[0], 'rect'):
                    player_rect = tanks[0].rect
                    for tank in tanks:
                        if hasattr(tank, 'health_pack') and tank.health_pack:
                            if player_rect.colliderect(tank.health_pack.rect):
                                # 玩家拾取血包
                                tanks[0].health = min(tanks[0].health + 1, tanks[0].max_health)
                                tank.health_pack = None
                                sound_manager.play_powerup_sound()

                # 信息显示
                if current_mode == "ENDLESS":
                    wave_text = small_font.render(f"波次: {current_wave}", True, BLACK)
                    level_text = small_font.render(f"等级: {player_level}", True, BLACK)
                    exp_text = small_font.render(f"经验: {player_exp}/{player_level * 200}", True, BLACK)
                    screen.blit(wave_text, (10, 10))
                    screen.blit(level_text, (10, 40))
                    screen.blit(exp_text, (10, 70))
                    
                    if boss_tank and hasattr(boss_tank, 'health') and boss_tank.health > 0:
                        boss_health_text = small_font.render(f"BOSS生命值: {boss_tank.health}/{boss_tank.max_health}", True, (128, 0, 128))
                        screen.blit(boss_health_text, (SCREEN_WIDTH - 200, 10))
                else:
                    map_name_text = small_font.render(f"地图: {getattr(game_map, 'name', '未知')}", True, BLACK)
                    screen.blit(map_name_text, (10, 10))
                
                enemy_count_text = small_font.render(f"敌方剩余: {len(alive_enemies)}", True, BLACK)
                screen.blit(enemy_count_text, (10, 100 if current_mode == "ENDLESS" else 40))
                
                if tanks and len(tanks) > 0 and hasattr(tanks[0], 'health'):
                    player_health_text = small_font.render(f"玩家生命值: {tanks[0].health}/{getattr(tanks[0], 'max_health', 3)}", True, BLACK)
                    screen.blit(player_health_text, (10, 130 if current_mode == "ENDLESS" else 70))
                
                destroyable_count = small_font.render(f"掩体剩余: {len(getattr(game_map, 'destroyable_obstacles', []))}", True, BLACK)
                screen.blit(destroyable_count, (10, 160 if current_mode == "ENDLESS" else 100))
                
                # 显示开发者复活提示（仅在无尽模式）
                if current_mode == "ENDLESS":
                    dev_text = small_font.render("按*键复活（开发者功能）", True, (128, 128, 128))
                    screen.blit(dev_text, (SCREEN_WIDTH - 220, SCREEN_HEIGHT - 30))
            except Exception as e:
                print(f"游戏逻辑错误: {e}")
                traceback.print_exc()
                GAME_STATE = "GAME_OVER"
                winner_text = "游戏出错!"

        elif GAME_STATE == "GAME_OVER":
            try:
                screen.fill(WHITE)
                result_text = large_font.render(winner_text, True, RED if "AI" in winner_text or "出错" in winner_text else GREEN)
                screen.blit(result_text, (SCREEN_WIDTH//2 - result_text.get_width()//2, 200))
                
                if current_mode == "ENDLESS":
                    stats_text = medium_font.render(f"最终波次: {current_wave} | 最终等级: {player_level}", True, BLACK)
                    screen.blit(stats_text, (SCREEN_WIDTH//2 - stats_text.get_width()//2, 280))
                else:
                    map_text = medium_font.render(f"地图: {getattr(game_map, 'name', '未知')}", True, BLACK)
                    screen.blit(map_text, (SCREEN_WIDTH//2 - map_text.get_width()//2, 280))
                
                stats_text2 = small_font.render(f"剩余掩体: {len(getattr(game_map, 'destroyable_obstacles', []))}", True, BLACK)
                screen.blit(stats_text2, (SCREEN_WIDTH//2 - stats_text2.get_width()//2, 330))
                
                if current_mode == "ENDLESS":
                    restart_text = small_font.render("按R键重新开始 | 按ESC键返回菜单 | 按*键复活", True, BLACK)
                else:
                    restart_text = small_font.render("按R键重新开始 | 按ESC键返回菜单", True, BLACK)
                screen.blit(restart_text, (SCREEN_WIDTH//2 - restart_text.get_width()//2, 380))
            except Exception as e:
                print(f"游戏结束界面错误: {e}")

        pygame.display.flip()
        clock.tick(FPS)
        
except Exception as e:
    print(f"主循环错误: {e}")
    traceback.print_exc()
finally:
    pygame.quit()
    print("游戏已退出")