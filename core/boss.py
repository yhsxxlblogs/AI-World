# 老板角色类 - 玩家控制的角色
import pygame
import math
from core.config import COLORS, SCREEN_WIDTH, SCREEN_HEIGHT, GRID_SIZE

class Boss:
    """老板角色 - 由玩家WASD控制"""
    
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.size = 24
        self.speed = 4
        self.direction = 0  # 0=下, 1=左, 2=右, 3=上
        self.anim_frame = 0
        
        # 移动状态
        self.moving_up = False
        self.moving_down = False
        self.moving_left = False
        self.moving_right = False
        
    def update(self, dt, pathfinder, work_area, ent_area, particle_system=None):
        """更新老板位置"""
        # 计算移动
        dx = 0
        dy = 0
        
        if self.moving_up:
            dy -= self.speed
            self.direction = 3
        if self.moving_down:
            dy += self.speed
            self.direction = 0
        if self.moving_left:
            dx -= self.speed
            self.direction = 1
        if self.moving_right:
            dx += self.speed
            self.direction = 2
        
        # 更新动画帧
        is_moving = dx != 0 or dy != 0
        if is_moving:
            self.anim_frame += 0.2
            
            # 检查新位置是否有效
            new_x = self.x + dx
            new_y = self.y + dy
            
            # 边界检查
            new_x = max(self.size, min(SCREEN_WIDTH - self.size, new_x))
            new_y = max(self.size, min(SCREEN_HEIGHT - self.size, new_y))
            
            # 检查所有障碍物碰撞（墙体、家具、设备等）
            if not self._check_collision(new_x, new_y, work_area, ent_area):
                self.x = new_x
                self.y = new_y
                
                # 走路时产生脚步粒子
                if particle_system and int(self.anim_frame) % 2 == 0:
                    particle_system.create_footstep(self.x, self.y + 10, self.direction)
    
    def _check_collision(self, x, y, work_area, ent_area):
        """检查是否与任何障碍物碰撞"""
        # 检查工作区所有碰撞对象
        for obj in work_area.collision_objects:
            if obj['blocking'] and obj['rect'].collidepoint(x, y):
                return True
        
        # 检查娱乐区所有碰撞对象
        for obj in ent_area.collision_objects:
            if obj['blocking'] and obj['rect'].collidepoint(x, y):
                return True
        
        return False
    
    def draw_shadow(self, surface):
        """绘制阴影"""
        shadow_x = self.x + 4
        shadow_y = self.y + 4
        shadow_surface = pygame.Surface((self.size, self.size // 2), pygame.SRCALPHA)
        pygame.draw.ellipse(shadow_surface, (0, 0, 0, 60), 
                          (0, 0, self.size, self.size // 2))
        surface.blit(shadow_surface, (shadow_x - self.size // 2, shadow_y - self.size // 4))
    
    def draw(self, surface):
        """绘制老板 - 根据方向选择不同绘制方式（取消侧面，只使用正面和背面）"""
        self.draw_shadow(surface)
        
        # 根据方向选择绘制方式
        # 0=下/正面, 1=左, 2=右, 3=上/背面
        # 向左/右行走时也使用正面形象
        if self.direction == 3:  # 向上/背面
            self._draw_back(surface)
        else:  # 向下/正面/左/右都使用正面
            self._draw_front(surface)
    
    def _draw_front(self, surface):
        """绘制老板正面"""
        x = int(self.x)
        y = int(self.y)
        
        is_moving = self.moving_up or self.moving_down or self.moving_left or self.moving_right
        bounce = 0
        body_tilt = 0
        if is_moving:
            bounce = abs(math.sin(self.anim_frame * math.pi / 2)) * 3
            body_tilt = math.sin(self.anim_frame * math.pi / 2) * 1.5
        
        body_y = y - self.size // 2 + bounce
        
        # 绘制腿
        if is_moving:
            leg_swing = math.sin(self.anim_frame * math.pi / 2)
            left_leg_offset = int(leg_swing * 5)
            right_leg_offset = int(-leg_swing * 5)
            
            pygame.draw.rect(surface, (60, 60, 80), (x - 8 + left_leg_offset, body_y + 14, 5, 6))
            pygame.draw.rect(surface, (60, 60, 80), (x - 8 + left_leg_offset // 2, body_y + 20, 5, 6))
            pygame.draw.rect(surface, (40, 30, 30), (x - 8 + left_leg_offset, body_y + 24, 5, 4))
            
            pygame.draw.rect(surface, (60, 60, 80), (x + 3 + right_leg_offset, body_y + 14, 5, 6))
            pygame.draw.rect(surface, (60, 60, 80), (x + 3 + right_leg_offset // 2, body_y + 20, 5, 6))
            pygame.draw.rect(surface, (40, 30, 30), (x + 3 + right_leg_offset, body_y + 24, 5, 4))
        else:
            pygame.draw.rect(surface, (60, 60, 80), (x - 8, body_y + 14, 5, 10))
            pygame.draw.rect(surface, (40, 30, 30), (x - 8, body_y + 22, 5, 4))
            pygame.draw.rect(surface, (60, 60, 80), (x + 3, body_y + 14, 5, 10))
            pygame.draw.rect(surface, (40, 30, 30), (x + 3, body_y + 22, 5, 4))
        
        # 绘制身体
        body_rect = pygame.Rect(x - 9 + int(body_tilt), body_y, 18, 16)
        pygame.draw.rect(surface, (50, 50, 70), body_rect)
        pygame.draw.rect(surface, (40, 40, 60), body_rect, 1)
        pygame.draw.rect(surface, (70, 70, 90), (x - 7 + int(body_tilt), body_y + 2, 4, 8))
        pygame.draw.rect(surface, (255, 255, 255), (x - 2 + int(body_tilt), body_y + 2, 4, 8))
        pygame.draw.rect(surface, (200, 60, 60), (x - 1 + int(body_tilt), body_y + 3, 2, 6))
        
        # 绘制手臂
        if is_moving:
            arm_swing = math.sin(self.anim_frame * math.pi / 2 + math.pi)
            left_arm_offset = int(arm_swing * 4)
            right_arm_offset = int(-arm_swing * 4)
        else:
            left_arm_offset = 0
            right_arm_offset = 0
        
        pygame.draw.rect(surface, (50, 50, 70), (x - 13 + int(body_tilt), body_y + 2 + left_arm_offset, 4, 10))
        pygame.draw.rect(surface, COLORS['skin'], (x - 13 + int(body_tilt), body_y + 10 + left_arm_offset, 4, 4))
        pygame.draw.rect(surface, (50, 50, 70), (x + 9 + int(body_tilt), body_y + 2 + right_arm_offset, 4, 10))
        pygame.draw.rect(surface, COLORS['skin'], (x + 9 + int(body_tilt), body_y + 10 + right_arm_offset, 4, 4))
        
        # 绘制头
        head_bounce = 0
        if is_moving:
            head_bounce = math.sin(self.anim_frame * math.pi / 2) * 1
        
        head_y = body_y - 8 + int(head_bounce)
        head_x = x + int(body_tilt * 0.5)
        
        pygame.draw.ellipse(surface, COLORS['skin'], (head_x - 10, head_y - 4, 20, 18))
        pygame.draw.ellipse(surface, COLORS['skin_shadow'], (head_x - 10, head_y + 8, 20, 6))
        
        # 头发
        pygame.draw.rect(surface, (80, 60, 50), (head_x - 10, head_y - 8, 20, 7))
        pygame.draw.rect(surface, (80, 60, 50), (head_x - 10, head_y - 6, 6, 10))
        pygame.draw.rect(surface, (80, 60, 50), (head_x + 4, head_y - 6, 6, 8))
        
        # 眼睛
        eye_y = head_y + 2
        pygame.draw.rect(surface, COLORS['eye_white'], (head_x - 6, eye_y, 5, 6))
        pygame.draw.rect(surface, COLORS['eye_black'], (head_x - 4, eye_y + 2, 3, 3))
        pygame.draw.rect(surface, COLORS['eye_white'], (head_x + 1, eye_y, 5, 6))
        pygame.draw.rect(surface, COLORS['eye_black'], (head_x + 3, eye_y + 2, 3, 3))
        
        # 嘴巴
        pygame.draw.rect(surface, (180, 100, 100), (head_x - 3, head_y + 10, 6, 2))
    
    def _draw_side(self, surface):
        """绘制老板侧面"""
        is_left = (self.direction == 1)
        x = int(self.x)
        y = int(self.y)
        
        is_moving = self.moving_up or self.moving_down or self.moving_left or self.moving_right
        bounce = 0
        if is_moving:
            bounce = abs(math.sin(self.anim_frame * math.pi / 2)) * 3
        
        body_y = y - self.size // 2 + bounce
        
        # 绘制腿
        if is_moving:
            leg_swing = math.sin(self.anim_frame * math.pi / 2)
            front_leg_offset = int(leg_swing * 6)
            back_leg_offset = int(-leg_swing * 4)
            
            pygame.draw.rect(surface, (60, 60, 80), (x - 3 + back_leg_offset, body_y + 14, 4, 6))
            pygame.draw.rect(surface, (60, 60, 80), (x - 3 + back_leg_offset // 2, body_y + 20, 4, 6))
            pygame.draw.rect(surface, (40, 30, 30), (x - 3 + back_leg_offset, body_y + 24, 4, 4))
            
            pygame.draw.rect(surface, (60, 60, 80), (x + 1 + front_leg_offset, body_y + 14, 4, 6))
            pygame.draw.rect(surface, (60, 60, 80), (x + 1 + front_leg_offset // 2, body_y + 20, 4, 6))
            pygame.draw.rect(surface, (40, 30, 30), (x + 1 + front_leg_offset, body_y + 24, 4, 4))
        else:
            pygame.draw.rect(surface, (60, 60, 80), (x - 3, body_y + 14, 4, 10))
            pygame.draw.rect(surface, (40, 30, 30), (x - 3, body_y + 22, 4, 4))
            pygame.draw.rect(surface, (60, 60, 80), (x + 1, body_y + 14, 4, 10))
            pygame.draw.rect(surface, (40, 30, 30), (x + 1, body_y + 22, 4, 4))
        
        # 绘制身体（侧面更窄）
        body_rect = pygame.Rect(x - 6, body_y, 12, 16)
        pygame.draw.rect(surface, (50, 50, 70), body_rect)
        pygame.draw.rect(surface, (40, 40, 60), body_rect, 1)
        pygame.draw.rect(surface, (70, 70, 90), (x - 4, body_y + 2, 3, 8))
        pygame.draw.rect(surface, (255, 255, 255), (x - 1, body_y + 2, 3, 8))
        pygame.draw.rect(surface, (200, 60, 60), (x, body_y + 3, 2, 6))
        
        # 绘制侧面手臂
        if is_moving:
            arm_swing = math.sin(self.anim_frame * math.pi / 2 + math.pi)
            arm_offset = int(arm_swing * 5)
        else:
            arm_offset = 0
        
        pygame.draw.rect(surface, (50, 50, 70), (x + 4, body_y + 2 + arm_offset, 3, 10))
        pygame.draw.rect(surface, COLORS['skin'], (x + 4, body_y + 10 + arm_offset, 3, 4))
        pygame.draw.rect(surface, (50, 50, 70), (x - 7, body_y + 2 - arm_offset, 3, 10))
        pygame.draw.rect(surface, COLORS['skin'], (x - 7, body_y + 10 - arm_offset, 3, 4))
        
        # 绘制头
        head_bounce = 0
        if is_moving:
            head_bounce = math.sin(self.anim_frame * math.pi / 2) * 1
        
        head_y = body_y - 8 + int(head_bounce)
        head_x = x
        
        pygame.draw.ellipse(surface, COLORS['skin'], (head_x - 8, head_y - 4, 16, 18))
        pygame.draw.ellipse(surface, COLORS['skin_shadow'], (head_x - 8, head_y + 8, 16, 6))
        
        # 侧面头发
        pygame.draw.rect(surface, (80, 60, 50), (head_x - 8, head_y - 8, 16, 7))
        pygame.draw.rect(surface, (80, 60, 50), (head_x + (5 if is_left else -8), head_y - 6, 3, 8))
        
        # 侧面眼睛
        eye_y = head_y + 2
        pygame.draw.rect(surface, COLORS['eye_white'], (head_x + 2, eye_y, 5, 6))
        pygame.draw.rect(surface, COLORS['eye_black'], (head_x + 3, eye_y + 2, 3, 3))
        
        # 侧面嘴巴
        pygame.draw.rect(surface, (180, 100, 100), (head_x + 1, head_y + 10, 4, 2))
    
    def _draw_back(self, surface):
        """绘制老板背面"""
        x = int(self.x)
        y = int(self.y)
        
        is_moving = self.moving_up or self.moving_down or self.moving_left or self.moving_right
        bounce = 0
        if is_moving:
            bounce = abs(math.sin(self.anim_frame * math.pi / 2)) * 3
        
        body_y = y - self.size // 2 + bounce
        
        # 绘制腿
        if is_moving:
            leg_swing = math.sin(self.anim_frame * math.pi / 2)
            left_leg_offset = int(leg_swing * 5)
            right_leg_offset = int(-leg_swing * 5)
            
            pygame.draw.rect(surface, (60, 60, 80), (x - 8 + left_leg_offset, body_y + 14, 5, 6))
            pygame.draw.rect(surface, (60, 60, 80), (x - 8 + left_leg_offset // 2, body_y + 20, 5, 6))
            pygame.draw.rect(surface, (40, 30, 30), (x - 8 + left_leg_offset, body_y + 24, 5, 4))
            
            pygame.draw.rect(surface, (60, 60, 80), (x + 3 + right_leg_offset, body_y + 14, 5, 6))
            pygame.draw.rect(surface, (60, 60, 80), (x + 3 + right_leg_offset // 2, body_y + 20, 5, 6))
            pygame.draw.rect(surface, (40, 30, 30), (x + 3 + right_leg_offset, body_y + 24, 5, 4))
        else:
            pygame.draw.rect(surface, (60, 60, 80), (x - 8, body_y + 14, 5, 10))
            pygame.draw.rect(surface, (40, 30, 30), (x - 8, body_y + 22, 5, 4))
            pygame.draw.rect(surface, (60, 60, 80), (x + 3, body_y + 14, 5, 10))
            pygame.draw.rect(surface, (40, 30, 30), (x + 3, body_y + 22, 5, 4))
        
        # 绘制身体（背面）
        body_rect = pygame.Rect(x - 9, body_y, 18, 16)
        pygame.draw.rect(surface, (50, 50, 70), body_rect)
        pygame.draw.rect(surface, (40, 40, 60), body_rect, 1)
        
        # 背面手臂
        if is_moving:
            arm_swing = math.sin(self.anim_frame * math.pi / 2 + math.pi)
            left_arm_offset = int(arm_swing * 4)
            right_arm_offset = int(-arm_swing * 4)
        else:
            left_arm_offset = 0
            right_arm_offset = 0
        
        pygame.draw.rect(surface, (50, 50, 70), (x - 13, body_y + 2 + left_arm_offset, 4, 10))
        pygame.draw.rect(surface, (50, 50, 70), (x + 9, body_y + 2 + right_arm_offset, 4, 10))
        
        # 绘制头（背面）
        head_bounce = 0
        if is_moving:
            head_bounce = math.sin(self.anim_frame * math.pi / 2) * 1
        
        head_y = body_y - 8 + int(head_bounce)
        head_x = x
        
        pygame.draw.ellipse(surface, COLORS['skin'], (head_x - 10, head_y - 4, 20, 18))
        
        # 背面头发（更多头发）
        pygame.draw.rect(surface, (80, 60, 50), (head_x - 10, head_y - 10, 20, 9))
        pygame.draw.rect(surface, (80, 60, 50), (head_x - 10, head_y - 8, 5, 12))
        pygame.draw.rect(surface, (80, 60, 50), (head_x + 5, head_y - 8, 5, 12))
        pygame.draw.rect(surface, (80, 60, 50), (head_x - 8, head_y - 12, 16, 4))
    
    def get_rect(self):
        """获取碰撞矩形"""
        return pygame.Rect(
            self.x - self.size // 2,
            self.y - self.size // 2,
            self.size,
            self.size
        )
    
    def get_interact_rect(self):
        """获取交互范围矩形"""
        return pygame.Rect(
            self.x - 40,
            self.y - 40,
            80,
            80
        )
