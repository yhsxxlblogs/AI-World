# -*- coding: utf-8 -*-
"""
模型管理器 - 自动管理多个AI模型的调用和切换
支持阿里云百炼和智谱GLM平台
当模型额度用尽时自动切换到下一个可用模型
"""

import os
import time
from typing import Optional, Dict, List, Callable
from dataclasses import dataclass, field
from datetime import datetime

from openai import OpenAI
from ai_systems.bailian_models import (
    ALL_MODELS, ModelConfig, get_next_available_model,
    BAILIAN_API_URL, DEFAULT_BAILIAN_API_KEY
)


@dataclass
class ModelUsage:
    """模型使用情况记录"""
    model_name: str
    call_count: int = 0
    token_count: int = 0
    last_used: Optional[datetime] = None
    error_count: int = 0
    is_exhausted: bool = False  # 额度是否已用尽


class ModelManager:
    """
    AI模型管理器
    - 管理多个模型配置
    - 自动切换额度用尽的模型
    - 记录使用情况
    """

    def __init__(self, api_key: Optional[str] = None):
        # 阿里云百炼配置
        self.bailian_api_key = api_key or os.environ.get('DASHSCOPE_API_KEY', DEFAULT_BAILIAN_API_KEY)
        self.bailian_client = OpenAI(
            api_key=self.bailian_api_key,
            base_url=BAILIAN_API_URL
        )

        # 智谱GLM配置（原有）
        self.zhipu_api_key = os.environ.get('ZHIPU_API_KEY', '')
        self.zhipu_api_url = "https://open.bigmodel.cn/api/paas/v4"
        self.zhipu_client = None
        if self.zhipu_api_key:
            self.zhipu_client = OpenAI(
                api_key=self.zhipu_api_key,
                base_url=self.zhipu_api_url
            )

        # 模型使用记录
        self.usage_stats: Dict[str, ModelUsage] = {
            model.name: ModelUsage(model_name=model.name)
            for model in ALL_MODELS
        }

        # 当前使用的模型优先级
        self.current_priority = 1

        # 失败重试配置
        self.max_retries = 3
        self.retry_delay = 1  # 秒

    def get_current_model(self) -> Optional[ModelConfig]:
        """获取当前应该使用的模型"""
        for model in ALL_MODELS:
            if model.priority >= self.current_priority:
                usage = self.usage_stats[model.name]
                if not usage.is_exhausted:
                    return model
        return None

    def switch_to_next_model(self):
        """切换到下一个可用模型"""
        current_model = self.get_current_model()
        if current_model:
            # 标记当前模型为已用尽
            self.usage_stats[current_model.name].is_exhausted = True
            print(f"[ModelManager] 模型 {current_model.display_name} 额度已用尽，切换到下一个")

            # 切换到下一个
            next_model = get_next_available_model(current_model.priority)
            if next_model:
                self.current_priority = next_model.priority
                print(f"[ModelManager] 已切换到模型: {next_model.display_name}")
                return next_model

        print("[ModelManager] 警告：所有模型额度均已用尽")
        return None

    def call_model(
        self,
        messages: List[Dict],
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        on_token: Optional[Callable[[str], None]] = None
    ) -> Optional[str]:
        """
        调用模型生成回复
        如果失败或额度用尽，自动切换到下一个模型

        Args:
            messages: 消息列表
            temperature: 温度参数
            max_tokens: 最大生成token数
            on_token: 流式输出回调函数

        Returns:
            生成的文本，如果所有模型都失败则返回None
        """
        retries = 0

        while retries < self.max_retries:
            model = self.get_current_model()
            if not model:
                print("[ModelManager] 错误：没有可用模型")
                return None

            try:
                # 选择客户端
                if model.name.startswith('glm'):
                    client = self.zhipu_client
                    if not client:
                        print(f"[ModelManager] 智谱API未配置，跳过 {model.name}")
                        self.switch_to_next_model()
                        retries += 1
                        continue
                else:
                    client = self.bailian_client

                # 记录使用情况
                usage = self.usage_stats[model.name]
                usage.call_count += 1
                usage.last_used = datetime.now()

                print(f"[ModelManager] 使用模型: {model.display_name}")

                # 调用API
                if on_token:
                    # 流式输出
                    response = client.chat.completions.create(
                        model=model.name,
                        messages=messages,
                        temperature=temperature,
                        max_tokens=max_tokens,
                        stream=True
                    )

                    result = ""
                    for chunk in response:
                        if chunk.choices and chunk.choices[0].delta.content:
                            token = chunk.choices[0].delta.content
                            result += token
                            on_token(token)

                    return result
                else:
                    # 非流式输出
                    response = client.chat.completions.create(
                        model=model.name,
                        messages=messages,
                        temperature=temperature,
                        max_tokens=max_tokens,
                        stream=False
                    )

                    result = response.choices[0].message.content
                    # 估算token使用量
                    usage.token_count += len(result) // 4  # 粗略估算

                    return result

            except Exception as e:
                error_msg = str(e)
                print(f"[ModelManager] 模型 {model.name} 调用失败: {error_msg}")

                usage = self.usage_stats[model.name]
                usage.error_count += 1

                # 检查是否是额度用尽的错误
                if any(keyword in error_msg.lower() for keyword in [
                    'quota', 'exhausted', 'limit', 'insufficient',
                    '额度', '用尽', '不足', '限制'
                ]):
                    print(f"[ModelManager] 检测到额度用尽，切换模型...")
                    next_model = self.switch_to_next_model()
                    if next_model:
                        continue  # 立即尝试新模型

                retries += 1
                if retries < self.max_retries:
                    time.sleep(self.retry_delay)

        # 所有重试都失败
        print("[ModelManager] 错误：所有重试均失败")
        return None

    def get_usage_report(self) -> str:
        """获取使用报告"""
        report = ["\n" + "=" * 80]
        report.append("模型使用报告")
        report.append("=" * 80)
        report.append(f"{'模型名称':<25}{'调用次数':<10}{'Token数':<12}{'错误次数':<10}{'状态'}")
        report.append("-" * 80)

        for model in ALL_MODELS:
            usage = self.usage_stats[model.name]
            status = "已用尽" if usage.is_exhausted else "可用"
            report.append(
                f"{model.display_name:<25}{usage.call_count:<10}{usage.token_count:<12}{usage.error_count:<10}{status}"
            )

        current = self.get_current_model()
        if current:
            report.append("-" * 80)
            report.append(f"当前使用模型: {current.display_name}")

        report.append("=" * 80)
        return "\n".join(report)

    def reset_exhausted_models(self):
        """重置所有已用尽的模型状态（例如额度重置后）"""
        for usage in self.usage_stats.values():
            usage.is_exhausted = False
            usage.error_count = 0
        self.current_priority = 1
        print("[ModelManager] 已重置所有模型状态")


# ==================== 全局模型管理器实例 ====================
_model_manager: Optional[ModelManager] = None


def get_model_manager(api_key: Optional[str] = None) -> ModelManager:
    """获取全局模型管理器实例"""
    global _model_manager
    if _model_manager is None:
        _model_manager = ModelManager(api_key)
    return _model_manager


def set_model_manager(manager: ModelManager):
    """设置全局模型管理器实例"""
    global _model_manager
    _model_manager = manager


# ==================== 便捷函数 ====================

def generate_with_fallback(
    messages: List[Dict],
    temperature: float = 0.7,
    max_tokens: Optional[int] = None,
    on_token: Optional[Callable[[str], None]] = None,
    api_key: Optional[str] = None
) -> Optional[str]:
    """
    使用模型管理器生成回复（带自动切换）

    Args:
        messages: 消息列表
        temperature: 温度参数
        max_tokens: 最大生成token数
        on_token: 流式输出回调
        api_key: API密钥（可选）

    Returns:
        生成的文本
    """
    manager = get_model_manager(api_key)
    return manager.call_model(messages, temperature, max_tokens, on_token)


if __name__ == "__main__":
    # 测试模型管理器
    manager = ModelManager()

    print("可用模型列表:")
    for model in ALL_MODELS[:5]:  # 只显示前5个
        print(f"  {model.priority}. {model.display_name} - {model.description}")

    print("\n当前模型:", manager.get_current_model().display_name if manager.get_current_model() else "None")

    # 测试调用
    test_messages = [
        {"role": "system", "content": "你是一个有帮助的AI助手。"},
        {"role": "user", "content": "你好，请介绍一下你自己。"}
    ]

    print("\n测试调用...")
    result = manager.call_model(test_messages, max_tokens=100)
    if result:
        print(f"回复: {result[:100]}...")
    else:
        print("调用失败")

    print(manager.get_usage_report())
