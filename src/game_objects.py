import pygame

class GameObject:
    """通用游戏对象基类，包含基础属性和绘制方法"""
    def __init__(self, x, y, width, height, color):
        self.rect = pygame.Rect(x, y, width, height)  # 碰撞矩形
        self.color = color  # 对象颜色

    def draw(self, screen):
        """绘制对象到屏幕"""
        pygame.draw.rect(screen, self.color, self.rect)