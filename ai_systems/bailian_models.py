# -*- coding: utf-8 -*-
"""
阿里云百炼平台 - 免费模型配置
API URL: https://dashscope.aliyuncs.com/compatible-mode/v1

根据对员工AI的有用程度排序，优先使用更强的模型
当模型额度用尽时自动切换到下一个

用户实际开启的模型列表（已按优先级排序）
"""

from typing import List, Dict, Optional
from dataclasses import dataclass


@dataclass
class ModelConfig:
    """模型配置"""
    name: str  # 模型名称（API调用名）
    display_name: str  # 显示名称
    description: str  # 模型描述
    context_length: int  # 上下文长度
    priority: int  # 优先级（数字越小优先级越高）
    free_quota: str  # 免费额度说明
    use_case: str  # 适用场景
    is_thinking_model: bool = False  # 是否思考模型


# ==================== 用户实际开启的模型（按优先级排序） ====================
# 优先级规则：
# 1-10: 最强通用模型（Max/Plus系列）
# 11-20: 视觉理解模型（VL系列）
# 21-30: 代码/数学专用模型
# 31-40: 推理模型（QwQ/DeepSeek）
# 41-50: 轻量级/翻译模型
# 51+: 备用模型

BAILIAN_MODELS: List[ModelConfig] = [
    # ===== 第一梯队：最强通用模型 =====
    ModelConfig(
        name="qwen-max",
        display_name="Qwen-Max",
        description="千问系列最强商业版模型，适合复杂任务",
        context_length=32768,
        priority=1,
        free_quota="100万Token (2026/06/08)",
        use_case="复杂任务规划、深度推理、代码生成",
        is_thinking_model=True
    ),
    ModelConfig(
        name="qwen3.6-plus",
        display_name="Qwen3.6-Plus",
        description="效果、速度、成本均衡，支持多模态",
        context_length=1000000,
        priority=2,
        free_quota="100万Token (2026/07/02)",
        use_case="通用对话、中等复杂度任务、多模态理解",
        is_thinking_model=True
    ),
    ModelConfig(
        name="qwen-plus-2025-07-28",
        display_name="Qwen-Plus-0728",
        description="能力均衡的Plus版本",
        context_length=131072,
        priority=3,
        free_quota="100万Token (2026/06/08)",
        use_case="通用任务、日常对话",
        is_thinking_model=True
    ),
    ModelConfig(
        name="qwen-plus",
        display_name="Qwen-Plus",
        description="能力均衡，介于Max和Flash之间",
        context_length=131072,
        priority=4,
        free_quota="100万Token (2026/06/08)",
        use_case="中等复杂任务、日常对话",
        is_thinking_model=True
    ),

    # ===== 第二梯队：视觉理解模型 =====
    ModelConfig(
        name="qwen3-vl-235b-a22b-thinking",
        display_name="Qwen3-VL-235B-Thinking",
        description="最强视觉理解模型，235B参数，支持思考",
        context_length=131072,
        priority=11,
        free_quota="100万Token (2026/06/08)",
        use_case="图像理解、视觉推理、OCR、图文分析",
        is_thinking_model=True
    ),
    ModelConfig(
        name="qwen3-vl-32b-thinking",
        display_name="Qwen3-VL-32B-Thinking",
        description="视觉理解模型，32B参数，支持思考",
        context_length=131072,
        priority=12,
        free_quota="100万Token (2026/06/08)",
        use_case="图像理解、视觉推理、图文分析",
        is_thinking_model=True
    ),
    ModelConfig(
        name="qwen3-vl-30b-a3b-thinking",
        display_name="Qwen3-VL-30B-Thinking",
        description="视觉理解模型，30B参数，支持思考",
        context_length=65536,
        priority=13,
        free_quota="100万Token (2026/06/08)",
        use_case="图像理解、视觉推理",
        is_thinking_model=True
    ),
    ModelConfig(
        name="qwen2.5-vl-72b-instruct",
        display_name="Qwen2.5-VL-72B",
        description="Qwen2.5视觉理解模型，72B参数",
        context_length=131072,
        priority=14,
        free_quota="100万Token (2026/06/08)",
        use_case="图像理解、视频理解、视觉定位",
        is_thinking_model=False
    ),
    ModelConfig(
        name="qwen-vl-plus-latest",
        display_name="Qwen-VL-Plus-Latest",
        description="最新版视觉理解Plus模型",
        context_length=131072,
        priority=15,
        free_quota="100万Token (2026/06/08)",
        use_case="图像理解、OCR、图文分析",
        is_thinking_model=False
    ),
    ModelConfig(
        name="qwen-vl-plus-2025-05-07",
        display_name="Qwen-VL-Plus-0507",
        description="视觉理解Plus模型",
        context_length=131072,
        priority=16,
        free_quota="100万Token (2026/06/08)",
        use_case="图像理解、OCR",
        is_thinking_model=False
    ),
    ModelConfig(
        name="qwen2.5-vl-3b-instruct",
        display_name="Qwen2.5-VL-3B",
        description="轻量级视觉理解模型",
        context_length=32768,
        priority=17,
        free_quota="100万Token (2026/06/08)",
        use_case="简单图像理解、快速OCR",
        is_thinking_model=False
    ),
    ModelConfig(
        name="qwen-vl-ocr-latest",
        display_name="Qwen-VL-OCR-Latest",
        description="OCR专用模型",
        context_length=8192,
        priority=18,
        free_quota="100万Token (2026/06/08)",
        use_case="文字识别、文档解析",
        is_thinking_model=False
    ),

    # ===== 第三梯队：代码专用模型 =====
    ModelConfig(
        name="qwen-coder-turbo-0919",
        display_name="Qwen-Coder-Turbo",
        description="代码生成Turbo模型",
        context_length=131072,
        priority=21,
        free_quota="100万Token (2026/06/08)",
        use_case="代码生成、代码审查、编程辅助",
        is_thinking_model=False
    ),

    # ===== 第四梯队：数学专用模型 =====
    ModelConfig(
        name="qwen-math-turbo",
        display_name="Qwen-Math-Turbo",
        description="数学解题Turbo模型",
        context_length=4096,
        priority=31,
        free_quota="100万Token (2026/06/08)",
        use_case="数学解题、数学推理",
        is_thinking_model=False
    ),
    ModelConfig(
        name="qwen2.5-math-7b-instruct",
        display_name="Qwen2.5-Math-7B",
        description="数学解题模型，7B参数",
        context_length=4096,
        priority=32,
        free_quota="100万Token (2026/06/08)",
        use_case="数学解题、数学推理",
        is_thinking_model=False
    ),

    # ===== 第五梯队：推理模型 =====
    ModelConfig(
        name="qvq-max-2025-03-25",
        display_name="QvQ-Max-0325",
        description="视觉推理最强模型",
        context_length=131072,
        priority=41,
        free_quota="100万Token (2026/06/08)",
        use_case="视觉推理、数学推理、逻辑分析",
        is_thinking_model=True
    ),
    ModelConfig(
        name="deepseek-r1-distill-qwen-7b",
        display_name="DeepSeek-R1-Distill-Qwen-7B",
        description="DeepSeek蒸馏模型，7B参数",
        context_length=32768,
        priority=42,
        free_quota="100万Token (2026/06/08)",
        use_case="推理任务、代码生成",
        is_thinking_model=True
    ),

    # ===== 第六梯队：轻量级模型 =====
    ModelConfig(
        name="qwen3-32b",
        display_name="Qwen3-32B",
        description="开源版32B参数模型",
        context_length=129024,
        priority=51,
        free_quota="100万Token (2026/06/08)",
        use_case="通用任务、代码生成",
        is_thinking_model=True
    ),
    ModelConfig(
        name="qwen2.5-14b-instruct",
        display_name="Qwen2.5-14B",
        description="Qwen2.5指令模型，14B参数",
        context_length=131072,
        priority=52,
        free_quota="100万Token (2026/06/08)",
        use_case="简单任务、快速响应",
        is_thinking_model=False
    ),

    # ===== 第七梯队：翻译模型 =====
    ModelConfig(
        name="qwen-mt-flash",
        display_name="Qwen-MT-Flash",
        description="翻译专用Flash模型",
        context_length=16384,
        priority=61,
        free_quota="100万Token (2026/06/08)",
        use_case="多语言翻译",
        is_thinking_model=False
    ),
]

# ==================== 智谱GLM模型（备用） ====================
GLM_MODELS: List[ModelConfig] = [
    ModelConfig(
        name="glm-5",
        display_name="GLM-5",
        description="智谱最新GLM-5模型",
        context_length=128000,
        priority=71,
        free_quota="100万Token (2026/06/08)",
        use_case="通用对话、中文理解",
        is_thinking_model=False
    ),
    ModelConfig(
        name="glm-4",
        display_name="GLM-4",
        description="智谱GLM-4模型",
        context_length=128000,
        priority=72,
        free_quota="根据智谱平台政策",
        use_case="中文对话、内容生成",
        is_thinking_model=False
    ),
    ModelConfig(
        name="glm-4-flash",
        display_name="GLM-4-Flash",
        description="智谱GLM-4快速版",
        context_length=128000,
        priority=73,
        free_quota="根据智谱平台政策",
        use_case="快速响应、简单任务",
        is_thinking_model=False
    ),
]

# ==================== 合并所有模型（按优先级排序） ====================
ALL_MODELS: List[ModelConfig] = sorted(
    BAILIAN_MODELS + GLM_MODELS,
    key=lambda x: x.priority
)

# ==================== API配置 ====================
BAILIAN_API_URL = "https://dashscope.aliyuncs.com/compatible-mode/v1"

# 默认API密钥
DEFAULT_BAILIAN_API_KEY = "sk-7c497750be384766a027179211f1c010"


def get_model_by_priority(priority: int) -> Optional[ModelConfig]:
    """根据优先级获取模型配置"""
    for model in ALL_MODELS:
        if model.priority == priority:
            return model
    return None


def get_next_available_model(current_priority: int) -> Optional[ModelConfig]:
    """获取下一个可用模型（当当前模型额度用尽时）"""
    for model in ALL_MODELS:
        if model.priority > current_priority:
            return model
    return None


def get_models_by_use_case(use_case: str) -> List[ModelConfig]:
    """根据使用场景获取模型列表"""
    return [m for m in ALL_MODELS if use_case.lower() in m.use_case.lower()]


def get_models_by_category() -> Dict[str, List[ModelConfig]]:
    """按类别获取模型"""
    categories = {
        "通用模型": [],
        "视觉模型": [],
        "代码模型": [],
        "数学模型": [],
        "推理模型": [],
        "轻量模型": [],
        "其他": []
    }
    
    for model in ALL_MODELS:
        if "视觉" in model.use_case or "VL" in model.name.upper() or "OCR" in model.name.upper():
            categories["视觉模型"].append(model)
        elif "代码" in model.use_case or "coder" in model.name.lower():
            categories["代码模型"].append(model)
        elif "数学" in model.use_case or "math" in model.name.lower():
            categories["数学模型"].append(model)
        elif "推理" in model.use_case or "qvq" in model.name.lower() or "deepseek" in model.name.lower():
            categories["推理模型"].append(model)
        elif model.priority >= 51:
            categories["轻量模型"].append(model)
        elif model.priority <= 10:
            categories["通用模型"].append(model)
        else:
            categories["其他"].append(model)
    
    return categories


def print_model_list():
    """打印所有可用模型列表"""
    print("=" * 100)
    print("阿里云百炼 + 智谱GLM 可用模型列表（用户实际开启）")
    print("=" * 100)
    print(f"{'优先级':<8}{'模型名称':<35}{'显示名称':<25}{'上下文':<10}{'免费额度'}")
    print("-" * 100)
    for model in ALL_MODELS:
        ctx = f"{model.context_length/1000:.0f}K" if model.context_length < 1000000 else f"{model.context_length/1000000:.1f}M"
        print(f"{model.priority:<8}{model.name:<35}{model.display_name:<25}{ctx:<10}{model.free_quota}")
    print("=" * 100)
    print(f"\n总计: {len(ALL_MODELS)} 个模型")


def print_models_by_category():
    """按类别打印模型"""
    categories = get_models_by_category()
    
    print("\n" + "=" * 80)
    print("模型分类列表")
    print("=" * 80)
    
    for category, models in categories.items():
        if models:
            print(f"\n【{category}】")
            print("-" * 80)
            for model in models:
                thinking = "[思考]" if model.is_thinking_model else ""
                print(f"  {model.priority:2d}. {model.display_name:<25} - {model.description[:40]}... {thinking}")
    
    print("\n" + "=" * 80)


if __name__ == "__main__":
    print_model_list()
    print_models_by_category()
