# 粒子系统 - 用于游戏特效
import pygame
import random
import math

class Particle:
    """单个粒子"""
    def __init__(self, x, y, vx, vy, color, lifetime, size=3):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.color = color
        self.lifetime = lifetime
        self.max_lifetime = lifetime
        self.size = size
        self.alpha = 255
    
    def update(self, dt):
        """更新粒子状态"""
        self.x += self.vx * dt * 0.06
        self.y += self.vy * dt * 0.06
        self.lifetime -= dt
        # 渐隐效果
        self.alpha = int(255 * (self.lifetime / self.max_lifetime))
    
    def draw(self, surface):
        """绘制粒子"""
        if self.lifetime <= 0:
            return
        # 创建带透明度的表面
        particle_surface = pygame.Surface((self.size * 2, self.size * 2), pygame.SRCALPHA)
        color_with_alpha = (*self.color[:3], self.alpha)
        pygame.draw.circle(particle_surface, color_with_alpha, 
                          (self.size, self.size), self.size)
        surface.blit(particle_surface, (int(self.x - self.size), int(self.y - self.size)))
    
    def is_alive(self):
        """检查粒子是否还活着"""
        return self.lifetime > 0


class ParticleSystem:
    """粒子系统管理器"""
    def __init__(self):
        self.particles = []
    
    def update(self, dt):
        """更新所有粒子"""
        for particle in self.particles[:]:
            particle.update(dt)
            if not particle.is_alive():
                self.particles.remove(particle)
    
    def draw(self, surface):
        """绘制所有粒子"""
        for particle in self.particles:
            particle.draw(surface)
    
    def add_particle(self, x, y, vx, vy, color, lifetime, size=3):
        """添加单个粒子"""
        self.particles.append(Particle(x, y, vx, vy, color, lifetime, size))
    
    def create_explosion(self, x, y, color=None, count=10):
        """创建爆炸效果"""
        if color is None:
            color = (255, 200, 100)
        for _ in range(count):
            angle = random.uniform(0, math.pi * 2)
            speed = random.uniform(1, 4)
            vx = math.cos(angle) * speed
            vy = math.sin(angle) * speed
            lifetime = random.randint(300, 600)
            size = random.randint(2, 5)
            self.add_particle(x, y, vx, vy, color, lifetime, size)
    
    def create_hearts(self, x, y, count=3):
        """创建爱心效果"""
        for _ in range(count):
            vx = random.uniform(-0.5, 0.5)
            vy = random.uniform(-2, -1)
            lifetime = random.randint(500, 800)
            size = random.randint(4, 6)
            self.add_particle(x, y, vx, vy, (255, 100, 150), lifetime, size)
    
    def create_sparkles(self, x, y, count=5):
        """创建闪光效果"""
        colors = [(255, 255, 200), (255, 200, 100), (200, 255, 255), (255, 255, 255)]
        for _ in range(count):
            angle = random.uniform(0, math.pi * 2)
            speed = random.uniform(0.5, 2)
            vx = math.cos(angle) * speed
            vy = math.sin(angle) * speed
            lifetime = random.randint(200, 400)
            size = random.randint(2, 4)
            color = random.choice(colors)
            self.add_particle(x, y, vx, vy, color, lifetime, size)
    
    def create_footstep(self, x, y, direction=0):
        """创建脚步效果"""
        # 方向: 0=下, 1=左, 2=右, 3=上
        dust_color = (200, 200, 180)
        for _ in range(2):
            vx = random.uniform(-0.5, 0.5)
            vy = random.uniform(-0.5, 0.5)
            lifetime = random.randint(200, 300)
            size = random.randint(2, 3)
            offset_x = random.randint(-5, 5)
            offset_y = random.randint(-3, 3)
            self.add_particle(x + offset_x, y + offset_y, vx, vy, dust_color, lifetime, size)
    
    def clear(self):
        """清除所有粒子"""
        self.particles.clear()
