# AI World - 员工AI提示词系统
# 严格规范的输入输出格式，每个部分都有明确标记便于程序提取
# 仅支持并行模式

class EmployeePrompts:
    """员工AI提示词模板 - 严格格式版本（仅并行模式）"""
    
    @staticmethod
    def get_parallel_prompt(
        role: str,
        responsibility: str,
        task_description: str,
        project_goal: str
    ) -> str:
        """
        分工并行式任务提示词 - 超严格格式版本
        """
        prompt = f"""[AIWORLD_TASK_START]
[TASK_TYPE:PARALLEL]
[ROLE]{role}[/ROLE]
[RESPONSIBILITY]{responsibility}[/RESPONSIBILITY]
[PROJECT_GOAL]{project_goal}[/PROJECT_GOAL]
[TASK_DESC]{task_description}[/TASK_DESC]

[INSTRUCTION]
【角色定位】
你是一位专业的AI员工，正在执行分配给你的任务。你与其他员工【并行工作】，各自负责独立的部分。

【工作原则】
1. 专注于你的职责范围，不需要等待其他员工
2. 确保你的输出可以独立存在，完整且可用
3. 你的产出将被整合到最终结果中
4. 严格按照输出格式要求，便于程序解析
5. 【重要】考虑与其他员工产出的兼容性，确保能无缝整合

【任务间协作规范】
虽然是并行工作，但请注意以下协作要求：

1. **接口兼容性**：
   - 如果你的输出会被其他员工使用，请明确说明输出格式
   - 如果你依赖其他员工的输出，请说明期望的输入格式
   - 使用通用的数据格式（如JSON、Markdown、标准API格式）

2. **命名一致性**：
   - 使用清晰、规范的命名（变量名、函数名、文件名）
   - 避免使用可能与其他部分冲突的命名
   - 如有共享配置，请明确说明

3. **边界清晰**：
   - 明确说明你负责的范围边界
   - 说明与其他部分的交接点
   - 列出你做出的关键决策及其理由

4. **整合友好**：
   - 输出格式便于自动整合
   - 提供清晰的目录结构和文件说明
   - 包含必要的注释和文档

【质量要求】
- 内容必须专业、准确、可执行
- 输出必须完整，不要省略关键信息
- 格式必须规范，便于后续整合
- 必须考虑与其他部分的协作接口
[/INSTRUCTION]

[STRICT_OUTPUT_FORMAT]
【强制要求】你必须100%严格按照以下格式输出！

[AIWORLD_OUTPUT_START]

【工作成果标题】
写一个简洁的标题概括你的工作成果

【工作成果内容】
直接输出你的工作成果内容，使用Markdown格式：
- 使用 ## 作为章节标题
- 使用 - 作为列表项
- 使用 ``` 包裹代码块
- 使用 | 创建表格

重要规则：
1. 只输出内容，不要解释说明
2. 不要使用JSON格式
3. 不要输出"我完成了..."等描述性文字
4. 内容应该是可直接阅读的文档

示例（正确）：
## 市场分析报告

### 市场规模
2024年市场规模达到100亿元，预计2025年增长至150亿元。

### 竞争对手
- 公司A：市场份额30%
- 公司B：市场份额25%

示例（错误）：
```json
{"market_size": "100亿"}
```

[AIWORLD_OUTPUT_END]
[AIWORLD_TASK_END]"""
        
        return prompt


class PlannerPrompts:
    """规划师提示词模板 - 严格格式版本（仅并行模式）"""
    
    @staticmethod
    def get_planning_prompt(user_requirement: str) -> str:
        """
        规划师初始规划提示词 - 严格格式版本
        """
        prompt = f"""[AIWORLD_PLANNING_START]
[USER_REQUIREMENT]
{user_requirement}
[/USER_REQUIREMENT]

[INSTRUCTION]
你是AI World公司的首席规划师。请根据用户需求，规划一个高效的AI团队。

【核心要求】
1. 深度分析用户需求，提炼核心目标
2. 为每个角色定义明确的职责（避免重叠）
3. 所有员工采用【并行工作模式】，各自独立完成自己的部分
4. 确保分工覆盖用户需求的全部内容

【输出要求】
- 角色定义清晰具体
- 职责分工无重叠
- 覆盖需求完整全面
[/INSTRUCTION]

[STRICT_OUTPUT_FORMAT]
【强制要求】你必须100%严格按照以下格式输出！

[AIWORLD_PLAN_START]

[SECTION:项目概述]
[PROJECT_GOAL]用一句话准确描述项目的核心目标（不超过50字）[/PROJECT_GOAL]
[/SECTION:项目概述]

[SECTION:员工分工]
[MEMBER:1]
[ROLE]角色名称[/ROLE]
[RESPONSIBILITY]详细职责描述[/RESPONSIBILITY]
[/MEMBER:1]

[MEMBER:2]
[ROLE]角色名称[/ROLE]
[RESPONSIBILITY]详细职责描述[/RESPONSIBILITY]
[/MEMBER:2]

（继续添加更多成员...）
[/SECTION:员工分工]

[SECTION:工作流程]
所有员工并行工作，各自独立完成分配的任务，最后由系统自动整合所有产出。
[/SECTION:工作流程]

[AIWORLD_PLAN_END]

【绝对重要】
1. 必须包含 [AIWORLD_PLAN_START] 和 [AIWORLD_PLAN_END] 标记！
2. 所有员工都采用并行模式，没有执行顺序！
3. 确保分工合理，覆盖用户需求的全部内容！
[/STRICT_OUTPUT_FORMAT]
[AIWORLD_PLANNING_END]
"""
        
        return prompt


# 便捷函数
def get_employee_prompt(
    role: str,
    responsibility: str,
    task_description: str,
    project_goal: str
) -> str:
    """
    获取员工提示词的便捷函数（仅并行模式）
    
    Args:
        role: 角色名称
        responsibility: 职责描述
        task_description: 任务描述
        project_goal: 项目目标
    """
    return EmployeePrompts.get_parallel_prompt(
        role=role,
        responsibility=responsibility,
        task_description=task_description,
        project_goal=project_goal
    )


def get_planner_prompt(user_requirement: str) -> str:
    """
    获取规划师提示词的便捷函数
    """
    return PlannerPrompts.get_planning_prompt(user_requirement)
