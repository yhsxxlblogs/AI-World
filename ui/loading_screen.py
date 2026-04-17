# 启动界面 - 游戏启动时的加载和配置界面
import pygame
import os
import json
import time
import threading
import math
from typing import Dict, List, Optional, Callable
from core.config import get_font
from core.constants import (
    SAVE_DIR, CONFIG_FILE, DEFAULT_EMPLOYEE_NAMES, PRECONFIGURED_EMPLOYEE_IDS,
    EMPLOYEE_MODEL_ASSIGNMENTS, BAILIAN_API_URL, BAILIAN_API_KEY
)


# 加载语录 - 加载界面显示
LOADING_QUOTE = "不应一生忙碌喂养终将衰老的躯体，而忽视相伴至死的灵魂"

# 启动页面语录 - 标题和按钮之间漂浮显示
MENU_QUOTES = [
    "不应一生忙碌喂养终将衰老的躯体，而忽视相伴至死的灵魂",
    "在代码的世界里寻找诗意",
    "让AI成为灵魂的延伸",
    "工作是为了生活，而不是生活为了工作",
    "每一个bug都是成长的契机",
    "技术与艺术在此交融",
    "理性与感性在此平衡",
    "探索无限可能，创造非凡价值",
]


class APIConfig:
    """API配置数据类"""
    def __init__(self, employee_id: int, name: str = "", api_url: str = "", api_key: str = "", model_name: str = ""):
        self.employee_id = employee_id
        self.name = name
        self.api_url = api_url
        self.api_key = api_key
        self.model_name = model_name
    
    def to_dict(self) -> dict:
        return {
            'employee_id': self.employee_id,
            'name': self.name,
            'api_url': self.api_url,
            'api_key': self.api_key,
            'model_name': self.model_name
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'APIConfig':
        return cls(
            employee_id=data.get('employee_id', 0),
            name=data.get('name', ''),
            api_url=data.get('api_url', ''),
            api_key=data.get('api_key', ''),
            model_name=data.get('model_name', '')
        )
    
    def is_configured(self) -> bool:
        return bool(self.api_url and self.api_key and self.model_name)


class ConfigManager:
    """配置管理器 - 保存和加载API配置"""
    
    SAVE_DIR = SAVE_DIR
    CONFIG_FILE = CONFIG_FILE
    
    @staticmethod
    def ensure_save_dir():
        """确保保存目录存在"""
        if not os.path.exists(ConfigManager.SAVE_DIR):
            os.makedirs(ConfigManager.SAVE_DIR)
            print(f"[配置管理] 创建保存目录: {ConfigManager.SAVE_DIR}")
    
    @staticmethod
    def save_configs(configs: List[APIConfig]):
        """保存API配置到文件"""
        ConfigManager.ensure_save_dir()
        filepath = os.path.join(ConfigManager.SAVE_DIR, ConfigManager.CONFIG_FILE)
        
        data = {'configs': [config.to_dict() for config in configs]}
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        print(f"[配置管理] 已保存 {len(configs)} 个API配置到 {filepath}")
    
    @staticmethod
    def load_configs() -> List[APIConfig]:
        """从文件加载API配置"""
        filepath = os.path.join(ConfigManager.SAVE_DIR, ConfigManager.CONFIG_FILE)
        
        if not os.path.exists(filepath):
            print(f"[配置管理] 配置文件不存在，使用默认配置")
            return ConfigManager.get_default_configs()
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            configs = [APIConfig.from_dict(cfg) for cfg in data.get('configs', [])]
            print(f"[配置管理] 已加载 {len(configs)} 个API配置")
            return configs
        except Exception as e:
            print(f"[配置管理] 加载配置失败: {e}")
            return ConfigManager.get_default_configs()
    
    @staticmethod
    def get_default_configs() -> List[APIConfig]:
        """获取默认API配置（为所有员工配置最优模型）"""
        configs = []

        # 为所有员工创建配置（基于EMPLOYEE_MODEL_ASSIGNMENTS）
        for emp_id in range(len(DEFAULT_EMPLOYEE_NAMES)):
            if emp_id in EMPLOYEE_MODEL_ASSIGNMENTS:
                # 使用预设的最优模型配置
                model_config = EMPLOYEE_MODEL_ASSIGNMENTS[emp_id]
                configs.append(APIConfig(
                    employee_id=emp_id,
                    name=DEFAULT_EMPLOYEE_NAMES[emp_id],
                    api_url=model_config["api_url"],
                    api_key=model_config["api_key"],
                    model_name=model_config["model"]
                ))
            else:
                # 使用默认配置
                configs.append(APIConfig(
                    employee_id=emp_id,
                    name=DEFAULT_EMPLOYEE_NAMES[emp_id],
                    api_url=BAILIAN_API_URL,
                    api_key=BAILIAN_API_KEY,
                    model_name="qwen-plus"
                ))

        return configs


class LoadingScreen:
    """启动界面 - 游戏启动时的加载和配置界面"""
    
    def __init__(self, screen_width: int, screen_height: int):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.state = "MENU"  # MENU, LOADING, CONFIG, ERROR
        
        # 字体 - 像素风字体
        self.font_title = get_font(100)  # 标题更大
        self.font_subtitle = get_font(28)  # 副标题也变大
        self.font_large = get_font(32)
        self.font_medium = get_font(22)
        self.font_small = get_font(16)
        self.font_tiny = get_font(13)
        self.font_quote = get_font(22)  # 语录字体更大
        
        # 加载配置
        self.api_configs = ConfigManager.load_configs()
        self.selected_employee = 0
        
        # 加载状态
        self.loading_progress = 0
        self.loading_status = ""
        self.loading_errors = []
        self.loading_complete = False
        self.loading_start_time = 0
        self.target_progress = 0  # 目标进度，用于平滑动画
        
        # 语录显示 - 单条语录随进度漂浮
        self.quote_alpha = 0  # 语录透明度
        self.quote_float_offset = 0  # 语录漂浮偏移
        
        # 菜单语录显示
        self.menu_quote_index = 0
        self.menu_quote_timer = 0
        self.menu_quote_alpha = 0
        
        # 配置界面状态
        self.config_scroll_y = 0
        self.input_focus = None
        self.temp_config = None
        
        # 动画
        self.animation_time = 0
        self.particles = []  # 背景粒子
        self._init_particles()
        
        # 按钮定义
        self._init_buttons()
    
    def _init_particles(self):
        """初始化动态几何线形"""
        import random
        self.geo_lines = []
        for _ in range(15):
            self.geo_lines.append({
                'x1': random.randint(0, self.screen_width),
                'y1': random.randint(0, self.screen_height),
                'x2': random.randint(0, self.screen_width),
                'y2': random.randint(0, self.screen_height),
                'vx1': random.uniform(-0.8, 0.8),
                'vy1': random.uniform(-0.8, 0.8),
                'vx2': random.uniform(-0.8, 0.8),
                'vy2': random.uniform(-0.8, 0.8),
                'alpha': random.randint(20, 50)
            })
        
        # 添加几何节点
        self.geo_nodes = []
        for _ in range(8):
            self.geo_nodes.append({
                'x': random.randint(100, self.screen_width - 100),
                'y': random.randint(100, self.screen_height - 100),
                'vx': random.uniform(-0.5, 0.5),
                'vy': random.uniform(-0.5, 0.5),
                'size': random.randint(2, 4)
            })
    
    def _init_buttons(self):
        """初始化按钮 - 更暗的色系风格"""
        center_x = self.screen_width // 2
        base_y = self.screen_height // 2 + 80
        
        self.menu_buttons = {
            'load_game': {
                'rect': pygame.Rect(center_x - 160, base_y, 320, 55),
                'text': "开始游戏",
                'color': (35, 38, 42),  # 更深的灰蓝
                'hover_color': (50, 55, 62),
                'text_color': (160, 158, 155),
                'border_color': (55, 58, 65)
            },
            'config_api': {
                'rect': pygame.Rect(center_x - 160, base_y + 75, 320, 55),
                'text': "配置API",
                'color': (32, 35, 40),  # 更深的灰
                'hover_color': (48, 52, 58),
                'text_color': (155, 153, 150),
                'border_color': (52, 55, 62)
            },
            'exit': {
                'rect': pygame.Rect(center_x - 160, base_y + 150, 320, 55),
                'text': "退出游戏",
                'color': (38, 32, 32),  # 更深的暗红灰
                'hover_color': (55, 45, 45),
                'text_color': (165, 155, 155),
                'border_color': (65, 55, 55)
            }
        }
        
        # 配置界面按钮
        self.config_buttons = {
            'save': {
                'rect': pygame.Rect(self.screen_width - 340, self.screen_height - 90, 150, 50),
                'text': "保存配置",
                'color': (70, 140, 100),
                'hover_color': (90, 170, 120)
            },
            'back': {
                'rect': pygame.Rect(self.screen_width - 180, self.screen_height - 90, 150, 50),
                'text': "[返回]",
                'color': (120, 110, 90),
                'hover_color': (150, 140, 110)
            }
        }
    
    def start_loading(self):
        """开始加载游戏"""
        self.state = "LOADING"
        self.loading_progress = 0
        self.target_progress = 0
        self.loading_status = "正在初始化..."
        self.loading_errors = []
        self.loading_complete = False
        self.loading_start_time = time.time()
        
        # 重置语录显示
        self.current_quote_index = 0
        self.quote_display_progress = 0
        self.quote_alpha = 0
        
        # 在后台线程执行加载
        thread = threading.Thread(target=self._loading_thread)
        thread.daemon = True
        thread.start()
    
    def _loading_thread(self):
        """加载线程 - 真实资源加载"""
        try:
            # 阶段1: 预加载游戏资源 (0-30%)
            self.loading_status = "正在预加载游戏资源..."
            self._preload_game_resources()
            self.target_progress = 30
            time.sleep(0.3)
            
            # 阶段2: 加载字体和UI资源 (30-50%)
            self.loading_status = "正在加载字体和UI资源..."
            self._preload_fonts_and_ui()
            self.target_progress = 50
            time.sleep(0.3)
            
            # 阶段3: 检测API连接 (50-70%)
            self.loading_status = "正在检测API连接..."
            self._check_api_connections()
            self.target_progress = 70
            time.sleep(0.3)
            
            # 阶段4: 加载员工数据和语录 (70-90%)
            self.loading_status = "正在加载员工数据..."
            self._load_employee_data()
            self.target_progress = 90
            time.sleep(0.3)
            
            # 阶段5: 最终初始化和内存优化 (90-100%)
            self.loading_status = "正在完成初始化..."
            self._finalize_loading()
            self.target_progress = 100
            time.sleep(0.3)
            
            self.loading_complete = True
            self.loading_status = "加载完成！"
            
        except Exception as e:
            self.loading_errors.append(str(e))
            self.loading_status = f"加载出错: {e}"
    
    def _preload_game_resources(self):
        """预加载游戏资源 - 完整性检查和自动修复"""
        try:
            import os
            
            # 检查并创建必要的目录
            self.loading_status = "正在检查目录结构..."
            dirs_to_check = ['save', 'results', 'skill']
            for dir_name in dirs_to_check:
                if not os.path.exists(dir_name):
                    os.makedirs(dir_name)
                    print(f"[资源加载] 创建缺失目录: {dir_name}")
                else:
                    print(f"[资源加载] 目录检查通过: {dir_name}")
            
            # 检查核心Python文件 - 更新为新的目录结构
            self.loading_status = "正在检查核心文件..."
            core_files = [
                'main.py',
                'core/config.py', 'core/ai_employee.py', 'core/pathfinding.py',
                'ai_systems/cloud_ai_client.py', 'ai_systems/employee_ai_worker.py',
                'ui/workflow_system.py',
                'utils/result_manager.py', 'utils/content_formatter.py'
            ]
            missing_files = []
            for file_name in core_files:
                if not os.path.exists(file_name):
                    missing_files.append(file_name)
                    print(f"[资源加载] 警告: 缺失核心文件 {file_name}")
            
            if missing_files:
                self.loading_errors.append(f"缺失 {len(missing_files)} 个核心文件，游戏可能无法正常运行")
            else:
                print("[资源加载] 核心文件检查通过")
            
            # 检查并创建默认技能文件
            self.loading_status = "正在检查技能文件..."
            skill_files = []
            for i in range(6):
                skill_path = f'skill/skill{i}.md'
                if not os.path.exists(skill_path):
                    # 创建默认技能文件
                    self._create_default_skill_file(i, skill_path)
                    print(f"[资源加载] 创建默认技能文件: {skill_path}")
                else:
                    try:
                        with open(skill_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                            skill_files.append((i, len(content)))
                    except Exception as e:
                        print(f"[资源加载] 技能文件{i}读取失败: {e}")
            
            if skill_files:
                print(f"[资源加载] 已加载 {len(skill_files)} 个技能文件")
            
            # 检查字体可用性
            self.loading_status = "正在检查字体资源..."
            try:
                test_font = pygame.font.SysFont('microsoftyahei', 12)
                print("[资源加载] 字体资源检查通过")
            except Exception as e:
                print(f"[资源加载] 字体检查警告: {e}")
            
            # 检查配置文件
            self.loading_status = "正在检查配置文件..."
            config_path = os.path.join('save', 'api_configs.json')
            if not os.path.exists(config_path):
                print(f"[资源加载] 配置文件不存在，将使用默认配置")
            else:
                print("[资源加载] 配置文件检查通过")
            
        except Exception as e:
            self.loading_errors.append(f"资源预加载失败: {e}")
    
    def _create_default_skill_file(self, employee_id: int, filepath: str):
        """创建默认技能文件"""
        default_names = ['小明', '小红', '阿强', '小丽', '大伟', '晓晓']
        name = default_names[employee_id] if employee_id < len(default_names) else f'员工{employee_id}'
        
        default_content = f"""# {name}的技能配置

## 角色定位
{name}是AI World公司的员工，负责协助完成各类AI任务。

## 技能描述
- 基础AI对话能力
- 任务执行与协作
- 代码生成与优化
- 文档撰写与整理

## 工作风格
专业、高效、协作

---
*此文件由系统自动生成*
"""
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(default_content)
        except Exception as e:
            print(f"[资源加载] 创建技能文件失败: {e}")
    
    def _preload_fonts_and_ui(self):
        """预加载字体和UI资源"""
        try:
            # 预渲染常用字体表面（缓存）
            self.loading_status = "正在缓存字体..."
            
            # 预加载各种字体大小
            font_sizes = [12, 14, 16, 18, 20, 24, 28, 32]
            for size in font_sizes:
                try:
                    font = pygame.font.SysFont('microsoftyahei', size)
                    # 预渲染一个测试字符来初始化字体
                    _ = font.render("测试", True, (255, 255, 255))
                except Exception as e:
                    print(f"[资源加载] 字体大小{size}初始化失败: {e}")
            
            print("[资源加载] 字体缓存完成")
            
        except Exception as e:
            self.loading_errors.append(f"字体加载失败: {e}")
    
    def _load_employee_data(self):
        """加载员工数据"""
        try:
            # 加载员工语录
            self.loading_status = "正在加载员工语录..."
            from core.ai_employee import EMPLOYEE_QUOTES
            quote_count = sum(len(quotes['rest']) + len(quotes['work']) 
                            for quotes in EMPLOYEE_QUOTES.values())
            print(f"[资源加载] 已加载 {len(EMPLOYEE_QUOTES)} 个员工，共 {quote_count} 条语录")
            
            # 加载API配置
            self.loading_status = "正在加载API配置..."
            configured_count = sum(1 for cfg in self.api_configs if cfg.is_configured())
            print(f"[资源加载] 已加载 {len(self.api_configs)} 个API配置，{configured_count} 个已配置")
            
        except Exception as e:
            self.loading_errors.append(f"员工数据加载失败: {e}")
    
    def _finalize_loading(self):
        """完成加载，进行最终初始化"""
        try:
            self.loading_status = "正在优化内存..."
            
            # 强制垃圾回收
            import gc
            gc.collect()
            
            # 检查系统资源
            try:
                import psutil
                process = psutil.Process()
                mem_info = process.memory_info()
                print(f"[资源加载] 内存使用: {mem_info.rss / 1024 / 1024:.1f} MB")
            except ImportError:
                pass
            
            self.loading_status = "正在准备游戏环境..."
            print("[资源加载] 资源预加载完成")
            
        except Exception as e:
            self.loading_errors.append(f"最终初始化失败: {e}")
    
    def _check_api_connections(self):
        """检测API连接"""
        for config in self.api_configs:
            if config.is_configured():
                try:
                    self.loading_status = f"正在检测 {config.name} 的API..."
                    time.sleep(0.15)
                except Exception as e:
                    self.loading_errors.append(f"{config.name} API检测失败: {e}")
    
    def open_config(self):
        """打开配置界面"""
        self.state = "CONFIG"
        self.selected_employee = 0
        self.temp_config = APIConfig.from_dict(self.api_configs[0].to_dict())
        self.config_scroll_y = 0
    
    def save_config(self):
        """保存当前配置"""
        if self.temp_config:
            self.api_configs[self.selected_employee] = self.temp_config
            ConfigManager.save_configs(self.api_configs)
            print(f"[配置] 已保存 {self.temp_config.name} 的API配置")
    
    def handle_event(self, event) -> Optional[str]:
        """处理事件，返回操作结果"""
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                mouse_pos = pygame.mouse.get_pos()
                return self._handle_click(mouse_pos)
        
        elif event.type == pygame.KEYDOWN:
                if self.state == "CONFIG":
                    return self._handle_config_key(event)
                # 加载界面禁用ESC跳过
        
        return None
    
    def _handle_click(self, mouse_pos) -> Optional[str]:
        """处理鼠标点击"""
        if self.state == "MENU":
            for btn_name, btn in self.menu_buttons.items():
                if btn['rect'].collidepoint(mouse_pos):
                    if btn_name == 'load_game':
                        self.start_loading()
                        return None
                    elif btn_name == 'config_api':
                        self.open_config()
                        return None
                    elif btn_name == 'exit':
                        return "EXIT"
        
        elif self.state == "CONFIG":
            # 检查员工选择
            list_x = 60
            list_y = 140
            item_height = 70
            for i, config in enumerate(self.api_configs):
                item_rect = pygame.Rect(list_x, list_y + i * item_height - self.config_scroll_y, 220, 65)
                if item_rect.collidepoint(mouse_pos):
                    self.selected_employee = i
                    self.temp_config = APIConfig.from_dict(self.api_configs[i].to_dict())
                    return None
            
            # 检查按钮
            for btn_name, btn in self.config_buttons.items():
                if btn['rect'].collidepoint(mouse_pos):
                    if btn_name == 'save':
                        self.save_config()
                    elif btn_name == 'back':
                        self.state = "MENU"
                    return None
            
            # 检查输入框
            self._handle_config_input_click(mouse_pos)
        
        return None
    
    def _handle_config_input_click(self, mouse_pos):
        """处理配置界面输入框点击"""
        if not self.temp_config:
            return
        
        input_x = 320
        input_y = 180
        input_width = 450
        input_height = 40
        spacing = 60
        
        # API URL输入框
        url_rect = pygame.Rect(input_x, input_y, input_width, input_height)
        if url_rect.collidepoint(mouse_pos):
            self.input_focus = 'url'
            return
        
        # API Key输入框
        key_rect = pygame.Rect(input_x, input_y + spacing, input_width, input_height)
        if key_rect.collidepoint(mouse_pos):
            self.input_focus = 'key'
            return
        
        # Model输入框
        model_rect = pygame.Rect(input_x, input_y + spacing * 2, input_width, input_height)
        if model_rect.collidepoint(mouse_pos):
            self.input_focus = 'model'
            return
        
        self.input_focus = None
    
    def _handle_config_key(self, event) -> Optional[str]:
        """处理配置界面的键盘输入"""
        if not self.temp_config or not self.input_focus:
            return None
        
        if event.key == pygame.K_BACKSPACE:
            if self.input_focus == 'url':
                self.temp_config.api_url = self.temp_config.api_url[:-1]
            elif self.input_focus == 'key':
                self.temp_config.api_key = self.temp_config.api_key[:-1]
            elif self.input_focus == 'model':
                self.temp_config.model_name = self.temp_config.model_name[:-1]
        
        elif event.key == pygame.K_RETURN or event.key == pygame.K_KP_ENTER:
            self.input_focus = None
        
        elif event.unicode.isprintable():
            if self.input_focus == 'url':
                self.temp_config.api_url += event.unicode
            elif self.input_focus == 'key':
                self.temp_config.api_key += event.unicode
            elif self.input_focus == 'model':
                self.temp_config.model_name += event.unicode
        
        return None
    
    def update(self, dt):
        """更新动画"""
        self.animation_time += dt / 1000.0
        
        # 更新几何线形动画
        self._update_geo_animation()
        
        # 更新菜单语录
        if self.state == "MENU":
            self._update_menu_quote(dt)
        
        # 平滑更新进度条
        if self.state == "LOADING":
            # 进度条平滑动画
            diff = self.target_progress - self.loading_progress
            if abs(diff) > 0.1:
                self.loading_progress += diff * 0.05  # 平滑系数
            
            # 更新语录显示
            self._update_quote_display(dt)
            
            # 检查加载是否完成
            if self.loading_complete and self.loading_progress >= 99:
                elapsed = time.time() - self.loading_start_time
                if elapsed >= 5.0:
                    return "START_GAME"
        
        return None
    
    def _update_menu_quote(self, dt):
        """更新菜单语录动画"""
        # 每5秒切换一次语录
        self.menu_quote_timer += dt / 1000.0
        
        # 淡入淡出效果
        if self.menu_quote_timer < 0.5:  # 前0.5秒淡入
            self.menu_quote_alpha = min(255, int(self.menu_quote_alpha + 10))
        elif self.menu_quote_timer > 4.5:  # 后0.5秒淡出
            self.menu_quote_alpha = max(0, int(self.menu_quote_alpha - 10))
        else:  # 中间保持
            self.menu_quote_alpha = 255
        
        # 切换语录
        if self.menu_quote_timer >= 5.0:
            self.menu_quote_timer = 0
            self.menu_quote_alpha = 0
            self.menu_quote_index = (self.menu_quote_index + 1) % len(MENU_QUOTES)
    
    def _update_quote_display(self, dt):
        """更新语录显示动画 - 单条语录淡入"""
        # 进度超过15%开始淡入
        if self.loading_progress > 15:
            # 淡入动画
            if self.quote_alpha < 255:
                self.quote_alpha = min(255, self.quote_alpha + 2)
        else:
            self.quote_alpha = 0
    
    def draw(self, surface):
        """绘制界面"""
        # 绘制背景
        self._draw_background(surface)
        
        if self.state == "MENU":
            self._draw_menu(surface)
        elif self.state == "LOADING":
            self._draw_loading(surface)
        elif self.state == "CONFIG":
            self._draw_config(surface)
    
    def _draw_background(self, surface):
        """绘制背景 - 神秘的暗色系渐变"""
        # 深色渐变背景 - 更暗的色调
        for y in range(self.screen_height):
            progress = y / self.screen_height
            r = int(12 + 5 * progress)
            g = int(10 + 4 * progress)
            b = int(8 + 3 * progress)
            pygame.draw.line(surface, (r, g, b), (0, y), (self.screen_width, y))
        
        # 绘制动态几何线形
        self._draw_geo_lines(surface)
    
    def _draw_geo_lines(self, surface):
        """绘制动态几何线形 - 神秘专业风格"""
        # 绘制几何线条
        for line in self.geo_lines:
            # 线条颜色 - 暗青色/灰色
            color = (60, 70, 80, line['alpha'])
            pygame.draw.line(surface, color[:3], 
                           (int(line['x1']), int(line['y1'])), 
                           (int(line['x2']), int(line['y2'])), 1)
            
            # 端点
            pygame.draw.circle(surface, (80, 90, 100), (int(line['x1']), int(line['y1'])), 2)
            pygame.draw.circle(surface, (80, 90, 100), (int(line['x2']), int(line['y2'])), 2)
        
        # 绘制节点和连接线
        for i, node in enumerate(self.geo_nodes):
            # 节点
            pygame.draw.circle(surface, (70, 80, 90), 
                             (int(node['x']), int(node['y'])), node['size'])
            pygame.draw.circle(surface, (100, 110, 120), 
                             (int(node['x']), int(node['y'])), node['size'], 1)
            
            # 连接附近的节点
            for j in range(i + 1, len(self.geo_nodes)):
                other = self.geo_nodes[j]
                dist = math.sqrt((node['x'] - other['x'])**2 + (node['y'] - other['y'])**2)
                if dist < 200:  # 距离小于200才连接
                    alpha = int(30 * (1 - dist / 200))
                    pygame.draw.line(surface, (60, 70, 80), 
                                   (int(node['x']), int(node['y'])), 
                                   (int(other['x']), int(other['y'])))
    
    def _update_geo_animation(self):
        """更新几何线形动画"""
        # 更新线条端点位置
        for line in self.geo_lines:
            line['x1'] += line['vx1']
            line['y1'] += line['vy1']
            line['x2'] += line['vx2']
            line['y2'] += line['vy2']
            
            # 边界碰撞检测
            if line['x1'] < 0 or line['x1'] > self.screen_width:
                line['vx1'] *= -1
            if line['y1'] < 0 or line['y1'] > self.screen_height:
                line['vy1'] *= -1
            if line['x2'] < 0 or line['x2'] > self.screen_width:
                line['vx2'] *= -1
            if line['y2'] < 0 or line['y2'] > self.screen_height:
                line['vy2'] *= -1
        
        # 更新节点位置
        for node in self.geo_nodes:
            node['x'] += node['vx']
            node['y'] += node['vy']
            
            # 边界碰撞
            if node['x'] < 50 or node['x'] > self.screen_width - 50:
                node['vx'] *= -1
            if node['y'] < 50 or node['y'] > self.screen_height - 50:
                node['vy'] *= -1
    
    def _draw_menu(self, surface):
        """绘制主菜单 - 简洁专业风格"""
        center_x = self.screen_width // 2
        
        # 绘制装饰性几何图形
        self._draw_decorative_shapes(surface)
        
        # 主标题 - 简洁无发光
        title = self.font_title.render("AI World", True, (160, 155, 145))
        title_x = center_x - title.get_width() // 2
        title_y = 80
        surface.blit(title, (title_x, title_y))
        
        # 副标题 - 根据标题大小调整位置（更大间距避免重叠）
        subtitle = self.font_subtitle.render("AI公司模拟器", True, (120, 115, 110))
        subtitle_x = center_x - subtitle.get_width() // 2
        surface.blit(subtitle, (subtitle_x, title_y + 120))
        
        # 简洁装饰线 - 下移避免重叠
        line_y = title_y + 170
        pygame.draw.line(surface, (70, 68, 65), 
                        (center_x - 100, line_y), 
                        (center_x + 100, line_y), 1)
        
        # 动态漂浮语录 - 标题和按钮之间（位置再往下一点）
        if MENU_QUOTES:
            quote_text = MENU_QUOTES[self.menu_quote_index]
            # 计算漂浮偏移
            float_offset = math.sin(self.animation_time * 0.6) * 3
            
            # 渲染语录 - 带透明度（使用font_quote）
            quote_surface = self.font_quote.render(f'"{quote_text}"', True, (130, 125, 120))
            quote_surface.set_alpha(self.menu_quote_alpha)
            
            # 创建描边效果
            if not hasattr(self, '_menu_quote_outline'):
                self._menu_quote_outline = {}
            
            if self.menu_quote_index not in self._menu_quote_outline:
                outline_color = (35, 33, 30)
                w = quote_surface.get_width() + 4
                h = quote_surface.get_height() + 4
                outline_surf = pygame.Surface((w, h), pygame.SRCALPHA)
                for dx, dy in [(-1, -1), (1, -1), (-1, 1), (1, 1), (0, -1), (0, 1), (-1, 0), (1, 0)]:
                    outline_text = self.font_quote.render(f'"{quote_text}"', True, outline_color)
                    outline_surf.blit(outline_text, (2 + dx, 2 + dy))
                self._menu_quote_outline[self.menu_quote_index] = outline_surf
            
            quote_x = center_x - quote_surface.get_width() // 2
            quote_y = line_y + 60 + float_offset  # 位置再往下
            
            # 绘制描边
            outline = self._menu_quote_outline[self.menu_quote_index].copy()
            outline.set_alpha(self.menu_quote_alpha)
            surface.blit(outline, (quote_x - 2, quote_y - 2))
            
            # 绘制文字
            surface.blit(quote_surface, (quote_x, quote_y))
        
        # 版本号
        version = self.font_tiny.render("v1.1.0", True, (70, 68, 65))
        surface.blit(version, (self.screen_width - 60, self.screen_height - 25))
        
        # 左下角提示
        hint = self.font_tiny.render("选择选项开始游戏", True, (65, 63, 60))
        surface.blit(hint, (30, self.screen_height - 25))
        
        # 绘制按钮
        mouse_pos = pygame.mouse.get_pos()
        for btn_name, btn in self.menu_buttons.items():
            self._draw_elegant_button(surface, btn, mouse_pos)
    
    def _draw_decorative_shapes(self, surface):
        """绘制装饰性几何图形 - 暗色系"""
        w, h = self.screen_width, self.screen_height
        
        # 左上角装饰三角形
        triangle_points = [
            (0, 0),
            (120, 0),
            (0, 120)
        ]
        pygame.draw.polygon(surface, (25, 23, 22), triangle_points)
        pygame.draw.polygon(surface, (45, 42, 40), triangle_points, 1)
        
        # 右下角装饰三角形
        triangle_points2 = [
            (w, h),
            (w - 120, h),
            (w, h - 120)
        ]
        pygame.draw.polygon(surface, (25, 23, 22), triangle_points2)
        pygame.draw.polygon(surface, (45, 42, 40), triangle_points2, 1)
        
        # 角落小方块装饰 - 更暗
        square_size = 6
        positions = [(25, 25), (w - 31, 25), (25, h - 31), (w - 31, h - 31)]
        for pos in positions:
            pygame.draw.rect(surface, (50, 48, 45), (pos[0], pos[1], square_size, square_size))
            pygame.draw.rect(surface, (70, 68, 65), (pos[0], pos[1], square_size, square_size), 1)
    
    def _draw_elegant_button(self, surface, btn, mouse_pos):
        """绘制优雅风格的按钮 - 暗色系"""
        rect = btn['rect']
        is_hover = rect.collidepoint(mouse_pos)
        
        # 按钮颜色
        base_color = btn['hover_color'] if is_hover else btn['color']
        border_color = btn.get('border_color', (80, 80, 80))
        text_color = btn.get('text_color', (200, 200, 200))
        
        # 按钮背景 - 圆角矩形
        pygame.draw.rect(surface, base_color, rect, border_radius=8)
        
        # 边框
        pygame.draw.rect(surface, border_color, rect, width=2, border_radius=8)
        
        # 悬停时的高亮边框
        if is_hover:
            highlight_color = (min(border_color[0] + 30, 255), 
                             min(border_color[1] + 30, 255), 
                             min(border_color[2] + 30, 255))
            pygame.draw.rect(surface, highlight_color, rect, width=3, border_radius=8)
        
        # 按钮文字 - 使用按钮定义的颜色
        text_surface = self.font_medium.render(btn['text'], True, text_color)
        text_x = rect.centerx - text_surface.get_width() // 2
        text_y = rect.centery - text_surface.get_height() // 2
        surface.blit(text_surface, (text_x, text_y))
    
    def _draw_loading(self, surface):
        """绘制加载界面 - 流畅动画风格"""
        center_x = self.screen_width // 2
        center_y = self.screen_height // 2 - 50
        
        # 加载标题
        title = self.font_large.render("正在进入游戏世界", True, (255, 220, 180))
        title_x = center_x - title.get_width() // 2
        surface.blit(title, (title_x, center_y - 80))
        
        # 进度条容器
        bar_width = 500
        bar_height = 12
        bar_x = center_x - bar_width // 2
        bar_y = center_y
        
        # 进度条背景
        pygame.draw.rect(surface, (40, 40, 45), (bar_x, bar_y, bar_width, bar_height), border_radius=6)
        
        # 进度条填充 - 平滑渐变
        fill_width = int(bar_width * self.loading_progress / 100)
        if fill_width > 0:
            # 创建渐变效果
            for i in range(fill_width):
                progress = i / bar_width
                # 金色到橙色的渐变
                r = int(200 + 40 * progress)
                g = int(170 - 30 * progress)
                b = int(100 - 40 * progress)
                pygame.draw.line(surface, (r, g, b), 
                               (bar_x + i, bar_y), 
                               (bar_x + i, bar_y + bar_height - 1))
        
        # 进度条发光边框
        pygame.draw.rect(surface, (200, 180, 140, 100), 
                        (bar_x - 2, bar_y - 2, bar_width + 4, bar_height + 4), 
                        width=2, border_radius=8)
        
        # 进度百分比
        progress_text = self.font_medium.render(f"{int(self.loading_progress)}%", True, (220, 200, 170))
        surface.blit(progress_text, (center_x - progress_text.get_width() // 2, bar_y + 25))
        
        # 状态文字
        status = self.font_small.render(self.loading_status, True, (160, 160, 160))
        surface.blit(status, (center_x - status.get_width() // 2, bar_y + 55))
        
        # 语录显示 - 单条语录随进度漂浮出现
        if self.loading_progress > 15:  # 进度超过15%开始显示
            # 预渲染语录表面（避免每帧重新渲染）
            if not hasattr(self, '_quote_surface'):
                self._quote_surface = self.font_quote.render(f'"{LOADING_QUOTE}"', True, (160, 150, 135))
            
            # 预渲染描边表面
            if not hasattr(self, '_quote_surface_outline'):
                # 创建描边效果 - 使用更深的颜色
                outline_color = (40, 38, 35)
                outline_surface = pygame.Surface((self._quote_surface.get_width() + 4, self._quote_surface.get_height() + 4), pygame.SRCALPHA)
                # 在四个方向绘制描边
                for dx, dy in [(-1, -1), (1, -1), (-1, 1), (1, 1), (0, -1), (0, 1), (-1, 0), (1, 0)]:
                    outline_text = self.font_quote.render(f'"{LOADING_QUOTE}"', True, outline_color)
                    outline_surface.blit(outline_text, (2 + dx, 2 + dy))
                self._quote_surface_outline = outline_surface
            
            # 创建带透明度的副本
            quote_surface = self._quote_surface.copy()
            quote_surface.set_alpha(self.quote_alpha)
            
            # 计算漂浮偏移 - 使用更平滑的动画
            float_y = math.sin(self.animation_time * 0.8) * 4  # 更慢的漂浮速度，更大的幅度
            quote_x = center_x - quote_surface.get_width() // 2
            quote_y = bar_y + 140 + float_y  # 位置再往下一点（从120改为140）
            
            # 先绘制描边
            outline_copy = self._quote_surface_outline.copy()
            outline_copy.set_alpha(self.quote_alpha)
            surface.blit(outline_copy, (quote_x - 2, quote_y - 2))
            
            # 再绘制文字
            surface.blit(quote_surface, (quote_x, quote_y))
        
        # 错误信息
        if self.loading_errors:
            error_y = bar_y + 130
            for error in self.loading_errors[-2:]:
                error_text = self.font_tiny.render(f"[!] {error}", True, (200, 120, 120))
                surface.blit(error_text, (center_x - error_text.get_width() // 2, error_y))
                error_y += 22
        
        # 底部装饰文字
        hint = self.font_tiny.render("AI World - 探索无限可能", True, (80, 80, 80))
        surface.blit(hint, (center_x - hint.get_width() // 2, self.screen_height - 30))
    
    def _draw_config(self, surface):
        """绘制配置界面 - 优雅布局"""
        # 标题栏背景
        header_rect = pygame.Rect(0, 0, self.screen_width, 80)
        pygame.draw.rect(surface, (30, 28, 26), header_rect)
        pygame.draw.line(surface, (80, 70, 60), (0, 80), (self.screen_width, 80), 2)
        
        # 标题
        title = self.font_large.render("[设置] API 配置管理", True, (255, 220, 180))
        surface.blit(title, (60, 25))
        
        # 副标题
        subtitle = self.font_small.render("为每个员工配置独立的AI API", True, (150, 140, 130))
        surface.blit(subtitle, (60, 58))
        
        # 绘制员工列表
        self._draw_employee_list_elegant(surface)
        
        # 绘制配置表单
        self._draw_config_form_elegant(surface)
        
        # 绘制按钮
        mouse_pos = pygame.mouse.get_pos()
        for btn_name, btn in self.config_buttons.items():
            self._draw_elegant_button(surface, btn, mouse_pos)
    
    def _draw_employee_list_elegant(self, surface):
        """绘制优雅风格的员工列表"""
        list_x = 60
        list_y = 120
        item_width = 240
        item_height = 75
        
        # 列表标题
        list_title = self.font_medium.render("选择员工", True, (200, 190, 180))
        surface.blit(list_title, (list_x, 95))
        
        # 绘制每个员工
        for i, config in enumerate(self.api_configs):
            item_rect = pygame.Rect(list_x, list_y + i * item_height, item_width, item_height - 5)
            
            # 选中状态
            if i == self.selected_employee:
                # 选中背景
                pygame.draw.rect(surface, (50, 65, 80), item_rect, border_radius=8)
                pygame.draw.rect(surface, (100, 140, 180), item_rect, width=2, border_radius=8)
                # 左侧指示条
                pygame.draw.rect(surface, (120, 170, 220), 
                               (list_x, item_rect.y + 10, 4, item_rect.height - 20), 
                               border_radius=2)
            else:
                # 未选中背景
                pygame.draw.rect(surface, (40, 38, 36), item_rect, border_radius=8)
                pygame.draw.rect(surface, (60, 58, 55), item_rect, width=1, border_radius=8)
            
            # 员工名称
            name_color = (140, 220, 140) if config.is_configured() else (200, 195, 190)
            name_text = self.font_medium.render(config.name, True, name_color)
            surface.blit(name_text, (list_x + 20, list_y + i * item_height + 12))
            
            # 配置状态
            if config.is_configured():
                status = f"[OK] {config.model_name}"
                status_color = (120, 200, 120)
            else:
                status = "未配置"
                status_color = (140, 140, 140)
            
            status_text = self.font_small.render(status, True, status_color)
            surface.blit(status_text, (list_x + 20, list_y + i * item_height + 42))
    
    def _draw_config_form_elegant(self, surface):
        """绘制优雅风格的配置表单"""
        if not self.temp_config:
            return
        
        form_x = 340
        form_y = 110  # 整体上移一点
        label_width = 130  # 增加标签宽度
        input_width = 450  # 相应减少输入框宽度
        input_height = 45  # 增加输入框高度
        spacing = 80  # 增加间距
        
        # 当前员工卡片
        card_rect = pygame.Rect(form_x, form_y, input_width + label_width + 20, 60)
        pygame.draw.rect(surface, (45, 50, 55), card_rect, border_radius=10)
        pygame.draw.rect(surface, (80, 90, 100), card_rect, width=1, border_radius=10)
        
        # 员工名称
        name_text = self.font_large.render(f"正在配置: {self.temp_config.name}", True, (255, 220, 180))
        surface.blit(name_text, (form_x + 15, form_y + 15))
        
        # 输入框起始位置
        input_start_y = form_y + 90
        
        # API URL
        self._draw_elegant_input_field(surface, "API URL", form_x, input_start_y, 
                                      label_width, input_width, input_height,
                                      self.temp_config.api_url, self.input_focus == 'url')
        
        # API Key
        self._draw_elegant_input_field(surface, "API Key", form_x, input_start_y + spacing, 
                                      label_width, input_width, input_height,
                                      self._mask_key(self.temp_config.api_key), self.input_focus == 'key')
        
        # Model Name
        self._draw_elegant_input_field(surface, "模型名称", form_x, input_start_y + spacing * 2, 
                                      label_width, input_width, input_height,
                                      self.temp_config.model_name, self.input_focus == 'model')
        
        # 提示信息框 - 大幅增加高度避免溢出
        hint_y = input_start_y + spacing * 3 + 35
        hint_rect = pygame.Rect(form_x, hint_y, input_width + label_width + 20, 110)  # 增加到110
        pygame.draw.rect(surface, (40, 45, 50), hint_rect, border_radius=8)
        pygame.draw.rect(surface, (70, 80, 90), hint_rect, width=1, border_radius=8)
        
        # 提示图标
        hint_icon = self.font_medium.render("[i]", True, (255, 255, 255))
        surface.blit(hint_icon, (form_x + 15, hint_y + 20))
        
        # 提示文字 - 使用更大字体和行间距
        hints = [
            "• 留空则使用游戏内默认配置",
            "• 支持 OpenAI 格式 API (如智谱、DeepSeek等)",
            "• API Key 将被安全保存在本地"
        ]
        for i, hint in enumerate(hints):
            hint_text = self.font_medium.render(hint, True, (160, 170, 180))  # 改用medium字体
            surface.blit(hint_text, (form_x + 50, hint_y + 20 + i * 28))  # 行间距28
    
    def _draw_elegant_input_field(self, surface, label, x, y, label_width, input_width, input_height, value, is_focused):
        """绘制优雅风格的输入框"""
        # 标签 - 垂直居中
        label_surface = self.font_small.render(label, True, (180, 175, 170))
        label_y = y + (input_height - label_surface.get_height()) // 2
        surface.blit(label_surface, (x, label_y))
        
        # 输入框
        input_x = x + label_width + 15
        input_rect = pygame.Rect(input_x, y, input_width, input_height)
        
        # 背景色
        if is_focused:
            bg_color = (55, 60, 70)
            border_color = (120, 160, 200)
            # 发光效果
            pygame.draw.rect(surface, (100, 140, 180, 50), 
                           input_rect.inflate(4, 4), border_radius=6)
        else:
            bg_color = (40, 42, 45)
            border_color = (70, 70, 75)
        
        pygame.draw.rect(surface, bg_color, input_rect, border_radius=6)
        pygame.draw.rect(surface, border_color, input_rect, width=2, border_radius=6)
        
        # 输入文字
        if value:
            text_color = (255, 255, 255) if not is_focused else (220, 230, 255)
            text_surface = self.font_small.render(value, True, text_color)
            
            # 裁剪显示 - 文字垂直居中
            text_y = y + (input_height - text_surface.get_height()) // 2
            max_text_width = input_width - 20
            if text_surface.get_width() > max_text_width:
                surface.blit(text_surface, (input_x + 10, text_y), 
                           (text_surface.get_width() - max_text_width + 10, 0, max_text_width, input_height))
            else:
                surface.blit(text_surface, (input_x + 10, text_y))
        
        # 光标
        if is_focused:
            cursor_x = input_x + 12
            if value:
                text_width = self.font_small.render(value, True, (255, 255, 255)).get_width()
                cursor_x = min(input_x + 10 + text_width, input_x + input_width - 5)
            
            # 闪烁光标 - 垂直居中
            cursor_top = y + 10
            cursor_bottom = y + input_height - 10
            if int(self.animation_time * 2) % 2 == 0:
                pygame.draw.line(surface, (200, 220, 255), 
                               (cursor_x, cursor_top), (cursor_x, cursor_bottom), 2)
    
    def _mask_key(self, key: str) -> str:
        """隐藏API Key的大部分内容"""
        if len(key) <= 10:
            return key if key else ""
        return key[:6] + "········" + key[-4:]
    
    def get_api_configs(self) -> List[APIConfig]:
        """获取API配置列表"""
        return self.api_configs
