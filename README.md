# AI World - AI公司模拟器

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.10+-blue.svg" alt="Python 3.10+">
  <img src="https://img.shields.io/badge/Pygame-2.6.1-green.svg" alt="Pygame 2.6.1">
  <img src="https://img.shields.io/badge/OpenAI-SDK-orange.svg" alt="OpenAI SDK">
  <img src="https://img.shields.io/badge/阿里云百炼-23个模型-red.svg" alt="阿里云百炼">
</p>

<p align="center">
  <b>扮演公司老板，指挥AI员工协作完成项目</b>
</p>

---

## 🎮 项目简介

AI World 是一款2D俯视视角的剧情类游戏，玩家扮演一家AI公司的老板，通过AI规划师为员工分配任务，员工使用真实的AI大模型并行工作，最终自动整合成果并生成格式规范的Markdown文档。

### 核心特色

- 🤖 **6名AI员工** - 每位员工配置不同的大模型（通用/视觉/代码/推理/翻译）
- 🎯 **智能规划** - AI规划师自动分析需求并生成分工方案
- ⚡ **并行执行** - 多名员工同时工作，实时显示进度
- 📄 **自动整合** - 严格处理AI输出，格式化为标准Markdown
- 🖼️ **多模态支持** - 支持上传图片和文档作为参考
- 🔄 **模型自动切换** - 额度用尽时自动降级到备用模型

---

## 🚀 快速开始

### 环境要求

- Python 3.10 或更高版本
- Windows 10/11

### 安装依赖

```bash
pip install -r requirements.txt
```

### 启动游戏

```bash
py main.py
```

---

## 🎮 游戏操作

| 按键 | 功能 |
|------|------|
| `WASD` | 控制老板移动 |
| `E` | 与附近员工对话 |
| `P` | 打开流程编辑器 |
| `T` | 切换工作流面板 |
| `L` | 切换语言(中/英) |
| `SPACE` | 发布工作号令 |
| `ESC` | 退出游戏 |
| `鼠标左键` | 点击员工查看详情 |
| `鼠标拖动` | 拖动工作流面板 |
| `鼠标滚轮` | 滚动任务列表 |

---

## 🏢 游戏场景

### 工作区
- 6个工位，配备桌椅和电脑
- 员工在此执行AI任务
- 实时显示工作进度

### 休息区
- 沙发、绿植、饮水机
- 员工休息和等待区域
- 随机走动和坐下休息

### 老板角色
- 玩家控制的角色
- 可移动并与员工交互
- 发布工作号令

---

## 👥 AI员工配置

| 员工 | 角色 | AI模型 | 平台 | 专长 |
|------|------|--------|------|------|
| 小明 | 技术专员 | qwen-max | 阿里云百炼 | 最强通用 |
| 小红 | 人事专员 | qwen3.6-plus | 阿里云百炼 | 多模态均衡 |
| 阿强 | 市场专员 | qwen3-vl-235b-thinking | 阿里云百炼 | 视觉理解 |
| 小丽 | 财务专员 | qwen-coder-turbo-0919 | 阿里云百炼 | 代码生成 |
| 大伟 | 运营专员 | qvq-max-2025-03-25 | 阿里云百炼 | 逻辑推理 |
| 晓晓 | 行政专员 | qwen-plus | 阿里云百炼 | 通用均衡 |

**备用模型**: 智谱GLM-5/GLM-4（当百炼额度用尽时自动切换）

---

## 🔄 工作流程

```
1. 输入项目需求 + 上传参考文件/图片
        ↓
2. AI规划师分析并生成分工方案
        ↓
3. 为每位员工生成专属技能文件(skill.md)
        ↓
4. 按空格发布号令，员工前往工位
        ↓
5. 并行执行AI任务（实时显示进度）
        ↓
6. 严格处理每位员工的AI输出
        ↓
7. 缝合所有结果
        ↓
8. 规划师整合并格式化为Markdown
        ↓
9. 生成MERGED_RESULT.md
        ↓
10. 员工返回休息区
```

---

## 📁 项目结构

```
AI-World/
├── main.py                    # 游戏主入口
├── requirements.txt           # 依赖列表
├── README.md                  # 项目说明
├── PROJECT_STATUS.md          # 项目状态文档
│
├── core/                      # 核心模块
│   ├── config.py              # 游戏配置
│   ├── constants.py           # 常量定义
│   ├── ai_employee.py         # 员工类
│   ├── boss.py                # 老板角色
│   ├── pathfinding.py         # A*寻路系统
│   └── ...
│
├── ai_systems/                # AI系统模块
│   ├── agent_planner.py       # AI规划师
│   ├── agent_planner_v2.py    # 增强版规划师
│   ├── employee_ai_worker.py  # 员工AI工作器
│   ├── bailian_models.py      # 百炼模型配置
│   ├── model_manager.py       # 模型管理器
│   └── ...
│
├── ui/                        # UI模块
│   ├── loading_screen.py      # 启动页
│   ├── workflow_editor.py     # 流程编辑器
│   ├── workflow_system.py     # 工作流系统
│   └── ...
│
├── utils/                     # 工具模块
│   ├── result_manager.py      # 成果管理器
│   ├── ai_output_processor.py # AI输出处理器
│   └── ...
│
├── skill/                     # 技能文件目录
│   └── skill*.md
│
└── results/                   # 成果输出目录
    └── [项目文件夹]/
        ├── MERGED_RESULT.md
        ├── README.md
        └── ...
```

---

## 🔧 技术栈

- **语言**: Python 3.10+
- **游戏框架**: Pygame 2.6.1
- **AI SDK**: OpenAI SDK（兼容百炼和智谱）
- **主要API**: 阿里云百炼 (Qwen系列) + 智谱AI (GLM系列)

---

## 🔑 API配置

### 阿里云百炼（默认）

游戏已预配置API，开箱即用：
- API URL: `https://dashscope.aliyuncs.com/compatible-mode/v1`
- 免费额度: 每个模型100万Token（开通后90天内）

### 智谱GLM（备用）

当百炼额度用尽时自动切换：
- API URL: `https://open.bigmodel.cn/api/paas/v4`
- 默认模型: glm-4

### 自定义API密钥（可选）

如需使用自己的API密钥，可设置环境变量：

```powershell
# PowerShell
$env:DASHSCOPE_API_KEY="your-key"
$env:ZHIPU_API_KEY="your-key"
```

---

## 📸 截图

*游戏截图待添加*

---

## 📝 更新日志

### v2.0.0 (2026-04-10)
- ✅ 重构项目结构，文件按功能分散到二级目录
- ✅ 集成阿里云百炼平台（23个免费大模型）
- ✅ 6名员工各配置最优AI模型
- ✅ 新增AI输出处理器（严格格式化）
- ✅ 新增结果整合器（自动缝合+规划师整理）
- ✅ 模型自动切换（额度用尽时降级）
- ✅ 增强版规划师V2（支持文件上传）

---

## 🤝 贡献

欢迎提交Issue和Pull Request！

---

## 📄 许可证

MIT License

---

## 🙏 致谢

- [阿里云百炼](https://bailian.aliyun.com/) - 提供大模型API
- [智谱AI](https://open.bigmodel.cn/) - 提供备用模型API
- [Pygame](https://www.pygame.org/) - 游戏开发框架

---

<p align="center">
  Made with ❤️ by AI World Team
</p>
