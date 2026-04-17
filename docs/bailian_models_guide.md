# 阿里云百炼模型使用指南

## 概述

AI World 现已集成阿里云百炼平台的174个免费大模型，支持自动切换和负载均衡。

## 配置说明

### 1. API密钥

你的阿里云百炼API密钥已配置：
```
sk-7c497750be384766a027179211f1c010
```

### 2. 模型优先级（按员工AI有用程度排序）

| 优先级 | 模型名称 | 说明 | 免费额度 |
|--------|----------|------|----------|
| 1 | qwen3-max | 千问系列最强模型，适合复杂任务 | 100万Token |
| 2 | qwen3.6-plus | 效果、速度、成本均衡 | 100万Token |
| 3 | qwen3.5-plus | 效果媲美Max，成本更低 | 100万Token |
| 4 | qwen-plus | 能力均衡，中等复杂任务 | 100万Token |
| 5 | qwen3.5-flash | 速度最快，成本低 | 100万Token |
| 6 | qwen-flash | 快速响应 | 100万Token |
| 7-10 | qwen3-235b/32b/14b/8b | 开源版模型 | 100万Token |
| 11-12 | qwen3-coder-plus/flash | 代码专用 | 100万Token |
| 13 | qwq-plus | 推理专用，数学代码强 | 100万Token |
| 14 | qwen-long | 长文本处理（1000万上下文） | 100万Token |
| 15-18 | qwen2.5系列 | 备用模型 | 100万Token |
| 20-21 | glm-4/flash | 智谱GLM（原有） | 根据平台政策 |

### 3. 自动切换机制

当某个模型的免费额度用尽时，系统会自动切换到下一个优先级的模型，无需手动干预。

## 使用方法

### 方法1：使用模型管理器（推荐）

```python
from ai_systems.model_manager import get_model_manager

# 获取模型管理器
manager = get_model_manager()

# 调用模型（自动切换）
messages = [
    {"role": "system", "content": "你是一个AI助手"},
    {"role": "user", "content": "你好"}
]

result = manager.call_model(messages)
print(result)

# 查看使用报告
print(manager.get_usage_report())
```

### 方法2：便捷函数

```python
from ai_systems.model_manager import generate_with_fallback

result = generate_with_fallback(messages)
```

### 方法3：流式输出

```python
def on_token(token: str):
    print(token, end="", flush=True)

result = manager.call_model(messages, on_token=on_token)
```

## 查看模型列表

运行以下命令查看所有可用模型：

```bash
cd ai_systems
python bailian_models.py
```

## 免费额度说明

- **有效期**：开通百炼后90天内
- **额度**：每个模型输入输出各100万Token（部分模型10万Token）
- **重置**：90天后额度自动重置

## 环境变量配置（可选）

如果不想在代码中硬编码API密钥，可以设置环境变量：

```powershell
# PowerShell
$env:DASHSCOPE_API_KEY="sk-7c497750be384766a027179211f1c010"

# 或者永久设置
[Environment]::SetEnvironmentVariable("DASHSCOPE_API_KEY", "sk-7c497750be384766a027179211f1c010", "User")
```

## 文件说明

- `ai_systems/bailian_models.py` - 模型配置列表
- `ai_systems/model_manager.py` - 模型管理器（自动切换）
- `core/constants.py` - API配置常量

## 注意事项

1. 免费额度用完后会自动切换到下一个模型
2. 所有模型都通过OpenAI兼容接口调用
3. 支持流式输出和非流式输出
4. 智谱GLM模型仍然可用，作为备用选项
