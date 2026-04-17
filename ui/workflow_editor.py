# AI World - 流程编辑器
# 选择配置好API的员工进行工作

import pygame
from core.config import SCREEN_WIDTH, SCREEN_HEIGHT, COLORS
from ui.text_input import TextInput

class WorkflowEditor:
    """流程编辑器 - 选择有效API的员工进行工作"""
    
    def __init__(self, font_large, font_medium, font_small, employees=None):
        self.font_large = font_large
        self.font_medium = font_medium
        self.font_small = font_small
        self.employees = employees or []  # 员工列表引用
        
        # 窗口尺寸 - 增加高度以避免元素重叠
        self.width = 650
        self.height = 600
        self.x = (SCREEN_WIDTH - self.width) // 2
        self.y = (SCREEN_HEIGHT - self.height) // 2
        
        # 状态
        self.active = False
        
        # 配置项
        self.selected_employees = []  # 选中的员工ID列表
        self.initial_prompt = ""  # 初始需求提示词
        
        # 输入框焦点
        self.prompt_input_active = False
        self.cursor_visible = True
        self.cursor_timer = 0
        
        # 使用TextInput处理文本输入
        self.text_input = TextInput(max_length=1000, allow_chinese=True)
        
        # 员工按钮区域
        self.employee_buttons = []
        
    def set_employees(self, employees):
        """设置员工列表"""
        self.employees = employees
        
    def show(self):
        """显示编辑器"""
        self.active = True
        self.prompt_input_active = False
        self.selected_employees = []  # 重置选择
        self.text_input.text = ""  # 重置文本
        self.initial_prompt = ""
        print("[流程编辑] 打开流程编辑器")
        
    def hide(self):
        """隐藏编辑器"""
        self.active = False
        self.prompt_input_active = False
        self.text_input.disable_text_input()
        
    def _is_employee_valid(self, employee):
        """检查员工是否配置了有效API"""
        return bool(employee.api_url and employee.api_key and employee.model_name)
    
    def handle_event(self, event):
        """处理输入事件"""
        if not self.active:
            return False
            
        if event.type == pygame.KEYDOWN:
            # ESC关闭
            if event.key == pygame.K_ESCAPE:
                self.hide()
                return True
                
            # 回车确认
            if event.key == pygame.K_RETURN and event.mod & pygame.KMOD_CTRL:
                self._confirm_settings()
                return True
                
            # 输入提示词 - 只处理特殊键，不处理字符输入（字符由TEXTINPUT处理）
            if self.prompt_input_active:
                # 只让TextInput处理特殊键（Backspace、Delete、Ctrl+V、回车等）
                if event.key == pygame.K_BACKSPACE or event.key == pygame.K_DELETE or \
                   event.key == pygame.K_RETURN or event.key == pygame.K_KP_ENTER or \
                   event.key == pygame.K_v and (event.mod & pygame.KMOD_CTRL) or \
                   event.key == pygame.K_c and (event.mod & pygame.KMOD_CTRL) or \
                   event.key == pygame.K_a and (event.mod & pygame.KMOD_CTRL):
                    self.text_input.handle_event(event)
                    self.initial_prompt = self.text_input.text
                    
        # 处理TEXTINPUT和TEXTEDITING事件（中文输入和常规字符输入）
        if self.prompt_input_active and (event.type == pygame.TEXTINPUT or event.type == pygame.TEXTEDITING):
            self.text_input.handle_event(event)
            self.initial_prompt = self.text_input.text
            return True
            
        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_x, mouse_y = event.pos
            
            # 检查是否点击输入框 - 调整位置避免与按钮重叠
            prompt_rect = pygame.Rect(self.x + 25, self.y + 340, self.width - 50, 120)
            was_active = self.prompt_input_active
            self.prompt_input_active = prompt_rect.collidepoint(mouse_x, mouse_y)
            
            # 启用/禁用文本输入
            if self.prompt_input_active and not was_active:
                self.text_input.enable_text_input()
            elif not self.prompt_input_active and was_active:
                self.text_input.disable_text_input()
            
            # 检查员工选择按钮 - 优化布局参数
            for i, emp in enumerate(self.employees):
                btn_rect = pygame.Rect(
                    self.x + 35 + (i % 2) * 295,  # 2列布局，增加水平间距
                    self.y + 95 + (i // 2) * 70,  # 增加垂直间距
                    270, 55  # 增大按钮尺寸
                )
                if btn_rect.collidepoint(mouse_x, mouse_y):
                    if self._is_employee_valid(emp):
                        # 切换选择状态
                        if emp.id in self.selected_employees:
                            self.selected_employees.remove(emp.id)
                            print(f"[流程编辑] 取消选择员工: {emp.name}")
                        else:
                            self.selected_employees.append(emp.id)
                            print(f"[流程编辑] 选择员工: {emp.name}")
                    else:
                        print(f"[流程编辑] 员工 {emp.name} 未配置有效API")
                    return True
                
            # 检查确认按钮 - 调整到底部中央
            confirm_rect = pygame.Rect(self.x + (self.width - 180) // 2, self.y + 500, 180, 45)
            if confirm_rect.collidepoint(mouse_x, mouse_y):
                self._confirm_settings()
                return True
                
        return True
    
    def _paste_from_clipboard(self):
        """从剪贴板粘贴"""
        try:
            import pyperclip
            clipboard_text = pyperclip.paste()
            if clipboard_text:
                self.initial_prompt += clipboard_text
                print(f"[粘贴] 已粘贴 {len(clipboard_text)} 字符")
        except ImportError:
            print("[粘贴] 错误: 未安装pyperclip模块")
        except Exception as e:
            print(f"[粘贴] 错误: {e}")
    
    def _copy_to_clipboard(self):
        """复制到剪贴板"""
        try:
            import pyperclip
            if self.initial_prompt:
                pyperclip.copy(self.initial_prompt)
                print(f"[复制] 已复制 {len(self.initial_prompt)} 字符")
        except ImportError:
            print("[复制] 错误: 未安装pyperclip模块")
        except Exception as e:
            print(f"[复制] 错误: {e}")
        
    def _confirm_settings(self):
        """确认设置 - 返回配置给main.py处理规划"""
        if not self.selected_employees:
            print("[流程编辑] 错误: 请至少选择一个配置了有效API的员工")
            return

        if not self.initial_prompt.strip():
            print("[流程编辑] 错误: 请输入初始需求提示词")
            return

        # 获取选中的员工对象
        selected_employee_objects = []
        for eid in self.selected_employees:
            if eid < len(self.employees):
                selected_employee_objects.append(self.employees[eid])

        selected_names = [emp.name for emp in selected_employee_objects]

        print(f"\n{'='*60}")
        print("[流程编辑] 配置确认:")
        print(f"  选中员工: {', '.join(selected_names)}")
        print(f"  提示词长度: {len(self.initial_prompt)} 字符")
        print(f"{'='*60}\n")

        # 关闭编辑器，返回配置
        self.active = False

        # 触发配置完成回调
        if hasattr(self, 'on_config_complete'):
            self.on_config_complete({
                'selected_employees': self.selected_employees,
                'selected_employee_objects': selected_employee_objects,
                'mode': 'parallel',
                'initial_prompt': self.initial_prompt
            })
            
    def update(self, dt):
        """更新状态"""
        self.cursor_timer += dt
        if self.cursor_timer > 500:
            self.cursor_visible = not self.cursor_visible
            self.cursor_timer = 0
        
        # 更新TextInput的按键重复
        if self.prompt_input_active:
            self.text_input.update(dt)
            
    def draw(self, surface):
        """绘制编辑器"""
        if not self.active:
            return
            
        # 半透明背景遮罩
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        surface.blit(overlay, (0, 0))
        
        # 主窗口背景
        dialog_rect = pygame.Rect(self.x, self.y, self.width, self.height)
        pygame.draw.rect(surface, (45, 40, 35), dialog_rect, border_radius=10)
        pygame.draw.rect(surface, (100, 90, 80), dialog_rect, width=3, border_radius=10)
        
        # 标题
        title = self.font_large.render("[流程编辑器]", True, (255, 220, 150))
        surface.blit(title, (self.x + (self.width - title.get_width()) // 2, self.y + 20))
        
        # 说明文字
        desc = self.font_small.render("选择配置了有效API的员工（灰色为未配置）", True, (180, 170, 160))
        surface.blit(desc, (self.x + (self.width - desc.get_width()) // 2, self.y + 60))
        
        # 绘制员工选择按钮 - 优化为2列布局，增加间距
        for i, emp in enumerate(self.employees):
            btn_x = self.x + 35 + (i % 2) * 295  # 2列，水平间距295
            btn_y = self.y + 95 + (i // 2) * 70   # 垂直间距70
            btn_rect = pygame.Rect(btn_x, btn_y, 270, 55)  # 按钮尺寸增大
            
            is_valid = self._is_employee_valid(emp)
            is_selected = emp.id in self.selected_employees
            
            if not is_valid:
                # 未配置API - 灰色禁用状态
                pygame.draw.rect(surface, (50, 50, 50), btn_rect, border_radius=5)
                pygame.draw.rect(surface, (80, 80, 80), btn_rect, width=2, border_radius=5)
                text_color = (120, 120, 120)
            elif is_selected:
                # 已选中 - 绿色
                pygame.draw.rect(surface, (80, 150, 80), btn_rect, border_radius=5)
                pygame.draw.rect(surface, (120, 200, 120), btn_rect, width=2, border_radius=5)
                text_color = (255, 255, 255)
            else:
                # 可选但未选中
                pygame.draw.rect(surface, (60, 60, 60), btn_rect, border_radius=5)
                pygame.draw.rect(surface, (120, 120, 120), btn_rect, width=2, border_radius=5)
                text_color = (200, 200, 200)
            
            # 员工名称 - 增加左边距
            name_text = self.font_medium.render(emp.name[:10], True, text_color)
            surface.blit(name_text, (btn_x + 15, btn_y + 8))
            
            # API状态指示 - 调整位置
            if is_valid:
                status_text = self.font_small.render("[已配置]", True, (150, 255, 150))
            else:
                status_text = self.font_small.render("[未配置]", True, (150, 150, 150))
            surface.blit(status_text, (btn_x + 15, btn_y + 30))
        
        # 输入提示词区域 - 调整位置到员工按钮下方
        y_offset = self.y + 310
        label = self.font_medium.render("初始需求提示词:", True, (220, 220, 220))
        surface.blit(label, (self.x + 25, y_offset))
        
        # 快捷键提示
        hint = self.font_small.render("(Ctrl+V粘贴 | Ctrl+C复制)", True, (150, 150, 150))
        surface.blit(hint, (self.x + 220, y_offset + 3))
        
        # 输入框 - 增大尺寸并调整位置
        prompt_rect = pygame.Rect(self.x + 25, y_offset + 30, self.width - 50, 120)
        if self.prompt_input_active:
            pygame.draw.rect(surface, (50, 50, 50), prompt_rect, border_radius=5)
            border_color = (150, 200, 255)
        else:
            pygame.draw.rect(surface, (35, 35, 35), prompt_rect, border_radius=5)
            border_color = (100, 100, 100)
        pygame.draw.rect(surface, border_color, prompt_rect, width=2, border_radius=5)
        
        # 提示词文本 - 显示已输入文本和输入法组合文本
        display_text = self.initial_prompt
        
        # 如果有组合文本（输入法候选），添加显示
        if self.prompt_input_active and self.text_input.composition_text:
            composition = self.text_input.composition_text
        else:
            composition = ""
        
        full_text = display_text + composition
        
        if full_text:
            # 自动换行显示
            lines = []
            current_line = ""
            for char in full_text:
                test_line = current_line + char
                if self.font_small.size(test_line)[0] < prompt_rect.width - 20:
                    current_line = test_line
                else:
                    lines.append(current_line)
                    current_line = char
            if current_line:
                lines.append(current_line)
            
            # 计算组合文本的起始行和列（用于高亮显示）
            comp_start_pos = len(display_text)
            current_pos = 0
            comp_start_line = 0
            comp_start_col = 0
            
            for i, line in enumerate(lines):
                line_start = current_pos
                line_end = current_pos + len(line)
                if comp_start_pos >= line_start and comp_start_pos < line_end:
                    comp_start_line = i
                    comp_start_col = comp_start_pos - line_start
                    break
                current_pos = line_end
            
            # 只显示前6行
            for i, line in enumerate(lines[:6]):
                if i == comp_start_line and composition:
                    # 这一行包含组合文本，分开渲染
                    before_comp = line[:comp_start_col]
                    comp_part = line[comp_start_col:]
                    
                    x_offset = prompt_rect.x + 10
                    if before_comp:
                        before_surface = self.font_small.render(before_comp, True, (220, 220, 220))
                        surface.blit(before_surface, (x_offset, prompt_rect.y + 10 + i * 18))
                        x_offset += before_surface.get_width()
                    
                    if comp_part:
                        comp_surface = self.font_small.render(comp_part, True, (180, 200, 255))
                        surface.blit(comp_surface, (x_offset, prompt_rect.y + 10 + i * 18))
                        # 绘制下划线
                        underline_y = prompt_rect.y + 10 + i * 18 + comp_surface.get_height() + 1
                        pygame.draw.line(surface, (180, 200, 255),
                                       (x_offset, underline_y),
                                       (x_offset + comp_surface.get_width(), underline_y), 1)
                else:
                    text_surface = self.font_small.render(line, True, (220, 220, 220))
                    surface.blit(text_surface, (prompt_rect.x + 10, prompt_rect.y + 10 + i * 18))
                
            # 显示省略号
            if len(lines) > 6:
                ellipsis = self.font_small.render("...", True, (150, 150, 150))
                surface.blit(ellipsis, (prompt_rect.x + 10, prompt_rect.y + 10 + 6 * 18))
        else:
            # 占位符
            placeholder = self.font_small.render("点击输入初始需求提示词...", True, (120, 120, 120))
            surface.blit(placeholder, (prompt_rect.x + 10, prompt_rect.y + 15))
            
        # 光标
        if self.prompt_input_active and self.cursor_visible:
            cursor_x = prompt_rect.x + 10
            cursor_y = prompt_rect.y + 15
            if self.initial_prompt:
                lines = self.initial_prompt.split('\n')
                if lines:
                    last_line = lines[-1]
                    cursor_x += self.font_small.size(last_line)[0]
                    cursor_y += (len(lines) - 1) * 18
            pygame.draw.line(surface, (200, 200, 200), 
                           (cursor_x, cursor_y), 
                           (cursor_x, cursor_y + 16), 2)
                           
        # 确认按钮 - 调整到底部中央，增加边距
        confirm_rect = pygame.Rect(self.x + (self.width - 180) // 2, self.y + 500, 180, 45)
        pygame.draw.rect(surface, (80, 120, 80), confirm_rect, border_radius=5)
        pygame.draw.rect(surface, (120, 180, 120), confirm_rect, width=2, border_radius=5)
        
        confirm_text = self.font_medium.render("确认 (Ctrl+Enter)", True, (255, 255, 255))
        surface.blit(confirm_text, (confirm_rect.x + 15, confirm_rect.y + 10))
        
        # 提示信息 - 调整位置到底部右侧
        hint_text = self.font_small.render("按 ESC 取消", True, (150, 150, 150))
        surface.blit(hint_text, (self.x + self.width - 110, self.y + self.height - 30))
        
    def get_config(self):
        """获取当前配置"""
        return {
            'selected_employees': self.selected_employees,
            'mode': 'parallel',
            'initial_prompt': self.initial_prompt
        }
