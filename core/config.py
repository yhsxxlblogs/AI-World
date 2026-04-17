# AI World - 游戏配置文件
# 2D俯视视角AI公司模拟游戏

import pygame
import os

# 窗口设置
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 800
FPS = 60
TITLE = "AI World - AI公司模拟器"

# 字体配置 - 像素风字体
FONTS = {
    'pixel': os.path.join('fonts', 'HYPixel11pxU-2.ttf'),
}

def get_font(size, font_type='pixel'):
    """获取字体，支持外部字体文件，失败时回退到系统字体"""
    font_path = FONTS.get(font_type, FONTS['pixel'])
    try:
        if os.path.exists(font_path):
            return pygame.font.Font(font_path, size)
    except Exception as e:
        print(f"[字体] 加载外部字体失败: {e}")
    
    # 回退到系统字体
    try:
        return pygame.font.SysFont('microsoftyahei', size)
    except:
        return pygame.font.SysFont('simhei', size)

# 版本信息
VERSION = "1.1.0"
BUILD_DATE = "2026-04-08"

# 网格设置 - 统一网格大小
GRID_SIZE = 40

# 颜色定义 - 卡通像素风格
COLORS = {
    # 地板颜色 - 卡通像素风格 (明亮饱和)
    'floor_base': (210, 180, 140),
    'floor_light': (235, 205, 165),
    'floor_dark': (185, 155, 115),
    'floor_accent': (200, 170, 130),
    'floor_border': (160, 130, 95),
    'floor_grid_line': (175, 145, 110),
    
    # 墙壁颜色 - 卡通风格
    'wall': (255, 245, 230),
    'wall_shadow': (220, 210, 195),
    'wall_trim': (200, 185, 165),
    'wall_outer': (180, 165, 150),
    
    # 工作区颜色 - 卡通高饱和
    'desk': (200, 160, 110),
    'desk_dark': (170, 130, 85),
    'chair': (140, 100, 70),
    'computer_frame': (80, 80, 90),
    'computer_screen_off': (50, 50, 60),
    'computer_screen_on': (100, 230, 255),
    'computer_glow': (120, 240, 255, 150),
    'bookshelf': (180, 140, 100),
    'printer': (220, 220, 225),
    'filing_cabinet': (160, 170, 180),
    'whiteboard': (255, 255, 250),
    'potted_plant': (120, 180, 100),
    'clock': (240, 220, 180),
    'lamp': (255, 235, 180),
    
    # 娱乐区颜色 - 卡通鲜艳
    'sofa': (180, 120, 90),
    'sofa_dark': (150, 95, 70),
    'coffee_table': (180, 140, 105),
    'plant_green': (100, 180, 85),
    'plant_dark': (70, 140, 60),
    'arcade_machine': (230, 90, 120),
    'arcade_screen': (100, 255, 150),
    'water_cooler': (240, 240, 245),
    'tv': (70, 70, 80),
    'tv_screen': (180, 220, 255),
    'pingpong_table': (80, 160, 100),
    'vending_machine': (130, 190, 240),
    'rug': (200, 160, 120),
    'books': [(255, 100, 100), (100, 200, 255), (255, 230, 80), (200, 100, 220)],
    
    # AI员工颜色 - 卡通风格
    'skin': (255, 200, 150),
    'skin_shadow': (235, 175, 125),
    'shirt_blue': (100, 160, 230),
    'shirt_red': (230, 100, 100),
    'shirt_green': (100, 200, 100),
    'shirt_yellow': (255, 220, 80),
    'shirt_purple': (190, 120, 220),
    'shirt_cyan': (100, 200, 220),
    'pants': (90, 90, 110),
    'pants_light': (110, 110, 130),
    'hair_black': (60, 60, 70),
    'hair_brown': (140, 100, 70),
    'hair_blonde': (255, 220, 120),
    'eye_white': (255, 255, 255),
    'eye_black': (50, 50, 60),
    'shoes': (80, 60, 50),
    
    # UI颜色
    'ui_bg': (50, 45, 40),
    'ui_border': (120, 110, 100),
    'ui_text': (255, 250, 240),
    'ui_highlight': (255, 200, 100),
    'ui_button': (100, 90, 85),
    'ui_button_hover': (140, 130, 120),
    
    # 特效颜色
    'shadow': (0, 0, 0, 80),
    'glow': (255, 255, 200, 60),
    'selection': (255, 220, 100, 150),
    
    # 通道颜色
    'corridor': (190, 170, 140),
}

# 区域设置
AREAS = {
    'work': {
        'x': 60,
        'y': 60,
        'width': 520,
        'height': 600,
        'name': '工作区',
        'color': (158, 140, 118),
    },
    'corridor': {
        'x': 580,
        'y': 260,
        'width': 80,
        'height': 200,
        'name': '通道',
        'color': (140, 125, 108),
    },
    'entertainment': {
        'x': 660,
        'y': 60,
        'width': 480,
        'height': 600,
        'name': '娱乐区',
        'color': (148, 135, 115),
    },
}

# 墙体设置
WALLS = {
    'thickness': 16,
    'color': (220, 210, 195),
    'shadow_color': (160, 150, 138),
    'outer_color': (180, 170, 155),
}

# 工作区布局
WORK_ZONE = {
    'desk_rows': 2,
    'desk_cols': 3,
    'desk_width': 100,
    'desk_height': 60,
    'desk_spacing_x': 140,
    'desk_spacing_y': 180,
    'desk_start_x': 90,
    'desk_start_y': 110,
    'computer_width': 40,
    'computer_height': 30,
}

# AI员工设置
EMPLOYEE = {
    'size': 20,
    'speed': 1.5,
    'work_time': 6000,
    'rest_time': 4000,
    'walk_anim_speed': 300,
}

# 寻路设置
PATHFINDING = {
    'grid_size': 20,
    'diagonal': False,
}

# 3D效果设置
PERSPECTIVE = {
    'enabled': True,
    'shadow_offset': 5,
    'shadow_alpha': 50,
    'height_offset': 4,
}
