# Planner Chat - AI规划师聊天界面
import pygame
from typing import List, Optional, Callable
from core.config import get_font
from core.constants import (
    MAX_STREAMING_TEXT_LENGTH, STREAMING_DISPLAY_LIMIT, MAX_DISPLAY_LINES,
    LINE_HEIGHT, SCROLL_SPEED, MOUSE_SCROLL_SPEED, CURSOR_BLINK_INTERVAL
)


class PlannerChat:
    """AI规划师聊天界面 - 显示aider的思考和流式输出"""
    
    def __init__(self, screen_width: int, screen_height: int):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.visible = False
        
        # 字体
        self.font_title = get_font(28)
        self.font_large = get_font(20)
        self.font_medium = get_font(16)
        self.font_small = get_font(14)
        
        # 聊天内容
        self.messages = []  # [(sender, content), ...]
        self.streaming_text = ""  # 当前流式输出的文本
        self.is_streaming = False
        self.plan_complete = False
        
        # 滚动
        self.scroll_y = 0
        self.max_scroll = 0
        
        # 动画
        self.cursor_visible = True
        self.cursor_timer = 0
        

    
    def show(self):
        """显示聊天界面"""
        self.visible = True
        self.messages = []
        self.streaming_text = ""
        self.is_streaming = False
        self.plan_complete = False
        self.scroll_y = 0
        
        # 添加欢迎消息 (使用文字替代emoji)
        self.add_message("system", "[AI规划师] 已启动，正在分析您的需求...")
    
    def hide(self):
        """隐藏聊天界面"""
        self.visible = False
    
    def add_message(self, sender: str, content: str):
        """添加消息"""
        self.messages.append((sender, content))
        # 自动滚动到底部
        self.scroll_y = max(0, len(self.messages) * 30 - self.screen_height + 200)
    
    def on_streaming_token(self, token: str):
        """接收流式输出token"""
        self.streaming_text += token
        self.is_streaming = True
        # 限制流式文本长度，避免内存问题
        if len(self.streaming_text) > MAX_STREAMING_TEXT_LENGTH:
            # 将当前内容转为消息，清空流式文本
            self.add_message("planner", self.streaming_text)
            self.streaming_text = ""
    
    def on_plan_complete(self, plan: Optional[dict]):
        """规划完成回调"""
        self.is_streaming = False
        self.plan_complete = True
        
        # 将剩余的流式文本转为消息
        if self.streaming_text:
            self.add_message("planner", self.streaming_text)
            self.streaming_text = ""
        
        if plan:
            self.add_message("system", "[完成] 分工规划已完成！")
            self.add_message("system", "[文件] 已生成各员工的技能配置文件")
            self.add_message("system", "[提示] 按 ESC 退出，按 空格 关闭")
        else:
            self.add_message("system", "[错误] 规划失败，请检查配置后重试")
    
    def handle_event(self, event) -> Optional[str]:
        """处理事件，返回操作结果"""
        if not self.visible:
            return None
        
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.hide()
                return "CLOSE"
            elif event.key == pygame.K_SPACE and self.plan_complete:
                self.hide()
                return "START_TASK"
            elif event.key == pygame.K_UP:
                self.scroll_y = max(0, self.scroll_y - SCROLL_SPEED)
            elif event.key == pygame.K_DOWN:
                self.scroll_y = min(self.max_scroll, self.scroll_y + SCROLL_SPEED)

        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 4:  # 鼠标滚轮向上
                self.scroll_y = max(0, self.scroll_y - MOUSE_SCROLL_SPEED)
            elif event.button == 5:  # 鼠标滚轮向下
                self.scroll_y = min(self.max_scroll, self.scroll_y + MOUSE_SCROLL_SPEED)
        
        return None
    
    def update(self, dt: float):
        """更新动画"""
        if not self.visible:
            return
        
        # 光标闪烁动画
        self.cursor_timer += dt
        if self.cursor_timer > CURSOR_BLINK_INTERVAL:
            self.cursor_visible = not self.cursor_visible
            self.cursor_timer = 0
    
    def draw(self, surface: pygame.Surface):
        """绘制聊天界面"""
        if not self.visible:
            return
        
        # 绘制半透明背景
        overlay = pygame.Surface((self.screen_width, self.screen_height))
        overlay.fill((20, 22, 25))
        overlay.set_alpha(240)
        surface.blit(overlay, (0, 0))
        
        # 绘制标题栏
        header_height = 60
        pygame.draw.rect(surface, (35, 38, 42), (0, 0, self.screen_width, header_height))
        pygame.draw.line(surface, (60, 65, 70), (0, header_height), (self.screen_width, header_height), 2)
        
        # 标题 (使用文字替代emoji)
        title = self.font_title.render("AI 规划师", True, (255, 220, 180))
        surface.blit(title, (30, 15))
        
        # 状态指示
        if self.is_streaming:
            status_text = "思考中" + ("..." if self.cursor_visible else "")
            status_color = (100, 200, 100)
        elif self.plan_complete:
            status_text = "已完成"
            status_color = (100, 200, 100)
        else:
            status_text = "等待中"
            status_color = (150, 150, 150)
        
        status = self.font_medium.render(status_text, True, status_color)
        surface.blit(status, (self.screen_width - 150, 20))
        
        # 绘制聊天区域背景
        chat_area = pygame.Rect(20, header_height + 10, self.screen_width - 40, self.screen_height - header_height - 100)
        pygame.draw.rect(surface, (30, 32, 35), chat_area, border_radius=10)
        pygame.draw.rect(surface, (50, 55, 60), chat_area, width=2, border_radius=10)
        
        # 绘制消息
        y_offset = chat_area.y + 10 - self.scroll_y
        line_height = LINE_HEIGHT
        
        # 创建裁剪区域
        clip_rect = chat_area.inflate(-20, -10)
        
        for sender, content in self.messages:
            if y_offset + line_height < chat_area.y:
                y_offset += self._estimate_text_height(content, chat_area.width - 40) + 15
                continue
            if y_offset > chat_area.bottom:
                break
            
            # 根据发送者设置颜色
            if sender == "system":
                color = (180, 180, 180)
                prefix = ""
            elif sender == "planner":
                color = (150, 200, 255)
                prefix = "[AI] "
            else:
                color = (255, 255, 255)
                prefix = ""
            
            # 绘制消息文本（自动换行）
            text = prefix + content
            lines = self._wrap_text(text, chat_area.width - 40)
            
            for line in lines:
                if y_offset >= chat_area.y and y_offset + line_height <= chat_area.bottom:
                    text_surface = self.font_small.render(line, True, color)
                    surface.blit(text_surface, (chat_area.x + 15, y_offset))
                y_offset += line_height
            
            y_offset += 10  # 消息间距
        
        # 绘制流式输出文本
        streaming_lines_count = 0
        if self.is_streaming and self.streaming_text:
            # 只显示最后一部分避免过长
            display_text = self.streaming_text[-STREAMING_DISPLAY_LIMIT:] if len(self.streaming_text) > STREAMING_DISPLAY_LIMIT else self.streaming_text
            lines = self._wrap_text("[AI] " + display_text, chat_area.width - 40)
            streaming_lines_count = len(lines)

            for i, line in enumerate(lines):
                if y_offset >= chat_area.y and y_offset + line_height <= chat_area.bottom:
                    text_surface = self.font_small.render(line, True, (150, 200, 255))
                    surface.blit(text_surface, (chat_area.x + 15, y_offset))
                y_offset += line_height
                if i >= MAX_DISPLAY_LINES:  # 限制显示行数
                    break
            
            # 绘制闪烁光标
            if self.cursor_visible and y_offset >= chat_area.y and y_offset <= chat_area.bottom:
                cursor_x = chat_area.x + 15 + self.font_small.size(lines[-1] if lines else "")[0]
                pygame.draw.line(surface, (150, 200, 255), 
                               (cursor_x, y_offset - line_height + 5),
                               (cursor_x, y_offset - 5), 2)
        
        # 更新最大滚动值 - 只计算实际内容高度
        old_max_scroll = self.max_scroll
        self.max_scroll = max(0, y_offset - chat_area.bottom + 20)
        
        # 流式输出时自动滚动到底部
        if self.is_streaming and self.max_scroll > old_max_scroll:
            self.scroll_y = self.max_scroll
        
        # 确保滚动值在有效范围内
        self.scroll_y = max(0, min(self.scroll_y, self.max_scroll))
        
        # 绘制滚动条
        if self.max_scroll > 0:
            scrollbar_height = max(50, chat_area.height * chat_area.height / (chat_area.height + self.max_scroll))
            scrollbar_y = chat_area.y + (chat_area.height - scrollbar_height) * self.scroll_y / self.max_scroll
            pygame.draw.rect(surface, (80, 85, 90), 
                           (chat_area.right - 8, scrollbar_y, 6, scrollbar_height), 
                           border_radius=3)
        
        # 绘制底部提示
        footer_y = self.screen_height - 70
        if self.plan_complete:
            hint = self.font_medium.render("按 ESC 或 空格 关闭", True, (180, 180, 180))
        else:
            hint = self.font_medium.render("规划中，请稍候...", True, (150, 150, 150))
        surface.blit(hint, (self.screen_width // 2 - hint.get_width() // 2, footer_y))
    

    
    def _wrap_text(self, text: str, max_width: int) -> List[str]:
        """自动换行文本 - 支持中文和英文混合"""
        lines = []
        current_line = ""
        
        for char in text:
            test_line = current_line + char
            # 检查是否超过最大宽度或者是换行符
            if char == '\n':
                if current_line:
                    lines.append(current_line)
                current_line = ""
            elif self.font_small.size(test_line)[0] <= max_width:
                current_line = test_line
            else:
                # 当前行已满，保存并开始新行
                if current_line:
                    lines.append(current_line)
                current_line = char
        
        # 添加最后一行
        if current_line:
            lines.append(current_line)
        
        # 如果没有换行（单行），直接返回
        if not lines:
            lines = [text]
        
        return lines
    
    def _estimate_text_height(self, text: str, max_width: int) -> int:
        """估算文本高度"""
        lines = self._wrap_text(text, max_width)
        return len(lines) * 24 + 10
