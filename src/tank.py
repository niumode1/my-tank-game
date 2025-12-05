import math
import pygame
import random
from game_objects import GameObject
from bullet import Bullet

class Tank(GameObject):
    """坦克类，优化炮管动画和AI智能"""
    def __init__(self, x, y, color, is_player=False, is_boss=False):
        super().__init__(x, y, 30, 30, color)
        self.speed = 2
        self.direction = (0, -1)  # 方向向量
        self.angle = 90  # 炮管角度（向上为90度）
        self.is_player = is_player
        self.is_boss = is_boss  # 添加BOSS标识
        self.max_health = 3
        self.health = self.max_health
        self.bullets = []
        self.shoot_cooldown = 0
        self.alive = True
        
        # AI属性
        self.ai_move_timer = 0
        self.ai_shoot_timer = 0
        self.ai_target = None
        self.ai_difficulty = 1  # AI难度等级（影响反应速度）
        
        # 血包掉落相关
        self.drop_health_prob = 0.5  # 50%概率掉落血包
        self.health_pack = None  # 掉落的血包

    def update_angle(self):
        """根据方向更新炮管角度"""
        dx, dy = self.direction
        if dx == 1 and dy == 0:
            self.angle = 0
        elif dx == 1 and dy == -1:
            self.angle = 45
        elif dx == 0 and dy == -1:
            self.angle = 90
        elif dx == -1 and dy == -1:
            self.angle = 135
        elif dx == -1 and dy == 0:
            self.angle = 180
        elif dx == -1 and dy == 1:
            self.angle = 225
        elif dx == 0 and dy == 1:
            self.angle = 270
        elif dx == 1 and dy == 1:
            self.angle = 315

    def move(self, dx, dy, game_map=None):
        if not self.alive:
            return
        # 更新方向向量（支持8方向）
        if dx != 0 or dy != 0:
            self.direction = (dx, dy)
            self.update_angle()
        
        new_x = self.rect.x + dx * self.speed
        new_y = self.rect.y + dy * self.speed
        temp_rect = pygame.Rect(new_x, new_y, self.rect.width, self.rect.height)
        
        if (0 <= new_x <= 770 and 0 <= new_y <= 570 and 
            (game_map is None or not game_map.check_collision(temp_rect))):
            self.rect.x = new_x
            self.rect.y = new_y

    def shoot(self, sound_manager=None):
        """发射子弹（播放音效）"""
        if not self.alive or self.shoot_cooldown > 0:
            return
        
        # 播放射击音效
        if sound_manager:
            sound_manager.play_shoot_sound()
        
        # 计算炮口位置（根据角度偏移）
        gun_offset = 20
        rad_angle = math.radians(self.angle)
        bullet_x = self.rect.centerx + math.cos(rad_angle) * gun_offset - 2
        bullet_y = self.rect.centery - math.sin(rad_angle) * gun_offset - 2
        
        self.bullets.append(Bullet(bullet_x, bullet_y, self.direction))
        self.shoot_cooldown = 10 if self.is_boss else 15  # BOSS射击冷却更短

    def take_damage(self, damage=1, sound_manager=None):
        """受到伤害（播放爆炸音效）"""
        if self.alive:
            self.health -= damage
            if self.health <= 0:
                self.health = 0
                self.alive = False
                # 敌人死亡时掉落血包
                if not self.is_player:
                    self.drop_health()
                if sound_manager:
                    sound_manager.play_explosion_sound()

    def drop_health(self):
        """掉落血包（50%概率）"""
        if random.random() < self.drop_health_prob and not self.is_player:
            self.health_pack = GameObject(
                self.rect.x, self.rect.y, 15, 15, (255, 0, 255)  # 粉色血包
            )
            return self.health_pack
        return None

    def _ai_find_path(self, target_pos, game_map):
        """智能路径寻找，包含距离控制"""
        dx = target_pos[0] - self.rect.centerx
        dy = target_pos[1] - self.rect.centery
        distance = math.sqrt(dx*dx + dy*dy)
        
        # BOSS坦克更擅长走位
        if self.is_boss:
            # 更多横向移动和规避动作
            if random.random() < 0.4:
                # 随机横向移动
                return (random.choice([-1, 1, 0]), random.choice([-1, 1, 0]))
            # 更频繁地改变方向
            if self.ai_move_timer % 5 == 0:
                move_dir = (random.choice([-1, 1, 0]), random.choice([-1, 1, 0]))
                return move_dir
        
        # 理想距离控制在150-250之间
        ideal_min_distance = 150
        ideal_max_distance = 250
        
        # 距离过近则远离目标
        if distance < ideal_min_distance:
            move_x = -1 if dx > 0 else 1 if dx < 0 else 0
            move_y = -1 if dy > 0 else 1 if dy < 0 else 0
            move_dir = (move_x, move_y)
        # 距离过远则靠近目标
        elif distance > ideal_max_distance:
            move_x = 1 if dx > 0 else -1 if dx < 0 else 0
            move_y = 1 if dy > 0 else -1 if dy < 0 else 0
            # 对角线优化
            if abs(dx) > 10 and abs(dy) > 10:
                move_dir = (move_x, move_y)
            else:
                move_dir = (move_x, move_y)
        # 距离适中则保持并横向移动
        else:
            # 随机横向移动保持活跃
            if random.random() < 0.7:
                move_dir = (random.choice([-1, 1, 0]), random.choice([-1, 1, 0]))
            else:
                move_x = 1 if dx > 0 else -1 if dx < 0 else 0
                move_y = 1 if dy > 0 else -1 if dy < 0 else 0
                move_dir = (move_x, move_y)
        
        # 检查碰撞
        temp_rect = pygame.Rect(
            self.rect.x + move_dir[0] * self.speed,
            self.rect.y + move_dir[1] * self.speed,
            self.rect.width,
            self.rect.height
        )
        
        if game_map and game_map.check_collision(temp_rect):
            directions = [(1,0), (-1,0), (0,1), (0,-1), (1,1), (1,-1), (-1,1), (-1,-1)]
            random.shuffle(directions)
            for dir in directions:
                temp_rect = pygame.Rect(
                    self.rect.x + dir[0] * self.speed,
                    self.rect.y + dir[1] * self.speed,
                    self.rect.width,
                    self.rect.height
                )
                if not game_map.check_collision(temp_rect):
                    return dir
            return (0, 0)
        
        return move_dir

    def _predict_bullet_path(self, player_tank, game_map):
        """预测玩家子弹路径并返回躲避方向"""
        if not player_tank or not hasattr(player_tank, 'bullets'):
            return None
        
        # 只关注朝向自己的子弹
        dangerous_bullets = []
        for bullet in player_tank.bullets:
            if not bullet.active:
                continue
                
            # 计算子弹到AI坦克的向量
            bullet_to_ai = (self.rect.centerx - bullet.rect.x, 
                           self.rect.centery - bullet.rect.y)
            # 计算子弹移动方向与子弹到AI向量的点积
            dot_product = bullet.direction[0] * bullet_to_ai[0] + bullet.direction[1] * bullet_to_ai[1]
            
            # 点积为正表示子弹朝向AI移动
            if dot_product > 0:
                # 计算子弹到达AI位置的大致时间
                distance = math.sqrt(bullet_to_ai[0]**2 + bullet_to_ai[1]** 2)
                time_to_reach = distance / (bullet.speed * 3)  # 留出反应时间
                
                # BOSS坦克反应更快
                if self.is_boss:
                    time_threshold = 20
                else:
                    time_threshold = 15 - self.ai_difficulty * 2  # 难度越高反应越快
                
                # 近距离且即将命中的子弹才视为危险
                if distance < 200 and time_to_reach < time_threshold:
                    dangerous_bullets.append((distance, bullet))
        
        if dangerous_bullets:
            # 优先躲避最近的子弹
            dangerous_bullets.sort()
            closest_distance, closest_bullet = dangerous_bullets[0]
            
            # 计算躲避方向（垂直于子弹路径）
            bullet_dir = closest_bullet.direction
            # 垂直方向（两种可能）
            perpendicular_dirs = [(-bullet_dir[1], bullet_dir[0]), 
                                 (bullet_dir[1], -bullet_dir[0])]
            
            # 选择一个可行的躲避方向
            for dir in perpendicular_dirs:
                temp_rect = pygame.Rect(
                    self.rect.x + dir[0] * self.speed * 3,  # 快速移动
                    self.rect.y + dir[1] * self.speed * 3,
                    self.rect.width,
                    self.rect.height
                )
                if not game_map.check_collision(temp_rect):
                    return dir
            
            # 如果垂直方向不可行，尝试反方向躲避
            return (-bullet_dir[0], -bullet_dir[1])
        
        return None

    def _ai_aim(self, target_pos):
        dx = target_pos[0] - self.rect.centerx
        dy = target_pos[1] - self.rect.centery
        
        # 8方向瞄准
        if abs(dx) > abs(dy):
            if abs(dy) > abs(dx) * 0.3:
                return (1 if dx > 0 else -1, 1 if dy > 0 else -1)
            return (1 if dx > 0 else -1, 0)
        else:
            if abs(dx) > abs(dy) * 0.3:
                return (1 if dx > 0 else -1, 1 if dy > 0 else -1)
            return (0, 1 if dy > 0 else -1)

    def update(self, keys=None, game_map=None, target_tank=None, sound_manager=None):
        if not self.alive:
            return
        if self.shoot_cooldown > 0:
            self.shoot_cooldown -= 1

        if self.is_player and keys:
            # 8方向移动控制
            dx, dy = 0, 0
            if keys[pygame.K_w]:
                dy = -1
            if keys[pygame.K_s]:
                dy = 1
            if keys[pygame.K_a]:
                dx = -1
            if keys[pygame.K_d]:
                dx = 1
            
            if dx != 0 or dy != 0:
                self.move(dx, dy, game_map)
            
            if keys[pygame.K_SPACE]:
                self.shoot(sound_manager)
        
        elif not self.is_player and target_tank and target_tank.alive:
            self.ai_target = target_tank
            self.ai_move_timer += 1
            self.ai_shoot_timer += 1
            
            # BOSS坦克射击冷却更短
            shoot_interval = 10 if self.is_boss else 15
            # AI难度影响射击频率
            shoot_interval = max(5, shoot_interval - self.ai_difficulty)
            
            # 检查是否需要躲避子弹
            dodge_dir = self._predict_bullet_path(target_tank, game_map)
            
            if dodge_dir:
                # 立即执行躲避动作
                self.move(dodge_dir[0], dodge_dir[1], game_map)
                self.ai_move_timer = 0  # 重置移动计时器
            elif self.ai_move_timer >= random.randint(10, 20 - self.ai_difficulty * 2):
                self.ai_move_timer = 0
                if random.random() < 0.8 + (self.ai_difficulty * 0.1):  # 难度越高越可能追踪目标
                    target_pos = (self.ai_target.rect.centerx, self.ai_target.rect.centery)
                    move_dir = self._ai_find_path(target_pos, game_map)
                else:
                    # 随机移动增加不可预测性
                    move_dir = (random.choice([-1, 0, 1]), random.choice([-1, 0, 1]))
                
                self.move(move_dir[0], move_dir[1], game_map)
            
            # 射击逻辑
            if self.ai_shoot_timer >= shoot_interval:
                self.ai_shoot_timer = 0
                # 瞄准目标
                aim_dir = self._ai_aim((target_tank.rect.centerx, target_tank.rect.centery))
                self.direction = aim_dir
                self.update_angle()
                # 有一定概率射击（难度越高概率越大）
                if random.random() < 0.7 + (self.ai_difficulty * 0.1):
                    self.shoot(sound_manager)

        for bullet in self.bullets[:]:
            bullet.update()
            if not bullet.active:
                self.bullets.remove(bullet)

    def draw_health_bar(self, screen):
        if not self.alive:
            return
        bg_rect = pygame.Rect(self.rect.x, self.rect.y - 10, self.rect.width, 5)
        pygame.draw.rect(screen, (200, 0, 0), bg_rect)
        health_width = (self.health / self.max_health) * self.rect.width
        health_rect = pygame.Rect(self.rect.x, self.rect.y - 10, health_width, 5)
        
        # BOSS坦克使用不同颜色的血条
        if self.is_boss:
            pygame.draw.rect(screen, (128, 0, 128), health_rect)  # 紫色血条
        else:
            pygame.draw.rect(screen, (0, 200, 0), health_rect)

    def draw(self, screen):
        if not self.alive:
            # 绘制血包（如果有）
            if self.health_pack:
                pygame.draw.rect(screen, self.health_pack.color, self.health_pack.rect)
            return
        
        super().draw(screen)
        
        # 绘制旋转炮管（优化动画）
        gun_length = 20
        rad_angle = math.radians(self.angle)
        end_x = self.rect.centerx + math.cos(rad_angle) * gun_length
        end_y = self.rect.centery - math.sin(rad_angle) * gun_length
        
        # BOSS坦克炮管更粗
        gun_width = 5 if self.is_boss else 3
        pygame.draw.line(screen, (0,0,0), self.rect.center, (end_x, end_y), gun_width)
        
        self.draw_health_bar(screen)
        for bullet in self.bullets:
            bullet.draw(screen)