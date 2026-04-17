# AI World

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.10+-blue.svg" alt="Python 3.10+">
  <img src="https://img.shields.io/badge/Pygame-2.6.1-green.svg" alt="Pygame 2.6.1">
  <img src="https://img.shields.io/badge/License-MIT-yellow.svg" alt="MIT License">
</p>

<p align="center">
  <b>多智能体协作模拟系统</b>
</p>

---

## 项目概述

AI World 是一款基于多智能体架构的协作模拟系统，采用游戏化界面展示分布式任务处理流程。系统通过可视化方式呈现多模型协同工作机制，适用于团队协作教学、分布式系统演示及人工智能应用研究。

### 核心特性

- **多智能体架构**: 6个独立智能体，各自配置专用大语言模型
- **任务编排系统**: 基于规划器的自动化任务分解与分配
- **并行执行引擎**: 支持多任务并发处理，实时状态监控
- **结果整合模块**: 自动化输出格式化与文档生成
- **多模态输入**: 支持文本、图像及文档作为任务输入

---

## 系统架构

### 技术栈

| 组件 | 技术选型 |
|------|----------|
| 运行时环境 | Python 3.10+ |
| 图形界面 | Pygame 2.6.1 |
| 模型接口 | OpenAI Compatible API |
| 主要模型 | 阿里云百炼 Qwen 系列 |
| 备用模型 | 智谱 GLM 系列 |

### 智能体配置

系统包含 6 个专用智能体，针对不同任务类型优化：

| 智能体 ID | 角色定位 | 模型配置 | 功能领域 |
|-----------|----------|----------|----------|
| 0 | 技术专员 | qwen-max | 通用复杂任务 |
| 1 | 人事专员 | qwen3.6-plus | 多模态处理 |
| 2 | 市场专员 | qwen3-vl-235b | 视觉理解分析 |
| 3 | 财务专员 | qwen-coder-turbo | 代码生成与审查 |
| 4 | 运营专员 | qvq-max | 逻辑推理与决策 |
| 5 | 行政专员 | qwen-plus | 通用均衡任务 |

### 模型管理策略

- **主模型池**: 23 个百炼平台模型，覆盖通用、视觉、代码、数学、推理等场景
- **降级机制**: 主模型额度耗尽时自动切换至备用模型
- **负载均衡**: 根据任务类型智能分配最优模型

---

## 安装与部署

### 环境要求

- 操作系统: Windows 10/11
- Python 版本: 3.10 或更高
- 内存: 4GB 以上
- 网络: 需连接互联网以调用模型 API

### 安装步骤

```bash
# 克隆仓库
git clone https://github.com/yhsxxlblogs/AI-World.git
cd AI-World

# 安装依赖
pip install -r requirements.txt

# 启动系统
py main.py
```

---

## 使用指南

### 基本操作

| 操作 | 按键 | 说明 |
|------|------|------|
| 移动 | WASD | 控制角色在场景中移动 |
| 交互 | E | 与智能体进行对话 |
| 任务编排 | P | 打开任务规划界面 |
| 监控面板 | T | 切换执行状态面板 |
| 语言切换 | L | 中英文界面切换 |
| 任务启动 | SPACE | 发布执行指令 |
| 退出 | ESC | 关闭系统 |

### 工作流程

1. **任务输入**: 在规划界面输入任务需求，可附加参考文件
2. **智能规划**: 系统自动分析需求并生成分工方案
3. **技能生成**: 为每个智能体生成专属执行策略文档
4. **任务分发**: 智能体自动前往工作区域就位
5. **并行执行**: 多智能体同时处理各自子任务
6. **结果整合**: 系统自动合并输出并格式化为标准文档

### 输出目录结构

```
results/
└── [项目名称]_[时间戳]/
    ├── README.md              # 执行报告
    ├── MERGED_RESULT.md       # 整合成果文档
    ├── project_meta.json      # 项目元数据
    └── [编号]_[角色].md        # 各智能体独立输出
```

---

## 系统模块

### 核心模块 (core/)

- **ai_employee.py**: 智能体状态机与行为控制
- **boss.py**: 用户角色控制与交互
- **pathfinding.py**: A* 寻路算法实现
- **constants.py**: 系统常量集中管理

### 智能体系统 (ai_systems/)

- **agent_planner.py**: 任务规划与分解
- **agent_planner_v2.py**: 增强版规划器，支持多模态输入
- **employee_ai_worker.py**: 智能体执行引擎
- **bailian_models.py**: 模型配置与优先级管理
- **model_manager.py**: 模型调度与降级处理

### 用户界面 (ui/)

- **workflow_editor.py**: 任务编排界面
- **workflow_system.py**: 执行状态监控
- **loading_screen.py**: 系统启动与配置管理
- **planner_chat.py**: 规划交互界面

### 工具模块 (utils/)

- **result_manager.py**: 成果管理与文档生成
- **ai_output_processor.py**: 输出格式化与质量处理
- **content_formatter.py**: 内容类型识别与格式化

---

## 配置说明

### API 配置

系统预配置以下模型服务：

**主服务 - 阿里云百炼**
- 接入点: `https://dashscope.aliyuncs.com/compatible-mode/v1`
- 免费额度: 每模型 100 万 Token（开通后 90 天内有效）
- 认证方式: API Key

**备用服务 - 智谱 AI**
- 接入点: `https://open.bigmodel.cn/api/paas/v4`
- 默认模型: glm-4
- 触发条件: 主服务额度耗尽时自动切换

### 自定义配置

可通过环境变量覆盖默认配置：

```powershell
$env:DASHSCOPE_API_KEY="your-api-key"
$env:ZHIPU_API_KEY="your-api-key"
```

---

## 项目结构

```
AI-World/
├── main.py                    # 系统入口
├── requirements.txt           # 依赖清单
├── README.md                  # 项目文档
├── PROJECT_STATUS.md          # 开发状态文档
│
├── core/                      # 核心模块
│   ├── config.py              # 基础配置
│   ├── constants.py           # 常量定义
│   ├── ai_employee.py         # 智能体实现
│   ├── boss.py                # 用户角色
│   ├── pathfinding.py         # 寻路系统
│   └── ...
│
├── ai_systems/                # 智能体系统
│   ├── agent_planner.py       # 任务规划
│   ├── agent_planner_v2.py    # 增强规划器
│   ├── bailian_models.py      # 模型配置
│   ├── model_manager.py       # 模型管理
│   └── ...
│
├── ui/                        # 用户界面
│   ├── workflow_editor.py     # 任务编排
│   ├── workflow_system.py     # 状态监控
│   └── ...
│
├── utils/                     # 工具模块
│   ├── result_manager.py      # 成果管理
│   ├── ai_output_processor.py # 输出处理
│   └── ...
│
├── skill/                     # 策略文档
├── results/                   # 输出目录
└── docs/                      # 技术文档
```

---

## 开发状态

### 已完成功能

- [x] 多智能体并行执行框架
- [x] 基于规划器的任务编排系统
- [x] 23 个模型配置与自动调度
- [x] 多模态输入支持（文本、图像、文档）
- [x] 输出格式化与质量处理流水线
- [x] 实时状态监控面板
- [x] 成果自动整合与文档生成

### 开发计划

- [ ] 可视化结果预览
- [ ] 历史项目回溯
- [ ] 执行性能分析
- [ ] 自定义模型接入

---

## 许可证

MIT License

---

## 联系方式

- 项目主页: https://github.com/yhsxxlblogs/AI-World
- 问题反馈: https://github.com/yhsxxlblogs/AI-World/issues

---

<p align="center">
  AI World Team
</p>
