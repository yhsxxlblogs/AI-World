# 员工对话系统 - 休息区员工之间的随机对话
import random
import math
import pygame
from typing import List, Dict, Tuple, Optional
from core.config import get_font

# 对话主题库
DIALOGUE_TOPICS = {
    'food': {
        'name': '美食',
        'starters': [
            "中午吃啥好？",
            "附近新开了家火锅店",
            "昨天那家外卖真不错",
            "减肥计划又失败了",
            "想喝奶茶了",
        ],
        'responses': [
            "好啊好啊！",
            "我也想吃",
            "带上我！",
            "太远了不想动",
            "刚吃完又饿？",
            "减肥呢别诱惑我",
        ],
    },
    'work': {
        'name': '工作吐槽',
        'starters': [
            "这需求改第几版了？",
            "老板又画饼了",
            "今天能准时下班吗",
            "KPI压力山大",
            "这项目要延期了",
        ],
        'responses': [
            "习惯就好",
            "淡定淡定",
            "一起摸鱼？",
            "卷不动了",
            "躺平吧",
            "加油打工人",
        ],
    },
    'weather': {
        'name': '天气',
        'starters': [
            "今天真热啊",
            "好像要下雨了",
            "这天气适合睡觉",
            "空调开太低了",
            "明天降温记得带外套",
        ],
        'responses': [
            "是啊是啊",
            "最讨厌这种天气",
            "想在家躺着",
            "公司空调不要钱吗",
            "已经感冒了",
        ],
    },
    'weekend': {
        'name': '周末计划',
        'starters': [
            "周末有啥安排？",
            "想去爬山",
            "在家打游戏",
            "又要加班",
            "约个电影？",
        ],
        'responses': [
            "好啊一起！",
            "已经安排满了",
            "宅家不香吗",
            "加班狗不配拥有周末",
            "看情况吧",
        ],
    },
    'gossip': {
        'name': '八卦',
        'starters': [
            "听说隔壁部门...",
            "那个新来的...",
            "你知道吗？",
            "有大瓜！",
            "小道消息",
        ],
        'responses': [
            "真的假的？",
            "快说快说！",
            "我早就知道了",
            "不会吧",
            "细说细说",
            "保熟吗这瓜",
        ],
    },
    'tech': {
        'name': '科技',
        'starters': [
            "新出的那款手机...",
            "AI又进化了",
            "显卡降价了吗",
            "这个框架真香",
            "bug修不完",
        ],
        'responses': [
            "买不起买不起",
            "等等党永不为奴",
            "已经入手了",
            "还在观望",
            "技术迭代太快了",
        ],
    },
}

# 员工特定对话风格
EMPLOYEE_DIALOGUE_STYLES = {
    0: {  # 小明 - 技术宅
        'prefixes': ["哎，", "说实话，", "讲道理，", "不是我说，"],
        'suffixes': ["...", "（叹气）", "（推眼镜）", "（喝咖啡）"],
    },
    1: {  # 小红 - 人事
        'prefixes': ["哎呀，", "亲爱的，", "宝，", "跟你说哦，"],
        'suffixes': ["~", "（眨眼）", "（笑）", "（比心）"],
    },
    2: {  # 阿强 - 市场
        'prefixes': ["兄弟，", "信我，", "没问题，", "包在我身上，"],
        'suffixes': ["！", "（拍胸脯）", "（自信笑）", "（握手）"],
    },
    3: {  # 小丽 - 财务
        'prefixes': ["那个，", "说实话，", "从数据看，", "精打细算的话，"],
        'suffixes': ["...", "（算笔账）", "（皱眉）", "（叹气）"],
    },
    4: {  # 大伟 - 运营
        'prefixes': ["随便吧，", "佛系点，", "随缘，", "都行，"],
        'suffixes': ["...", "（躺平）", "（喝茶）", "（无所谓）"],
    },
    5: {  # 晓晓 - 行政
        'prefixes': ["大家注意，", "温馨提示，", "那个，", "记得哦，"],
        'suffixes': ["~", "（微笑）", "（递水）", "（整理东西）"],
    },
}


class DialogueBubble:
    """对话气泡"""
    
    def __init__(self, employee_id: int, text: str, is_starter: bool = True):
        self.employee_id = employee_id
        self.text = text
        self.is_starter = is_starter  # 是否是发起者
        self.duration = 4000 if is_starter else 3000  # 发起者显示更久
        self.timer = self.duration
        self.alpha = 255
        
    def update(self, dt: int):
        """更新气泡状态"""
        self.timer -= dt
        
        # 淡出效果
        if self.timer < 500:
            self.alpha = int(255 * (self.timer / 500))
        
        return self.timer > 0
    
    def is_expired(self) -> bool:
        """检查是否过期"""
        return self.timer <= 0


class EmployeeDialogueSystem:
    """员工对话系统 - 管理休息区员工之间的对话"""
    
    def __init__(self):
        self.active_dialogues: Dict[int, DialogueBubble] = {}  # employee_id -> DialogueBubble
        self.dialogue_cooldowns: Dict[int, int] = {}  # employee_id -> last_dialogue_time
        self.cooldown_duration = 25000  # 对话冷却时间 25秒
        self.min_distance = 50  # 触发对话的最小距离（像素）- 必须靠得很近
        self.max_distance = 100  # 触发对话的最大距离（像素）- 最大100像素
        self.dialogue_chance = 0.012  # 每帧对话触发概率（约每8秒检查一次）
        self.font = None  # 延迟初始化
        
    def update(self, employees: List, current_time: int):
        """更新对话系统"""
        # 延迟初始化字体
        if self.font is None:
            self.font = get_font(10)
        
        # 更新现有对话
        expired_dialogues = []
        for emp_id, dialogue in self.active_dialogues.items():
            if not dialogue.update(16):  # 假设16ms一帧
                expired_dialogues.append(emp_id)
        
        # 移除过期对话
        for emp_id in expired_dialogues:
            del self.active_dialogues[emp_id]
        
        # 尝试触发新对话
        self._try_trigger_dialogue(employees, current_time)
    
    def _try_trigger_dialogue(self, employees: List, current_time: int):
        """尝试触发新对话"""
        # 随机触发检查
        if random.random() > self.dialogue_chance:
            return
        
        # 检查是否有任何员工正在显示单人消息气泡
        for emp in employees:
            if emp.message_bubble_timer > 0:
                return  # 有人正在说话，不触发对话
        
        # 检查是否已有活跃对话
        if len(self.active_dialogues) > 0:
            return  # 已有对话在进行中
        
        # 只考虑在休息区的员工
        rest_employees = [e for e in employees 
                         if e.state == 'rest' and e.id not in self.active_dialogues]
        
        if len(rest_employees) < 2:
            return
        
        # 随机选择一个员工作为发起者
        starter = random.choice(rest_employees)
        
        # 检查冷却时间
        if starter.id in self.dialogue_cooldowns:
            if current_time - self.dialogue_cooldowns[starter.id] < self.cooldown_duration:
                return
        
        # 寻找附近的其他员工
        nearby_employees = self._find_nearby_employees(starter, rest_employees)
        
        if not nearby_employees:
            return
        
        # 选择一个回应者
        responder = random.choice(nearby_employees)
        
        # 检查回应者的冷却时间
        if responder.id in self.dialogue_cooldowns:
            if current_time - self.dialogue_cooldowns[responder.id] < self.cooldown_duration:
                return
        
        # 生成对话
        self._generate_dialogue(starter, responder, current_time)
    
    def _find_nearby_employees(self, employee, all_employees) -> List:
        """找到附近的员工"""
        nearby = []
        for other in all_employees:
            if other.id == employee.id:
                continue
            
            distance = math.sqrt((employee.x - other.x)**2 + (employee.y - other.y)**2)
            
            # 距离在有效范围内
            if self.min_distance <= distance <= self.max_distance:
                nearby.append(other)
        
        return nearby
    
    def _generate_dialogue(self, starter, responder, current_time: int):
        """生成对话内容"""
        # 随机选择主题
        topic_key = random.choice(list(DIALOGUE_TOPICS.keys()))
        topic = DIALOGUE_TOPICS[topic_key]
        
        # 生成发起者对话
        starter_text = self._format_dialogue_text(starter.id, topic['starters'], True)
        
        # 生成回应者对话
        responder_text = self._format_dialogue_text(responder.id, topic['responses'], False)
        
        # 创建对话气泡
        self.active_dialogues[starter.id] = DialogueBubble(starter.id, starter_text, True)
        
        # 回应者延迟显示（0.8秒后）
        responder_dialogue = DialogueBubble(responder.id, responder_text, False)
        responder_dialogue.timer = -800  # 负值表示延迟显示
        self.active_dialogues[responder.id] = responder_dialogue
        
        # 更新冷却时间
        self.dialogue_cooldowns[starter.id] = current_time
        self.dialogue_cooldowns[responder.id] = current_time
        
        print(f"[对话] {starter.name} -> {responder.name}: {starter_text}")
        print(f"[对话] {responder.name} 回应: {responder_text}")
    
    def _format_dialogue_text(self, employee_id: int, text_options: List[str], is_starter: bool) -> str:
        """格式化对话文本，添加员工个性"""
        text = random.choice(text_options)
        
        # 添加个性化前缀/后缀
        if employee_id in EMPLOYEE_DIALOGUE_STYLES:
            style = EMPLOYEE_DIALOGUE_STYLES[employee_id]
            if random.random() < 0.5:  # 50%概率添加前缀
                prefix = random.choice(style['prefixes'])
                text = prefix + text
            if random.random() < 0.3:  # 30%概率添加后缀
                suffix = random.choice(style['suffixes'])
                text = text + suffix
        
        return text
    
    def draw(self, surface: pygame.Surface, employees: List):
        """绘制对话气泡"""
        if self.font is None:
            return
        
        for emp_id, dialogue in self.active_dialogues.items():
            # 跳过延迟显示的对话
            if dialogue.timer < 0:
                continue
            
            # 找到对应的员工
            employee = None
            for emp in employees:
                if emp.id == emp_id:
                    employee = emp
                    break
            
            if employee is None:
                continue
            
            self._draw_dialogue_bubble(surface, employee, dialogue)
    
    def _draw_dialogue_bubble(self, surface: pygame.Surface, employee, dialogue: DialogueBubble):
        """绘制单个对话气泡"""
        # 计算气泡位置（头部上方，比消息气泡更高）
        padding = 4
        text_surface = self.font.render(dialogue.text, True, (50, 50, 50))
        text_width = text_surface.get_width()
        text_height = text_surface.get_height()
        
        bubble_width = text_width + padding * 2
        bubble_height = text_height + padding * 2
        
        # 位置：头部上方55像素
        bubble_x = int(employee.visual_x - bubble_width // 2)
        bubble_y = int(employee.visual_y - employee.size // 2 - 55 - bubble_height)
        
        # 确保不超出屏幕
        bubble_y = max(2, bubble_y)
        bubble_x = max(2, min(bubble_x, surface.get_width() - bubble_width - 2))
        
        # 创建带透明度的表面
        bubble_surface = pygame.Surface((bubble_width, bubble_height + 5), pygame.SRCALPHA)
        
        # 对话气泡颜色（与消息气泡区分）
        if dialogue.is_starter:
            # 发起者：淡绿色
            bg_color = (230, 255, 230, dialogue.alpha)
            border_color = (150, 200, 150, dialogue.alpha)
        else:
            # 回应者：淡粉色
            bg_color = (255, 230, 240, dialogue.alpha)
            border_color = (200, 150, 170, dialogue.alpha)
        
        # 绘制气泡
        pygame.draw.rect(bubble_surface, bg_color, (0, 0, bubble_width, bubble_height), border_radius=5)
        pygame.draw.rect(bubble_surface, border_color, (0, 0, bubble_width, bubble_height), 1, border_radius=5)
        
        # 小三角
        triangle_points = [
            (bubble_width // 2 - 3, bubble_height),
            (bubble_width // 2 + 3, bubble_height),
            (bubble_width // 2, bubble_height + 5)
        ]
        pygame.draw.polygon(bubble_surface, bg_color, triangle_points)
        pygame.draw.polygon(bubble_surface, border_color, triangle_points, 1)
        
        # 文字
        text_surface.set_alpha(dialogue.alpha)
        bubble_surface.blit(text_surface, (padding, padding))
        
        surface.blit(bubble_surface, (bubble_x, bubble_y))


# 全局对话系统实例
dialogue_system = EmployeeDialogueSystem()
