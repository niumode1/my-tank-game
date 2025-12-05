import pygame
import os
import sys


class SoundManager:
    """音效管理器"""
    def __init__(self):
        pygame.mixer.init()
        # 新增：获取资源根目录（兼容开发和打包模式）
        self.base_path = self._get_base_path()
        # 音效目录：基于根目录拼接
        self.sounds_dir = os.path.join(self.base_path, "assets", "sounds")
        
        # 加载音效（若无文件则使用默认音效）
        self.shoot_sound = self._load_sound("shoot.wav", None)
        self.explosion_sound = self._load_sound("explosion.wav", None)
        self.hit_sound = self._load_sound("hit.wav", None)
        self.powerup_sound = self._load_sound("powerup.wav", self.shoot_sound)  # 新增血包音效
        self.levelup_sound = self._load_sound("levelup.wav", self.shoot_sound)  # 新增升级音效

    def _get_base_path(self):
        """获取项目根目录（兼容开发和打包模式）"""
        try:
            # 打包后：sys._MEIPASS是exe解压后的临时目录（包含assets）
            return sys._MEIPASS
        except Exception:
            # 开发时：获取src的上级目录（项目根目录）
            return os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

    def _load_sound(self, filename, default=None):
        """加载音效文件，失败则返回默认"""
        try:
            sound_path = os.path.join(self.sounds_dir, filename)
            print(f"[音效调试] 尝试加载: {sound_path} {'(存在)' if os.path.exists(sound_path) else '(不存在)'}" )
            if os.path.exists(sound_path):
                return pygame.mixer.Sound(sound_path)
            return default
        except Exception as e:
            print(f"[音效错误] 加载{filename}失败: {e}")
            return default

    def play_shoot_sound(self):
        """播放射击音效"""
        if self.shoot_sound:
            self.shoot_sound.play()

    def play_explosion_sound(self):
        """播放爆炸音效"""
        if self.explosion_sound:
            self.explosion_sound.play()

    def play_hit_sound(self):
        """播放击中音效"""
        if self.hit_sound:
            self.hit_sound.play()

    def play_game_over_sound(self):
        """播放游戏结束音效（使用爆炸音效替代）"""
        if self.explosion_sound:
            self.explosion_sound.play()

    def play_victory_sound(self):
        """播放胜利音效（使用射击音效替代）"""
        if self.shoot_sound:
            self.shoot_sound.play()

    def play_powerup_sound(self):
        """播放血包拾取音效"""
        if self.powerup_sound:
            self.powerup_sound.play()

    def play_levelup_sound(self):
        """播放升级音效"""
        if self.levelup_sound:
            self.levelup_sound.play()