# AI员工类 - 每个AI都是一个员工

import pygame
import random
import math
import os
from core.config import COLORS, EMPLOYEE, PERSPECTIVE, GRID_SIZE, AREAS, get_font
from core.constants import (
    DEFAULT_API_URL, DEFAULT_API_MODEL, DEFAULT_API_KEY, MESSAGE_BUBBLE_DURATION,
    MIN_MESSAGE_INTERVAL, MOVE_LERP_SPEED, TURN_DURATION,
    DEFAULT_HAPPINESS_MIN, DEFAULT_HAPPINESS_MAX, DEFAULT_ENERGY_MIN,
    DEFAULT_ENERGY_MAX, LOW_ENERGY_THRESHOLD, HIGH_HAPPINESS_THRESHOLD,
    LOW_HAPPINESS_THRESHOLD, MESSAGE_TRIGGER_CHANCE, BUBBLE_PADDING,
    BUBBLE_FLOAT_AMPLITUDE, BUBBLE_OFFSET_Y, PRECONFIGURED_EMPLOYEE_IDS,
    DEFAULT_POSITIONS, MIN_WANDER_DELAY, MAX_WANDER_DELAY,
    MIN_WANDER_INTERVAL, MAX_WANDER_INTERVAL, MAX_HAPPINESS, MAX_ENERGY,
    ENERGY_CONSUMPTION_RATE, ENERGY_RECOVERY_RATE, HAPPINESS_RECOVERY_RATE,
    EMPLOYEE_MODEL_ASSIGNMENTS, FALLBACK_MODELS
)
from ai_systems.cloud_ai_client import EmployeeAIClient

# 员工语录库 - 按员工ID和状态分类
EMPLOYEE_QUOTES = {
    0: {  # 小明
        'rest': [
            "先歇会儿，等规划",
            "规划师快分配任务",
            "待命状态...",
            "等待指令中",
            "随时准备开工",
            "等待任务分配",
            "等待角色分配",
            "准备就绪",
            "等待任务中",
            "规划师请指示",
        ],
        'work': [
            "任务执行中",
            "按计划推进",
            "专注工作中",
            "进度正常",
            "任务进行中",
            "执行到位",
            "稳步推进",
            "工作有序",
            "效率良好",
            "任务完成",
        ],
    },
    1: {  # 小红
        'rest': [
            "等待规划分配",
            "等待角色分配",
            "准备就绪",
            "等待指令",
            "规划师请安排",
            "待命状态",
            "等待任务分配",
            "准备开工",
            "等待角色确定",
            "等待任务分配",
        ],
        'work': [
            "任务执行中",
            "按计划完成",
            "工作推进中",
            "进度良好",
            "任务有序进行",
            "执行顺利",
            "工作正常",
            "任务完成",
            "执行到位",
            "工作完毕",
        ],
    },
    2: {  # 阿强
        'rest': [
            "等待规划",
            "等待角色分配",
            "准备就绪",
            "等待分配",
            "规划师请指示",
            "待命",
            "等待任务",
            "准备开工",
            "角色未确定",
            "等待任务分配",
        ],
        'work': [
            "按计划执行",
            "任务推进中",
            "工作进行中",
            "进度正常",
            "任务有序",
            "执行中",
            "工作良好",
            "任务完成",
            "执行完毕",
            "工作结束",
        ],
    },
    3: {  # 小丽
        'rest': [
            "等待规划分配",
            "等待角色分配",
            "准备就绪",
            "等待指令",
            "规划师请安排",
            "待命状态",
            "等待任务",
            "准备开工",
            "角色未确定",
            "等待任务分配",
        ],
        'work': [
            "任务执行中",
            "按计划完成",
            "工作推进中",
            "进度良好",
            "任务有序",
            "执行顺利",
            "工作正常",
            "任务完成",
            "执行到位",
            "工作完毕",
        ],
    },
    4: {  # 大伟
        'rest': [
            "等待规划",
            "等待角色分配",
            "准备就绪",
            "等待分配",
            "规划师请指示",
            "待命",
            "等待任务",
            "准备开工",
            "角色未确定",
            "等待任务分配",
        ],
        'work': [
            "按计划执行",
            "任务推进中",
            "工作进行中",
            "进度正常",
            "任务有序",
            "执行中",
            "工作良好",
            "任务完成",
            "执行完毕",
            "工作结束",
        ],
    },
    5: {  # 晓晓
        'rest': [
            "等待规划分配",
            "等待角色分配",
            "准备就绪",
            "等待指令",
            "规划师请安排",
            "待命状态",
            "等待任务分配",
            "准备开工",
            "等待角色确定",
            "等待任务分配",
        ],
        'work': [
            "任务执行中",
            "按计划完成",
            "工作推进中",
            "进度良好",
            "任务有序进行",
            "执行顺利",
            "工作正常",
            "任务完成",
            "执行到位",
            "工作完毕",
        ],
    },
}
            "活跃度维护",
            "运营策略调整",
        ],
    },
    5: {  # 晓晓 - 行政专员（细心，爱操心，小管家）
        'rest': [
            "打印机又坏了",
            "空调温度调一下",
            "会议室谁占了",
            "办公用品没了",
            "保洁阿姨辛苦了",
            "绿植该浇水了",
            "快递到了",
            "门禁卡忘带了",
            "饮水机没水了",
            "行政无小事",
        ],
        'work': [
            "办公环境整理好",
            "会议安排妥当",
            "物资采购完成",
            "文档归档完毕",
            "后勤服务到位",
            "设备维护好",
            "员工福利发放",
            "规章制度更新",
            "安全管理检查",
            "行政效率提升",
        ],
    },
}

class AIEmployee:
    """AI员工类 - 代表公司中的每个AI员工"""
    
    # 两种主要状态
    STATE_REST = 'rest'      # 休息状态（在休息区）
    STATE_WORK = 'work'      # 工作状态（在工作区）
    
    # 子状态
    SUBSTATE_IDLE = 'idle'
    SUBSTATE_WALKING = 'walking'
    SUBSTATE_SITTING = 'sitting'
    SUBSTATE_WANDERING = 'wandering'
    SUBSTATE_READY = 'ready'  # 就绪等待状态
    
    def __init__(self, employee_id, name, x, y, shirt_color=None):
        self.id = employee_id
        self.name = name
        # 将位置对齐到网格
        self.x = self._align_to_grid(x)
        self.y = self._align_to_grid(y)
        
        # 主状态：休息或工作
        self.state = self.STATE_REST
        # 子状态
        self.substate = self.SUBSTATE_IDLE
        
        self.size = EMPLOYEE['size']
        # 移动速度
        self.speed = EMPLOYEE['speed'] * random.uniform(0.8, 1.2)
        
        self.shirt_color = shirt_color or random.choice([
            COLORS['shirt_blue'], COLORS['shirt_red'], COLORS['shirt_green'],
            COLORS['shirt_yellow'], COLORS['shirt_purple'], COLORS['shirt_cyan']
        ])
        self.hair_color = random.choice([
            COLORS['hair_black'], COLORS['hair_brown'], COLORS['hair_blonde']
        ])
        
        self.anim_frame = 0
        self.anim_timer = 0
        self.direction = 0
        self.is_sitting = False
        
        self.assigned_desk = None
        self.work_progress = 0
        self.work_task = None
        
        # 目标位置
        self.target_pos = None
        # 当前路径
        self.path = []
        self.path_index = 0
        
        # 休息区随机走动
        self.wander_timer = 0
        self.wander_delay = random.randint(MIN_WANDER_DELAY, MAX_WANDER_DELAY)

        # 工作/休息计时
        self.state_timer = 0

        # 是否需要计算路径的标志
        self.needs_path = False

        # 心情/满意度系统 (0-100)
        self.happiness = random.randint(DEFAULT_HAPPINESS_MIN, DEFAULT_HAPPINESS_MAX)
        self.energy = random.randint(DEFAULT_ENERGY_MIN, DEFAULT_ENERGY_MAX)
        
        # 员工详细信息 - 默认全部为空
        self.gender = ""
        self.position = ""
        self.employee_id = f"AI-{1000 + self.id:04d}"  # 工牌号
        self.department = ""
        self.entry_date = "2024-01-15"
        
        # 云端AI配置
        self.api_url = ""
        self.api_key = ""
        self.model_name = ""
        self.skill_file = f"skill/skill{self.id}.md"
        
        # 每个员工有自己的AI客户端
        self.ai_client = EmployeeAIClient(self.id)
        self._load_skill()
        
        # 为所有员工自动配置最优模型
        self._setup_ai_model()
        
        # 设置默认职位名称
        if not self.position:
            self.position = DEFAULT_POSITIONS[self.id] if self.id < len(DEFAULT_POSITIONS) else '专员'
        
        # 互动反馈效果
        self.interact_effect_timer = 0
        self.interact_effect_type = None  # 'heart', 'note', 'zzz'
        
        # 平滑移动插值
        self.visual_x = self.x  # 视觉位置（用于平滑插值）
        self.visual_y = self.y
        self.move_lerp_speed = MOVE_LERP_SPEED  # 插值速度

        # 转身动画
        self.facing_direction = self.direction  # 当前实际朝向
        self.turn_timer = 0  # 转身计时
        self.is_turning = False  # 是否正在转身
        
        # 消息气泡系统
        self.message_bubble = None  # 当前显示的消息
        self.message_bubble_timer = 0  # 消息显示计时器
        self.message_bubble_duration = MESSAGE_BUBBLE_DURATION  # 消息显示持续时间（毫秒）
        self.last_message_time = 0  # 上次显示消息的时间（每个员工独立）
        self.min_message_interval = MIN_MESSAGE_INTERVAL  # 最小间隔（每个员工独立）
        self.message_font = None  # 消息字体（延迟初始化）
    
    def _setup_ai_model(self):
        """为员工配置最优AI模型"""
        # 检查是否有预设配置
        if self.id in EMPLOYEE_MODEL_ASSIGNMENTS:
            config = EMPLOYEE_MODEL_ASSIGNMENTS[self.id]
            self.api_url = config["api_url"]
            self.api_key = config["api_key"]
            self.model_name = config["model"]
            self.ai_client.set_api_config(self.api_url, self.api_key, self.model_name)
            print(f"[员工{self.id}] 已配置: {config['desc']} ({self.model_name})")
        else:
            # 使用默认配置
            self.api_url = DEFAULT_API_URL
            self.api_key = DEFAULT_API_KEY
            self.model_name = DEFAULT_API_MODEL
            self.ai_client.set_api_config(self.api_url, self.api_key, self.model_name)
            print(f"[员工{self.id}] 已配置默认模型: {self.model_name}")

    def switch_to_fallback_model(self):
        """切换到备用模型（当主模型额度用尽时）"""
        if self.id < len(FALLBACK_MODELS):
            fallback = FALLBACK_MODELS[self.id]
            self.api_url = fallback["api_url"]
            self.api_key = fallback["api_key"]
            self.model_name = fallback["model"]
            self.ai_client.set_api_config(self.api_url, self.api_key, self.model_name)
            print(f"[员工{self.id}] 已切换到备用模型: {self.model_name}")
            return True
        return False

    def _load_skill(self):
        """加载技能文件"""
        skill_path = self.skill_file
        if os.path.exists(skill_path):
            self.ai_client.load_skill(skill_path)
        else:
            # 确保目录存在
            os.makedirs(os.path.dirname(skill_path), exist_ok=True)
            # 创建空技能文件
            try:
                with open(skill_path, 'w', encoding='utf-8') as f:
                    f.write(f"# 员工{self.id} 技能定义\n\n")
            except:
                pass
    
    def update_api_config(self):
        """更新API配置到客户端"""
        if self.api_url and self.api_key and self.model_name:
            self.ai_client.set_api_config(self.api_url, self.api_key, self.model_name)
            return True
        return False
    
    def _align_to_grid(self, value):
        """将坐标对齐到网格中心"""
        grid_index = round(value / GRID_SIZE)
        return grid_index * GRID_SIZE + GRID_SIZE // 2
    
    def assign_desk(self, desk):
        """分配工位"""
        self.assigned_desk = desk
    
    def assign_task(self, task_name):
        """分配任务"""
        self.work_task = task_name
        self.work_progress = 0
    
    def set_target(self, target_x, target_y, path=None):
        """设置目标位置"""
        self.target_pos = (self._align_to_grid(target_x), self._align_to_grid(target_y))
        if path:
            self.path = [(self._align_to_grid(p[0]), self._align_to_grid(p[1])) for p in path]
            self.path_index = 0
            self.substate = self.SUBSTATE_WALKING
            self.is_sitting = False
    
    def set_target_exact(self, target_x, target_y, path=None):
        """设置精确目标位置（不进行网格对齐）"""
        self.target_pos = (target_x, target_y)
        if path:
            self.path = path
            self.path_index = 0
            self.substate = self.SUBSTATE_WALKING
            self.is_sitting = False
    
    def switch_to_work(self, path=None):
        """切换到工作状态"""
        if self.assigned_desk and self.state != self.STATE_WORK:
            self.state = self.STATE_WORK
            # 目标位置是电脑座椅位置（椅子在桌子后面）
            target_x = self.assigned_desk['x']
            target_y = self.assigned_desk['y'] + 25  # 椅子位置
            self.set_target(target_x, target_y, path)
            return True
        return False
    
    def switch_to_rest(self, rest_pos, path=None):
        """切换到休息状态"""
        if self.state != self.STATE_REST:
            self.state = self.STATE_REST
            self.set_target(rest_pos[0], rest_pos[1], path)
            return True
        return False
    
    def update(self, dt, particle_system=None, current_time=None, dialogue_active=False):
        """更新员工状态"""
        if current_time is None:
            current_time = pygame.time.get_ticks()
        
        self.anim_timer += dt
        if self.anim_timer >= EMPLOYEE['walk_anim_speed']:
            self.anim_timer = 0
            self.anim_frame = (self.anim_frame + 1) % 4
            
            # 走路时产生脚步粒子
            if self.substate == self.SUBSTATE_WALKING and particle_system:
                if self.anim_frame % 2 == 0:  # 每隔一帧产生粒子
                    particle_system.create_footstep(self.visual_x, self.visual_y + 10, self.direction)
        
        # 更新互动效果计时器
        if self.interact_effect_timer > 0:
            self.interact_effect_timer -= dt
        
        # 更新消息气泡计时器
        if self.message_bubble_timer > 0:
            self.message_bubble_timer -= dt
            if self.message_bubble_timer <= 0:
                self.message_bubble = None
        
        # 尝试显示新消息（随机触发，有冷却时间，检查是否有对话在进行）
        self._try_show_message(current_time, dialogue_active)
        
        # 平滑移动插值 - 视觉位置跟随逻辑位置
        self.visual_x += (self.x - self.visual_x) * self.move_lerp_speed
        self.visual_y += (self.y - self.visual_y) * self.move_lerp_speed
        
        # 转身动画
        if self.direction != self.facing_direction:
            if not self.is_turning:
                self.is_turning = True
                self.turn_timer = 0
            else:
                self.turn_timer += dt
                # 转身完成
                if self.turn_timer >= 150:  # 150ms转身时间
                    self.facing_direction = self.direction
                    self.is_turning = False
                    self.turn_timer = 0
        
        # 休息时恢复能量
        if self.state == self.STATE_REST:
            self.energy = min(MAX_ENERGY, self.energy + dt * ENERGY_RECOVERY_RATE)
            if self.substate == self.SUBSTATE_SITTING:
                self.happiness = min(MAX_HAPPINESS, self.happiness + dt * HAPPINESS_RECOVERY_RATE)
        
        # 根据主状态更新
        if self.state == self.STATE_REST:
            self._update_rest_state(dt)
        elif self.state == self.STATE_WORK:
            self._update_work_state(dt)
    
    def _try_show_message(self, current_time, dialogue_system_active=False):
        """尝试显示消息气泡（独立随机，有最小间隔）"""
        # 如果正在显示消息，不触发新的
        if self.message_bubble_timer > 0:
            return
        
        # 如果有对话在进行，不触发单人消息
        if dialogue_system_active:
            return
        
        # 检查最小间隔（每个员工独立）
        if current_time - self.last_message_time < self.min_message_interval:
            return
        
        # 独立随机触发 - 每个员工有自己的随机种子，完全独立
        random.seed(current_time + self.id * 10000 + hash(self.name))
        trigger_chance = random.random()
        random.seed()  # 重置随机种子
        
        # 很低的触发概率，约每30-50秒触发一次
        if trigger_chance > MESSAGE_TRIGGER_CHANCE:
            return
        
        # 根据当前状态选择语录
        state_key = 'work' if self.state == self.STATE_WORK else 'rest'
        
        # 获取该员工的语录
        if self.id in EMPLOYEE_QUOTES and state_key in EMPLOYEE_QUOTES[self.id]:
            quotes = EMPLOYEE_QUOTES[self.id][state_key]
            if quotes:
                # 随机选择一条语录
                self.message_bubble = random.choice(quotes)
                self.message_bubble_timer = self.message_bubble_duration
                self.last_message_time = current_time
                print(f"[员工{self.name}] 说: {self.message_bubble}")
    
    def draw_message_bubble(self, surface):
        """绘制消息气泡（极简优雅版）"""
        if not self.message_bubble or self.message_bubble_timer <= 0:
            return
        
        # 延迟初始化字体 - 使用更小的字体
        if self.message_font is None:
            self.message_font = get_font(10)
        
        # 计算透明度（淡入淡出效果）
        progress = 1.0
        if self.message_bubble_timer > self.message_bubble_duration * 0.85:
            # 淡入（前15%时间）
            progress = (self.message_bubble_duration - self.message_bubble_timer) / (self.message_bubble_duration * 0.15)
        elif self.message_bubble_timer < self.message_bubble_duration * 0.15:
            # 淡出（后15%时间）
            progress = self.message_bubble_timer / (self.message_bubble_duration * 0.15)
        
        alpha = int(240 * progress)  # 稍微降低最大透明度
        
        # 极小的内边距，让气泡更紧凑
        bubble_padding = 4
        text_surface = self.message_font.render(self.message_bubble, True, (60, 60, 60))
        text_width = text_surface.get_width()
        text_height = text_surface.get_height()
        
        bubble_width = text_width + bubble_padding * 2
        bubble_height = text_height + bubble_padding * 2
        
        # 极轻微的浮动动画
        float_offset = math.sin(pygame.time.get_ticks() / 800) * 1.5
        
        # 更靠近头部（28像素）
        bubble_x = int(self.visual_x - bubble_width // 2)
        bubble_y = int(self.visual_y - self.size // 2 - 28 - bubble_height + float_offset)
        
        # 确保气泡不超出屏幕顶部
        bubble_y = max(3, bubble_y)
        
        # 创建带透明度的表面
        bubble_surface = pygame.Surface((bubble_width, bubble_height + 4), pygame.SRCALPHA)
        
        # 气泡背景颜色（根据状态）- 更淡雅的色调
        if self.state == self.STATE_WORK:
            bg_color = (255, 252, 230, alpha)  # 工作：极淡的暖黄色
            border_color = (230, 210, 160, alpha)
            shadow_color = (200, 180, 130, int(alpha * 0.3))
        else:
            bg_color = (240, 248, 255, alpha)  # 休息：极淡的淡蓝色
            border_color = (170, 200, 220, alpha)
            shadow_color = (140, 170, 190, int(alpha * 0.3))
        
        # 绘制阴影（增加层次感）
        shadow_offset = 2
        pygame.draw.rect(bubble_surface, shadow_color, 
                        (shadow_offset, shadow_offset, bubble_width, bubble_height), border_radius=4)
        
        # 绘制圆角矩形气泡 - 小圆角
        pygame.draw.rect(bubble_surface, bg_color, (0, 0, bubble_width, bubble_height), border_radius=4)
        pygame.draw.rect(bubble_surface, border_color, (0, 0, bubble_width, bubble_height), 1, border_radius=4)
        
        # 绘制小三角（指向员工）- 精致小巧
        triangle_points = [
            (bubble_width // 2 - 3, bubble_height),
            (bubble_width // 2 + 3, bubble_height),
            (bubble_width // 2, bubble_height + 4)
        ]
        pygame.draw.polygon(bubble_surface, bg_color, triangle_points)
        pygame.draw.polygon(bubble_surface, border_color, triangle_points, 1)
        
        # 绘制文字
        text_surface.set_alpha(alpha)
        bubble_surface.blit(text_surface, (bubble_padding, bubble_padding))
        
        # 绘制到主表面
        surface.blit(bubble_surface, (bubble_x, bubble_y))
    
    def _update_rest_state(self, dt):
        """更新休息状态"""
        if self.substate == self.SUBSTATE_WALKING:
            self._update_walking()
        elif self.substate == self.SUBSTATE_SITTING:
            self._update_sitting(dt)
        elif self.substate == self.SUBSTATE_IDLE:
            self._update_rest_idle(dt)
    
    def _update_work_state(self, dt):
        """更新工作状态"""
        if self.substate == self.SUBSTATE_WALKING:
            self._update_walking()
        elif self.substate == self.SUBSTATE_SITTING:
            self._update_working(dt)
    
    def _update_walking(self):
        """更新行走"""
        if not self.path or self.path_index >= len(self.path):
            # 到达目的地，坐下工作
            self.substate = self.SUBSTATE_SITTING
            self.is_sitting = True
            if self.state == self.STATE_WORK:
                self.work_progress = 0
            return
        
        target = self.path[self.path_index]
        dx = target[0] - self.x
        dy = target[1] - self.y
        distance = math.sqrt(dx * dx + dy * dy)
        
        if distance < self.speed:
            # 到达路径点
            self.x = target[0]
            self.y = target[1]
            self.path_index += 1
        else:
            # 移动
            move_x = (dx / distance) * self.speed
            move_y = (dy / distance) * self.speed
            self.x += move_x
            self.y += move_y
            
            # 更新朝向
            if abs(dx) > abs(dy):
                self.direction = 2 if dx > 0 else 1
            else:
                self.direction = 0 if dy > 0 else 3
    
    def _update_sitting(self, dt):
        """更新坐着休息"""
        self.state_timer += dt
        
        # 只有在休息状态下才会自动离开
        # 工作状态下等待用户按下空格键
        if self.state == self.STATE_REST and self.state_timer >= EMPLOYEE['rest_time']:
            self.state_timer = 0
            self.substate = self.SUBSTATE_IDLE
            self.is_sitting = False
    
    def _update_rest_idle(self, dt):
        """更新休息区空闲状态 - 随机走动"""
        self.wander_timer += dt
        
        if self.wander_timer >= self.wander_delay:
            self.wander_timer = 0
            self.wander_delay = random.randint(MIN_WANDER_INTERVAL, MAX_WANDER_INTERVAL)
            # 设置随机走动目标
            self._set_random_wander_target()
    
    def _set_random_wander_target(self):
        """设置休息区随机走动目标"""
        ent = AREAS['entertainment']
        margin = 60
        target_x = random.randint(ent['x'] + margin, ent['x'] + ent['width'] - margin)
        target_y = random.randint(ent['y'] + margin, ent['y'] + ent['height'] - margin)
        self.target_pos = (self._align_to_grid(target_x), self._align_to_grid(target_y))
        # 设置需要路径标志，由外部寻路系统计算路径
        self.needs_path = True
        self.substate = self.SUBSTATE_IDLE
    
    def _update_working(self, dt):
        """更新工作中 - 持续工作直到用户按下空格"""
        self.work_progress += dt
        
        # 工作会消耗能量，降低满意度
        self.energy = max(0, self.energy - dt * ENERGY_CONSUMPTION_RATE)
        if self.energy < LOW_ENERGY_THRESHOLD:
            self.happiness = max(0, self.happiness - dt * 0.001)
        
        # 工作完成后重置进度，继续工作（循环工作）
        # 不自动切换状态，等待用户按下空格键
        if self.work_progress >= EMPLOYEE['work_time']:
            self.work_progress = 0
    
    def trigger_interact_effect(self, effect_type='heart'):
        """触发互动效果"""
        self.interact_effect_timer = 1000  # 显示1秒
        self.interact_effect_type = effect_type
    
    def draw_interact_effect(self, surface):
        """绘制互动效果（爱心、音符等）"""
        if self.interact_effect_timer <= 0:
            return
        
        # 计算浮动位置 - 使用视觉位置
        float_offset = (1000 - self.interact_effect_timer) / 1000 * 20
        x = int(self.visual_x)
        y = int(self.visual_y - self.size // 2 - 35 - float_offset)
        
        # 绘制效果
        if self.interact_effect_type == 'heart':
            # 绘制爱心
            pygame.draw.circle(surface, (255, 100, 100), (x - 4, y), 4)
            pygame.draw.circle(surface, (255, 100, 100), (x + 4, y), 4)
            pygame.draw.polygon(surface, (255, 100, 100), [
                (x - 8, y + 2), (x + 8, y + 2), (x, y + 10)
            ])
        elif self.interact_effect_type == 'note':
            # 绘制音符
            pygame.draw.circle(surface, (100, 200, 255), (x, y + 6), 4)
            pygame.draw.line(surface, (100, 200, 255), (x + 4, y + 6), (x + 4, y - 4), 2)
            pygame.draw.line(surface, (100, 200, 255), (x + 4, y - 4), (x + 8, y - 2), 2)
        elif self.interact_effect_type == 'zzz':
            # 绘制Zzz
            font = get_font(14)
            z_text = font.render("Zzz", True, (150, 150, 255))
            surface.blit(z_text, (x - z_text.get_width() // 2, y))
    
    def get_current_target(self):
        """获取当前目标位置"""
        if self.state == self.STATE_WORK and self.assigned_desk:
            return (self.assigned_desk['x'], self.assigned_desk['y'] + 25)
        elif self.state == self.STATE_REST and self.target_pos:
            return self.target_pos
        return None
    
    def draw_shadow(self, surface):
        """绘制阴影 - 使用视觉位置"""
        if PERSPECTIVE['enabled']:
            shadow_x = self.visual_x + PERSPECTIVE['shadow_offset']
            shadow_y = self.visual_y + PERSPECTIVE['shadow_offset']
            shadow_surface = pygame.Surface((self.size, self.size // 2), pygame.SRCALPHA)
            pygame.draw.ellipse(shadow_surface, (0, 0, 0, PERSPECTIVE['shadow_alpha']), 
                              (0, 0, self.size, self.size // 2))
            surface.blit(shadow_surface, (shadow_x - self.size // 2, shadow_y - self.size // 4))
    
    def draw_name_tag(self, surface, font, is_selected=False):
        """绘制头顶名字标签"""
        # 名字标签背景
        name_text = font.render(self.name, True, (255, 255, 255))
        text_width = name_text.get_width()
        text_height = name_text.get_height()
        
        # 标签位置（头顶上方）- 使用视觉位置
        tag_x = int(self.visual_x - text_width // 2)
        tag_y = int(self.visual_y - self.size // 2 - 25)
        
        # 绘制标签背景（圆角矩形）
        padding = 4
        bg_rect = pygame.Rect(tag_x - padding, tag_y - padding, 
                             text_width + padding * 2, text_height + padding * 2)
        
        # 如果被选中，使用高亮背景
        if is_selected:
            pygame.draw.rect(surface, (255, 200, 100, 200), bg_rect, border_radius=3)
            pygame.draw.rect(surface, (255, 150, 50), bg_rect, 2, border_radius=3)
        else:
            pygame.draw.rect(surface, (40, 40, 50, 180), bg_rect, border_radius=3)
            pygame.draw.rect(surface, (100, 100, 120), bg_rect, 1, border_radius=3)
        
        # 绘制文字
        surface.blit(name_text, (tag_x, tag_y))
        
        # 如果被选中，绘制选中圈
        if is_selected:
            circle_surface = pygame.Surface((self.size + 16, self.size + 16), pygame.SRCALPHA)
            pygame.draw.ellipse(circle_surface, (255, 200, 100, 100), 
                              (0, 0, self.size + 16, self.size + 16), 2)
            surface.blit(circle_surface, (int(self.visual_x - self.size // 2 - 8), 
                                         int(self.visual_y - self.size // 2 - 8)))
    
    def draw(self, surface):
        """绘制员工 - 机器人形象，工作时显示背面"""
        self.draw_shadow(surface)
        
        # 工作时（坐在电脑前）显示背面（面向电脑）
        # 其他状态显示正面
        if self.state == self.STATE_WORK and self.substate == self.SUBSTATE_SITTING:
            self._draw_robot_back(surface)
        else:
            self._draw_robot_front(surface)
    
    def _draw_front(self, surface):
        """绘制正面形象 - 精致版"""
        draw_y = self.visual_y
        if self.is_sitting:
            draw_y += 8
        
        # 行走动画参数
        walk_cycle = self.anim_frame * math.pi / 2
        bounce = abs(math.sin(walk_cycle)) * 2 if self.substate == self.SUBSTATE_WALKING else 0
        body_tilt = math.sin(walk_cycle) * 1 if self.substate == self.SUBSTATE_WALKING else 0
        
        body_y = draw_y - self.size // 2 + bounce
        x = int(self.visual_x)
        y = int(body_y)
        
        # ===== 绘制腿部 =====
        if not self.is_sitting:
            if self.substate == self.SUBSTATE_WALKING:
                # 行走时腿部摆动
                left_angle = math.sin(walk_cycle) * 0.4
                right_angle = math.sin(walk_cycle + math.pi) * 0.4
                
                # 左腿（大腿+小腿）
                self._draw_leg(surface, x - 5, y + 14, left_angle, True)
                # 右腿
                self._draw_leg(surface, x + 5, y + 14, right_angle, False)
            else:
                # 站立姿势
                self._draw_leg(surface, x - 5, y + 14, 0, True)
                self._draw_leg(surface, x + 5, y + 14, 0, False)
        else:
            # 坐姿腿部
            pygame.draw.rect(surface, COLORS['pants'], (x - 8, y + 14, 6, 5))
            pygame.draw.rect(surface, COLORS['pants'], (x + 2, y + 14, 6, 5))
            pygame.draw.rect(surface, COLORS['shoes'], (x - 8, y + 17, 6, 3))
            pygame.draw.rect(surface, COLORS['shoes'], (x + 2, y + 17, 6, 3))
        
        # ===== 绘制身体 =====
        body_w, body_h = 16, 14
        body_rect = pygame.Rect(x - body_w//2 + int(body_tilt), y, body_w, body_h)
        
        # 身体主体
        pygame.draw.ellipse(surface, self.shirt_color, body_rect)
        # 身体阴影（立体感）
        pygame.draw.ellipse(surface, (min(255, self.shirt_color[0] - 20), 
                                     min(255, self.shirt_color[1] - 20), 
                                     min(255, self.shirt_color[2] - 20)), 
                          body_rect, 1)
        # 高光
        highlight_rect = pygame.Rect(x - body_w//2 + 2 + int(body_tilt), y + 2, 4, 6)
        pygame.draw.ellipse(surface, (min(255, self.shirt_color[0] + 30), 
                                     min(255, self.shirt_color[1] + 30), 
                                     min(255, self.shirt_color[2] + 30)), 
                          highlight_rect)
        
        # ===== 绘制手臂 =====
        if self.substate == self.SUBSTATE_WALKING:
            left_arm_angle = math.sin(walk_cycle + math.pi) * 0.5
            right_arm_angle = math.sin(walk_cycle) * 0.5
        else:
            left_arm_angle = 0.1
            right_arm_angle = -0.1
        
        self._draw_arm(surface, x - 10 + int(body_tilt), y + 3, left_arm_angle, True)
        self._draw_arm(surface, x + 10 + int(body_tilt), y + 3, right_arm_angle, False)
        
        # ===== 绘制头部 =====
        head_bounce = math.sin(walk_cycle) * 0.5 if self.substate == self.SUBSTATE_WALKING else 0
        head_y = y - 10 + int(head_bounce)
        head_x = x + int(body_tilt * 0.3)
        
        self._draw_head_front(surface, head_x, head_y)
    
    def _draw_leg(self, surface, x, y, angle, is_left):
        """绘制一条腿（带关节）"""
        leg_len = 8
        foot_len = 4
        
        # 大腿
        thigh_end_x = x + math.sin(angle) * leg_len
        thigh_end_y = y + math.cos(angle) * leg_len
        pygame.draw.line(surface, COLORS['pants'], (x, y), (thigh_end_x, thigh_end_y), 5)
        
        # 小腿（与大腿有相位差）
        knee_angle = angle + math.sin(angle) * 0.3
        calf_end_x = thigh_end_x + math.sin(knee_angle) * leg_len
        calf_end_y = thigh_end_y + math.cos(knee_angle) * leg_len
        pygame.draw.line(surface, COLORS['pants'], (thigh_end_x, thigh_end_y), (calf_end_x, calf_end_y), 4)
        
        # 鞋子
        shoe_color = COLORS['shoes']
        pygame.draw.ellipse(surface, shoe_color, (calf_end_x - 4, calf_end_y - 1, 8, 5))
        # 鞋头高光
        pygame.draw.ellipse(surface, (min(255, shoe_color[0] + 30), 
                                     min(255, shoe_color[1] + 30), 
                                     min(255, shoe_color[2] + 30)), 
                          (calf_end_x - 2, calf_end_y, 3, 2))
    
    def _draw_arm(self, surface, x, y, angle, is_left):
        """绘制一只手臂（带关节）"""
        upper_len = 6
        lower_len = 5
        
        # 上臂
        upper_end_x = x + math.sin(angle) * upper_len
        upper_end_y = y + math.cos(angle) * upper_len
        pygame.draw.line(surface, self.shirt_color, (x, y), (upper_end_x, upper_end_y), 4)
        
        # 前臂（自然弯曲）
        elbow_angle = angle + 0.2
        hand_x = upper_end_x + math.sin(elbow_angle) * lower_len
        hand_y = upper_end_y + math.cos(elbow_angle) * lower_len
        pygame.draw.line(surface, self.shirt_color, (upper_end_x, upper_end_y), (hand_x, hand_y), 3)
        
        # 手
        pygame.draw.circle(surface, COLORS['skin'], (int(hand_x), int(hand_y)), 3)
    
    def _draw_head_front(self, surface, x, y):
        """绘制正面头部"""
        head_w, head_h = 18, 16
        
        # 脸部轮廓（更圆润）
        face_rect = pygame.Rect(x - head_w//2, y, head_w, head_h)
        pygame.draw.ellipse(surface, COLORS['skin'], face_rect)
        
        # 脸部阴影（下巴）
        chin_rect = pygame.Rect(x - head_w//2 + 2, y + head_h - 4, head_w - 4, 4)
        pygame.draw.ellipse(surface, COLORS['skin_shadow'], chin_rect)
        
        # 耳朵
        pygame.draw.circle(surface, COLORS['skin'], (x - head_w//2, y + 8), 3)
        pygame.draw.circle(surface, COLORS['skin'], (x + head_w//2, y + 8), 3)
        
        # 头发（更精致的发型）
        self._draw_hair_front(surface, x, y, head_w)
        
        # 眼睛（更生动）
        self._draw_eyes_front(surface, x, y + 5)
        
        # 眉毛
        if self.energy < 30:
            # 疲惫的眉毛
            pygame.draw.line(surface, self.hair_color, (x - 7, y + 3), (x - 2, y + 4), 2)
            pygame.draw.line(surface, self.hair_color, (x + 2, y + 4), (x + 7, y + 3), 2)
        elif self.happiness > 80:
            # 开心的眉毛
            pygame.draw.line(surface, self.hair_color, (x - 7, y + 2), (x - 2, y + 1), 2)
            pygame.draw.line(surface, self.hair_color, (x + 2, y + 1), (x + 7, y + 2), 2)
        else:
            # 正常眉毛
            pygame.draw.line(surface, self.hair_color, (x - 7, y + 2), (x - 2, y + 2), 2)
            pygame.draw.line(surface, self.hair_color, (x + 2, y + 2), (x + 7, y + 2), 2)
        
        # 鼻子
        pygame.draw.line(surface, COLORS['skin_shadow'], (x, y + 6), (x - 1, y + 9), 1)
        
        # 嘴巴
        self._draw_mouth(surface, x, y + 11)
    
    def _draw_hair_front(self, surface, x, y, head_w):
        """绘制正面头发"""
        hair_style = self.id % 3
        
        if hair_style == 0:  # 短发平头
            # 顶部
            pygame.draw.arc(surface, self.hair_color, (x - head_w//2 - 1, y - 4, head_w + 2, 10), 0, math.pi, 4)
            # 两侧
            pygame.draw.rect(surface, self.hair_color, (x - head_w//2 - 1, y, 4, 6))
            pygame.draw.rect(surface, self.hair_color, (x + head_w//2 - 3, y, 4, 6))
        elif hair_style == 1:  # 中分长发
            # 顶部
            pygame.draw.arc(surface, self.hair_color, (x - head_w//2 - 2, y - 5, head_w + 4, 12), 0, math.pi, 5)
            # 中分线
            pygame.draw.line(surface, COLORS['skin'], (x, y - 2), (x, y + 3), 2)
            # 两侧头发
            pygame.draw.rect(surface, self.hair_color, (x - head_w//2 - 2, y, 5, 10))
            pygame.draw.rect(surface, self.hair_color, (x + head_w//2 - 3, y, 5, 10))
        else:  # 侧分短发
            # 顶部
            pygame.draw.arc(surface, self.hair_color, (x - head_w//2 - 1, y - 4, head_w + 2, 10), 0, math.pi, 4)
            # 侧分
            pygame.draw.rect(surface, self.hair_color, (x - head_w//2 - 1, y, 7, 8))
            pygame.draw.rect(surface, self.hair_color, (x + head_w//2 - 3, y, 4, 6))
    
    def _draw_eyes_front(self, surface, x, y):
        """绘制正面眼睛"""
        eye_w, eye_h = 5, 6
        
        if self.energy < 30:
            # 疲惫的眼睛（半闭）
            pygame.draw.line(surface, COLORS['eye_black'], (x - 6, y + 2), (x - 1, y + 2), 2)
            pygame.draw.line(surface, COLORS['eye_black'], (x + 1, y + 2), (x + 6, y + 2), 2)
        elif self.happiness > 80:
            # 开心的笑眼
            pygame.draw.arc(surface, COLORS['eye_black'], (x - 7, y - 1, 6, 5), 0.3, 2.8, 2)
            pygame.draw.arc(surface, COLORS['eye_black'], (x + 1, y - 1, 6, 5), 0.3, 2.8, 2)
        else:
            # 正常眼睛
            # 左眼白
            pygame.draw.ellipse(surface, COLORS['eye_white'], (x - 6, y, eye_w, eye_h))
            # 左眼珠
            pygame.draw.circle(surface, COLORS['eye_black'], (x - 3, y + 3), 2)
            # 左眼高光
            pygame.draw.circle(surface, (255, 255, 255), (x - 4, y + 2), 1)
            
            # 右眼白
            pygame.draw.ellipse(surface, COLORS['eye_white'], (x + 1, y, eye_w, eye_h))
            # 右眼珠
            pygame.draw.circle(surface, COLORS['eye_black'], (x + 4, y + 3), 2)
            # 右眼高光
            pygame.draw.circle(surface, (255, 255, 255), (x + 3, y + 2), 1)
    
    def _draw_mouth(self, surface, x, y):
        """绘制嘴巴"""
        if self.happiness > 80:
            # 大笑（露齿）
            pygame.draw.arc(surface, (200, 80, 80), (x - 5, y - 2, 10, 8), 0, math.pi, 2)
            # 牙齿
            pygame.draw.rect(surface, (255, 255, 255), (x - 3, y + 1, 6, 2))
        elif self.happiness < 40:
            # 难过
            pygame.draw.arc(surface, (200, 80, 80), (x - 4, y + 2, 8, 5), math.pi, 0, 2)
        elif self.energy < 30:
            # 疲惫（张嘴）
            pygame.draw.ellipse(surface, (200, 100, 100), (x - 3, y, 6, 4))
        else:
            # 正常微笑
            pygame.draw.arc(surface, (200, 100, 100), (x - 4, y - 1, 8, 5), 0.2, 2.9, 2)
    
    def _draw_side(self, surface):
        """绘制侧面形象（向左或向右）"""
        is_left = (self.facing_direction == 1)
        
        draw_y = self.visual_y
        if self.is_sitting:
            draw_y += 8
        
        bounce = 0
        if self.substate == self.SUBSTATE_WALKING:
            bounce = abs(math.sin(self.anim_frame * math.pi / 2)) * 3
        
        body_y = draw_y - self.size // 2 + bounce
        x = int(self.visual_x)
        y = int(body_y)
        
        # 侧面朝向因子（向左或向右）
        facing = -1 if is_left else 1
        
        # 绘制腿
        if not self.is_sitting:
            if self.substate == self.SUBSTATE_WALKING:
                leg_swing = math.sin(self.anim_frame * math.pi / 2)
                front_leg_offset = int(leg_swing * 6)
                back_leg_offset = int(-leg_swing * 4)
                
                # 后腿
                pygame.draw.rect(surface, COLORS['pants'], (x - 3 + back_leg_offset, y + 14, 4, 6))
                pygame.draw.rect(surface, COLORS['pants'], (x - 3 + back_leg_offset // 2, y + 20, 4, 6))
                pygame.draw.rect(surface, COLORS['shoes'], (x - 3 + back_leg_offset, y + 24, 4, 4))
                
                # 前腿
                pygame.draw.rect(surface, COLORS['pants'], (x + 1 + front_leg_offset, y + 14, 4, 6))
                pygame.draw.rect(surface, COLORS['pants'], (x + 1 + front_leg_offset // 2, y + 20, 4, 6))
                pygame.draw.rect(surface, COLORS['shoes'], (x + 1 + front_leg_offset, y + 24, 4, 4))
            else:
                pygame.draw.rect(surface, COLORS['pants'], (x - 3, y + 14, 4, 10))
                pygame.draw.rect(surface, COLORS['shoes'], (x - 3, y + 22, 4, 4))
                pygame.draw.rect(surface, COLORS['pants'], (x + 1, y + 14, 4, 10))
                pygame.draw.rect(surface, COLORS['shoes'], (x + 1, y + 22, 4, 4))
        else:
            pygame.draw.rect(surface, COLORS['pants'], (x - 3, y + 14, 4, 6))
            pygame.draw.rect(surface, COLORS['pants'], (x + 1, y + 14, 4, 6))
            pygame.draw.rect(surface, COLORS['shoes'], (x - 3, y + 18, 4, 3))
            pygame.draw.rect(surface, COLORS['shoes'], (x + 1, y + 18, 4, 3))
        
        # 绘制身体（侧面更窄）
        body_rect = pygame.Rect(x - 6, y, 12, 16)
        pygame.draw.rect(surface, self.shirt_color, body_rect)
        pygame.draw.rect(surface, (min(255, self.shirt_color[0] - 30), min(255, self.shirt_color[1] - 30), min(255, self.shirt_color[2] - 30)), body_rect, 1)
        
        # 绘制侧面手臂
        if self.substate == self.SUBSTATE_WALKING:
            arm_swing = math.sin(self.anim_frame * math.pi / 2 + math.pi)
            arm_offset = int(arm_swing * 5)
        else:
            arm_offset = 0
        
        # 前手臂
        pygame.draw.rect(surface, self.shirt_color, (x + 4, y + 2 + arm_offset, 3, 10))
        pygame.draw.rect(surface, COLORS['skin'], (x + 4, y + 10 + arm_offset, 3, 4))
        
        # 后手臂
        pygame.draw.rect(surface, self.shirt_color, (x - 7, y + 2 - arm_offset, 3, 10))
        pygame.draw.rect(surface, COLORS['skin'], (x - 7, y + 10 - arm_offset, 3, 4))
        
        # 绘制头
        head_bounce = 0
        if self.substate == self.SUBSTATE_WALKING:
            head_bounce = math.sin(self.anim_frame * math.pi / 2) * 1
        
        head_y = y - 8 + int(head_bounce)
        head_x = x
        
        # 侧面头部（椭圆）
        pygame.draw.ellipse(surface, COLORS['skin'], (head_x - 8, head_y - 4, 16, 18))
        pygame.draw.ellipse(surface, COLORS['skin_shadow'], (head_x - 8, head_y + 8, 16, 6))
        
        # 侧面头发
        hair_style = self.id % 3
        if hair_style == 0:  # 平头
            pygame.draw.rect(surface, self.hair_color, (head_x - 8, head_y - 8, 16, 7))
            pygame.draw.rect(surface, self.hair_color, (head_x + (5 if is_left else -8), head_y - 6, 3, 8))
        elif hair_style == 1:  # 中分
            pygame.draw.rect(surface, self.hair_color, (head_x - 8, head_y - 8, 16, 6))
            pygame.draw.rect(surface, self.hair_color, (head_x - 2, head_y - 8, 4, 10))
        else:  # 短发
            pygame.draw.rect(surface, self.hair_color, (head_x - 8, head_y - 8, 16, 7))
            pygame.draw.rect(surface, self.hair_color, (head_x + (4 if is_left else -7), head_y - 6, 3, 9))
        
        # 侧面眼睛（只看到一只）
        eye_y = head_y + 2
        if self.energy < 30:
            pygame.draw.line(surface, COLORS['eye_black'], (head_x + 2, eye_y + 2), (head_x + 6, eye_y + 2), 2)
        elif self.happiness > 80:
            pygame.draw.arc(surface, COLORS['eye_black'], (head_x + 1, eye_y - 2, 6, 6), 0.2, 2.8, 2)
        else:
            pygame.draw.rect(surface, COLORS['eye_white'], (head_x + 2, eye_y, 5, 6))
            pygame.draw.rect(surface, COLORS['eye_black'], (head_x + 3, eye_y + 2, 3, 3))
        
        # 侧面嘴巴
        if self.happiness > 80:
            pygame.draw.arc(surface, (200, 80, 80), (head_x - 2, head_y + 6, 8, 6), 0, 3.14, 2)
        elif self.happiness < 40:
            pygame.draw.arc(surface, (200, 80, 80), (head_x - 2, head_y + 10, 8, 5), 3.14, 0, 2)
        else:
            pygame.draw.rect(surface, (200, 100, 100), (head_x + 1, head_y + 10, 4, 2))
    
    def _draw_back(self, surface):
        """绘制背面形象（向上走）"""
        draw_y = self.visual_y
        if self.is_sitting:
            draw_y += 8
        
        bounce = 0
        if self.substate == self.SUBSTATE_WALKING:
            bounce = abs(math.sin(self.anim_frame * math.pi / 2)) * 3
        
        body_y = draw_y - self.size // 2 + bounce
        x = int(self.visual_x)
        y = int(body_y)
        
        # 绘制腿
        if not self.is_sitting:
            if self.substate == self.SUBSTATE_WALKING:
                leg_swing = math.sin(self.anim_frame * math.pi / 2)
                left_leg_offset = int(leg_swing * 5)
                right_leg_offset = int(-leg_swing * 5)
                
                pygame.draw.rect(surface, COLORS['pants'], (x - 8 + left_leg_offset, y + 14, 5, 6))
                pygame.draw.rect(surface, COLORS['pants'], (x - 8 + left_leg_offset // 2, y + 20, 5, 6))
                pygame.draw.rect(surface, COLORS['shoes'], (x - 8 + left_leg_offset, y + 24, 5, 4))
                
                pygame.draw.rect(surface, COLORS['pants'], (x + 3 + right_leg_offset, y + 14, 5, 6))
                pygame.draw.rect(surface, COLORS['pants'], (x + 3 + right_leg_offset // 2, y + 20, 5, 6))
                pygame.draw.rect(surface, COLORS['shoes'], (x + 3 + right_leg_offset, y + 24, 5, 4))
            else:
                pygame.draw.rect(surface, COLORS['pants'], (x - 8, y + 14, 5, 10))
                pygame.draw.rect(surface, COLORS['shoes'], (x - 8, y + 22, 5, 4))
                pygame.draw.rect(surface, COLORS['pants'], (x + 3, y + 14, 5, 10))
                pygame.draw.rect(surface, COLORS['shoes'], (x + 3, y + 22, 5, 4))
        else:
            pygame.draw.rect(surface, COLORS['pants'], (x - 8, y + 14, 5, 6))
            pygame.draw.rect(surface, COLORS['pants'], (x + 3, y + 14, 5, 6))
            pygame.draw.rect(surface, COLORS['shoes'], (x - 8, y + 18, 5, 3))
            pygame.draw.rect(surface, COLORS['shoes'], (x + 3, y + 18, 5, 3))
        
        # 绘制身体（背面）
        body_rect = pygame.Rect(x - 9, y, 18, 16)
        pygame.draw.rect(surface, self.shirt_color, body_rect)
        pygame.draw.rect(surface, (min(255, self.shirt_color[0] - 30), min(255, self.shirt_color[1] - 30), min(255, self.shirt_color[2] - 30)), body_rect, 1)
        
        # 背面手臂摆动
        if self.substate == self.SUBSTATE_WALKING:
            arm_swing = math.sin(self.anim_frame * math.pi / 2 + math.pi)
            left_arm_offset = int(arm_swing * 4)
            right_arm_offset = int(-arm_swing * 4)
        else:
            left_arm_offset = 0
            right_arm_offset = 0
        
        pygame.draw.rect(surface, self.shirt_color, (x - 13, y + 2 + left_arm_offset, 4, 10))
        pygame.draw.rect(surface, self.shirt_color, (x + 9, y + 2 + right_arm_offset, 4, 10))
        
        # 绘制头（背面）
        head_bounce = 0
        if self.substate == self.SUBSTATE_WALKING:
            head_bounce = math.sin(self.anim_frame * math.pi / 2) * 1
        
        head_y = y - 8 + int(head_bounce)
        head_x = x
        
        # 背面头部
        pygame.draw.ellipse(surface, COLORS['skin'], (head_x - 10, head_y - 4, 20, 18))
        
        # 背面头发（更多头发，因为看不到脸）
        hair_style = self.id % 3
        if hair_style == 0:  # 平头
            pygame.draw.rect(surface, self.hair_color, (head_x - 10, head_y - 8, 20, 9))
            pygame.draw.rect(surface, self.hair_color, (head_x - 10, head_y - 4, 4, 8))
            pygame.draw.rect(surface, self.hair_color, (head_x + 6, head_y - 4, 4, 8))
            pygame.draw.rect(surface, self.hair_color, (head_x - 8, head_y - 10, 16, 4))
        elif hair_style == 1:  # 中分
            pygame.draw.rect(surface, self.hair_color, (head_x - 10, head_y - 10, 20, 8))
            pygame.draw.rect(surface, self.hair_color, (head_x - 2, head_y - 10, 4, 12))
            pygame.draw.rect(surface, self.hair_color, (head_x - 10, head_y - 8, 4, 10))
            pygame.draw.rect(surface, self.hair_color, (head_x + 6, head_y - 8, 4, 10))
        else:  # 短发
            pygame.draw.rect(surface, self.hair_color, (head_x - 10, head_y - 10, 20, 9))
            pygame.draw.rect(surface, self.hair_color, (head_x - 10, head_y - 8, 4, 12))
            pygame.draw.rect(surface, self.hair_color, (head_x + 6, head_y - 8, 4, 12))
            pygame.draw.rect(surface, self.hair_color, (head_x - 6, head_y - 12, 12, 4))
    
    def _draw_robot_front(self, surface):
        """绘制机器人正面形象"""
        draw_y = self.visual_y
        if self.is_sitting:
            draw_y += 8
        
        walk_cycle = self.anim_frame * math.pi / 2
        bounce = abs(math.sin(walk_cycle)) * 1.5 if self.substate == self.SUBSTATE_WALKING else 0
        
        body_y = draw_y - self.size // 2 + bounce
        x = int(self.visual_x)
        y = int(body_y)
        
        # 机器人颜色
        body_color = (180, 190, 200)  # 银灰色
        joint_color = (120, 130, 140)  # 深灰色关节
        eye_color = (100, 200, 255)  # 蓝色眼睛
        
        # ===== 腿部（机械腿） =====
        if not self.is_sitting:
            if self.substate == self.SUBSTATE_WALKING:
                left_angle = math.sin(walk_cycle) * 0.3
                right_angle = math.sin(walk_cycle + math.pi) * 0.3
                self._draw_robot_leg(surface, x - 6, y + 12, left_angle, body_color, joint_color)
                self._draw_robot_leg(surface, x + 6, y + 12, right_angle, body_color, joint_color)
            else:
                self._draw_robot_leg(surface, x - 6, y + 12, 0, body_color, joint_color)
                self._draw_robot_leg(surface, x + 6, y + 12, 0, body_color, joint_color)
        else:
            # 坐姿腿部
            pygame.draw.rect(surface, body_color, (x - 8, y + 12, 5, 8))
            pygame.draw.rect(surface, body_color, (x + 3, y + 12, 5, 8))
            pygame.draw.circle(surface, joint_color, (x - 5, y + 18), 3)
            pygame.draw.circle(surface, joint_color, (x + 5, y + 18), 3)
        
        # ===== 身体（机械躯干） =====
        body_w, body_h = 18, 16
        # 主体
        body_rect = pygame.Rect(x - body_w//2, y - 2, body_w, body_h)
        pygame.draw.rect(surface, body_color, body_rect, border_radius=4)
        pygame.draw.rect(surface, joint_color, body_rect, 2, border_radius=4)
        
        # 胸部显示屏
        screen_rect = pygame.Rect(x - 6, y + 2, 12, 8)
        pygame.draw.rect(surface, (50, 60, 70), screen_rect, border_radius=2)
        # 屏幕上的状态灯
        if self.energy > 50:
            pygame.draw.circle(surface, (100, 255, 100), (x - 3, y + 6), 2)  # 绿灯
        else:
            pygame.draw.circle(surface, (255, 100, 100), (x - 3, y + 6), 2)  # 红灯
        pygame.draw.circle(surface, (100, 200, 255), (x + 3, y + 6), 2)  # 蓝灯
        
        # ===== 手臂（机械臂） =====
        if self.substate == self.SUBSTATE_WALKING:
            left_arm_angle = math.sin(walk_cycle + math.pi) * 0.4
            right_arm_angle = math.sin(walk_cycle) * 0.4
        else:
            left_arm_angle = 0
            right_arm_angle = 0
        
        self._draw_robot_arm(surface, x - 12, y + 2, left_arm_angle, body_color, joint_color)
        self._draw_robot_arm(surface, x + 12, y + 2, right_arm_angle, body_color, joint_color)
        
        # ===== 头部（机器人头） =====
        head_bounce = math.sin(walk_cycle) * 0.5 if self.substate == self.SUBSTATE_WALKING else 0
        head_y = y - 10 + int(head_bounce)
        
        # 头部主体
        head_rect = pygame.Rect(x - 10, head_y - 4, 20, 16)
        pygame.draw.rect(surface, body_color, head_rect, border_radius=3)
        pygame.draw.rect(surface, joint_color, head_rect, 2, border_radius=3)
        
        # 眼睛（发光）
        pygame.draw.ellipse(surface, eye_color, (x - 7, head_y + 2, 5, 6))
        pygame.draw.ellipse(surface, eye_color, (x + 2, head_y + 2, 5, 6))
        # 眼睛高光
        pygame.draw.circle(surface, (255, 255, 255), (x - 5, head_y + 4), 1)
        pygame.draw.circle(surface, (255, 255, 255), (x + 4, head_y + 4), 1)
        
        # 天线
        pygame.draw.line(surface, joint_color, (x, head_y - 4), (x, head_y - 10), 2)
        pygame.draw.circle(surface, (255, 100, 100), (x, head_y - 10), 2)  # 红色指示灯
    
    def _draw_robot_back(self, surface):
        """绘制机器人背面形象（工作时面向电脑）"""
        draw_y = self.visual_y
        if self.is_sitting:
            draw_y += 8
        
        # 工作时轻微动作（打字动画）
        type_cycle = self.anim_frame * math.pi / 2
        type_bounce = math.sin(type_cycle) * 0.5 if self.substate == self.SUBSTATE_SITTING else 0
        
        body_y = draw_y - self.size // 2 + type_bounce
        x = int(self.visual_x)
        y = int(body_y)
        
        # 机器人颜色
        body_color = (180, 190, 200)  # 银灰色
        joint_color = (120, 130, 140)  # 深灰色关节
        
        # ===== 腿部（坐姿） =====
        pygame.draw.rect(surface, body_color, (x - 8, y + 12, 5, 8))
        pygame.draw.rect(surface, body_color, (x + 3, y + 12, 5, 8))
        pygame.draw.circle(surface, joint_color, (x - 5, y + 18), 3)
        pygame.draw.circle(surface, joint_color, (x + 5, y + 18), 3)
        
        # ===== 身体（背面） =====
        body_w, body_h = 18, 16
        body_rect = pygame.Rect(x - body_w//2, y - 2, body_w, body_h)
        pygame.draw.rect(surface, body_color, body_rect, border_radius=4)
        pygame.draw.rect(surface, joint_color, body_rect, 2, border_radius=4)
        
        # 背部散热口
        for i in range(3):
            pygame.draw.line(surface, (100, 110, 120), 
                           (x - 6, y + 4 + i * 4), (x + 6, y + 4 + i * 4), 2)
        
        # ===== 手臂（打字动作） =====
        # 左臂打字
        left_hand_x = x - 8 + math.sin(type_cycle) * 2
        pygame.draw.line(surface, body_color, (x - 12, y + 4), (left_hand_x, y + 10), 4)
        pygame.draw.circle(surface, joint_color, (int(left_hand_x), y + 10), 3)
        
        # 右臂打字
        right_hand_x = x + 8 + math.cos(type_cycle) * 2
        pygame.draw.line(surface, body_color, (x + 12, y + 4), (right_hand_x, y + 10), 4)
        pygame.draw.circle(surface, joint_color, (int(right_hand_x), y + 10), 3)
        
        # ===== 头部（背面） =====
        head_y = y - 10 + int(type_bounce)
        
        # 头部主体
        head_rect = pygame.Rect(x - 10, head_y - 4, 20, 16)
        pygame.draw.rect(surface, body_color, head_rect, border_radius=3)
        pygame.draw.rect(surface, joint_color, head_rect, 2, border_radius=3)
        
        # 后脑勺接口
        pygame.draw.circle(surface, (80, 90, 100), (x, head_y + 4), 4)
        pygame.draw.circle(surface, (100, 200, 255), (x, head_y + 4), 2)  # 蓝色指示灯
        
        # 天线（背面）
        pygame.draw.line(surface, joint_color, (x, head_y - 4), (x, head_y - 10), 2)
        pygame.draw.circle(surface, (100, 200, 100), (x, head_y - 10), 2)  # 绿色指示灯
    
    def _draw_robot_leg(self, surface, x, y, angle, body_color, joint_color):
        """绘制机器人腿部"""
        leg_len = 7
        
        # 大腿
        thigh_end_x = x + math.sin(angle) * leg_len
        thigh_end_y = y + math.cos(angle) * leg_len
        pygame.draw.line(surface, body_color, (x, y), (thigh_end_x, thigh_end_y), 5)
        pygame.draw.circle(surface, joint_color, (int(thigh_end_x), int(thigh_end_y)), 3)
        
        # 小腿
        knee_angle = angle * 0.5
        calf_end_x = thigh_end_x + math.sin(knee_angle) * leg_len
        calf_end_y = thigh_end_y + math.cos(knee_angle) * leg_len
        pygame.draw.line(surface, body_color, (thigh_end_x, thigh_end_y), (calf_end_x, calf_end_y), 4)
        
        # 脚
        pygame.draw.ellipse(surface, joint_color, (calf_end_x - 3, calf_end_y - 1, 6, 4))
    
    def _draw_robot_arm(self, surface, x, y, angle, body_color, joint_color):
        """绘制机器人手臂"""
        upper_len = 5
        lower_len = 4
        
        # 上臂
        upper_end_x = x + math.sin(angle) * upper_len
        upper_end_y = y + math.cos(angle) * upper_len
        pygame.draw.line(surface, body_color, (x, y), (upper_end_x, upper_end_y), 4)
        pygame.draw.circle(surface, joint_color, (int(upper_end_x), int(upper_end_y)), 2)
        
        # 前臂
        elbow_angle = angle + 0.1
        hand_x = upper_end_x + math.sin(elbow_angle) * lower_len
        hand_y = upper_end_y + math.cos(elbow_angle) * lower_len
        pygame.draw.line(surface, body_color, (upper_end_x, upper_end_y), (hand_x, hand_y), 3)
        
        # 机械手
        pygame.draw.circle(surface, joint_color, (int(hand_x), int(hand_y)), 3)
    
    def get_rect(self):
        """获取碰撞矩形"""
        return pygame.Rect(
            self.x - self.size // 2,
            self.y - self.size // 2,
            self.size,
            self.size
        )
