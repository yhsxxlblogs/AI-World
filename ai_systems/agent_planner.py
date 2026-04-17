# Agent Planner - 使用OpenAI SDK + 智谱API
import os
import re
import json
import asyncio
import threading
from typing import List, Dict, Optional, Callable
from datetime import datetime
from pathlib import Path

try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    print("[警告] 未安装openai SDK，请运行: py -m pip install openai")


def load_planner_skill() -> str:
    """从skill文件加载规划师提示词"""
    skill_path = Path("skill/planner_skill.md")
    
    # 默认提示词（如果文件不存在）
    default_prompt = """你是AI World公司的首席规划师。你的任务是根据用户需求，为团队成员制定详细的工作分工。

【核心任务】
1. 深度分析用户需求，提炼核心目标
2. 为每位员工分配明确的角色和职责
3. 生成符合格式要求的分工规划

【输出格式要求】
你必须严格按照以下格式输出分工结果：

[AIWORLD_PLAN_START]

[SECTION:项目概述]
[PROJECT_GOAL]用一句话描述项目核心目标[/PROJECT_GOAL]
[/SECTION:项目概述]

[SECTION:员工分工]
[EMPLOYEE:0]
[EMP_ID]0[/EMP_ID]
[EMP_NAME]员工姓名[/EMP_NAME]
[ROLE]角色名称[/ROLE]
[SKILL_DEFINITION]
## 身份定位
你是【角色】，负责【一句话描述核心职责】。

## 工作内容
1. 【任务1】：【详细描述】
2. 【任务2】：【详细描述】
3. 【任务3】：【详细描述】

## 输入要求
- 前置信息：【需要什么输入】
- 格式要求：【输入格式】

## 输出标准
- 产出物：【输出什么内容】
- 格式规范：【输出格式】
- 质量指标：【质量标准】

## 工作方法
- 分析思路：【如何分析】
- 执行步骤：【具体步骤】
- 关键要点：【注意事项】
[/SKILL_DEFINITION]
[/EMPLOYEE:0]

[/SECTION:员工分工]

[SECTION:任务间联系与协作规范]
1. 数据/接口一致性要求
2. 员工间协作接口
3. 共享资源/配置
4. 整合检查清单
5. 最终交付物结构
[/SECTION:任务间联系与协作规范]

[AIWORLD_PLAN_END]

【强制要求】
1. 必须包含 [AIWORLD_PLAN_START] 和 [AIWORLD_PLAN_END] 标记
2. 每位员工必须有 [EMPLOYEE:N] 和 [/EMPLOYEE:N] 标记
3. 必须包含完整的SKILL_DEFINITION（5个部分）
4. 所有员工采用并行工作模式
5. 分工要覆盖用户需求的全部内容
"""
    
    try:
        if skill_path.exists():
            with open(skill_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 解析Markdown内容（移除YAML frontmatter）
            if content.startswith('---'):
                # 找到第二个---
                end_idx = content.find('---', 3)
                if end_idx != -1:
                    content = content[end_idx + 3:].strip()
            
            print(f"[AgentPlanner] 已从 {skill_path} 加载规划师技能")
            return content
        else:
            print(f"[AgentPlanner] 技能文件不存在，使用默认提示词")
            return default_prompt
    except Exception as e:
        print(f"[AgentPlanner] 加载技能文件失败: {e}，使用默认提示词")
        return default_prompt


class AgentPlanner:
    """使用OpenAI SDK作为AI规划师，支持智谱/DeepSeek等OpenAI兼容API"""
    
    # 规划师系统提示词（动态加载）
    PLANNER_SYSTEM_PROMPT = load_planner_skill()

    def __init__(self, api_key: str = "", api_url: str = "", model: str = "glm-4"):
        self.api_key = api_key
        self.api_url = api_url or "https://open.bigmodel.cn/api/paas/v4"
        self.model = model
        self.plan_result = None
        self.is_running = False
        self.client = None
        
        if OPENAI_AVAILABLE and api_key:
            self._init_client()
    
    def _init_client(self):
        """初始化OpenAI客户端 - 连接智谱API"""
        try:
            self.client = OpenAI(
                api_key=self.api_key,
                base_url=self.api_url
            )
            print(f"[AgentPlanner] OpenAI客户端初始化成功 (API: {self.api_url})")
        except Exception as e:
            print(f"[AgentPlanner] 客户端初始化失败: {e}")
            self.client = None
    
    def set_config(self, api_key: str, api_url: str = "", model: str = "glm-4"):
        """设置API配置"""
        self.api_key = api_key
        self.api_url = api_url or "https://open.bigmodel.cn/api/paas/v4"
        self.model = model
        if OPENAI_AVAILABLE and api_key:
            self._init_client()
    
    def generate_plan(
        self,
        selected_employees: List,
        user_requirement: str,
        on_token: Optional[Callable[[str], None]] = None,
        on_complete: Optional[Callable[[Optional[Dict]], None]] = None
    ) -> Optional[Dict]:
        """
        使用OpenAI SDK生成规划
        
        Args:
            selected_employees: 选中的员工列表
            user_requirement: 用户需求
            on_token: 流式输出回调
            on_complete: 完成回调
        """
        if not selected_employees:
            print("[AgentPlanner] 错误：未选择任何员工")
            return None
        
        # 在后台线程运行规划
        thread = threading.Thread(
            target=self._run_planning,
            args=(selected_employees, user_requirement, on_token, on_complete)
        )
        thread.daemon = True
        thread.start()
        
        return None
    
    def _run_planning(
        self,
        employees: List,
        user_requirement: str,
        on_token: Optional[Callable[[str], None]],
        on_complete: Optional[Callable[[Optional[Dict]], None]]
    ):
        """运行规划 - 使用OpenAI SDK调用智谱API (支持真正的流式输出)"""
        self.is_running = True
        output = ""
        
        try:
            # 构建提示词
            prompt = self._build_planning_prompt(employees, user_requirement)
            
            # 发送开始消息
            if on_token:
                on_token("[AI规划师] 正在分析需求并制定分工方案...\n\n")
            
            # 使用OpenAI SDK调用智谱API - 真正的流式输出
            if self.client and OPENAI_AVAILABLE:
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": self.PLANNER_SYSTEM_PROMPT},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.7,
                    max_tokens=4096,
                    stream=True  # 启用真正的流式输出
                )
                
                # 实时接收流式数据
                for chunk in response:
                    if chunk.choices and chunk.choices[0].delta.content:
                        token = chunk.choices[0].delta.content
                        output += token
                        if on_token:
                            on_token(token)
            else:
                # 回退到cloud_ai_client (非流式)
                if on_token:
                    on_token("[系统] 使用备用方案...\n")
                output = self._call_api_via_cloud_client(prompt)
                if on_token and output:
                    on_token(output)
            
            # 解析结果
            plan = self._parse_output(output, employees)
            self.plan_result = plan
            self.is_running = False
            
            if on_complete:
                on_complete(plan)
                
        except Exception as e:
            print(f"[AgentPlanner] 错误: {e}")
            # 出错时尝试备用方案
            try:
                output = self._call_api_via_cloud_client(self._build_planning_prompt(employees, user_requirement))
                if on_token:
                    on_token("\n[系统] 使用备用方案...\n")
                    on_token(output)
                plan = self._parse_output(output, employees)
                self.plan_result = plan
                self.is_running = False
                if on_complete:
                    on_complete(plan)
            except:
                self.is_running = False
                if on_complete:
                    on_complete(None)
    
    def _call_api_via_cloud_client(self, prompt: str) -> str:
        """通过cloud_ai_client调用API（备用方案）"""
        try:
            from ai_systems.cloud_ai_client import cloud_ai_client
            
            output = cloud_ai_client.generate(
                prompt=prompt,
                system_prompt=self.PLANNER_SYSTEM_PROMPT,
                stream=False
            )
            
            if output and not output.startswith('[错误'):
                return output
            else:
                print(f"[AgentPlanner] API调用失败: {output}")
                return ""
        except Exception as e:
            print(f"[AgentPlanner] API调用错误: {e}")
            return ""
    
    def _build_planning_prompt(self, employees: List, user_requirement: str) -> str:
        """构建规划提示词"""
        employee_info = []
        for i, emp in enumerate(employees):
            employee_info.append(f"员工{i} (ID:{emp.id}): {emp.name}")
        
        employee_list = "\n".join(employee_info)
        
        prompt = f"""请为以下项目制定详细的分工规划：

【用户需求】
{user_requirement}

【团队信息】
团队规模: {len(employees)}人
团队成员:
{employee_list}

请按照系统提示词中的格式要求，输出完整的分工规划。
"""
        return prompt
    
    def _parse_output(self, output: str, employees: List) -> Optional[Dict]:
        """解析输出结果"""
        
        # 提取规划内容
        plan_match = re.search(
            r'\[AIWORLD_PLAN_START\](.*?)\[AIWORLD_PLAN_END\]',
            output,
            re.DOTALL
        )
        
        if not plan_match:
            print("[AgentPlanner] 错误：找不到规划标记")
            return self._fallback_parse(output, employees)
        
        plan_content = plan_match.group(1)
        
        # 解析项目概述
        project_goal = self._extract_tag(plan_content, 'PROJECT_GOAL')
        
        plan = {
            'project_goal': project_goal or '完成用户需求',
            'project_mode': '并行',
            'employees': [],
            'raw_response': output
        }
        
        # 解析每个员工的分工
        for i, emp in enumerate(employees):
            emp_pattern = rf'\[EMPLOYEE:{i}\](.*?)\[/EMPLOYEE:{i}\]'
            emp_match = re.search(emp_pattern, plan_content, re.DOTALL)
            
            if emp_match:
                emp_content = emp_match.group(1)
                
                emp_plan = {
                    'employee_id': emp.id,
                    'employee_name': emp.name,
                    'role': self._extract_tag(emp_content, 'ROLE'),
                    'mode': '并行',
                    'skill_definition': self._extract_tag(emp_content, 'SKILL_DEFINITION')
                }
                
                plan['employees'].append(emp_plan)
            else:
                # 使用默认模板
                plan['employees'].append({
                    'employee_id': emp.id,
                    'employee_name': emp.name,
                    'role': '执行专员',
                    'mode': '并行',
                    'skill_definition': self._get_default_skill()
                })
        
        return plan
    
    def _fallback_parse(self, output: str, employees: List) -> Dict:
        """备用解析方法"""
        plan = {
            'project_goal': '完成用户需求',
            'project_mode': '并行',
            'employees': [],
            'raw_response': output
        }
        
        for emp in employees:
            plan['employees'].append({
                'employee_id': emp.id,
                'employee_name': emp.name,
                'role': '执行专员',
                'mode': '并行',
                'skill_definition': self._get_default_skill()
            })
        
        return plan
    
    def _extract_tag(self, content: str, tag: str) -> str:
        """提取标签内容"""
        pattern = rf'\[{tag}\](.*?)\[/{tag}\]'
        match = re.search(pattern, content, re.DOTALL)
        if match:
            return match.group(1).strip()
        return ""
    
    def _get_default_skill(self) -> str:
        """获取默认技能定义"""
        return """## 身份定位
你是执行专员，负责完成分配的任务。

## 工作内容
1. 分析需求并理解任务目标
2. 执行分配的具体工作
3. 输出高质量的工作成果

## 输入要求
- 前置信息：用户需求描述

## 输出标准
- 产出物：工作成果文档
- 格式规范：Markdown格式

## 工作方法
- 分析思路：系统性地分析问题
- 执行步骤：按步骤有序执行
- 关键要点：注重细节和质量"""
    
    def generate_skill_files(self, plan: Dict):
        """生成skill.md文件"""
        for emp_plan in plan['employees']:
            emp_id = emp_plan['employee_id']
            skill_content = emp_plan.get('skill_definition', '')
            
            if not skill_content:
                skill_content = self._get_default_skill()
            
            skill_file = f"skill/skill{emp_id}.md"
            
            full_content = f"""# {emp_plan['employee_name']} - {emp_plan['role']}

> 由AI规划师自动生成
> 工作模式: 并行
> 生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

{skill_content}

---
*Generated by AI World Agent Planner*
"""
            
            try:
                os.makedirs('skill', exist_ok=True)
                with open(skill_file, 'w', encoding='utf-8') as f:
                    f.write(full_content)
                print(f"[AgentPlanner] 已生成技能文件: {skill_file}")
            except Exception as e:
                print(f"[AgentPlanner] 错误：写入技能文件失败: {e}")
    
    def consolidate_results(
        self,
        plan: Dict,
        employee_results: List[Dict],
        output_dir: str,
        on_token: Optional[Callable[[str], None]] = None,
        on_complete: Optional[Callable[[Optional[str]], None]] = None
    ):
        """整理所有员工的工作结果"""
        thread = threading.Thread(
            target=self._run_consolidation,
            args=(plan, employee_results, output_dir, on_token, on_complete)
        )
        thread.daemon = True
        thread.start()
    
    def _run_consolidation(
        self,
        plan: Dict,
        employee_results: List[Dict],
        output_dir: str,
        on_token: Optional[Callable[[str], None]],
        on_complete: Optional[Callable[[Optional[str]], None]]
    ):
        """运行整理 - 使用OpenAI SDK调用智谱API"""
        try:
            # 构建整理提示词
            prompt = self._build_consolidation_prompt(plan, employee_results, output_dir)
            
            if on_token:
                on_token("[AI] 正在整理所有员工的工作成果...\n")
            
            # 使用OpenAI SDK调用智谱API
            if self.client and OPENAI_AVAILABLE:
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": "你是文档整理专家。请将多个员工的工作成果整合成一个完整的项目文档。"},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.7,
                    max_tokens=8000,
                    stream=False
                )
                output = response.choices[0].message.content if response.choices else ""
            else:
                # 回退到cloud_ai_client
                output = self._call_api_via_cloud_client_for_consolidation(prompt)
            
            # 模拟流式输出
            if on_token and output:
                chunk_size = 100
                for i in range(0, len(output), chunk_size):
                    chunk = output[i:i+chunk_size]
                    on_token(chunk)
            
            # 保存合并文档
            if output:
                os.makedirs(output_dir, exist_ok=True)
                merged_file = os.path.join(output_dir, "MERGED_RESULT.md")
                with open(merged_file, 'w', encoding='utf-8') as f:
                    f.write(f"# 项目整合结果\n\n生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
                    f.write(output)
                
                if on_token:
                    on_token(f"\n[完成] 合并文档已保存: {merged_file}\n")
                
                if on_complete:
                    on_complete(output)
            else:
                if on_complete:
                    on_complete(None)
                    
        except Exception as e:
            print(f"[AgentPlanner] 整理错误: {e}")
            # 出错时尝试备用方案
            try:
                output = self._call_api_via_cloud_client_for_consolidation(
                    self._build_consolidation_prompt(plan, employee_results, output_dir)
                )
                if output:
                    os.makedirs(output_dir, exist_ok=True)
                    merged_file = os.path.join(output_dir, "MERGED_RESULT.md")
                    with open(merged_file, 'w', encoding='utf-8') as f:
                        f.write(f"# 项目整合结果\n\n生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
                        f.write(output)
                    if on_complete:
                        on_complete(output)
                else:
                    if on_complete:
                        on_complete(None)
            except:
                if on_complete:
                    on_complete(None)
    
    def _call_api_via_cloud_client_for_consolidation(self, prompt: str) -> str:
        """通过cloud_ai_client调用API进行整理"""
        try:
            from ai_systems.cloud_ai_client import cloud_ai_client
            
            output = cloud_ai_client.generate(
                prompt=prompt,
                system_prompt="你是文档整理专家。请将多个员工的工作成果整合成一个完整的项目文档。",
                stream=False
            )
            
            if output and not output.startswith('[错误'):
                return output
            else:
                print(f"[AgentPlanner] 整理API调用失败: {output}")
                return ""
        except Exception as e:
            print(f"[AgentPlanner] 整理API调用错误: {e}")
            return ""
    
    def _build_consolidation_prompt(
        self,
        plan: Dict,
        employee_results: List[Dict],
        output_dir: str
    ) -> str:
        """构建整理提示词"""
        division_info = []
        for emp_plan in plan.get('employees', []):
            division_info.append(f"""
员工: {emp_plan['employee_name']}
角色: {emp_plan['role']}
职责: {emp_plan.get('skill_definition', '执行分配任务')[:200]}...
""")
        
        division_text = "\n".join(division_info)
        
        results_text = []
        for result in employee_results:
            emp_name = result.get('employee_name', 'Unknown')
            content = result.get('content', '')
            results_text.append(f"""
=== {emp_name} 的工作结果 ===
{content}
""")
        
        results_combined = "\n".join(results_text)
        
        prompt = f"""你是AI World公司的首席整理师。你的任务是根据之前的分工规划，整合所有员工的工作成果，生成最终的项目交付物。

【原始分工规划】
项目目标: {plan.get('project_goal', '完成用户需求')}

员工分工:
{division_text}

【各员工工作结果】
{results_combined}

【整理要求】
1. 阅读并理解每位员工的工作成果
2. 根据原始分工规划，将各部分内容整合成完整的项目
3. 确保整合后的内容逻辑连贯、格式统一
4. 生成项目说明文档

【输出要求】
- 生成一个完整的、可直接使用的项目文档
- 文件结构清晰，命名规范
- 包含README.md说明文档

请开始整理并生成项目文档。
"""
        return prompt


# 全局Agent规划师实例
agent_planner = AgentPlanner()
