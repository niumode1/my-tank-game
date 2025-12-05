import pygame
import random
import json
import os
from game_objects import GameObject

class Map:
    """地图类，支持从JSON文件加载和可破坏掩体"""
    def __init__(self, map_path=None):  # 支持传入路径或名称
        self.obstacles = []  # 不可破坏的边界
        self.destroyable_obstacles = []  # 可破坏的掩体
        self.name = "默认地图"
        self.description = "系统默认生成的地图"
        
        if map_path:
            # 判断传入的是路径还是名称
            if os.path.isfile(map_path) or map_path.endswith('.json'):
                self.load_from_path(map_path)
            else:
                self.load_from_name(map_path)
        else:
            # 使用默认地图
            self._generate_borders()
            self._generate_destroyable_obstacles()

    def get_maps_directory(self):
        """获取地图目录（支持多种路径）"""
        current_dir = os.path.dirname(os.path.abspath(__file__))
        possible_paths = [
            os.path.join(current_dir, "assets", "maps"),
            os.path.join(os.path.dirname(current_dir), "assets", "maps"),
            os.path.join(current_dir, "maps"),
            "assets/maps",
            "maps"
        ]
        
        for path in possible_paths:
            if os.path.exists(path):
                return path
        
        # 创建默认目录
        default_path = os.path.join(os.path.dirname(current_dir), "assets", "maps")
        os.makedirs(default_path, exist_ok=True)
        return default_path

    def load_from_name(self, map_name):
        """通过名称加载地图"""
        try:
            maps_dir = self.get_maps_directory()
            map_filename = map_name if map_name.endswith('.json') else f"{map_name}.json"
            map_path = os.path.join(maps_dir, map_filename)
            
            self.load_from_path(map_path)
        except Exception as e:
            print(f"通过名称加载地图失败 '{map_name}': {e}")
            self._generate_default_map()

    def load_from_path(self, map_path):
        """通过路径加载地图"""
        try:
            if not os.path.exists(map_path):
                raise FileNotFoundError(f"地图文件不存在: {map_path}")
            
            with open(map_path, 'r', encoding='utf-8') as f:
                map_data = json.load(f)
            
            # 加载地图基本信息
            self.name = map_data.get("name", os.path.splitext(os.path.basename(map_path))[0])
            self.description = map_data.get("description", "无描述")
            
            # 加载不可破坏障碍物
            for obs_data in map_data.get("obstacles", []):
                try:
                    obstacle = GameObject(
                        obs_data.get("x", 0),
                        obs_data.get("y", 0),
                        obs_data.get("width", 50),
                        obs_data.get("height", 50),
                        tuple(obs_data.get("color", [100, 100, 100]))
                    )
                    self.obstacles.append(obstacle)
                except Exception as e:
                    print(f"加载障碍物失败: {e}")
                    continue
            
            # 加载可破坏障碍物
            for obs_data in map_data.get("destroyable_obstacles", []):
                try:
                    obstacle = GameObject(
                        obs_data.get("x", 0),
                        obs_data.get("y", 0),
                        obs_data.get("width", 40),
                        obs_data.get("height", 40),
                        tuple(obs_data.get("color", [0, 200, 0]))
                    )
                    self.destroyable_obstacles.append(obstacle)
                except Exception as e:
                    print(f"加载可破坏障碍物失败: {e}")
                    continue
            
            # 如果没有边界，生成默认边界
            if not self.obstacles:
                self._generate_borders()
                
            print(f"成功加载地图: {self.name}")
                
        except Exception as e:
            print(f"加载地图失败 '{map_path}': {e}")
            self._generate_default_map()

    def _generate_default_map(self):
        """生成默认地图"""
        self.name = "应急默认地图"
        self._generate_borders()
        self._generate_destroyable_obstacles()

    def _generate_borders(self):
        """生成不可破坏的边界墙体"""
        self.obstacles.append(GameObject(-10, 0, 10, 600, (100, 100, 100)))
        self.obstacles.append(GameObject(800, 0, 10, 600, (100, 100, 100)))
        self.obstacles.append(GameObject(0, -10, 800, 10, (100, 100, 100)))
        self.obstacles.append(GameObject(0, 600, 800, 10, (100, 100, 100)))

    def _generate_destroyable_obstacles(self):
        """生成可破坏的掩体"""
        for _ in range(15):
            try:
                while True:
                    x = random.randint(50, 700)
                    y = random.randint(50, 500)
                    width = random.randint(30, 50)
                    height = random.randint(30, 50)
                    new_obstacle = GameObject(x, y, width, height, (0, 200, 0))
                    
                    # 检查是否与现有障碍物重叠
                    overlap = False
                    for obs in self.obstacles + self.destroyable_obstacles:
                        if new_obstacle.rect.colliderect(obs.rect):
                            overlap = True
                            break
                    if not overlap:
                        self.destroyable_obstacles.append(new_obstacle)
                        break
            except Exception:
                continue

    def check_collision(self, rect):
        """检测是否与任何障碍物碰撞"""
        try:
            for obstacle in self.obstacles + self.destroyable_obstacles:
                if rect and obstacle.rect and rect.colliderect(obstacle.rect):
                    return True
        except Exception:
            pass
        return False

    def check_bullet_collision(self, bullet):
        """检测子弹碰撞（破坏掩体）"""
        try:
            # 检查不可破坏障碍物
            for obstacle in self.obstacles:
                if bullet and bullet.rect and obstacle.rect and bullet.rect.colliderect(obstacle.rect):
                    bullet.active = False
                    return True
            
            # 检查可破坏障碍物
            for obstacle in self.destroyable_obstacles[:]:
                if bullet and bullet.rect and obstacle.rect and bullet.rect.colliderect(obstacle.rect):
                    self.destroyable_obstacles.remove(obstacle)
                    bullet.active = False
                    return True
        except Exception as e:
            print(f"碰撞检测错误: {e}")
        
        return False

    def draw(self, screen):
        """绘制所有障碍物"""
        try:
            for obstacle in self.obstacles:
                obstacle.draw(screen)
            for obstacle in self.destroyable_obstacles:
                obstacle.draw(screen)
        except Exception as e:
            print(f"绘制地图失败: {e}")

    # 兼容旧方法名
    load_map = load_from_name