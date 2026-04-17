# AI World - 输出解析器
# 严格解析AI输出中的标记，提取结构化数据

import re
from typing import Dict, List, Optional, Tuple

class OutputParser:
    """输出解析器 - 解析AI返回的标记格式内容"""
    
    @staticmethod
    def extract_tag_content(text: str, tag: str) -> Optional[str]:
        """
        提取标记之间的内容
        
        Args:
            text: 原始文本
            tag: 标记名称（如 SECTION:完成内容）
        
        Returns:
            标记之间的内容，如果没有找到则返回None
        """
        pattern = rf'\[{re.escape(tag)}\](.*?)\[/\s*{re.escape(tag)}\s*\]'
        match = re.search(pattern, text, re.DOTALL)
        if match:
            return match.group(1).strip()
        return None
    
    @staticmethod
    def extract_section(text: str, section_name: str) -> Optional[str]:
        """提取特定section的内容"""
        return OutputParser.extract_tag_content(text, f"SECTION:{section_name}")
    
    @staticmethod
    def parse_employee_output(text: str) -> Dict:
        """
        解析员工AI的输出
        
        Returns:
            {
                'stage_name': 阶段名称,
                'completed_content': 完成内容,
                'key_outputs': 关键产出列表,
                'quality_check': {
                    'meets_requirement': 是否满足需求,
                    'meets_standard': 是否达到标准,
                    'completion_percentage': 完成度百分比
                },
                'handoff': 向下传递内容,
                'output_files': 输出文件内容,
                'raw_text': 原始文本
            }
        """
        result = {
            'stage_name': '',
            'completed_content': '',
            'key_outputs': [],
            'quality_check': {
                'meets_requirement': False,
                'meets_standard': False,
                'completion_percentage': 0
            },
            'handoff': '',
            'output_files': '',
            'raw_text': text
        }
        
        # 提取 [AIWORLD_OUTPUT_START] 和 [AIWORLD_OUTPUT_END] 之间的内容
        start_marker = "[AIWORLD_OUTPUT_START]"
        end_marker = "[AIWORLD_OUTPUT_END]"
        
        start_idx = text.find(start_marker)
        end_idx = text.find(end_marker)
        
        if start_idx == -1 or end_idx == -1:
            print("[解析器] 警告: 未找到 AIWORLD_OUTPUT_START/END 标记")
            # 尝试解析整个文本
            content = text
        else:
            content = text[start_idx + len(start_marker):end_idx].strip()
        
        # 提取各个section
        result['stage_name'] = OutputParser.extract_section(content, "阶段名称") or \
                              OutputParser.extract_section(content, "角色名称") or ""
        
        result['completed_content'] = OutputParser.extract_section(content, "完成内容") or ""
        
        # 解析关键产出
        key_outputs_text = OutputParser.extract_section(content, "关键产出") or \
                          OutputParser.extract_section(content, "独立产出") or ""
        result['key_outputs'] = [line.strip() for line in key_outputs_text.split('\n') 
                                  if line.strip() and not line.strip().startswith('（')]
        
        # 解析质量检查
        quality_text = OutputParser.extract_section(content, "质量检查") or ""
        result['quality_check'] = OutputParser._parse_quality_check(quality_text)
        
        # 提取向下传递/整合说明
        result['handoff'] = OutputParser.extract_section(content, "向下传递") or \
                           OutputParser.extract_section(content, "整合说明") or ""
        
        # 提取输出文件
        result['output_files'] = OutputParser.extract_section(content, "输出文件") or ""
        
        return result
    
    @staticmethod
    def _parse_quality_check(text: str) -> Dict:
        """解析质量检查部分"""
        result = {
            'meets_requirement': False,
            'meets_standard': False,
            'completion_percentage': 0
        }
        
        # 检查是否满足需求
        if re.search(r'是否满足需求[:：]\s*是', text):
            result['meets_requirement'] = True
        
        # 检查是否达到标准
        if re.search(r'是否达到标准[:：]\s*是', text):
            result['meets_standard'] = True
        
        # 提取完成度百分比
        percentage_match = re.search(r'完成度百分比[:：]?\s*(\d+)', text)
        if percentage_match:
            result['completion_percentage'] = int(percentage_match.group(1))
        
        return result
    
    @staticmethod
    def parse_planner_output(text: str) -> Dict:
        """
        解析规划师的输出
        
        Returns:
            {
                'team_size': 团队规模,
                'members': [
                    {
                        'role': 角色名称,
                        'responsibility': 职责描述,
                        'mode': 工作模式,
                        'order': 执行顺序
                    }
                ],
                'workflow': 工作流程,
                'project_goal': 项目目标,
                'raw_text': 原始文本
            }
        """
        result = {
            'team_size': 0,
            'members': [],
            'workflow': '',
            'project_goal': '',
            'raw_text': text
        }
        
        # 提取 [AIWORLD_PLAN_START] 和 [AIWORLD_PLAN_END] 之间的内容
        start_marker = "[AIWORLD_PLAN_START]"
        end_marker = "[AIWORLD_PLAN_END]"
        
        start_idx = text.find(start_marker)
        end_idx = text.find(end_marker)
        
        if start_idx == -1 or end_idx == -1:
            print("[解析器] 警告: 未找到 AIWORLD_PLAN_START/END 标记")
            content = text
        else:
            content = text[start_idx + len(start_marker):end_idx].strip()
        
        # 提取团队规模
        team_size_text = OutputParser.extract_section(content, "团队规模") or ""
        size_match = re.search(r'(\d+)', team_size_text)
        if size_match:
            result['team_size'] = int(size_match.group(1))
        
        # 提取团队成员
        members_text = OutputParser.extract_section(content, "团队成员") or ""
        result['members'] = OutputParser._parse_members(members_text)
        
        # 提取工作流程
        result['workflow'] = OutputParser.extract_section(content, "工作流程") or ""
        
        # 提取项目目标
        result['project_goal'] = OutputParser.extract_section(content, "项目目标") or ""
        
        return result
    
    @staticmethod
    def _parse_members(text: str) -> List[Dict]:
        """解析成员列表 - 支持严格格式和宽松格式"""
        members = []
        
        # 方法1: 查找所有 [MEMBER:X]...[/MEMBER:X] 块（严格格式）
        member_pattern = r'\[MEMBER:(\d+)\](.*?)\[/MEMBER:\1\]'
        matches = re.findall(member_pattern, text, re.DOTALL)
        
        if matches:
            print(f"[解析器] 使用严格格式解析，找到 {len(matches)} 个成员")
            for idx, (_, member_content) in enumerate(matches):
                member = {
                    'role': OutputParser.extract_tag_content(member_content, "ROLE") or "",
                    'responsibility': OutputParser.extract_tag_content(member_content, "RESPONSIBILITY") or "",
                    'mode': OutputParser.extract_tag_content(member_content, "MODE") or "sequential",
                    'order': idx + 1
                }
                
                # 尝试解析order
                order_text = OutputParser.extract_tag_content(member_content, "ORDER")
                if order_text:
                    try:
                        member['order'] = int(order_text)
                    except:
                        pass
                
                if member['role']:  # 只添加有角色名称的成员
                    members.append(member)
        
        # 方法2: 如果没有找到严格格式，尝试宽松格式（【角色名称】XXX）
        if not members:
            print("[解析器] 严格格式未找到成员，尝试宽松格式")
            # 匹配 【角色名称】XXX 或 [ROLE]XXX 格式
            role_patterns = [
                r'[【\[]角色名称[】\]]\s*([^\n]+?)(?:\n|$)',
                r'[【\[]ROLE[】\]]\s*([^\n]+?)(?:\n|$)',
                r'(?:^|\n)\d+\.\s*([^【\[\n]+?)(?:[（(]|\n|$)',  # 1. 角色名
            ]
            
            for pattern in role_patterns:
                matches = re.findall(pattern, text, re.MULTILINE)
                for i, match in enumerate(matches):
                    role_name = match.strip()
                    if len(role_name) > 1 and len(role_name) < 50:
                        # 尝试找到对应的职责描述
                        resp_pattern = rf'{re.escape(match)}.*?[【\[]职责描述[】\]]\s*([^\n]+?)(?:\n|$)'
                        resp_match = re.search(resp_pattern, text, re.DOTALL)
                        responsibility = resp_match.group(1).strip() if resp_match else f"负责{role_name}工作"
                        
                        # 尝试找到工作模式
                        mode = "sequential"
                        if re.search(r'分工并行|并行', text):
                            mode = "parallel"
                        
                        members.append({
                            'role': role_name,
                            'responsibility': responsibility,
                            'mode': mode,
                            'order': i + 1
                        })
                
                if members:
                    print(f"[解析器] 宽松格式解析成功，找到 {len(members)} 个成员")
                    break
        
        return members
    
    @staticmethod
    def extract_code_blocks(text: str) -> List[Tuple[str, str]]:
        """
        提取代码块
        
        Returns:
            [(language, code), ...]
        """
        # 匹配 ```language\ncode\n``` 或 ```\ncode\n```
        pattern = r'```(\w*)\n(.*?)```'
        matches = re.findall(pattern, text, re.DOTALL)
        return matches
    
    @staticmethod
    def extract_handoff_core_content(handoff_text: str) -> str:
        """从向下传递内容中提取核心内容"""
        # 查找 "已完成的核心内容" 或类似标记
        patterns = [
            r'已完成的核心内容[：:]\s*(.+?)(?=\n\s*[-•]|$)',
            r'核心内容[：:]\s*(.+?)(?=\n\s*[-•]|$)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, handoff_text, re.DOTALL)
            if match:
                return match.group(1).strip()
        
        # 如果没有找到，返回前200字符
        return handoff_text[:200] if handoff_text else ""


# 便捷函数
def parse_employee_output(text: str) -> Dict:
    """解析员工输出的便捷函数"""
    return OutputParser.parse_employee_output(text)


def parse_planner_output(text: str) -> Dict:
    """解析规划师输出的便捷函数"""
    return OutputParser.parse_planner_output(text)


def extract_section(text: str, section_name: str) -> Optional[str]:
    """提取section的便捷函数"""
    return OutputParser.extract_section(text, section_name)
