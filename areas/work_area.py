# 工作区类 - 包含6台电脑和办公桌椅

import pygame
import math
import random
from core.config import COLORS, WORK_ZONE, AREAS, WALLS, PERSPECTIVE, GRID_SIZE

class WorkArea:
    """工作区 - 包含6个工位"""
    
    def __init__(self):
        self.area = AREAS['work']
        self.desks = []
        self.computers = []
        self.walls = []
        self.collision_objects = []
        # 新增装饰物
        self.bookshelves = []
        self.printers = []
        self.filing_cabinets = []
        self.whiteboards = []
        self.potted_plants = []
        self.clocks = []
        self.lamps = []
        self._init_layout()
        self._init_walls()
        self._init_decorations()
    
    def _init_layout(self):
        """初始化工位布局"""
        rows = WORK_ZONE['desk_rows']
        cols = WORK_ZONE['desk_cols']
        spacing_x = WORK_ZONE['desk_spacing_x']
        spacing_y = WORK_ZONE['desk_spacing_y']
        start_x = self.area['x'] + WORK_ZONE['desk_start_x']
        start_y = self.area['y'] + WORK_ZONE['desk_start_y']
        
        desk_id = 0
        for row in range(rows):
            for col in range(cols):
                x = start_x + col * spacing_x
                y = start_y + row * spacing_y
                
                desk = {
                    'id': desk_id,
                    'x': x,
                    'y': y,
                    'width': WORK_ZONE['desk_width'],
                    'height': WORK_ZONE['desk_height'],
                    'occupied': False,
                    'employee': None,
                }
                self.desks.append(desk)
                
                # 桌子添加碰撞检测，员工无法穿过
                self.collision_objects.append({
                    'type': 'desk',
                    'rect': pygame.Rect(x - WORK_ZONE['desk_width'] // 2, 
                                       y - WORK_ZONE['desk_height'] // 2,
                                       WORK_ZONE['desk_width'], 
                                       WORK_ZONE['desk_height']),
                    'blocking': True
                })
                
                computer = {
                    'id': desk_id,
                    'x': x,
                    'y': y - 10,
                    'width': WORK_ZONE['computer_width'],
                    'height': WORK_ZONE['computer_height'],
                    'on': True,
                    'glow_phase': random.uniform(0, math.pi * 2),
                }
                self.computers.append(computer)
                
                desk_id += 1
        
        # 添加蓝白区域（前两行）的碰撞检测 - 禁止人物进入
        self._init_blue_white_collision()
    
    def _init_blue_white_collision(self):
        """初始化蓝白区域的碰撞检测 - 人物任何部分都不能进入"""
        ax, ay = self.area['x'], self.area['y']
        tile_size = GRID_SIZE
        
        # 前两行（grid_y = 0 和 1）
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
        
        # 外墙
        self.walls.append({'rect': pygame.Rect(ax - thickness, ay, thickness, ah), 'type': 'vertical', 'outer': True})
        self.walls.append({'rect': pygame.Rect(ax - thickness, ay - thickness, aw + thickness * 2, thickness), 'type': 'horizontal', 'outer': True})
        self.walls.append({'rect': pygame.Rect(ax - thickness, ay + ah, aw + thickness * 2, thickness), 'type': 'horizontal', 'outer': True})
        
        # 右墙 - 留出通道（通道在x=580处，右墙应该在通道外面）
        corridor_y = AREAS['corridor']['y']
        corridor_h = AREAS['corridor']['height']
        # 右墙分段：通道上方和通道下方（确保不阻塞通道）
        # 通道范围：y=260-460，右墙应该在 y<260 和 y>460 的区域
        self.walls.append({'rect': pygame.Rect(ax + aw, ay, thickness, corridor_y - ay), 'type': 'vertical', 'outer': True})
        self.walls.append({'rect': pygame.Rect(ax + aw, corridor_y + corridor_h, thickness, ay + ah - (corridor_y + corridor_h)), 'type': 'vertical', 'outer': True})
        
        for wall in self.walls:
            self.collision_objects.append({
                'type': 'wall',
                'rect': wall['rect'],
                'blocking': True
            })
    
    def _init_decorations(self):
        """初始化办公区装饰物"""
        ax, ay = self.area['x'], self.area['y']
        aw, ah = self.area['width'], self.area['height']
        
        # 书架 (左上角)
        self.bookshelves.append({
            'x': ax + 50,
            'y': ay + 60,
            'width': 60,
            'height': 25,
        })
        
        # 打印机 (左下角)
        self.printers.append({
            'x': ax + 50,
            'y': ay + ah - 80,
            'width': 35,
            'height': 30,
        })
        
        # 文件柜 (右下角)
        self.filing_cabinets.append({
            'x': ax + aw - 60,
            'y': ay + ah - 100,
            'width': 30,
            'height': 50,
        })
        
        # 白板 (右上角)
        self.whiteboards.append({
            'x': ax + aw - 80,
            'y': ay + 50,
            'width': 50,
            'height': 8,
        })
        
        # 盆栽 (分散摆放)
        self.potted_plants.append({'x': ax + 30, 'y': ay + 200, 'size': 18})
        self.potted_plants.append({'x': ax + aw - 40, 'y': ay + 300, 'size': 20})
        
        # 时钟 (墙上)
        self.clocks.append({
            'x': ax + aw // 2,
            'y': ay + 35,
            'radius': 12,
        })
        

        
        # 添加碰撞检测
        for shelf in self.bookshelves:
            self.collision_objects.append({
                'type': 'bookshelf',
                'rect': pygame.Rect(shelf['x'] - shelf['width'] // 2, 
                                   shelf['y'] - shelf['height'] // 2,
                                   shelf['width'], shelf['height']),
                'blocking': True
            })
        
        for printer in self.printers:
            self.collision_objects.append({
                'type': 'printer',
                'rect': pygame.Rect(printer['x'] - printer['width'] // 2,
                                   printer['y'] - printer['height'] // 2,
                                   printer['width'], printer['height']),
                'blocking': True
            })
        
        for cabinet in self.filing_cabinets:
            self.collision_objects.append({
                'type': 'cabinet',
                'rect': pygame.Rect(cabinet['x'] - cabinet['width'] // 2,
                                   cabinet['y'] - cabinet['height'] // 2,
                                   cabinet['width'], cabinet['height']),
                'blocking': True
            })
        
        for plant in self.potted_plants:
            self.collision_objects.append({
                'type': 'plant',
                'rect': pygame.Rect(plant['x'] - plant['size'] // 2,
                                   plant['y'] - plant['size'] // 2,
                                   plant['size'], plant['size']),
                'blocking': True
            })
    
    def get_collision_objects(self):
        return self.collision_objects
    
    def get_available_desk(self):
        for desk in self.desks:
            if not desk['occupied']:
                return desk
        return None
    
    def assign_employee(self, desk_id, employee):
        if 0 <= desk_id < len(self.desks):
            self.desks[desk_id]['occupied'] = True
            self.desks[desk_id]['employee'] = employee
            employee.assign_desk(self.desks[desk_id])
    
    def release_desk(self, desk_id):
        if 0 <= desk_id < len(self.desks):
            self.desks[desk_id]['occupied'] = False
            self.desks[desk_id]['employee'] = None
    
    def update(self, dt):
        for computer in self.computers:
            computer['glow_phase'] += dt * 0.002
    
    def draw(self, surface):
        """绘制工作区"""
        area_rect = pygame.Rect(self.area['x'], self.area['y'], self.area['width'], self.area['height'])
        
        # 绘制地板
        self._draw_grid_floor(surface, area_rect)
        
        # 绘制墙体
        self._draw_walls(surface)
        
        # 绘制装饰物
        for shelf in self.bookshelves:
            self._draw_bookshelf(surface, shelf)
        for printer in self.printers:
            self._draw_printer(surface, printer)
        for cabinet in self.filing_cabinets:
            self._draw_filing_cabinet(surface, cabinet)
        for whiteboard in self.whiteboards:
            self._draw_whiteboard(surface, whiteboard)
        for plant in self.potted_plants:
            self._draw_potted_plant(surface, plant)
        for clock in self.clocks:
            self._draw_clock(surface, clock)
        
        # 绘制工位
        for desk, computer in zip(self.desks, self.computers):
            self._draw_chair(surface, desk)
            self._draw_desk(surface, desk)
            self._draw_computer(surface, computer)
        
        # 绘制台灯(在桌子上面)
        for lamp in self.lamps:
            self._draw_lamp(surface, lamp)
    
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
        """绘制墙体 - 像素风格"""
        for wall in self.walls:
            rect = wall['rect']
            is_outer = wall.get('outer', False)
            
            if is_outer:
                # 像素风格外边框
                outer_rect = rect.inflate(6, 6)
                pygame.draw.rect(surface, COLORS['wall_outer'], outer_rect)
                pygame.draw.rect(surface, (120, 110, 100), outer_rect, 3)
            
            # 墙体主体 - 像素风格
            pygame.draw.rect(surface, WALLS['color'], rect)
            # 粗边框
            pygame.draw.rect(surface, WALLS['shadow_color'], rect, 3)
            
            # 像素风格高光和阴影
            if wall['type'] == 'vertical':
                # 左侧高光
                pygame.draw.rect(surface, (255, 250, 240), (rect.x, rect.y, 4, rect.height))
                # 右侧阴影
                pygame.draw.rect(surface, (140, 130, 120), (rect.right - 4, rect.y, 4, rect.height))
                # 像素装饰点
                for i in range(0, rect.height, 20):
                    pygame.draw.rect(surface, (200, 190, 180), (rect.x + 8, rect.y + i + 5, 3, 3))
            else:
                # 顶部高光
                pygame.draw.rect(surface, (255, 250, 240), (rect.x, rect.y, rect.width, 4))
                # 底部阴影
                pygame.draw.rect(surface, (140, 130, 120), (rect.x, rect.bottom - 4, rect.width, 4))
                # 像素装饰点
                for i in range(0, rect.width, 20):
                    pygame.draw.rect(surface, (200, 190, 180), (rect.x + i + 5, rect.y + 8, 3, 3))
    
    def _draw_bookshelf(self, surface, shelf):
        """绘制书架"""
        x, y = shelf['x'], shelf['y']
        w, h = shelf['width'], shelf['height']
        
        # 阴影
        if PERSPECTIVE['enabled']:
            shadow_surface = pygame.Surface((w + 4, h + 2), pygame.SRCALPHA)
            pygame.draw.rect(shadow_surface, (0, 0, 0, PERSPECTIVE['shadow_alpha']), (2, 2, w, h))
            surface.blit(shadow_surface, (x - w // 2 + PERSPECTIVE['shadow_offset'], y - h // 2 + PERSPECTIVE['shadow_offset']))
        
        # 书架主体
        shelf_rect = pygame.Rect(x - w // 2, y - h // 2, w, h)
        pygame.draw.rect(surface, COLORS['bookshelf'], shelf_rect, border_radius=2)
        pygame.draw.rect(surface, (100, 80, 60), shelf_rect, 2, border_radius=2)
        
        # 书架隔板
        for i in range(1, 4):
            line_y = shelf_rect.y + i * (h // 4)
            pygame.draw.line(surface, (100, 80, 60), (shelf_rect.x + 3, line_y), (shelf_rect.right - 3, line_y), 2)
        
        # 书籍
        book_colors = COLORS['books']
        for row in range(4):
            row_y = shelf_rect.y + row * (h // 4) + 3
            for col in range(6):
                if random.random() > 0.3:
                    book_x = shelf_rect.x + 4 + col * 9
                    book_w = 7
                    book_h = h // 4 - 6
                    color = book_colors[col % len(book_colors)]
                    pygame.draw.rect(surface, color, (book_x, row_y, book_w, book_h), border_radius=1)
                    pygame.draw.rect(surface, (60, 60, 60), (book_x, row_y, book_w, book_h), 1, border_radius=1)
    
    def _draw_printer(self, surface, printer):
        """绘制打印机"""
        x, y = printer['x'], printer['y']
        w, h = printer['width'], printer['height']
        
        # 阴影
        if PERSPECTIVE['enabled']:
            shadow_surface = pygame.Surface((w + 4, h // 2), pygame.SRCALPHA)
            pygame.draw.ellipse(shadow_surface, (0, 0, 0, PERSPECTIVE['shadow_alpha']), (0, 0, w + 4, h // 2))
            surface.blit(shadow_surface, (x - w // 2 + 2, y + 3))
        
        # 打印机主体
        printer_rect = pygame.Rect(x - w // 2, y - h // 2, w, h)
        pygame.draw.rect(surface, COLORS['printer'], printer_rect, border_radius=3)
        pygame.draw.rect(surface, (140, 140, 145), printer_rect, 2, border_radius=3)
        
        # 出纸口
        pygame.draw.rect(surface, (80, 80, 85), (x - w // 2 + 3, y - 3, w - 6, 6))
        
        # 指示灯
        pygame.draw.circle(surface, (50, 200, 50), (x + w // 2 - 6, y - h // 2 + 6), 3)
        
        # 纸张
        paper_rect = pygame.Rect(x - 4, y + 3, 8, 12)
        pygame.draw.rect(surface, (250, 250, 245), paper_rect)
        pygame.draw.rect(surface, (200, 200, 195), paper_rect, 1)
    
    def _draw_filing_cabinet(self, surface, cabinet):
        """绘制文件柜"""
        x, y = cabinet['x'], cabinet['y']
        w, h = cabinet['width'], cabinet['height']
        
        # 阴影
        if PERSPECTIVE['enabled']:
            shadow_surface = pygame.Surface((w + 4, h // 2), pygame.SRCALPHA)
            pygame.draw.ellipse(shadow_surface, (0, 0, 0, PERSPECTIVE['shadow_alpha']), (0, 0, w + 4, h // 2))
            surface.blit(shadow_surface, (x - w // 2 + 2, y + h // 2 - 3))
        
        # 柜体
        cabinet_rect = pygame.Rect(x - w // 2, y - h // 2, w, h)
        pygame.draw.rect(surface, COLORS['filing_cabinet'], cabinet_rect, border_radius=2)
        pygame.draw.rect(surface, (90, 100, 110), cabinet_rect, 2, border_radius=2)
        
        # 抽屉
        drawer_h = h // 4
        for i in range(4):
            drawer_y = cabinet_rect.y + i * drawer_h
            pygame.draw.rect(surface, (130, 140, 150), (cabinet_rect.x + 2, drawer_y + 2, w - 4, drawer_h - 4), border_radius=1)
            # 把手
            pygame.draw.rect(surface, (80, 80, 85), (x - 4, drawer_y + drawer_h // 2 - 2, 8, 4), border_radius=1)
    
    def _draw_whiteboard(self, surface, whiteboard):
        """绘制白板"""
        x, y = whiteboard['x'], whiteboard['y']
        w, h = whiteboard['width'], whiteboard['height']
        
        # 白板主体
        board_rect = pygame.Rect(x - w // 2, y - h // 2, w, h)
        pygame.draw.rect(surface, COLORS['whiteboard'], board_rect, border_radius=2)
        pygame.draw.rect(surface, (180, 180, 175), board_rect, 3, border_radius=2)
        
        # 支架
        pygame.draw.line(surface, (150, 150, 145), (x - w // 2 + 5, y + h // 2), (x - w // 2 + 5, y + h // 2 + 15), 3)
        pygame.draw.line(surface, (150, 150, 145), (x + w // 2 - 5, y + h // 2), (x + w // 2 - 5, y + h // 2 + 15), 3)
        
        # 一些涂鸦
        pygame.draw.line(surface, (200, 100, 100), (x - 15, y - 2), (x + 10, y - 2), 2)
        pygame.draw.line(surface, (100, 150, 200), (x - 10, y + 2), (x + 15, y + 2), 2)
        pygame.draw.circle(surface, (100, 200, 100), (x, y), 5, 1)
    
    def _draw_potted_plant(self, surface, plant):
        """绘制盆栽"""
        x, y = plant['x'], plant['y']
        size = plant['size']
        
        # 阴影
        if PERSPECTIVE['enabled']:
            shadow_surface = pygame.Surface((size, size // 2), pygame.SRCALPHA)
            pygame.draw.ellipse(shadow_surface, (0, 0, 0, PERSPECTIVE['shadow_alpha']), (0, 0, size, size // 2))
            surface.blit(shadow_surface, (x - size // 2 + 2, y + 3))
        
        # 花盆
        pot_h = size // 2
        pot_rect = pygame.Rect(x - size // 3, y, size // 1.5, pot_h)
        pygame.draw.rect(surface, (190, 140, 100), pot_rect, border_radius=2)
        pygame.draw.rect(surface, (140, 100, 70), pot_rect, 1, border_radius=2)
        
        # 植物
        leaf_color = COLORS['potted_plant']
        leaf_dark = (60, 110, 50)
        
        leaf_positions = [
            (x, y - size // 2, size // 2),
            (x - size // 3, y - size // 3, size // 3),
            (x + size // 3, y - size // 3, size // 3),
        ]
        
        for lx, ly, lsize in leaf_positions:
            points = [
                (lx, ly - lsize),
                (lx - lsize // 2, ly),
                (lx, ly + lsize // 3),
                (lx + lsize // 2, ly),
            ]
            pygame.draw.polygon(surface, leaf_color, points)
            pygame.draw.polygon(surface, leaf_dark, points, 1)
    
    def _draw_clock(self, surface, clock):
        """绘制时钟"""
        x, y = clock['x'], clock['y']
        r = clock['radius']
        
        # 时钟主体
        pygame.draw.circle(surface, COLORS['clock'], (x, y), r)
        pygame.draw.circle(surface, (160, 140, 120), (x, y), r, 2)
        
        # 刻度
        for i in range(12):
            angle = i * 30
            rad = math.radians(angle)
            x1 = x + (r - 3) * math.cos(rad)
            y1 = y + (r - 3) * math.sin(rad)
            x2 = x + (r - 1) * math.cos(rad)
            y2 = y + (r - 1) * math.sin(rad)
            pygame.draw.line(surface, (80, 80, 80), (x1, y1), (x2, y2), 1)
        
        # 指针
        import time
        t = time.time()
        hour_angle = (t / 3600) % 360
        min_angle = (t / 60) % 360
        
        # 时针
        rad_h = math.radians(hour_angle - 90)
        pygame.draw.line(surface, (60, 60, 60), (x, y), 
                        (x + r // 2 * math.cos(rad_h), y + r // 2 * math.sin(rad_h)), 2)
        
        # 分针
        rad_m = math.radians(min_angle - 90)
        pygame.draw.line(surface, (80, 80, 80), (x, y),
                        (x + (r - 3) * math.cos(rad_m), y + (r - 3) * math.sin(rad_m)), 1)
        
        # 中心点
        pygame.draw.circle(surface, (100, 80, 60), (x, y), 2)
    
    def _draw_lamp(self, surface, lamp):
        """绘制台灯"""
        x, y = lamp['x'], lamp['y']
        
        # 底座
        pygame.draw.ellipse(surface, (80, 80, 85), (x - 6, y + 2, 12, 6))
        
        # 灯杆
        pygame.draw.line(surface, (100, 100, 105), (x, y + 2), (x - 3, y - 10), 2)
        pygame.draw.line(surface, (100, 100, 105), (x - 3, y - 10), (x + 2, y - 15), 2)
        
        # 灯罩
        shade_points = [
            (x + 2, y - 15),
            (x - 6, y - 8),
            (x + 8, y - 8),
        ]
        pygame.draw.polygon(surface, COLORS['lamp'], shade_points)
        pygame.draw.polygon(surface, (180, 160, 130), shade_points, 1)
        
        # 光晕
        glow_surface = pygame.Surface((20, 15), pygame.SRCALPHA)
        pygame.draw.ellipse(glow_surface, (255, 250, 200, 40), (0, 0, 20, 15))
        surface.blit(glow_surface, (x - 10, y - 5))
    
    def _draw_desk(self, surface, desk):
        """绘制办公桌 - 像素风格"""
        x, y = desk['x'], desk['y']
        w, h = desk['width'], desk['height']
        
        if PERSPECTIVE['enabled']:
            shadow_surface = pygame.Surface((w + 8, h + 6), pygame.SRCALPHA)
            pygame.draw.rect(shadow_surface, (0, 0, 0, PERSPECTIVE['shadow_alpha']), (3, 3, w, h))
            surface.blit(shadow_surface, (x - w // 2 + PERSPECTIVE['shadow_offset'], y - h // 2 + PERSPECTIVE['shadow_offset']))
        
        # 桌子主体 - 像素风格
        desk_rect = pygame.Rect(x - w // 2, y - h // 2, w, h)
        pygame.draw.rect(surface, COLORS['desk'], desk_rect)
        # 粗边框
        pygame.draw.rect(surface, COLORS['desk_dark'], desk_rect, 3)
        
        # 像素风格高光
        pygame.draw.rect(surface, (220, 190, 150), (x - w // 2 + 4, y - h // 2 + 4, w - 8, 8))
        # 像素装饰
        pygame.draw.rect(surface, COLORS['desk_dark'], (x - w // 2 + 8, y - h // 2 + 8, 4, 4))
        pygame.draw.rect(surface, COLORS['desk_dark'], (x + w // 2 - 12, y - h // 2 + 8, 4, 4))
        
        # 桌腿 - 像素风格
        leg_w, leg_h = 6, 14
        pygame.draw.rect(surface, COLORS['desk_dark'], (x - w // 2 + 5, y + h // 2 - 2, leg_w, leg_h))
        pygame.draw.rect(surface, COLORS['desk_dark'], (x + w // 2 - 5 - leg_w, y + h // 2 - 2, leg_w, leg_h))
        # 腿部高光
        pygame.draw.rect(surface, (200, 170, 130), (x - w // 2 + 7, y + h // 2, 2, 10))
        pygame.draw.rect(surface, (200, 170, 130), (x + w // 2 - 3 - leg_w, y + h // 2, 2, 10))
    
    def _draw_computer(self, surface, computer):
        """绘制电脑 - 像素风格"""
        x, y = computer['x'], computer['y']
        w, h = computer['width'], computer['height']
        
        # 底座 - 像素风格
        base_w, base_h = 16, 5
        pygame.draw.rect(surface, COLORS['computer_frame'], (x - base_w // 2, y + h // 2 - base_h, base_w, base_h))
        pygame.draw.rect(surface, (60, 60, 70), (x - base_w // 2, y + h // 2 - base_h, base_w, base_h), 2)
        # 支架
        pygame.draw.rect(surface, COLORS['computer_frame'], (x - 3, y, 6, h // 2))
        pygame.draw.rect(surface, (60, 60, 70), (x - 3, y, 6, h // 2), 1)
        
        # 屏幕外框 - 像素风格
        screen_rect = pygame.Rect(x - w // 2, y - h // 2, w, h)
        pygame.draw.rect(surface, COLORS['computer_frame'], screen_rect)
        pygame.draw.rect(surface, (50, 50, 60), screen_rect, 3)
        
        # 屏幕内框
        inner_rect = pygame.Rect(x - w // 2 + 4, y - h // 2 + 4, w - 8, h - 8)
        
        if computer['on']:
            # 发光效果
            glow_intensity = int(40 + 30 * math.sin(computer['glow_phase']))
            screen_color = (
                min(255, COLORS['computer_screen_on'][0] + glow_intensity // 2),
                min(255, COLORS['computer_screen_on'][1] + glow_intensity // 2),
                min(255, COLORS['computer_screen_on'][2] + glow_intensity // 2)
            )
            pygame.draw.rect(surface, screen_color, inner_rect)
            
            # 像素风格光晕
            glow_surface = pygame.Surface((w + 10, h + 10), pygame.SRCALPHA)
            glow_color = (*COLORS['computer_glow'][:3], glow_intensity)
            pygame.draw.rect(glow_surface, glow_color, (0, 0, w + 10, h + 10))
            surface.blit(glow_surface, (x - w // 2 - 5, y - h // 2 - 5))
            
            # 像素风格代码行
            line_color = (200, 255, 255)
            for i in range(3):
                line_y = inner_rect.y + 5 + i * 7
                line_width = random.randint(8, w - 12)
                pygame.draw.rect(surface, line_color, (inner_rect.x + 3, line_y, line_width, 3))
            # 光标
            cursor_x = inner_rect.x + 3 + random.randint(0, w - 16)
            cursor_y = inner_rect.y + h - 12
            pygame.draw.rect(surface, (255, 255, 255), (cursor_x, cursor_y, 4, 6))
        else:
            pygame.draw.rect(surface, COLORS['computer_screen_off'], inner_rect)
            # 关闭状态的X
            pygame.draw.line(surface, (80, 80, 90), (inner_rect.x + 8, inner_rect.y + 8), (inner_rect.right - 8, inner_rect.bottom - 8), 2)
            pygame.draw.line(surface, (80, 80, 90), (inner_rect.right - 8, inner_rect.y + 8), (inner_rect.x + 8, inner_rect.bottom - 8), 2)
    
    def _draw_chair(self, surface, desk):
        """绘制椅子 - 像素风格"""
        x = desk['x']
        y = desk['y'] + 25
        
        chair_w, chair_h = 24, 28
        
        if PERSPECTIVE['enabled']:
            shadow_surface = pygame.Surface((chair_w + 4, chair_h // 2 + 2), pygame.SRCALPHA)
            pygame.draw.rect(shadow_surface, (0, 0, 0, PERSPECTIVE['shadow_alpha']), (2, 2, chair_w, chair_h // 2))
            surface.blit(shadow_surface, (x - chair_w // 2 + 3, y + 5))
        
        # 椅背 - 像素风格
        back_rect = pygame.Rect(x - chair_w // 2, y - chair_h // 2, chair_w, chair_h - 6)
        pygame.draw.rect(surface, COLORS['chair'], back_rect)
        pygame.draw.rect(surface, (80, 65, 55), back_rect, 2)
        # 椅背高光
        pygame.draw.rect(surface, (160, 130, 100), (x - chair_w // 2 + 4, y - chair_h // 2 + 4, 4, chair_h - 14))
        
        # 椅座 - 像素风格
        seat_rect = pygame.Rect(x - chair_w // 2, y + 2, chair_w, 10)
        pygame.draw.rect(surface, (130, 105, 85), seat_rect)
        pygame.draw.rect(surface, (100, 80, 65), seat_rect, 2)
        # 椅座高光
        pygame.draw.rect(surface, (150, 125, 100), (x - chair_w // 2 + 3, y + 4, chair_w - 6, 3))
        
        # 椅腿 - 像素风格
        leg_color = (70, 60, 50)
        pygame.draw.rect(surface, leg_color, (x - chair_w // 2 + 4, y + 12, 4, 10))
        pygame.draw.rect(surface, leg_color, (x + chair_w // 2 - 8, y + 12, 4, 10))
        # 腿部高光
        pygame.draw.rect(surface, (100, 85, 75), (x - chair_w // 2 + 5, y + 14, 2, 6))
        pygame.draw.rect(surface, (100, 85, 75), (x + chair_w // 2 - 7, y + 14, 2, 6))
    
    def get_desk_position(self, desk_id):
        if 0 <= desk_id < len(self.desks):
            desk = self.desks[desk_id]
            return (desk['x'], desk['y'] + 25)
        return None
