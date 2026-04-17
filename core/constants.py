# AI World - 常量定义
# 集中管理所有魔法数字和配置常量

import os

# ==================== API 配置 ====================
# 智谱GLM配置（原有）
ZHIPU_API_URL = "https://open.bigmodel.cn/api/paas/v4"
ZHIPU_DEFAULT_MODEL = "glm-4"
ZHIPU_API_KEY = os.environ.get('ZHIPU_API_KEY', '34df82e7443d423495faad8c09fb12ef.EjMYz7tAU4NgcA4Z')

# 阿里云百炼配置
BAILIAN_API_URL = "https://dashscope.aliyuncs.com/compatible-mode/v1"
BAILIAN_API_KEY = os.environ.get('DASHSCOPE_API_KEY', 'sk-7c497750be384766a027179211f1c010')

# 默认API配置（兼容旧代码）
DEFAULT_API_URL = ZHIPU_API_URL
DEFAULT_API_MODEL = ZHIPU_DEFAULT_MODEL
DEFAULT_API_KEY = ZHIPU_API_KEY

# ==================== 员工模型分配配置 ====================
# 为6名员工分配最优模型组合（基于优先级）
# 优先级1-4: 通用最强模型
# 优先级11-18: 视觉理解模型
# 优先级21: 代码模型
# 优先级31-32: 数学模型
# 优先级41-42: 推理模型
# 优先级51-52: 轻量级模型
EMPLOYEE_MODEL_ASSIGNMENTS = {
    0: {"model": "qwen-max", "api_url": BAILIAN_API_URL, "api_key": BAILIAN_API_KEY, "desc": "最强通用模型"},
    1: {"model": "qwen3.6-plus", "api_url": BAILIAN_API_URL, "api_key": BAILIAN_API_KEY, "desc": "多模态均衡模型"},
    2: {"model": "qwen3-vl-235b-a22b-thinking", "api_url": BAILIAN_API_URL, "api_key": BAILIAN_API_KEY, "desc": "最强视觉理解"},
    3: {"model": "qwen-coder-turbo-0919", "api_url": BAILIAN_API_URL, "api_key": BAILIAN_API_KEY, "desc": "代码专用模型"},
    4: {"model": "qvq-max-2025-03-25", "api_url": BAILIAN_API_URL, "api_key": BAILIAN_API_KEY, "desc": "推理专用模型"},
    5: {"model": "qwen-plus", "api_url": BAILIAN_API_URL, "api_key": BAILIAN_API_KEY, "desc": "通用均衡模型"},
}

# 备用模型配置（当主要模型额度用尽时使用）
FALLBACK_MODELS = [
    {"model": "qwen-plus-2025-07-28", "api_url": BAILIAN_API_URL, "api_key": BAILIAN_API_KEY},
    {"model": "qwen3-vl-32b-thinking", "api_url": BAILIAN_API_URL, "api_key": BAILIAN_API_KEY},
    {"model": "qwen-math-turbo", "api_url": BAILIAN_API_URL, "api_key": BAILIAN_API_KEY},
    {"model": "deepseek-r1-distill-qwen-7b", "api_url": BAILIAN_API_URL, "api_key": BAILIAN_API_KEY},
    {"model": "qwen3-32b", "api_url": BAILIAN_API_URL, "api_key": BAILIAN_API_KEY},
    {"model": "glm-5", "api_url": ZHIPU_API_URL, "api_key": ZHIPU_API_KEY},
]

# ==================== 时间常量 (毫秒) ====================
# 动画时间
CURSOR_BLINK_INTERVAL = 500  # 光标闪烁间隔
MESSAGE_BUBBLE_DURATION = 3000  # 消息气泡显示时间
MIN_MESSAGE_INTERVAL = 30000  # 消息最小间隔时间
WALK_ANIM_SPEED = 300  # 行走动画速度
TURN_DURATION = 150  # 转身动画时间

# 工作/休息时间
WORK_TIME = 6000  # 工作时间
REST_TIME = 4000  # 休息时间

# 随机走动
MIN_WANDER_DELAY = 2000  # 最小随机走动延迟
MAX_WANDER_DELAY = 4000  # 最大随机走动延迟
MIN_WANDER_INTERVAL = 3000  # 最小走动间隔
MAX_WANDER_INTERVAL = 6000  # 最大走动间隔

# ==================== 移动和物理 ====================
# 移动速度
DEFAULT_SPEED = 1.5  # 默认移动速度
SPEED_VARIATION = 0.2  # 速度变化范围 (±20%)

# 平滑移动
MOVE_LERP_SPEED = 0.15  # 移动插值速度

# 寻路
PATH_RANDOM_FACTOR = 0.3  # 路径随机因子
GRID_SIZE = 40  # 网格大小

# ==================== UI 尺寸 ====================
# 规划师聊天界面
MAX_STREAMING_TEXT_LENGTH = 10000  # 最大流式文本长度
STREAMING_DISPLAY_LIMIT = 1500  # 流式显示限制
MAX_DISPLAY_LINES = 20  # 最大显示行数
LINE_HEIGHT = 24  # 行高
SCROLL_SPEED = 50  # 滚动速度
MOUSE_SCROLL_SPEED = 30  # 鼠标滚动速度

# 对话框
DIALOG_PADDING = 40  # 对话框内边距
DIALOG_HEIGHT = 60  # 对话框高度

# 消息气泡
BUBBLE_PADDING = 4  # 气泡内边距
BUBBLE_FLOAT_AMPLITUDE = 1.5  # 气泡浮动幅度
BUBBLE_OFFSET_Y = 28  # 气泡Y轴偏移

# ==================== 游戏数值 ====================
# 员工属性
MAX_HAPPINESS = 100  # 最大满意度
MAX_ENERGY = 100  # 最大能量
DEFAULT_HAPPINESS_MIN = 60  # 默认最小满意度
DEFAULT_HAPPINESS_MAX = 90  # 默认最大满意度
DEFAULT_ENERGY_MIN = 70  # 默认最小能量
DEFAULT_ENERGY_MAX = 100  # 默认最大能量

# 能量消耗/恢复
ENERGY_CONSUMPTION_RATE = 0.002  # 能量消耗速率
ENERGY_RECOVERY_RATE = 0.005  # 能量恢复速率
HAPPINESS_RECOVERY_RATE = 0.002  # 满意度恢复速率
LOW_ENERGY_THRESHOLD = 30  # 低能量阈值
HIGH_HAPPINESS_THRESHOLD = 80  # 高满意度阈值
LOW_HAPPINESS_THRESHOLD = 40  # 低满意度阈值

# ==================== 概率和随机 ====================
MESSAGE_TRIGGER_CHANCE = 0.002  # 消息触发概率

# ==================== 文件路径 ====================
# 目录
SAVE_DIR = "save"
RESULTS_DIR = "results"
SKILL_DIR = "skill"

# 文件
CONFIG_FILE = "api_configs.json"

# ==================== 员工配置 ====================
# 默认员工名称
DEFAULT_EMPLOYEE_NAMES = ['小明', '小红', '阿强', '小丽', '大伟', '晓晓']
DEFAULT_POSITIONS = ['规划师待定', '规划师待定', '规划师待定', '规划师待定', '规划师待定', '规划师待定']

# 预配置API的员工ID
PRECONFIGURED_EMPLOYEE_IDS = [0, 1]
