# 娱乐区类 - 包含沙发、街机、植物等休闲设施

import pygame
import math
import random
from core.config import COLORS, AREAS, WALLS, PERSPECTIVE, GRID_SIZE

class EntertainmentArea:
    """娱乐区 - 员工休息放松的地方"""
    
    def __init__(self):
        self.area = AREAS['entertainment']
        self.sofas = []
        self.plants = []
        self.arcade_machines = []
        self.walls = []
        self.collision_objects = []
        # 新增装饰物
        self.tvs = []
        self.vending_machines = []
        self.rugs = []
        self.coffee_tables = []
        self.water_coolers = []
        self.rest_spots = []
        # 新装饰物
        self.bookshelves = []
        self.posters = []
        self.floor_lamps = []
        self._init_layout()
        self._init_walls()
    
    def _init_layout(self):
        """初始化娱乐区布局"""
        base_x = self.area['x']
        base_y = self.area['y']
        
        # 地毯 (中央区域)
        self.rugs.append({
            'x': base_x + 150,
            'y': base_y + 200,
            'width': 200,
            'height': 120,
        })
        
        # 沙发区域
        self.sofas.append({
            'x': base_x + 80,
            'y': base_y + 100,
            'width': 80,
            'height': 40,
            'color': COLORS['sofa']
        })
        
        self.sofas.append({
            'x': base_x + 80,
            'y': base_y + 180,
            'width': 80,
            'height': 40,
            'color': COLORS['sofa_dark']
        })
        
        # 咖啡桌
        self.coffee_tables.append({
            'x': base_x + 180,
            'y': base_y + 140,
            'width': 50,
            'height': 30,
        })
        
        # 街机
        self.arcade_machines.append({
            'x': base_x + 320,
            'y': base_y + 90,
            'width': 40,
            'height': 50,
            'screen_phase': random.uniform(0, math.pi * 2),
        })
        
        # 饮水机
        self.water_coolers.append({
            'x': base_x + 55,
            'y': base_y + 300,
            'width': 28,
            'height': 35,
        })
        
        # 电视
        self.tvs.append({
            'x': base_x + 380,
            'y': base_y + 80,
            'width': 60,
            'height': 40,
        })
        
        # 自动售货机 - 移到右上角靠墙位置，不挡路
        self.vending_machines.append({
            'x': base_x + 440,
            'y': base_y + 80,
            'width': 35,
            'height': 50,
        })
        
        # 绿植
        self.plants.append({
            'x': base_x + 350,
            'y': base_y + 250,
            'size': 28,
            'type': 'large'
        })
        
        # 挂式绿植（在前两层区域）
        self.plants.append({
            'x': base_x + 170,
            'y': base_y + 55,
            'size': 18,
            'type': 'hanging'
        })
        
        self.plants.append({
            'x': base_x + 45,
            'y': base_y + 420,
            'size': 20,
            'type': 'medium'
        })
        
        # 书架 - 添加在左下角
        self.bookshelves.append({
            'x': base_x + 60,
            'y': base_y + 480,
            'width': 80,
            'height': 30,
        })
        
        # 海报 - 墙上装饰
        self.posters.append({
            'x': base_x + 200,
            'y': base_y + 30,
            'width': 40,
            'height': 25,
            'type': 'art'
        })
        
        self.posters.append({
            'x': base_x + 350,
            'y': base_y + 30,
            'width': 50,
            'height': 30,
            'type': 'motivation'
        })
        
        # 落地灯 - 移到角落位置，不挡路
        self.floor_lamps.append({
            'x': base_x + 450,
            'y': base_y + 550,
            'width': 25,
            'height': 25,
        })
        
        self.floor_lamps.append({
            'x': base_x + 50,
            'y': base_y + 550,
            'width': 25,
            'height': 25,
        })
        
        # 添加到碰撞对象
        for sofa in self.sofas:
            self.collision_objects.append({
                'type': 'sofa',
                'rect': pygame.Rect(sofa['x'] - sofa['width'] // 2,
                                   sofa['y'] - sofa['height'] // 2,
                                   sofa['width'], sofa['height']),
                'blocking': True
            })
        
        for table in self.coffee_tables:
            self.collision_objects.append({
                'type': 'table',
                'rect': pygame.Rect(table['x'] - table['width'] // 2,
                                   table['y'] - table['height'] // 2,
                                   table['width'], table['height']),
                'blocking': True
            })
        
        for arcade in self.arcade_machines:
            self.collision_objects.append({
                'type': 'arcade',
                'rect': pygame.Rect(arcade['x'] - arcade['width'] // 2,
                                   arcade['y'] - arcade['height'] // 2,
                                   arcade['width'], arcade['height']),
                'blocking': True
            })
        
        for cooler in self.water_coolers:
            self.collision_objects.append({
                'type': 'cooler',
                'rect': pygame.Rect(cooler['x'] - cooler['width'] // 2,
                                   cooler['y'] - cooler['height'] // 2,
                                   cooler['width'], cooler['height']),
                'blocking': True
            })
        
        for tv in self.tvs:
            self.collision_objects.append({
                'type': 'tv',
                'rect': pygame.Rect(tv['x'] - tv['width'] // 2,
                                   tv['y'] - tv['height'] // 2,
                                   tv['width'], tv['height']),
                'blocking': True
            })
        
        for vending in self.vending_machines:
            self.collision_objects.append({
                'type': 'vending',
                'rect': pygame.Rect(vending['x'] - vending['width'] // 2,
                                   vending['y'] - vending['height'] // 2,
                                   vending['width'], vending['height']),
                'blocking': True
            })
        
        for plant in self.plants:
            self.collision_objects.append({
                'type': 'plant',
                'rect': pygame.Rect(plant['x'] - plant['size'] // 2,
                                   plant['y'] - plant['size'] // 2,
                                   plant['size'], plant['size']),
                'blocking': True
            })
        
        # 书架碰撞检测
        for bookshelf in self.bookshelves:
            self.collision_objects.append({
                'type': 'bookshelf',
                'rect': pygame.Rect(bookshelf['x'] - bookshelf['width'] // 2,
                                   bookshelf['y'] - bookshelf['height'] // 2,
                                   bookshelf['width'], bookshelf['height']),
                'blocking': True
            })
        
        # 海报碰撞检测（不阻挡，只是装饰）
        for poster in self.posters:
            self.collision_objects.append({
                'type': 'poster',
                'rect': pygame.Rect(poster['x'] - poster['width'] // 2,
                                   poster['y'] - poster['height'] // 2,
                                   poster['width'], poster['height']),
                'blocking': False
            })
        
        # 落地灯碰撞检测
        for lamp in self.floor_lamps:
            self.collision_objects.append({
                'type': 'floor_lamp',
                'rect': pygame.Rect(lamp['x'] - lamp['width'] // 2,
                                   lamp['y'] - lamp['height'] // 2,
                                   lamp['width'], lamp['height']),
                'blocking': True
            })
        
        # 前两层蓝白区域添加严格碰撞检测
        self._init_blue_white_collision()
        
        # 定义休息位置（确保不在障碍物上）
        self.rest_spots = [
            (base_x + 80, base_y + 220),   # 在第二个沙发下方
            (base_x + 300, base_y + 100),  # 在咖啡桌上方偏右
            (base_x + 180, base_y + 280),  # 在咖啡桌下方
            (base_x + 350, base_y + 200),  # 在中央区域
            (base_x + 100, base_y + 380),  # 在饮水机附近
            (base_x + 280, base_y + 350),  # 在中央区域
            (base_x + 400, base_y + 300),  # 在绿植附近
            (base_x + 280, base_y + 480),  # 在下部区域
            (base_x + 150, base_y + 520),  # 在左下角
            (base_x + 400, base_y + 450),  # 在右下角
        ]
    
    def _init_blue_white_collision(self):
        """初始化蓝白区域的碰撞检测 - 人物任何部分都不能进入"""
        ax, ay = self.area['x'], self.area['y']
        tile_size = GRID_SIZE
        
        # 前两层（grid_y = 0 和 1）添加严格碰撞
        for grid_y in range(2):
            for grid_x in range(0, self.area['width'] // tile_size + 1):
                # 计算每个蓝白方块的位置
                x = ax + grid_x * tile_size
                y = ay + grid_y * tile_size
                
                # 创建碰撞矩形
                collision_rect = pygame.Rect(x, y, tile_size, tile_size)
                
                self.collision_objects.append({
                    'type': 'blue_white_tile',
                    'rect': collision_rect,
                    'blocking': True,
                    'grid_x': grid_x,
                    'grid_y': grid_y
                })
    
    def _init_walls(self):
        """初始化墙体"""
        ax, ay = self.area['x'], self.area['y']
        aw, ah = self.area['width'], self.area['height']
        thickness = WALLS['thickness']
        
        # 右墙
        self.walls.append({'rect': pygame.Rect(ax + aw, ay, thickness, ah), 'type': 'vertical', 'outer': True})
        # 上墙
        self.walls.append({'rect': pygame.Rect(ax, ay - thickness, aw, thickness), 'type': 'horizontal', 'outer': True})
        # 下墙
        self.walls.append({'rect': pygame.Rect(ax, ay + ah, aw, thickness), 'type': 'horizontal', 'outer': True})
        # 左墙 - 留出通道入口（通道在x=660处，左墙应该在通道外面）
        corridor_y = AREAS['corridor']['y']
        corridor_h = AREAS['corridor']['height']
        # 左墙分段：通道上方和通道下方（确保不阻塞通道）
        # 通道范围：y=260-460，左墙应该在 y<260 和 y>460 的区域
        self.walls.append({'rect': pygame.Rect(ax - thickness, ay, thickness, corridor_y - ay), 'type': 'vertical', 'outer': True})
        self.walls.append({'rect': pygame.Rect(ax - thickness, corridor_y + corridor_h, thickness, ay + ah - (corridor_y + corridor_h)), 'type': 'vertical', 'outer': True})
        
        for wall in self.walls:
            self.collision_objects.append({
                'type': 'wall',
                'rect': wall['rect'],
                'blocking': True
            })
    
    def get_collision_objects(self):
        return self.collision_objects
    
    def get_random_rest_spot(self):
        return random.choice(self.rest_spots) if self.rest_spots else None
    
    def get_all_rest_spots(self):
        return self.rest_spots
    
    def update(self, dt):
        for arcade in self.arcade_machines:
            arcade['screen_phase'] += dt * 0.004
    
    def draw(self, surface):
        area_rect = pygame.Rect(self.area['x'], self.area['y'], self.area['width'], self.area['height'])
        
        self._draw_grid_floor(surface, area_rect)
        self._draw_walls(surface)
        
        # 绘制地毯(在最底层)
        for rug in self.rugs:
            self._draw_rug(surface, rug)
        
        # 绘制其他装饰物
        for sofa in self.sofas:
            self._draw_sofa(surface, sofa)
        
        for table in self.coffee_tables:
            self._draw_coffee_table(surface, table)
        
        for arcade in self.arcade_machines:
            self._draw_arcade(surface, arcade)
        
        for cooler in self.water_coolers:
            self._draw_water_cooler(surface, cooler)
        
        for tv in self.tvs:
            self._draw_tv(surface, tv)
        
        for vending in self.vending_machines:
            self._draw_vending_machine(surface, vending)
        
        for plant in self.plants:
            self._draw_plant(surface, plant)
        
        # 绘制新装饰物
        for bookshelf in self.bookshelves:
            self._draw_bookshelf(surface, bookshelf)
        
        for poster in self.posters:
            self._draw_poster(surface, poster)
        
        for lamp in self.floor_lamps:
            self._draw_floor_lamp(surface, lamp)
    
    def _draw_grid_floor(self, surface, rect):
        """绘制网格状地板 - 前两层蓝白色木板，其他层保持原样"""
        # 前两层（最底层两层）蓝白色木板
        blue_white_base = (220, 230, 245)
        pygame.draw.rect(surface, blue_white_base, rect)
        
        tile_size = GRID_SIZE
        # 前两层蓝白色木板纹理
        for y in range(rect.y, rect.y + tile_size * 2):  # 前两层
            for x in range(rect.x, rect.right, tile_size):
                grid_x = (x - rect.x) // tile_size
                
                # 蓝白相间的木板纹理
                if grid_x % 2 == 0:
                    color = (235, 245, 255)  # 亮蓝白
                else:
                    color = (200, 220, 240)  # 淡蓝色
                
                tile_rect = pygame.Rect(x, y, min(tile_size, rect.right - x), 1)
                pygame.draw.rect(surface, color, tile_rect)
        
        # 第二层底边加粗
        pygame.draw.line(surface, (100, 130, 170), 
                        (rect.x, rect.y + tile_size * 2 - 1), 
                        (rect.right, rect.y + tile_size * 2 - 1), 3)
        
        # 其他层保持原来的网格样式
        for y in range(rect.y + tile_size * 2, rect.bottom, tile_size):
            for x in range(rect.x, rect.right, tile_size):
                grid_x = (x - rect.x) // tile_size
                grid_y = (y - rect.y) // tile_size
                
                if (grid_x + grid_y) % 2 == 0:
                    color = COLORS['floor_light']
                else:
                    color = COLORS['floor_dark']
                
                tile_rect = pygame.Rect(x, y, min(tile_size, rect.right - x), min(tile_size, rect.bottom - y))
                pygame.draw.rect(surface, color, tile_rect)
                pygame.draw.rect(surface, COLORS['floor_grid_line'], tile_rect, 1)
    
    def _draw_walls(self, surface):
        """绘制墙体 - 加粗增强立体感"""
        for wall in self.walls:
            rect = wall['rect']
            is_outer = wall.get('outer', False)
            
            if is_outer:
                outer_rect = rect.inflate(4, 4)
                pygame.draw.rect(surface, COLORS['wall_outer'], outer_rect)
                pygame.draw.rect(surface, (140, 130, 120), outer_rect, 2)
            
            pygame.draw.rect(surface, WALLS['color'], rect)
            pygame.draw.rect(surface, WALLS['shadow_color'], rect, 2)
            
            if wall['type'] == 'vertical':
                pygame.draw.line(surface, (250, 245, 235), (rect.x + 2, rect.y), (rect.x + 2, rect.bottom), 3)
                pygame.draw.line(surface, (140, 130, 120), (rect.right - 2, rect.y), (rect.right - 2, rect.bottom), 2)
            else:
                pygame.draw.line(surface, (250, 245, 235), (rect.x, rect.y + 2), (rect.right, rect.y + 2), 3)
                pygame.draw.line(surface, (140, 130, 120), (rect.x, rect.bottom - 2), (rect.right, rect.bottom - 2), 2)
    
    def _draw_rug(self, surface, rug):
        """绘制地毯"""
        x, y = rug['x'], rug['y']
        w, h = rug['width'], rug['height']
        
        rug_rect = pygame.Rect(x - w // 2, y - h // 2, w, h)
        pygame.draw.ellipse(surface, COLORS['rug'], rug_rect)
        pygame.draw.ellipse(surface, (130, 105, 80), rug_rect, 3)
        
        # 装饰图案
        inner_rect = pygame.Rect(x - w // 2 + 10, y - h // 2 + 5, w - 20, h - 10)
        pygame.draw.ellipse(surface, (180, 150, 120), inner_rect, 2)
    
    def _draw_sofa(self, surface, sofa):
        """绘制沙发 - 优化外观"""
        x, y = sofa['x'], sofa['y']
        w, h = sofa['width'], sofa['height']
        
        if PERSPECTIVE['enabled']:
            shadow_surface = pygame.Surface((w + 6, h + 3), pygame.SRCALPHA)
            pygame.draw.ellipse(shadow_surface, (0, 0, 0, PERSPECTIVE['shadow_alpha']), (0, 0, w + 6, h + 3))
            surface.blit(shadow_surface, (x - w // 2 + 3, y - h // 2 + 6))
        
        back_h = 18
        back_rect = pygame.Rect(x - w // 2, y - h // 2 - back_h // 2, w, back_h)
        pygame.draw.rect(surface, sofa['color'], back_rect, border_radius=3)
        pygame.draw.rect(surface, (120, 95, 75), back_rect, 1, border_radius=3)
        
        seat_rect = pygame.Rect(x - w // 2, y - h // 2 + 3, w, h - 6)
        pygame.draw.rect(surface, sofa['color'], seat_rect, border_radius=2)
        pygame.draw.rect(surface, (120, 95, 75), seat_rect, 1, border_radius=2)
        
        arm_w = 8
        pygame.draw.rect(surface, sofa['color'], (x - w // 2 - arm_w // 2, y - h // 2, arm_w, h - 4), border_radius=2)
        pygame.draw.rect(surface, sofa['color'], (x + w // 2 - arm_w // 2, y - h // 2, arm_w, h - 4), border_radius=2)
        
        cushion_color = (min(255, sofa['color'][0] + 12), min(255, sofa['color'][1] + 12), min(255, sofa['color'][2] + 12))
        pygame.draw.rect(surface, cushion_color, (x - w // 2 + 3, y - h // 2 - 2, w - 6, 10), border_radius=2)
    
    def _draw_coffee_table(self, surface, table):
        """绘制咖啡桌 - 优化外观"""
        x, y = table['x'], table['y']
        w, h = table['width'], table['height']
        
        if PERSPECTIVE['enabled']:
            shadow_surface = pygame.Surface((w, h // 2), pygame.SRCALPHA)
            pygame.draw.ellipse(shadow_surface, (0, 0, 0, PERSPECTIVE['shadow_alpha']), (0, 0, w, h // 2))
            surface.blit(shadow_surface, (x - w // 2 + 3, y + 3))
        
        table_rect = pygame.Rect(x - w // 2, y - h // 2, w, h)
        pygame.draw.ellipse(surface, COLORS['coffee_table'], table_rect)
        pygame.draw.ellipse(surface, (100, 80, 60), table_rect, 1)
        
        highlight_rect = pygame.Rect(x - w // 2 + 3, y - h // 2 + 2, w - 6, h // 3)
        pygame.draw.ellipse(surface, (170, 140, 110), highlight_rect)
        
        cup_x, cup_y = x - 6, y - 3
        pygame.draw.circle(surface, (240, 240, 230), (cup_x, cup_y), 4)
        pygame.draw.circle(surface, (60, 40, 30), (cup_x, cup_y), 4, 1)
        pygame.draw.circle(surface, (80, 50, 30), (cup_x, cup_y), 2)
        
        steam_color = (255, 255, 255, 70)
        for i in range(2):
            offset = (pygame.time.get_ticks() // 250 + i * 8) % 10
            steam_surface = pygame.Surface((5, 8), pygame.SRCALPHA)
            pygame.draw.ellipse(steam_surface, steam_color, (0, 0, 4, 6))
            surface.blit(steam_surface, (cup_x - 2 + i * 2, cup_y - 10 - offset))
    
    def _draw_arcade(self, surface, arcade):
        """绘制街机 - 优化外观"""
        x, y = arcade['x'], arcade['y']
        w, h = arcade['width'], arcade['height']
        
        if PERSPECTIVE['enabled']:
            shadow_surface = pygame.Surface((w + 5, h // 2), pygame.SRCALPHA)
            pygame.draw.ellipse(shadow_surface, (0, 0, 0, PERSPECTIVE['shadow_alpha']), (0, 0, w + 5, h // 2))
            surface.blit(shadow_surface, (x - w // 2 + 2, y + h // 2 - 3))
        
        body_rect = pygame.Rect(x - w // 2, y - h // 2, w, h)
        pygame.draw.rect(surface, COLORS['arcade_machine'], body_rect, border_radius=3)
        pygame.draw.rect(surface, (150, 55, 75), body_rect, 1, border_radius=3)
        
        stripe_rect = pygame.Rect(x - w // 2 + 2, y - h // 2 + h // 3, w - 4, 5)
        pygame.draw.rect(surface, (220, 220, 60), stripe_rect)
        
        screen_w, screen_h = w - 6, h // 3
        screen_rect = pygame.Rect(x - screen_w // 2, y - h // 2 + 3, screen_w, screen_h)
        
        glow = int(35 + 30 * math.sin(arcade['screen_phase']))
        screen_color = (
            max(0, COLORS['arcade_screen'][0] - glow // 2),
            min(255, COLORS['arcade_screen'][1] + glow),
            max(0, COLORS['arcade_screen'][2] - glow // 2)
        )
        pygame.draw.rect(surface, screen_color, screen_rect, border_radius=2)
        pygame.draw.rect(surface, (50, 50, 50), screen_rect, 1, border_radius=2)
        
        button_colors = [(230, 70, 70), (70, 230, 70), (70, 70, 230)]
        for i, color in enumerate(button_colors):
            bx = x - w // 2 + 5 + i * 7
            by = y + h // 2 - 6
            pygame.draw.circle(surface, color, (bx, by), 2)
            pygame.draw.circle(surface, (100, 100, 100), (bx, by), 2, 1)
        
        pygame.draw.rect(surface, (100, 100, 100), (x + 3, y + h // 2 - 8, 5, 8))
        pygame.draw.circle(surface, (200, 60, 60), (x + 5, y + h // 2 - 10), 3)
    
    def _draw_water_cooler(self, surface, cooler):
        """绘制饮水机 - 优化外观"""
        x, y = cooler['x'], cooler['y']
        w, h = cooler['width'], cooler['height']
        
        if PERSPECTIVE['enabled']:
            shadow_surface = pygame.Surface((w, h // 2), pygame.SRCALPHA)
            pygame.draw.ellipse(shadow_surface, (0, 0, 0, PERSPECTIVE['shadow_alpha']), (0, 0, w, h // 2))
            surface.blit(shadow_surface, (x - w // 2 + 2, y + 3))
        
        body_rect = pygame.Rect(x - w // 2, y - h // 2, w, h)
        pygame.draw.rect(surface, COLORS['water_cooler'], body_rect, border_radius=2)
        pygame.draw.rect(surface, (180, 180, 185), body_rect, 1, border_radius=2)
        
        bucket_rect = pygame.Rect(x - w // 2 + 2, y - h // 2 - 6, w - 4, 10)
        pygame.draw.ellipse(surface, (130, 180, 220, 150), bucket_rect)
        pygame.draw.ellipse(surface, (110, 150, 190), bucket_rect, 1)
        pygame.draw.ellipse(surface, (170, 210, 250, 100), (x - w // 2 + 3, y - h // 2 - 4, w - 6, 5))
        
        pygame.draw.rect(surface, (120, 120, 125), (x - 2, y, 3, 5))
        pygame.draw.rect(surface, (160, 160, 165), (x - 2, y - 1, 4, 2))
    
    def _draw_tv(self, surface, tv):
        """绘制电视"""
        x, y = tv['x'], tv['y']
        w, h = tv['width'], tv['height']
        
        # 支架
        pygame.draw.line(surface, (80, 80, 85), (x - 10, y + h // 2), (x - 10, y + h // 2 + 12), 3)
        pygame.draw.line(surface, (80, 80, 85), (x + 10, y + h // 2), (x + 10, y + h // 2 + 12), 3)
        pygame.draw.line(surface, (80, 80, 85), (x - 10, y + h // 2 + 12), (x + 10, y + h // 2 + 12), 3)
        
        # 电视主体
        tv_rect = pygame.Rect(x - w // 2, y - h // 2, w, h)
        pygame.draw.rect(surface, COLORS['tv'], tv_rect, border_radius=3)
        pygame.draw.rect(surface, (40, 40, 45), tv_rect, 2, border_radius=3)
        
        # 屏幕
        screen_rect = pygame.Rect(x - w // 2 + 3, y - h // 2 + 3, w - 6, h - 6)
        pygame.draw.rect(surface, COLORS['tv_screen'], screen_rect, border_radius=2)
        
        # 屏幕内容
        pygame.draw.line(surface, (200, 230, 255), (x - 15, y - 5), (x + 10, y - 5), 2)
        pygame.draw.circle(surface, (255, 200, 100), (x + 5, y + 5), 4)
    
    def _draw_vending_machine(self, surface, vending):
        """绘制自动售货机"""
        x, y = vending['x'], vending['y']
        w, h = vending['width'], vending['height']
        
        # 阴影
        if PERSPECTIVE['enabled']:
            shadow_surface = pygame.Surface((w + 4, h // 2), pygame.SRCALPHA)
            pygame.draw.ellipse(shadow_surface, (0, 0, 0, PERSPECTIVE['shadow_alpha']), (0, 0, w + 4, h // 2))
            surface.blit(shadow_surface, (x - w // 2 + 2, y + h // 2 - 3))
        
        # 机体
        body_rect = pygame.Rect(x - w // 2, y - h // 2, w, h)
        pygame.draw.rect(surface, COLORS['vending_machine'], body_rect, border_radius=2)
        pygame.draw.rect(surface, (80, 130, 180), body_rect, 2, border_radius=2)
        
        # 玻璃窗
        glass_rect = pygame.Rect(x - w // 2 + 3, y - h // 2 + 8, w - 6, h - 20)
        pygame.draw.rect(surface, (100, 150, 200, 150), glass_rect)
        pygame.draw.rect(surface, (80, 130, 180), glass_rect, 1)
        
        # 饮料
        drink_colors = [(255, 100, 100), (100, 255, 100), (255, 255, 100), (100, 100, 255)]
        for row in range(3):
            for col in range(2):
                drink_x = x - w // 2 + 6 + col * 12
                drink_y = y - h // 2 + 12 + row * 10
                pygame.draw.rect(surface, drink_colors[(row + col) % len(drink_colors)], 
                               (drink_x, drink_y, 8, 8), border_radius=1)
        
        # 投币口
        pygame.draw.rect(surface, (60, 60, 65), (x + w // 2 - 8, y - 5, 6, 8))
    
    def _draw_plant(self, surface, plant):
        """绘制绿植 - 优化外观，添加花朵"""
        x, y = plant['x'], plant['y']
        size = plant['size']
        
        if PERSPECTIVE['enabled']:
            shadow_surface = pygame.Surface((size, size // 2), pygame.SRCALPHA)
            pygame.draw.ellipse(shadow_surface, (0, 0, 0, PERSPECTIVE['shadow_alpha']), (0, 0, size, size // 2))
            surface.blit(shadow_surface, (x - size // 2 + 2, y + 3))
        
        # 花盆 - 更精致的陶土色
        pot_h = size // 2
        pot_rect = pygame.Rect(x - size // 3, y, size // 1.5, pot_h)
        pygame.draw.rect(surface, (210, 160, 120), pot_rect, border_radius=3)
        pygame.draw.rect(surface, (160, 120, 90), pot_rect, 2, border_radius=3)
        # 花盆高光
        highlight_rect = pygame.Rect(x - size // 3 + 3, y + 3, size // 1.5 - 6, 4)
        pygame.draw.rect(surface, (230, 190, 150), highlight_rect, border_radius=1)
        
        # 土壤
        soil_rect = pygame.Rect(x - size // 3 + 2, y + 2, size // 1.5 - 4, 5)
        pygame.draw.rect(surface, (120, 80, 60), soil_rect, border_radius=1)
        
        # 叶子颜色 - 更生动的绿色
        leaf_color = (90, 170, 80)
        leaf_dark = (60, 130, 55)
        leaf_light = (120, 200, 100)
        
        if plant['type'] == 'hanging':
            # 挂式绿植 - 悬挂在墙上，向下垂
            self._draw_hanging_plant(surface, plant)
            return
        elif plant['type'] == 'large':
            leaf_positions = [
                (x, y - size // 2, size // 2),
                (x - size // 3, y - size // 3, size // 3),
                (x + size // 3, y - size // 3, size // 3),
                (x - size // 4, y - size // 1.5, size // 3),
                (x + size // 4, y - size // 1.5, size // 3),
                (x - size // 6, y - size // 2, size // 4),
                (x + size // 6, y - size // 2, size // 4),
            ]
            # 大植物添加花朵
            flower_colors = [(255, 150, 150), (255, 200, 100), (200, 150, 255)]
            for i, (fx, fy) in enumerate([(x - 5, y - size + 5), (x + 5, y - size + 8), (x, y - size + 2)]):
                self._draw_flower(surface, fx, fy, 4, flower_colors[i % len(flower_colors)])
        elif plant['type'] == 'medium':
            leaf_positions = [
                (x, y - size // 2, size // 2),
                (x - size // 4, y - size // 3, size // 3),
                (x + size // 4, y - size // 3, size // 3),
                (x, y - size // 1.3, size // 4),
            ]
            # 中等植物添加一朵花
            self._draw_flower(surface, x, y - size + 3, 4, (255, 180, 180))
        else:
            leaf_positions = [
                (x, y - size // 2, size // 2),
                (x - size // 5, y - size // 4, size // 3),
                (x + size // 5, y - size // 3, size // 3),
            ]
        
        # 绘制茎
        for lx, ly, lsize in leaf_positions:
            pygame.draw.line(surface, (100, 140, 70), (x, y), (lx, ly), 2)
        
        # 绘制叶子
        for lx, ly, lsize in leaf_positions:
            points = [
                (lx, ly - lsize),
                (lx - lsize // 2, ly),
                (lx, ly + lsize // 3),
                (lx + lsize // 2, ly),
            ]
            # 叶子渐变效果
            pygame.draw.polygon(surface, leaf_light, points)
            pygame.draw.polygon(surface, leaf_color, [(p[0], p[1] + 1) for p in points])
            pygame.draw.polygon(surface, leaf_dark, points, 1)
            # 叶脉
            pygame.draw.line(surface, leaf_dark, (lx, ly), (lx, ly - lsize + 3), 1)
    
    def _draw_flower(self, surface, x, y, size, color):
        """绘制花朵"""
        # 花瓣
        petal_color = color
        petal_dark = (max(0, color[0] - 40), max(0, color[1] - 40), max(0, color[2] - 40))
        
        # 5个花瓣
        for i in range(5):
            angle = i * 72  # 360 / 5 = 72度
            import math
            rad = math.radians(angle)
            px = x + int(size * 0.6 * math.cos(rad))
            py = y + int(size * 0.6 * math.sin(rad))
            pygame.draw.circle(surface, petal_color, (px, py), size // 2)
            pygame.draw.circle(surface, petal_dark, (px, py), size // 2, 1)
        
        # 花心
        pygame.draw.circle(surface, (255, 220, 100), (x, y), size // 2)
        pygame.draw.circle(surface, (200, 170, 80), (x, y), size // 2, 1)
        # 花蕊点
        for i in range(4):
            angle = i * 90 + 45
            rad = math.radians(angle)
            rx = x + int(size * 0.15 * math.cos(rad))
            ry = y + int(size * 0.15 * math.sin(rad))
            pygame.draw.circle(surface, (180, 140, 60), (rx, ry), 1)
    
    def _draw_hanging_plant(self, surface, plant):
        """绘制挂式绿植 - 悬挂在墙上向下垂"""
        x, y = plant['x'], plant['y']
        size = plant['size']
        
        # 挂钩
        pygame.draw.line(surface, (120, 120, 125), (x, y - size), (x, y - size // 2), 2)
        pygame.draw.circle(surface, (100, 100, 105), (x, y - size), 3)
        
        # 花盆（倒挂或侧挂样式）
        pot_w = size // 1.5
        pot_h = size // 2
        pot_rect = pygame.Rect(x - pot_w // 2, y - pot_h // 2, pot_w, pot_h)
        pygame.draw.ellipse(surface, (200, 150, 110), pot_rect)
        pygame.draw.ellipse(surface, (150, 110, 80), pot_rect, 2)
        
        # 向下垂的藤蔓和叶子
        leaf_color = (90, 170, 80)
        leaf_dark = (60, 130, 55)
        leaf_light = (120, 200, 100)
        
        # 藤蔓茎
        vine_points = [
            (x, y + pot_h // 2),
            (x - 2, y + size),
            (x + 3, y + size * 1.5),
            (x - 1, y + size * 2),
        ]
        for i in range(len(vine_points) - 1):
            pygame.draw.line(surface, (100, 140, 70), vine_points[i], vine_points[i + 1], 2)
        
        # 下垂的叶子
        leaf_positions = [
            (x - 6, y + size // 2, size // 3),
            (x + 5, y + size // 1.5, size // 3),
            (x - 4, y + size * 1.2, size // 2),
            (x + 6, y + size * 1.3, size // 3),
            (x, y + size * 1.8, size // 2),
        ]
        
        for lx, ly, lsize in leaf_positions:
            # 下垂的叶子（倒置的泪滴形状）
            points = [
                (lx, ly + lsize // 2),  # 底部
                (lx - lsize // 2, ly - lsize // 3),  # 左上
                (lx, ly - lsize // 2),  # 顶部
                (lx + lsize // 2, ly - lsize // 3),  # 右上
            ]
            pygame.draw.polygon(surface, leaf_light, points)
            pygame.draw.polygon(surface, leaf_color, [(p[0], p[1] - 1) for p in points])
            pygame.draw.polygon(surface, leaf_dark, points, 1)
            # 叶脉
            pygame.draw.line(surface, leaf_dark, (lx, ly - lsize // 2), (lx, ly + lsize // 3), 1)
        
        # 挂式植物的小花
        self._draw_flower(surface, x + 3, y + size * 1.8, 3, (255, 180, 180))
    
    def _draw_bookshelf(self, surface, bookshelf):
        """绘制书架"""
        x, y = bookshelf['x'], bookshelf['y']
        w, h = bookshelf['width'], bookshelf['height']
        
        # 阴影
        if PERSPECTIVE['enabled']:
            shadow_surface = pygame.Surface((w + 4, h // 2), pygame.SRCALPHA)
            pygame.draw.ellipse(shadow_surface, (0, 0, 0, PERSPECTIVE['shadow_alpha']), (0, 0, w + 4, h // 2))
            surface.blit(shadow_surface, (x - w // 2 + 2, y + 3))
        
        # 书架主体
        shelf_rect = pygame.Rect(x - w // 2, y - h // 2, w, h)
        pygame.draw.rect(surface, COLORS['bookshelf'], shelf_rect, border_radius=2)
        pygame.draw.rect(surface, (140, 110, 80), shelf_rect, 2, border_radius=2)
        
        # 书架隔板
        shelf_colors = COLORS['books']
        for row in range(2):
            # 隔板线
            pygame.draw.line(surface, (140, 110, 80), 
                           (x - w // 2 + 2, y - h // 2 + (row + 1) * h // 3),
                           (x + w // 2 - 2, y - h // 2 + (row + 1) * h // 3), 2)
            # 书籍
            for col in range(4):
                book_x = x - w // 2 + 5 + col * 18
                book_y = y - h // 2 + row * h // 3 + 2
                book_color = shelf_colors[(row * 4 + col) % len(shelf_colors)]
                pygame.draw.rect(surface, book_color, (book_x, book_y, 12, h // 3 - 4), border_radius=1)
                pygame.draw.rect(surface, (100, 100, 100), (book_x, book_y, 12, h // 3 - 4), 1, border_radius=1)
    
    def _draw_poster(self, surface, poster):
        """绘制海报"""
        x, y = poster['x'], poster['y']
        w, h = poster['width'], poster['height']
        
        # 海报主体
        poster_rect = pygame.Rect(x - w // 2, y - h // 2, w, h)
        
        if poster['type'] == 'art':
            # 艺术海报 - 抽象风格
            pygame.draw.rect(surface, (240, 240, 235), poster_rect, border_radius=2)
            pygame.draw.rect(surface, (180, 180, 175), poster_rect, 2, border_radius=2)
            # 艺术图案
            pygame.draw.circle(surface, (255, 150, 150), (x - 5, y - 3), 6)
            pygame.draw.rect(surface, (150, 200, 255), (x + 2, y - 6, 8, 8))
            pygame.draw.polygon(surface, (255, 220, 150), [(x, y + 5), (x - 6, y + 10), (x + 6, y + 10)])
        else:
            # 励志海报
            pygame.draw.rect(surface, (255, 250, 240), poster_rect, border_radius=2)
            pygame.draw.rect(surface, (200, 180, 140), poster_rect, 2, border_radius=2)
            # 文字线条模拟
            for i in range(3):
                pygame.draw.line(surface, (100, 100, 100), 
                               (x - w // 2 + 5, y - h // 2 + 8 + i * 7),
                               (x + w // 2 - 5, y - h // 2 + 8 + i * 7), 2)
    
    def _draw_floor_lamp(self, surface, lamp):
        """绘制落地灯"""
        x, y = lamp['x'], lamp['y']
        w, h = lamp['width'], lamp['height']
        
        # 阴影
        if PERSPECTIVE['enabled']:
            shadow_surface = pygame.Surface((w, h // 2), pygame.SRCALPHA)
            pygame.draw.ellipse(shadow_surface, (0, 0, 0, PERSPECTIVE['shadow_alpha']), (0, 0, w, h // 2))
            surface.blit(shadow_surface, (x - w // 2 + 2, y + 5))
        
        # 灯座
        base_rect = pygame.Rect(x - 8, y + h // 2 - 6, 16, 6)
        pygame.draw.ellipse(surface, (80, 80, 85), base_rect)
        pygame.draw.ellipse(surface, (60, 60, 65), base_rect, 1)
        
        # 灯杆
        pygame.draw.line(surface, (100, 100, 105), (x, y + h // 2 - 6), (x, y - h // 2 + 5), 3)
        
        # 灯罩
        shade_points = [
            (x - 12, y - h // 2 + 5),
            (x + 12, y - h // 2 + 5),
            (x + 8, y - h // 2 - 10),
            (x - 8, y - h // 2 - 10),
        ]
        pygame.draw.polygon(surface, (250, 240, 200), shade_points)
        pygame.draw.polygon(surface, (200, 190, 160), shade_points, 2)
        
        # 灯光效果
        glow_surface = pygame.Surface((40, 40), pygame.SRCALPHA)
        pygame.draw.circle(glow_surface, (255, 255, 200, 40), (20, 20), 20)
        surface.blit(glow_surface, (x - 20, y - h // 2 - 5))
