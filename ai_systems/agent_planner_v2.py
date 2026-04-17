# -*- coding: utf-8 -*-
"""
Agent Planner V2 - 增强版AI规划师
- 支持文件/图片上传
- 结果整合并格式化为Markdown
- 自动创建skill.md文件
"""

import os
import re
import json
import base64
import asyncio
import threading
from typing import List, Dict, Optional, Callable, Tuple
from datetime import datetime
from pathlib import Path

try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    print("[警告] 未安装openai SDK，请运行: py -m pip install openai")


class FileUploadHandler:
    """文件上传处理器 - 支持图片和文档"""
    
    # 支持的图片格式
    IMAGE_EXTENSIONS = {'.png', '.jpg', '.jpeg', '.gif', '.bmp', '.webp'}
    # 支持的文档格式
    DOCUMENT_EXTENSIONS = {'.txt', '.md', '.pdf', '.doc', '.docx', '.json', '.csv'}
    
    def __init__(self):
        self.uploaded_files: List[Dict] = []
    
    def add_file(self, file_path: str) -> bool:
        """添加文件到上传列表"""
        if not os.path.exists(file_path):
            print(f"[FileUpload] 文件不存在: {file_path}")
            return False
        
        ext = Path(file_path).suffix.lower()
        file_info = {
            'path': file_path,
            'name': os.path.basename(file_path),
            'extension': ext,
            'size': os.path.getsize(file_path),
            'type': 'image' if ext in self.IMAGE_EXTENSIONS else 'document'
        }
        
        self.uploaded_files.append(file_info)
        print(f"[FileUpload] 已添加文件: {file_info['name']} ({file_info['type']})")
        return True
    
    def clear_files(self):
        """清空上传列表"""
        self.uploaded_files.clear()
        print("[FileUpload] 已清空上传列表")
    
    def get_image_base64(self, file_path: str) -> Optional[str]:
        """将图片转换为base64编码"""
        try:
            with open(file_path, 'rb') as f:
                return base64.b64encode(f.read()).decode('utf-8')
        except Exception as e:
            print(f"[FileUpload] 图片编码失败: {e}")
            return None
    
    def read_document(self, file_path: str) -> Optional[str]:
        """读取文档内容"""
        try:
            ext = Path(file_path).suffix.lower()
            
            if ext == '.pdf':
                # PDF需要特殊处理，这里返回提示
                return f"[PDF文件: {os.path.basename(file_path)} - 请在对话中描述PDF内容]"
            
            elif ext in ['.doc', '.docx']:
                return f"[Word文档: {os.path.basename(file_path)} - 请在对话中描述文档内容]"
            
            else:
                # 文本文件直接读取
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                    # 限制长度
                    max_len = 10000
                    if len(content) > max_len:
                        content = content[:max_len] + f"\n... [内容已截断，共{len(content)}字符]"
                    return content
                    
        except Exception as e:
            print(f"[FileUpload] 读取文档失败: {e}")
            return None
    
    def build_message_content(self) -> List[Dict]:
        """构建包含文件的消息内容（用于OpenAI API）"""
        content_parts = []
        
        for file_info in self.uploaded_files:
            if file_info['type'] == 'image':
                # 图片使用base64编码
                base64_data = self.get_image_base64(file_info['path'])
                if base64_data:
                    mime_type = f"image/{file_info['extension'].replace('.', '')}"
                    if mime_type == 'image/jpg':
                        mime_type = 'image/jpeg'
                    content_parts.append({
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:{mime_type};base64,{base64_data}"
                        }
                    })
            else:
                # 文档读取文本内容
                doc_content = self.read_document(file_info['path'])
                if doc_content:
                    content_parts.append({
                        "type": "text",
                        "text": f"\n--- 文件: {file_info['name']} ---\n{doc_content}\n---\n"
                    })
        
        return content_parts
    
    def get_upload_summary(self) -> str:
        """获取上传文件摘要"""
        if not self.uploaded_files:
            return "未上传任何文件"
        
        summary = [f"已上传 {len(self.uploaded_files)} 个文件:"]
        for f in self.uploaded_files:
            size_kb = f['size'] / 1024
            summary.append(f"  - {f['name']} ({f['type']}, {size_kb:.1f}KB)")
        return "\n".join(summary)


def load_planner_skill() -> str:
    """从skill文件加载规划师提示词"""
    skill_path = Path("skill/planner_skill.md")
    
    default_prompt = """你是AI World公司的首席规划师。你的任务是根据用户需求和上传的文件，为团队成员制定详细的工作分工。

【核心任务】
1. 深度分析用户需求和上传的文件内容
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
            
            if content.startswith('---'):
                end_idx = content.find('---', 3)
                if end_idx != -1:
                    content = content[end_idx + 3:].strip()
            
            print(f"[AgentPlannerV2] 已从 {skill_path} 加载规划师技能")
            return content
        else:
            print(f"[AgentPlannerV2] 技能文件不存在，使用默认提示词")
            return default_prompt
    except Exception as e:
        print(f"[AgentPlannerV2] 加载技能文件失败: {e}")
        return default_prompt


class AgentPlannerV2:
    """增强版AI规划师 - 支持文件上传和结果整合"""
    
    PLANNER_SYSTEM_PROMPT = load_planner_skill()
    
    # 结果整合的系统提示词
    CONSOLIDATION_SYSTEM_PROMPT = """你是AI World公司的首席文档整理专家。

【任务】
将多个员工的工作成果整合成一个完整的、格式统一的Markdown项目文档。

【整理要求】
1. 阅读并理解每位员工的工作成果
2. 统一格式为标准的Markdown
3. 确保内容逻辑连贯、结构清晰
4. 添加适当的标题层级和目录结构
5. 移除重复内容，补充缺失信息

【输出格式】
必须输出标准的Markdown格式：
```markdown
# 项目名称

## 目录
- [章节1](#章节1)
- [章节2](#章节2)

## 章节1
内容...

## 章节2
内容...

## 总结
...
```

【质量标准】
- 使用正确的Markdown语法
- 标题层级清晰（# ## ###）
- 代码块使用正确的语言标记
- 列表、表格格式正确
- 文档结构完整
"""

    def __init__(self, api_key: str = "", api_url: str = "", model: str = "qwen-max"):
        self.api_key = api_key
        self.api_url = api_url or "https://dashscope.aliyuncs.com/compatible-mode/v1"
        self.model = model
        self.plan_result = None
        self.is_running = False
        self.client = None
        self.file_handler = FileUploadHandler()
        
        if OPENAI_AVAILABLE and api_key:
            self._init_client()
    
    def _init_client(self):
        """初始化OpenAI客户端"""
        try:
            self.client = OpenAI(
                api_key=self.api_key,
                base_url=self.api_url
            )
            print(f"[AgentPlannerV2] 客户端初始化成功")
        except Exception as e:
            print(f"[AgentPlannerV2] 客户端初始化失败: {e}")
            self.client = None
    
    def set_config(self, api_key: str, api_url: str = "", model: str = "qwen-max"):
        """设置API配置"""
        self.api_key = api_key
        self.api_url = api_url or "https://dashscope.aliyuncs.com/compatible-mode/v1"
        self.model = model
        if OPENAI_AVAILABLE and api_key:
            self._init_client()
    
    def upload_file(self, file_path: str) -> bool:
        """上传文件"""
        return self.file_handler.add_file(file_path)
    
    def clear_uploads(self):
        """清空上传的文件"""
        self.file_handler.clear_files()
    
    def get_upload_summary(self) -> str:
        """获取上传文件摘要"""
        return self.file_handler.get_upload_summary()
    
    def generate_plan(
        self,
        selected_employees: List,
        user_requirement: str,
        on_token: Optional[Callable[[str], None]] = None,
        on_complete: Optional[Callable[[Optional[Dict]], None]] = None
    ) -> Optional[Dict]:
        """生成规划（支持文件上传）"""
        if not selected_employees:
            print("[AgentPlannerV2] 错误：未选择任何员工")
            return None
        
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
        """运行规划"""
        self.is_running = True
        output = ""
        
        try:
            # 构建提示词
            prompt = self._build_planning_prompt(employees, user_requirement)
            
            if on_token:
                on_token("[AI规划师] 正在分析需求并制定分工方案...\n\n")
                if self.file_handler.uploaded_files:
                    on_token(f"{self.file_handler.get_upload_summary()}\n\n")
            
            # 构建消息
            messages = self._build_messages(prompt)
            
            # 调用API
            if self.client and OPENAI_AVAILABLE:
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=messages,
                    temperature=0.7,
                    max_tokens=4096,
                    stream=True
                )
                
                for chunk in response:
                    if chunk.choices and chunk.choices[0].delta.content:
                        token = chunk.choices[0].delta.content
                        output += token
                        if on_token:
                            on_token(token)
            else:
                if on_token:
                    on_token("[系统] 使用备用方案...\n")
                output = self._call_api_fallback(prompt)
                if on_token and output:
                    on_token(output)
            
            # 解析结果
            plan = self._parse_output(output, employees)
            self.plan_result = plan
            self.is_running = False
            
            # 生成skill文件
            if plan:
                self._generate_all_skill_files(plan)
            
            if on_complete:
                on_complete(plan)
                
        except Exception as e:
            print(f"[AgentPlannerV2] 错误: {e}")
            self.is_running = False
            if on_complete:
                on_complete(None)
    
    def _build_messages(self, prompt: str) -> List[Dict]:
        """构建API消息（包含上传的文件）"""
        messages = [
            {"role": "system", "content": self.PLANNER_SYSTEM_PROMPT}
        ]
        
        # 如果有上传的文件，构建多模态消息
        if self.file_handler.uploaded_files:
            content_parts = [{"type": "text", "text": prompt}]
            content_parts.extend(self.file_handler.build_message_content())
            messages.append({"role": "user", "content": content_parts})
        else:
            messages.append({"role": "user", "content": prompt})
        
        return messages
    
    def _build_planning_prompt(self, employees: List, user_requirement: str) -> str:
        """构建规划提示词"""
        employee_info = []
        for i, emp in enumerate(employees):
            employee_info.append(f"员工{i} (ID:{emp.id}): {emp.name}")
        
        employee_list = "\n".join(employee_info)
        
        file_context = ""
        if self.file_handler.uploaded_files:
            file_context = f"\n【上传文件信息】\n{self.file_handler.get_upload_summary()}\n"
        
        prompt = f"""请为以下项目制定详细的分工规划：

【用户需求】
{user_requirement}
{file_context}
【团队信息】
团队规模: {len(employees)}人
团队成员:
{employee_list}

请按照系统提示词中的格式要求，输出完整的分工规划。
"""
        return prompt
    
    def _parse_output(self, output: str, employees: List) -> Optional[Dict]:
        """解析输出结果"""
        plan_match = re.search(
            r'\[AIWORLD_PLAN_START\](.*?)\[AIWORLD_PLAN_END\]',
            output,
            re.DOTALL
        )
        
        if not plan_match:
            print("[AgentPlannerV2] 错误：找不到规划标记")
            return self._fallback_parse(output, employees)
        
        plan_content = plan_match.group(1)
        project_goal = self._extract_tag(plan_content, 'PROJECT_GOAL')
        
        plan = {
            'project_goal': project_goal or '完成用户需求',
            'project_mode': '并行',
            'employees': [],
            'raw_response': output
        }
        
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
                plan['employees'].append({
                    'employee_id': emp.id,
                    'employee_name': emp.name,
                    'role': '执行专员',
                    'mode': '并行',
                    'skill_definition': self._get_default_skill()
                })
        
        return plan
    
    def _fallback_parse(self, output: str, employees: List) -> Dict:
        """备用解析"""
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
        """获取默认技能"""
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
    
    def _generate_all_skill_files(self, plan: Dict) -> List[str]:
        """为所有员工生成skill.md文件"""
        generated_files = []
        
        for emp_plan in plan['employees']:
            file_path = self._generate_single_skill_file(emp_plan)
            if file_path:
                generated_files.append(file_path)
        
        print(f"[AgentPlannerV2] 已生成 {len(generated_files)} 个技能文件")
        return generated_files
    
    def _generate_single_skill_file(self, emp_plan: Dict) -> Optional[str]:
        """生成单个员工的skill.md文件"""
        emp_id = emp_plan['employee_id']
        skill_content = emp_plan.get('skill_definition', '')
        
        if not skill_content:
            skill_content = self._get_default_skill()
        
        skill_file = f"skill/skill{emp_id}.md"
        
        # 格式化skill内容
        formatted_skill = self._format_skill_content(
            emp_plan['employee_name'],
            emp_plan['role'],
            skill_content
        )
        
        full_content = f"""---
name: {emp_plan['employee_name']}
role: {emp_plan['role']}
employee_id: {emp_id}
mode: 并行
generated_at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
generated_by: AI World Agent Planner V2
---

{formatted_skill}

---
*This skill file was automatically generated by AI World Agent Planner V2*
"""
        
        try:
            os.makedirs('skill', exist_ok=True)
            with open(skill_file, 'w', encoding='utf-8') as f:
                f.write(full_content)
            print(f"[AgentPlannerV2] 已生成技能文件: {skill_file}")
            return skill_file
        except Exception as e:
            print(f"[AgentPlannerV2] 错误：写入技能文件失败: {e}")
            return None
    
    def _format_skill_content(self, name: str, role: str, content: str) -> str:
        """格式化技能内容为标准Markdown"""
        # 确保内容有正确的标题
        if not content.strip().startswith('#'):
            content = f"# {name} - {role}\n\n{content}"
        
        # 标准化Markdown格式
        content = self._standardize_markdown(content)
        
        return content
    
    def _standardize_markdown(self, text: str) -> str:
        """标准化Markdown格式"""
        # 确保标题前后有空行
        text = re.sub(r'^(#{1,6}\s+.+)$', r'\n\1\n', text, flags=re.MULTILINE)
        
        # 标准化列表
        text = re.sub(r'^\s*[-*]\s+', '- ', text, flags=re.MULTILINE)
        
        # 标准化代码块
        text = re.sub(r'```(\w*)\n', r'```\1\n', text)
        
        # 移除多余的空行
        text = re.sub(r'\n{3,}', '\n\n', text)
        
        return text.strip()
    
    def consolidate_results(
        self,
        plan: Dict,
        employee_results: List[Dict],
        output_dir: str,
        on_token: Optional[Callable[[str], None]] = None,
        on_complete: Optional[Callable[[Optional[str]], None]] = None
    ):
        """整合所有员工的工作结果并格式化为Markdown"""
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
        """运行结果整合"""
        try:
            if on_token:
                on_token("[AI规划师] 正在整合所有员工的工作成果...\n")
                on_token("[AI规划师] 正在格式化为标准Markdown...\n\n")
            
            # 构建整理提示词
            prompt = self._build_consolidation_prompt(plan, employee_results)
            
            # 调用API进行整合
            if self.client and OPENAI_AVAILABLE:
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": self.CONSOLIDATION_SYSTEM_PROMPT},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.7,
                    max_tokens=8000,
                    stream=True
                )
                
                output = ""
                for chunk in response:
                    if chunk.choices and chunk.choices[0].delta.content:
                        token = chunk.choices[0].delta.content
                        output += token
                        if on_token:
                            on_token(token)
            else:
                output = self._call_api_fallback(prompt)
                if on_token and output:
                    on_token(output)
            
            # 格式化输出
            formatted_output = self._format_consolidated_result(output, plan)
            
            # 保存文件
            if formatted_output:
                os.makedirs(output_dir, exist_ok=True)
                
                # 保存主文档
                merged_file = os.path.join(output_dir, "MERGED_RESULT.md")
                with open(merged_file, 'w', encoding='utf-8') as f:
                    f.write(formatted_output)
                
                # 保存元数据
                meta_file = os.path.join(output_dir, "project_meta.json")
                metadata = {
                    "project_goal": plan.get('project_goal', ''),
                    "generated_at": datetime.now().isoformat(),
                    "employee_count": len(plan.get('employees', [])),
                    "employees": [
                        {
                            "id": emp['employee_id'],
                            "name": emp['employee_name'],
                            "role": emp['role']
                        }
                        for emp in plan.get('employees', [])
                    ]
                }
                with open(meta_file, 'w', encoding='utf-8') as f:
                    json.dump(metadata, f, ensure_ascii=False, indent=2)
                
                if on_token:
                    on_token(f"\n\n[完成] 整合文档已保存: {merged_file}\n")
                    on_token(f"[完成] 项目元数据已保存: {meta_file}\n")
                
                if on_complete:
                    on_complete(formatted_output)
            else:
                if on_complete:
                    on_complete(None)
                    
        except Exception as e:
            print(f"[AgentPlannerV2] 整合错误: {e}")
            if on_complete:
                on_complete(None)
    
    def _build_consolidation_prompt(self, plan: Dict, employee_results: List[Dict]) -> str:
        """构建结果整合提示词"""
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
        
        prompt = f"""请整合以下员工的工作成果，生成一个完整的、格式统一的Markdown项目文档。

【项目目标】
{plan.get('project_goal', '完成用户需求')}

【员工分工】
{division_text}

【各员工工作结果】
{results_combined}

【输出要求】
1. 使用标准Markdown格式
2. 包含清晰的目录结构
3. 统一标题层级
4. 代码块使用正确的语言标记
5. 确保内容逻辑连贯
6. 添加项目总结部分

请直接输出格式化后的Markdown文档内容。
"""
        return prompt
    
    def _format_consolidated_result(self, output: str, plan: Dict) -> str:
        """格式化整合结果"""
        # 提取Markdown内容（如果输出包含代码块）
        md_match = re.search(r'```markdown\n(.*?)\n```', output, re.DOTALL)
        if md_match:
            output = md_match.group(1)
        
        # 标准化格式
        output = self._standardize_markdown(output)
        
        # 添加文档头
        header = f"""# 项目整合结果

> **项目目标**: {plan.get('project_goal', '完成用户需求')}
> **生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
> **参与员工**: {len(plan.get('employees', []))}人
> **整理工具**: AI World Agent Planner V2

---

"""
        
        # 添加文档尾
        footer = f"""

---

## 项目元数据

- **员工列表**:
"""
        for emp in plan.get('employees', []):
            footer += f"  - {emp['employee_name']} ({emp['role']})\n"
        
        footer += f"""
- **文档版本**: 1.0
- **最后更新**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

---
*本文档由 AI World Agent Planner V2 自动生成*
"""
        
        return header + output + footer
    
    def _call_api_fallback(self, prompt: str) -> str:
        """备用API调用"""
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
                print(f"[AgentPlannerV2] API调用失败: {output}")
                return ""
        except Exception as e:
            print(f"[AgentPlannerV2] API调用错误: {e}")
            return ""


# 全局实例
agent_planner_v2 = AgentPlannerV2()
