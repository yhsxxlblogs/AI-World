# 云端AI API客户端 - 使用OpenAI SDK支持多种云服务商
import os
import json
import time
import random
from typing import List, Dict, Optional, Generator

# 尝试导入OpenAI SDK，如果未安装则给出提示
try:
    from openai import OpenAI
    OPENAI_SDK_AVAILABLE = True
except ImportError:
    OPENAI_SDK_AVAILABLE = False
    print("[警告] 未安装OpenAI SDK，请运行: pip install openai")


class RetryConfig:
    """重试配置"""
    MAX_RETRIES = 3  # 最大重试次数
    BASE_DELAY = 1.0  # 基础延迟（秒）
    MAX_DELAY = 10.0  # 最大延迟（秒）
    EXPONENTIAL_BASE = 2  # 指数退避基数
    
    # 可重试的错误类型
    RETRYABLE_ERRORS = [
        'ConnectionError',
        'TimeoutError',
        'DNSLookupError',
        'NetworkError',
        'ServiceUnavailable',
        'RateLimitError',
        'APIConnectionError',
        'APIError',
    ]
    
    # 可重试的HTTP状态码
    RETRYABLE_STATUS_CODES = [408, 429, 500, 502, 503, 504]


def should_retry_error(error_msg: str, status_code: int = None) -> bool:
    """判断错误是否应该重试"""
    # 检查HTTP状态码
    if status_code and status_code in RetryConfig.RETRYABLE_STATUS_CODES:
        return True
    
    # 检查错误消息
    error_msg_lower = error_msg.lower()
    retryable_keywords = [
        'connection', 'timeout', 'dns', 'network', 'unavailable',
        'rate limit', 'too many requests', 'temporary', 'retry',
        'connectionerror', 'timeouterror', 'dnslookuperror',
        'networkerror', 'serviceunavailable', 'ratelimit',
        'apiconnectionerror', 'apierror', 'internal server error',
    ]
    
    for keyword in retryable_keywords:
        if keyword in error_msg_lower:
            return True
    
    return False


def calculate_retry_delay(retry_count: int) -> float:
    """计算重试延迟（指数退避 + 抖动）"""
    # 指数退避
    delay = RetryConfig.BASE_DELAY * (RetryConfig.EXPONENTIAL_BASE ** retry_count)
    # 添加随机抖动（0-1秒）
    jitter = random.uniform(0, 1)
    delay += jitter
    # 限制最大延迟
    return min(delay, RetryConfig.MAX_DELAY)


class CloudAIConfig:
    """云端AI配置管理"""
    
    def __init__(self):
        # API配置
        self.api_url = ""  # 如: https://api.moonshot.cn/v1
        self.api_key = ""  # API密钥
        self.model_name = ""  # 模型名称，如: kimi-k2.5, gpt-4
        
        # 默认参数
        self.temperature = 0.7
        self.max_tokens = 4096
        self.timeout = 120
        
    def is_configured(self) -> bool:
        """检查是否已配置API"""
        return bool(self.api_url and self.api_key and self.model_name)


class CloudAIClient:
    """云端AI API客户端 - 使用OpenAI SDK (新版 1.0.0+)"""
    
    def __init__(self, config: CloudAIConfig = None):
        self.config = config or CloudAIConfig()
        self.last_response_time = 0
        self.client = None
        
    def set_config(self, api_url: str, api_key: str, model_name: str):
        """设置API配置"""
        self.config.api_url = api_url
        self.config.api_key = api_key
        self.config.model_name = model_name
        
        # 创建OpenAI客户端 (新版API)
        if OPENAI_SDK_AVAILABLE and self.config.is_configured():
            try:
                self.client = OpenAI(
                    api_key=api_key,
                    base_url=api_url
                )
                print(f"[CloudAI] 已配置API: {api_url}, 模型: {model_name}")
            except Exception as e:
                print(f"[CloudAI] 配置失败: {e}")
                self.client = None
        
    def is_available(self) -> bool:
        """检查API是否可用"""
        if not OPENAI_SDK_AVAILABLE:
            return False
        if not self.config.is_configured():
            return False
        if not self.client:
            return False
        return True
    
    def generate(self, 
                 prompt: str, 
                 system_prompt: str = "",
                 stream: bool = False) -> str:
        """
        生成AI回复 - 使用OpenAI SDK (新版API)，带自动重试机制
        
        Args:
            prompt: 用户提示词
            system_prompt: 系统提示词
            stream: 是否流式输出
        
        Returns:
            AI生成的回复文本
        """
        if not OPENAI_SDK_AVAILABLE:
            return "[错误: 未安装OpenAI SDK，请运行: pip install openai]"
        
        if not self.config.is_configured():
            return "[错误: API未配置，请在员工面板中设置API信息]"
        
        if not self.client:
            return "[错误: API客户端未初始化]"
        
        # 构建消息
        messages = []
        if system_prompt:
            messages.append({'role': 'system', 'content': system_prompt})
        messages.append({'role': 'user', 'content': prompt})
        
        # 重试逻辑
        last_error = None
        for retry_count in range(RetryConfig.MAX_RETRIES + 1):
            try:
                start_time = time.time()
                
                # 使用新版OpenAI SDK调用API
                response = self.client.chat.completions.create(
                    model=self.config.model_name,
                    messages=messages,
                    temperature=self.config.temperature,
                    max_tokens=self.config.max_tokens,
                    stream=stream
                )
                
                self.last_response_time = time.time() - start_time
                
                # 解析响应 (新版API格式)
                if stream:
                    return "[错误: 流式响应请使用generate_stream方法]"
                else:
                    return response.choices[0].message.content
                
            except Exception as e:
                error_msg = str(e)
                last_error = e
                
                # 检查是否应该重试
                if retry_count < RetryConfig.MAX_RETRIES and should_retry_error(error_msg):
                    delay = calculate_retry_delay(retry_count)
                    print(f"[CloudAI] API调用失败 (尝试 {retry_count + 1}/{RetryConfig.MAX_RETRIES + 1}): {error_msg}")
                    print(f"[CloudAI] 等待 {delay:.1f} 秒后重试...")
                    time.sleep(delay)
                    continue
                else:
                    # 不重试或已达到最大重试次数
                    break
        
        # 所有重试都失败了
        return f"[API错误: {str(last_error)}]"
    
    def generate_stream(self, 
                       prompt: str, 
                       system_prompt: str = "") -> Generator[str, None, None]:
        """
        流式生成AI回复 - 使用OpenAI SDK (新版API)，带自动重试机制
        
        Args:
            prompt: 用户提示词
            system_prompt: 系统提示词
        
        Yields:
            生成的文本片段
        """
        if not OPENAI_SDK_AVAILABLE:
            yield "[错误: 未安装OpenAI SDK]"
            return
        
        if not self.config.is_configured():
            yield "[错误: API未配置]"
            return
        
        if not self.client:
            yield "[错误: API客户端未初始化]"
            return
        
        # 构建消息
        messages = []
        if system_prompt:
            messages.append({'role': 'system', 'content': system_prompt})
        messages.append({'role': 'user', 'content': prompt})
        
        # 重试逻辑
        last_error = None
        for retry_count in range(RetryConfig.MAX_RETRIES + 1):
            try:
                # 使用新版OpenAI SDK流式调用
                response = self.client.chat.completions.create(
                    model=self.config.model_name,
                    messages=messages,
                    temperature=self.config.temperature,
                    max_tokens=self.config.max_tokens,
                    stream=True
                )
                
                # 流式输出
                for chunk in response:
                    if chunk.choices and len(chunk.choices) > 0:
                        delta = chunk.choices[0].delta
                        if delta and hasattr(delta, 'content') and delta.content:
                            yield delta.content
                
                # 成功完成，直接返回
                return
                        
            except Exception as e:
                error_msg = str(e)
                last_error = e
                
                # 检查是否应该重试
                if retry_count < RetryConfig.MAX_RETRIES and should_retry_error(error_msg):
                    delay = calculate_retry_delay(retry_count)
                    yield f"\n[网络错误，正在重试 ({retry_count + 1}/{RetryConfig.MAX_RETRIES})...]\n"
                    print(f"[CloudAI] 流式API调用失败 (尝试 {retry_count + 1}/{RetryConfig.MAX_RETRIES + 1}): {error_msg}")
                    print(f"[CloudAI] 等待 {delay:.1f} 秒后重试...")
                    time.sleep(delay)
                    continue
                else:
                    # 不重试或已达到最大重试次数
                    break
        
        # 所有重试都失败了
        yield f"\n[API错误: {str(last_error)}]"


class EmployeeAIClient:
    """员工AI客户端 - 为每个员工提供独立的AI调用能力"""
    
    def __init__(self, employee_id: int):
        self.employee_id = employee_id
        self.config = CloudAIConfig()
        self.client = None
        self.skill_content = ""  # 技能文件内容
        
    def load_skill(self, skill_path: str):
        """加载技能文件"""
        try:
            if os.path.exists(skill_path):
                with open(skill_path, 'r', encoding='utf-8') as f:
                    self.skill_content = f.read()
                print(f"[EmployeeAIClient-{self.employee_id}] 已加载技能文件: {skill_path}")
            else:
                self.skill_content = ""
        except Exception as e:
            print(f"[EmployeeAIClient-{self.employee_id}] 加载技能文件失败: {e}")
            self.skill_content = ""
    
    def set_api_config(self, api_url: str, api_key: str, model_name: str):
        """设置API配置"""
        self.config.api_url = api_url
        self.config.api_key = api_key
        self.config.model_name = model_name
        
        # 创建OpenAI客户端
        if OPENAI_SDK_AVAILABLE and self.config.is_configured():
            try:
                self.client = OpenAI(
                    api_key=api_key,
                    base_url=api_url
                )
                print(f"[EmployeeAIClient-{self.employee_id}] 已配置API: {model_name}")
            except Exception as e:
                print(f"[EmployeeAIClient-{self.employee_id}] 配置失败: {e}")
                self.client = None
    
    def is_available(self) -> bool:
        """检查API是否可用"""
        if not OPENAI_SDK_AVAILABLE:
            return False
        if not self.config.is_configured():
            return False
        if not self.client:
            return False
        return True
    
    def generate(self, prompt: str, system_prompt: str = "", stream: bool = False) -> str:
        """生成AI回复"""
        if not OPENAI_SDK_AVAILABLE:
            return "[错误: 未安装OpenAI SDK]"
        
        if not self.config.is_configured():
            return "[错误: API未配置]"
        
        if not self.client:
            return "[错误: API客户端未初始化]"
        
        messages = []
        if system_prompt:
            messages.append({'role': 'system', 'content': system_prompt})
        messages.append({'role': 'user', 'content': prompt})
        
        try:
            response = self.client.chat.completions.create(
                model=self.config.model_name,
                messages=messages,
                temperature=self.config.temperature,
                max_tokens=self.config.max_tokens,
                stream=stream
            )
            
            if stream:
                return "[错误: 流式响应请使用generate_stream]"
            else:
                return response.choices[0].message.content
                
        except Exception as e:
            return f"[API错误: {str(e)}]"
    
    def generate_stream(self, prompt: str, system_prompt: str = ""):
        """流式生成AI回复"""
        if not OPENAI_SDK_AVAILABLE:
            yield "[错误: 未安装OpenAI SDK]"
            return
        
        if not self.config.is_configured():
            yield "[错误: API未配置]"
            return
        
        if not self.client:
            yield "[错误: API客户端未初始化]"
            return
        
        messages = []
        if system_prompt:
            messages.append({'role': 'system', 'content': system_prompt})
        messages.append({'role': 'user', 'content': prompt})
        
        try:
            response = self.client.chat.completions.create(
                model=self.config.model_name,
                messages=messages,
                temperature=self.config.temperature,
                max_tokens=self.config.max_tokens,
                stream=True
            )
            
            for chunk in response:
                if chunk.choices and len(chunk.choices) > 0:
                    delta = chunk.choices[0].delta
                    if delta and hasattr(delta, 'content') and delta.content:
                        yield delta.content
                        
        except Exception as e:
            yield f"\n[API错误: {str(e)}]"


# 全局客户端实例
cloud_ai_client = CloudAIClient()
