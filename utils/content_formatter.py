# 内容格式化工具 - 整理AI生成的文本格式
import re


class ContentFormatter:
    """整理和格式化AI生成的内容"""
    
    @staticmethod
    def format_content(content: str, content_type: str = "auto") -> str:
        """
        格式化内容
        
        Args:
            content: 原始内容
            content_type: 内容类型 (poem, article, code, auto)
        
        Returns:
            格式化后的内容
        """
        if not content:
            return ""
        
        # 自动检测内容类型
        if content_type == "auto":
            content_type = ContentFormatter._detect_content_type(content)
        
        # 清理内容
        formatted = content.strip()
        
        # 移除AI标记
        formatted = ContentFormatter._remove_ai_markers(formatted)
        
        # 根据类型格式化
        if content_type == "poem":
            formatted = ContentFormatter._format_poem(formatted)
        elif content_type == "article":
            formatted = ContentFormatter._format_article(formatted)
        elif content_type == "code":
            formatted = ContentFormatter._format_code(formatted)
        else:
            formatted = ContentFormatter._format_general(formatted)
        
        return formatted
    
    @staticmethod
    def _detect_content_type(content: str) -> str:
        """自动检测内容类型"""
        # 检测诗词
        if re.search(r'[词牌名|词牌|调寄|七律|五律|绝句]', content):
            return "poem"
        
        # 检测诗歌
        if re.search(r'[诗歌|现代诗|散文诗]', content) or len(re.findall(r'\n', content)) < 10:
            lines = content.strip().split('\n')
            avg_len = sum(len(line) for line in lines) / len(lines) if lines else 0
            if avg_len < 30:  # 短行可能是诗歌
                return "poem"
        
        # 检测代码
        if re.search(r'```|def |class |import |function |var |const ', content):
            return "code"
        
        # 默认为文章
        return "article"
    
    @staticmethod
    def _remove_ai_markers(content: str) -> str:
        """移除AI生成的标记"""
        # 移除常见的AI标记
        markers = [
            r'\[AIWORLD_OUTPUT_START\]\s*\n?',
            r'\[AIWORLD_OUTPUT_END\]\s*\n?',
            r'\[AIWORLD_[^\]]+\]',
            r'\[SECTION:[^\]]+\]\s*\n?',
            r'\[/SECTION:[^\]]+\]\s*\n?',
            r'^以下是.*?：\s*\n',
            r'^以下是.*?的.*?:\s*\n',
            r'^为您生成.*?：\s*\n',
            r'^根据您的要求.*?：\s*\n',
            r'【强制要求.*?】',
            r'【绝对重要.*?】',
            r'\[STRICT_OUTPUT_FORMAT\].*?\[/STRICT_OUTPUT_FORMAT\]',
        ]
        
        result = content
        for marker in markers:
            result = re.sub(marker, '', result, flags=re.MULTILINE | re.DOTALL)
        
        # 清理多余的空行
        result = re.sub(r'\n{3,}', '\n\n', result)
        
        return result.strip()
    
    @staticmethod
    def _format_poem(content: str) -> str:
        """格式化诗词"""
        lines = content.split('\n')
        formatted_lines = []
        
        # 标题和作者
        title = ""
        author = ""
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # 检测标题（通常在开头，较短）
            if not title and len(line) < 20 and not re.match(r'^[\d一二三四五六七八九十]', line):
                if '·' in line or '《' in line or '词牌' in line or len(line) < 10:
                    title = line
                    formatted_lines.append(f"## {title}")
                    formatted_lines.append("")
                    continue
            
            # 检测作者信息
            if re.match(r'^[作者|诗人|创作|by|By]', line) or (len(line) < 15 and '：' in line):
                author = line
                formatted_lines.append(f"*{author}*")
                formatted_lines.append("")
                continue
            
            # 诗词正文 - 保持原样，但确保格式正确
            if line:
                formatted_lines.append(line)
        
        return '\n'.join(formatted_lines)
    
    @staticmethod
    def _format_article(content: str) -> str:
        """格式化文章"""
        lines = content.split('\n')
        formatted_lines = []
        
        in_code_block = False
        paragraph_buffer = []
        
        for line in lines:
            stripped = line.strip()
            
            # 代码块处理
            if stripped.startswith('```'):
                # 先清空段落缓冲区
                if paragraph_buffer:
                    formatted_lines.append(''.join(paragraph_buffer))
                    formatted_lines.append("")
                    paragraph_buffer = []
                
                in_code_block = not in_code_block
                formatted_lines.append(stripped)
                continue
            
            if in_code_block:
                formatted_lines.append(line)
                continue
            
            # 空行处理
            if not stripped:
                if paragraph_buffer:
                    formatted_lines.append(''.join(paragraph_buffer))
                    formatted_lines.append("")
                    paragraph_buffer = []
                continue
            
            # 标题检测
            if re.match(r'^#{1,6}\s', stripped):
                if paragraph_buffer:
                    formatted_lines.append(''.join(paragraph_buffer))
                    formatted_lines.append("")
                    paragraph_buffer = []
                formatted_lines.append(stripped)
                formatted_lines.append("")
                continue
            
            # 列表项
            if re.match(r'^[\-\*\+\d]\.', stripped) or re.match(r'^\d+\)', stripped):
                if paragraph_buffer:
                    formatted_lines.append(''.join(paragraph_buffer))
                    formatted_lines.append("")
                    paragraph_buffer = []
                formatted_lines.append(stripped)
                continue
            
            # 普通段落
            paragraph_buffer.append(stripped)
        
        # 处理最后的段落
        if paragraph_buffer:
            formatted_lines.append(''.join(paragraph_buffer))
        
        # 清理多余空行
        result = []
        prev_empty = False
        for line in formatted_lines:
            is_empty = not line.strip()
            if is_empty and prev_empty:
                continue
            result.append(line)
            prev_empty = is_empty
        
        return '\n'.join(result)
    
    @staticmethod
    def _format_code(content: str) -> str:
        """格式化代码"""
        lines = content.split('\n')
        formatted_lines = []
        
        in_code_block = False
        code_buffer = []
        language = ""
        
        for line in lines:
            stripped = line.strip()
            
            # 检测代码块开始
            if stripped.startswith('```'):
                if not in_code_block:
                    # 开始代码块
                    in_code_block = True
                    language = stripped[3:].strip()
                    if code_buffer:
                        # 保存之前的说明文字
                        formatted_lines.append('\n'.join(code_buffer))
                        formatted_lines.append("")
                        code_buffer = []
                    formatted_lines.append(f"```{language}")
                else:
                    # 结束代码块
                    in_code_block = False
                    formatted_lines.append('```')
                    formatted_lines.append("")
                continue
            
            if in_code_block:
                formatted_lines.append(line)
            else:
                # 代码块外的说明文字
                if stripped:
                    code_buffer.append(stripped)
        
        # 处理未闭合的代码块
        if in_code_block:
            formatted_lines.append('```')
        
        # 处理剩余的说明文字
        if code_buffer:
            formatted_lines.append('\n'.join(code_buffer))
        
        return '\n'.join(formatted_lines)
    
    @staticmethod
    def _format_general(content: str) -> str:
        """通用格式化"""
        # 移除多余的空行
        content = re.sub(r'\n{3,}', '\n\n', content)
        
        # 确保段落之间有换行
        lines = content.split('\n')
        formatted_lines = []
        
        for line in lines:
            stripped = line.strip()
            if stripped:
                formatted_lines.append(stripped)
            else:
                formatted_lines.append("")
        
        return '\n'.join(formatted_lines)
    
    @staticmethod
    def extract_title(content: str) -> str:
        """从内容中提取标题"""
        lines = content.split('\n')
        
        for line in lines[:5]:  # 检查前5行
            line = line.strip()
            # Markdown标题
            if line.startswith('# '):
                return line[2:].strip()
            # 短行可能是标题
            if len(line) < 30 and not line.startswith('```') and not line.startswith('-'):
                return line
        
        return "未命名作品"
    
    @staticmethod
    def format_for_markdown(content: str, title: str = "", author: str = "") -> str:
        """
        将内容格式化为标准Markdown文档
        
        Args:
            content: 原始内容
            title: 标题
            author: 作者
        
        Returns:
            格式化后的Markdown文档
        """
        formatted_content = ContentFormatter.format_content(content)
        
        if not title:
            title = ContentFormatter.extract_title(content)
        
        md_parts = []
        
        # 标题
        md_parts.append(f"# {title}")
        md_parts.append("")
        
        # 作者
        if author:
            md_parts.append(f"**作者**: {author}")
            md_parts.append("")
        
        # 内容
        md_parts.append(formatted_content)
        
        return '\n'.join(md_parts)
