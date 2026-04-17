# -*- coding: utf-8 -*-
"""
AI输出处理器 - 严格处理各种不规范的AI输出
支持：格式修复、内容提取、智能缝合
"""

import re
import json
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass


@dataclass
class ProcessedOutput:
    """处理后的输出结果"""
    raw_content: str  # 原始内容
    cleaned_content: str  # 清理后的内容
    structured_data: Dict  # 结构化数据
    is_valid: bool  # 是否有效
    errors: List[str]  # 处理过程中的错误


class AIOutputProcessor:
    """AI输出处理器"""
    
    # 常见的AI输出标记
    MARKERS = {
        'start': [
            r'\[AIWORLD_OUTPUT_START\]',
            r'\[OUTPUT_START\]',
            r'\[RESULT_START\]',
            r'---\s*开始\s*---',
            r'===\s*输出开始\s*===',
        ],
        'end': [
            r'\[AIWORLD_OUTPUT_END\]',
            r'\[OUTPUT_END\]',
            r'\[RESULT_END\]',
            r'---\s*结束\s*---',
            r'===\s*输出结束\s*===',
        ],
        'section_start': [
            r'\[SECTION:([^\]]+)\]',
            r'##\s*\[([^\]]+)\]',
            r'【([^】]+)】',
        ],
        'section_end': [
            r'\[/SECTION:[^\]]+\]',
        ],
        'employee_start': [
            r'\[EMPLOYEE:(\d+)\]',
            r'\[员工:(\d+)\]',
            r'###\s*员工\s*(\d+)',
        ],
        'employee_end': [
            r'\[/EMPLOYEE:\d+\]',
        ],
    }
    
    # 需要移除的AI废话
    FLUFF_PATTERNS = [
        r'^以下是.*?[：:]\s*\n?',
        r'^这是.*?[：:]\s*\n?',
        r'^我来.*?[：:]\s*\n?',
        r'^根据.*?，',
        r'^好的[，,]\s*',
        r'^明白了[，,]\s*',
        r'^收到[，,]\s*',
        r'^开始.*?[：:]\s*\n?',
        r'^完成.*?[：:]\s*\n?',
    ]
    
    @classmethod
    def process(cls, content: str, expected_format: str = "markdown") -> ProcessedOutput:
        """处理AI输出"""
        errors = []
        
        if not content or not content.strip():
            return ProcessedOutput(
                raw_content=content,
                cleaned_content="",
                structured_data={},
                is_valid=False,
                errors=["内容为空"]
            )
        
        # 步骤1: 提取标记区域
        extracted, extract_errors = cls._extract_marked_content(content)
        errors.extend(extract_errors)
        
        # 步骤2: 清理废话和标记
        cleaned = cls._clean_content(extracted)
        
        # 步骤3: 修复格式
        formatted = cls._fix_format(cleaned, expected_format)
        
        # 步骤4: 结构化解析
        structured = cls._parse_structure(formatted)
        
        # 步骤5: 验证
        is_valid, validation_errors = cls._validate(formatted, expected_format)
        errors.extend(validation_errors)
        
        return ProcessedOutput(
            raw_content=content,
            cleaned_content=formatted,
            structured_data=structured,
            is_valid=is_valid,
            errors=errors
        )
    
    @classmethod
    def _extract_marked_content(cls, content: str) -> Tuple[str, List[str]]:
        """提取标记区域内的内容"""
        errors = []
        
        # 查找开始标记
        start_match = None
        for pattern in cls.MARKERS['start']:
            match = re.search(pattern, content, re.IGNORECASE)
            if match:
                start_match = match
                break
        
        # 查找结束标记
        end_match = None
        for pattern in cls.MARKERS['end']:
            match = re.search(pattern, content, re.IGNORECASE)
            if match:
                end_match = match
                break
        
        if start_match and end_match:
            start_pos = start_match.end()
            end_pos = end_match.start()
            if start_pos < end_pos:
                return content[start_pos:end_pos].strip(), errors
            else:
                errors.append("开始标记在结束标记之后")
        
        return content.strip(), errors
    
    @classmethod
    def _clean_content(cls, content: str) -> str:
        """清理内容中的废话和多余标记"""
        cleaned = content
        
        # 移除废话
        for pattern in cls.FLUFF_PATTERNS:
            cleaned = re.sub(pattern, '', cleaned, flags=re.MULTILINE | re.IGNORECASE)
        
        # 移除所有标记
        for marker_type, patterns in cls.MARKERS.items():
            for pattern in patterns:
                cleaned = re.sub(pattern, '', cleaned, flags=re.IGNORECASE)
        
        # 清理多余的空行
        cleaned = re.sub(r'\n{3,}', '\n\n', cleaned)
        
        # 清理行首行尾空白
        cleaned = '\n'.join(line.strip() for line in cleaned.split('\n'))
        
        return cleaned.strip()
    
    @classmethod
    def _fix_format(cls, content: str, expected_format: str) -> str:
        """修复格式问题"""
        if expected_format == "markdown":
            return cls._fix_markdown(content)
        elif expected_format == "json":
            return cls._fix_json(content)
        else:
            return content
    
    @classmethod
    def _fix_markdown(cls, content: str) -> str:
        """修复Markdown格式"""
        fixed = content
        
        # 确保标题格式正确
        fixed = re.sub(r'^(#{1,6})([^\s#])', r'\1 \2', fixed, flags=re.MULTILINE)
        
        # 确保列表格式正确
        fixed = re.sub(r'^\s*[-*]\s*', '- ', fixed, flags=re.MULTILINE)
        
        # 修复代码块
        fixed = cls._fix_code_blocks(fixed)
        
        # 确保段落之间有空行
        fixed = re.sub(r'([^\n])\n([^\n#\-`\s])', r'\1\n\n\2', fixed)
        
        return fixed.strip()
    
    @classmethod
    def _fix_code_blocks(cls, content: str) -> str:
        """修复代码块格式"""
        code_block_pattern = r'```[\w]*\n'
        matches = list(re.finditer(code_block_pattern, content))
        
        if len(matches) % 2 != 0:
            content += '\n```'
        
        return content
    
    @classmethod
    def _fix_json(cls, content: str) -> str:
        """修复JSON格式"""
        # 尝试解析JSON
        try:
            data = json.loads(content)
            return json.dumps(data, ensure_ascii=False, indent=2)
        except:
            # 尝试提取JSON部分
            json_match = re.search(r'\{.*\}', content, re.DOTALL)
            if json_match:
                try:
                    data = json.loads(json_match.group())
                    return json.dumps(data, ensure_ascii=False, indent=2)
                except:
                    pass
        return content
    
    @classmethod
    def _parse_structure(cls, content: str) -> Dict:
        """解析内容结构"""
        structure = {
            'has_title': bool(re.search(r'^#{1,6}\s+', content, re.MULTILINE)),
            'has_code': '```' in content,
            'has_table': '|' in content,
            'has_list': bool(re.search(r'^[-*]\s+', content, re.MULTILINE)),
            'paragraph_count': len([p for p in content.split('\n\n') if p.strip()]),
            'line_count': len([l for l in content.split('\n') if l.strip()]),
        }
        return structure
    
    @classmethod
    def _validate(cls, content: str, expected_format: str) -> Tuple[bool, List[str]]:
        """验证内容有效性"""
        errors = []
        
        if not content.strip():
            errors.append("内容为空")
            return False, errors
        
        if expected_format == "markdown":
            # 检查代码块是否闭合
            code_blocks = content.count('```')
            if code_blocks % 2 != 0:
                errors.append("代码块未闭合")
        
        return len(errors) == 0, errors
    
    @classmethod
    def stitch_outputs(cls, outputs: List[str], separator: str = "\n\n---\n\n") -> str:
        """
        将多个AI输出缝合在一起
        
        Args:
            outputs: 多个AI输出内容列表
            separator: 分隔符
        
        Returns:
            缝合后的内容
        """
        processed_outputs = []
        
        for i, output in enumerate(outputs):
            if not output or not output.strip():
                continue
            
            # 处理每个输出
            processed = cls.process(output)
            
            if processed.cleaned_content:
                header = f"## 部分 {i+1}\n\n"
                processed_outputs.append(header + processed.cleaned_content)
        
        return separator.join(processed_outputs)
    
    @classmethod
    def create_consolidation_prompt(cls, stitched_content: str, project_goal: str = "") -> str:
        """
        创建让规划师整理内容的提示词
        
        Args:
            stitched_content: 缝合后的内容
            project_goal: 项目目标
        
        Returns:
            提示词
        """
        # 构建项目目标部分（避免在f-string中使用反斜杠）
        goal_section = ""
        if project_goal:
            goal_section = "【项目目标】\n" + project_goal + "\n"
        
        prompt = f"""请整理以下内容，生成一个格式规范、结构清晰的Markdown文档。

{goal_section}【待整理内容】
{stitched_content}

【整理要求】
1. 统一标题层级（使用 # ## ###）
2. 确保代码块正确闭合
3. 修复列表格式
4. 移除重复内容
5. 确保段落之间有空行
6. 添加目录（如果内容较长）
7. 保持内容的逻辑连贯性

【输出格式】
直接输出整理后的Markdown内容，不要添加任何解释性文字。
"""
        return prompt


class ResultConsolidator:
    """结果整合器 - 整合多个员工的工作成果"""
    
    @staticmethod
    def consolidate(
        employee_results: List[Dict],
        project_goal: str = "",
        use_planner: bool = False,
        planner_client = None
    ) -> str:
        """
        整合所有员工的工作成果
        
        Args:
            employee_results: 员工结果列表，每个元素包含 'employee_name', 'role', 'content'
            project_goal: 项目目标
            use_planner: 是否使用规划师进行最终整理
            planner_client: 规划师客户端（如果使用规划师）
        
        Returns:
            整合后的Markdown内容
        """
        # 步骤1: 提取所有内容
        contents = []
        for result in employee_results:
            content = result.get('content', '')
            if content:
                # 添加员工信息头
                header = f"### {result.get('role', '员工')} - {result.get('employee_name', 'Unknown')}\n\n"
                contents.append(header + content)
        
        if not contents:
            return "# 项目结果\n\n暂无内容"
        
        # 步骤2: 缝合内容
        stitched = AIOutputProcessor.stitch_outputs(contents, separator="\n\n---\n\n")
        
        # 步骤3: 如果使用规划师，让规划师整理
        if use_planner and planner_client:
            prompt = AIOutputProcessor.create_consolidation_prompt(stitched, project_goal)
            
            try:
                # 调用规划师
                messages = [
                    {"role": "system", "content": "你是文档整理专家，擅长将多个文档整合为格式规范的Markdown。"},
                    {"role": "user", "content": prompt}
                ]
                
                response = planner_client.chat.completions.create(
                    model="qwen-max",
                    messages=messages,
                    temperature=0.3,
                    max_tokens=8000
                )
                
                consolidated = response.choices[0].message.content
                
                # 处理规划师的输出
                processed = AIOutputProcessor.process(consolidated)
                return processed.cleaned_content
                
            except Exception as e:
                print(f"[ResultConsolidator] 规划师整理失败: {e}")
                # 回退到简单缝合
                return stitched
        
        # 步骤4: 不使用规划师，直接返回缝合后的内容
        return stitched
    
    @staticmethod
    def format_final_document(
        content: str,
        project_name: str = "项目结果",
        project_goal: str = "",
        employee_count: int = 0
    ) -> str:
        """
        格式化最终文档
        
        Args:
            content: 整合后的内容
            project_name: 项目名称
            project_goal: 项目目标
            employee_count: 参与员工数
        
        Returns:
            格式化后的完整文档
        """
        from datetime import datetime
        
        # 处理内容
        processed = AIOutputProcessor.process(content)
        cleaned_content = processed.cleaned_content
        
        # 构建文档头
        header = f"""# {project_name}

> **生成时间**: {datetime.now().strftime('%Y年%m月%d日 %H:%M')}
> **参与人数**: {employee_count} 人
{f'> **项目目标**: {project_goal}' if project_goal else ''}

---

## 目录

- [项目概述](#项目概述)
- [详细内容](#详细内容)
- [总结](#总结)

---

## 项目概述

{f'**目标**: {project_goal}' if project_goal else '本项目由AI World团队协作完成。'}

---

## 详细内容

"""
        
        # 构建文档尾
        footer = f"""

---

## 总结

本项目由 {employee_count} 名AI员工协作完成。

### 文档信息

- **生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- **文档版本**: 1.0
- **格式状态**: {'已格式化' if processed.is_valid else '需要手动检查'}
{f"- **处理警告**: {', '.join(processed.errors)}" if processed.errors else ''}

---

*Generated by AI World Result Consolidator*
"""
        
        return header + cleaned_content + footer


# 便捷函数
def process_ai_output(content: str, expected_format: str = "markdown") -> ProcessedOutput:
    """处理AI输出"""
    return AIOutputProcessor.process(content, expected_format)


def stitch_ai_outputs(outputs: List[str]) -> str:
    """缝合多个AI输出"""
    return AIOutputProcessor.stitch_outputs(outputs)


def consolidate_results(
    employee_results: List[Dict],
    project_goal: str = "",
    use_planner: bool = False,
    planner_client = None
) -> str:
    """整合员工结果"""
    return ResultConsolidator.consolidate(employee_results, project_goal, use_planner, planner_client)
