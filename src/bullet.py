import pygame
from game_objects import GameObject

class Bullet(GameObject):
    """子弹类，负责子弹的移动、边界检测和碰撞体积"""
    def __init__(self, x, y, direction, speed=5):
        # 子弹尺寸5x5，红色
        super().__init__(x, y, 5, 5, (255, 0, 0))
        self.direction = direction  # 移动方向 (dx, dy)
        self.speed = speed
        self.active = True  # 子弹是否有效

    def update(self):
        """更新子弹位置，检测边界"""
        self.rect.x += self.direction[0] * self.speed
        self.rect.y += self.direction[1] * self.speed
        
        # 边界检测：超出屏幕则标记为无效
        if (self.rect.x < 0 or self.rect.x > 800 or
            self.rect.y < 0 or self.rect.y > 600):
            self.active = False

    def check_collision(self, obj):
        """检测子弹是否与目标对象碰撞"""
        if self.active and self.rect.colliderect(obj.rect):
            self.active = False
            return True
        return False