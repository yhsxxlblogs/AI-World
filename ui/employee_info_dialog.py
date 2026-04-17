# 员工信息弹窗 - 显示和编辑员工详细信息 - 剧情类风格
import pygame
import os
from core.config import COLORS, SCREEN_WIDTH, SCREEN_HEIGHT, get_font
from utils.localization import get_text
from ui.text_input import TextInput

class InputBox:
    """输入框组件 - 剧情类风格，支持中文输入和连续删除"""
    def __init__(self, x, y, width, height, text='', label='', password=False):
        self.rect = pygame.Rect(x, y, width, height)
        self.color = (130, 115, 95)
        self.text = text
        self.label = label
        self.password = password
        self.font = get_font(14)
        self.active = False
        self.cursor_visible = True
        self.cursor_timer = 0
        
        # 使用TextInput处理文本输入
        self.text_input = TextInput(max_length=500, allow_chinese=True)
        self.text_input.text = text
        
    def handle_event(self, event):
        """处理输入事件"""
        if event.type == pygame.MOUSEBUTTONDOWN:
            was_active = self.active
            if self.rect.collidepoint(event.pos):
                self.active = True
                if not was_active:
                    self.text_input.enable_text_input()
            else:
                if self.active:
                    self.active = False
                    self.text_input.disable_text_input()
            self.color = (200, 170, 130) if self.active else (130, 115, 95)
                
        # 使用TextInput处理事件
        if self.active:
            # 处理TEXTINPUT和TEXTEDITING事件（中文输入）
            if event.type == pygame.TEXTINPUT or event.type == pygame.TEXTEDITING:
                self.text_input.handle_event(event)
                self.text = self.text_input.text
                return
                
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    self.active = False
                    self.text_input.disable_text_input()
                    self.color = (130, 115, 95)
                    return
                elif event.key == pygame.K_BACKSPACE:
                    # Backspace删除
                    self.text_input.handle_event(event)
                    self.text = self.text_input.text
                    return
                elif event.key == pygame.K_v and (event.mod & pygame.KMOD_CTRL):
                    # Ctrl+V粘贴
                    self.text_input.handle_event(event)
                    self.text = self.text_input.text
                    return
                elif event.key == pygame.K_c and (event.mod & pygame.KMOD_CTRL):
                    # Ctrl+C复制
                    self.text_input.handle_event(event)
                    return
                elif event.key == pygame.K_a and (event.mod & pygame.KMOD_CTRL):
                    # Ctrl+A全选（暂不实现）
                    return
                else:
                    # 其他按键（包括中文输入的字符）传递给TextInput
                    self.text_input.handle_event(event)
                    self.text = self.text_input.text
                    return
                    
            elif event.type == pygame.KEYUP:
                self.text_input.handle_event(event)
                return
    
    def update(self, dt):
        """更新光标闪烁和按键重复"""
        if self.active:
            self.cursor_timer += dt
            if self.cursor_timer >= 500:
                self.cursor_timer = 0
                self.cursor_visible = not self.cursor_visible
            # 更新TextInput的按键重复
            self.text_input.update(dt)
    
    def draw(self, surface):
        """绘制输入框"""
        # 绘制标签
        if self.label:
            label_surface = self.font.render(self.label, True, (200, 190, 180))
            surface.blit(label_surface, (self.rect.x, self.rect.y - 20))
        
        # 绘制阴影
        shadow_rect = self.rect.copy()
        shadow_rect.x += 2
        shadow_rect.y += 2
        pygame.draw.rect(surface, (30, 28, 25), shadow_rect, border_radius=4)
        
        # 绘制输入框背景
        pygame.draw.rect(surface, (50, 45, 40), self.rect, border_radius=4)
        pygame.draw.rect(surface, self.color, self.rect, 2, border_radius=4)
        
        # 激活状态高亮
        if self.active:
            inner_rect = self.rect.inflate(-4, -4)
            pygame.draw.rect(surface, (60, 55, 50), inner_rect, border_radius=2)
        
        # 显示文本（密码模式显示星号）
        display_text = '*' * len(self.text) if self.password else self.text
        
        # 如果有组合文本（输入法候选），显示在文本后面
        composition = self.text_input.composition_text if self.active else ""
        full_display = display_text + composition
        
        # 截断显示文本以适应输入框
        max_width = self.rect.width - 20
        while self.font.size(full_display)[0] > max_width and len(full_display) > 0:
            full_display = full_display[:-1]
        
        # 分别渲染已确认文本和组合文本
        if composition and self.active:
            # 渲染已确认部分
            confirmed_surface = self.font.render(display_text, True, (255, 250, 240))
            # 渲染组合部分（用不同颜色）
            comp_surface = self.font.render(composition, True, (180, 200, 255))
            
            text_y = self.rect.y + (self.rect.height - confirmed_surface.get_height()) // 2
            surface.blit(confirmed_surface, (self.rect.x + 10, text_y))
            surface.blit(comp_surface, (self.rect.x + 10 + confirmed_surface.get_width(), text_y))
            
            # 绘制下划线表示组合状态
            underline_y = text_y + confirmed_surface.get_height() + 2
            underline_start = self.rect.x + 10 + confirmed_surface.get_width()
            underline_end = underline_start + comp_surface.get_width()
            pygame.draw.line(surface, (180, 200, 255), 
                           (underline_start, underline_y), 
                           (underline_end, underline_y), 1)
        else:
            text_surface = self.font.render(full_display, True, (255, 250, 240))
            text_y = self.rect.y + (self.rect.height - text_surface.get_height()) // 2
            surface.blit(text_surface, (self.rect.x + 10, text_y))
        
        # 绘制光标
        if self.active and self.cursor_visible:
            cursor_x = self.rect.x + 10 + self.font.size(full_display)[0]
            cursor_y = text_y
            pygame.draw.line(surface, (255, 220, 150), 
                           (cursor_x, cursor_y), 
                           (cursor_x, cursor_y + self.font.get_height()), 2)


class EmployeeInfoDialog:
    """员工信息编辑弹窗 - 剧情类风格"""
    def __init__(self, employee, font_title, font_normal):
        self.employee = employee
        self.font_title = font_title
        self.font_normal = font_normal
        self.active = False
        
        # 弹窗尺寸 - 增加宽度和高度以确保足够空间
        self.width = 800
        self.height = 700
        self.x = (SCREEN_WIDTH - self.width) // 2
        self.y = (SCREEN_HEIGHT - self.height) // 2
        
        self._create_input_boxes()
        
        # 按钮位置 - 放在底部中央
        btn_y = self.y + self.height - 80
        self.save_btn = pygame.Rect(self.x + 250, btn_y, 120, 45)
        self.close_btn = pygame.Rect(self.x + 430, btn_y, 120, 45)
        
        self.original_data = {}
        self._load_employee_config()
    
    def _create_input_boxes(self):
        """创建输入框 - 优化布局防止重叠"""
        # 布局参数
        margin_x = 40  # 左右边距
        margin_y = 90  # 顶部边距（标题下方）
        col_gap = 60   # 两列之间的间距
        row_gap = 65   # 行间距（增加以防止重叠）
        
        # 计算列宽
        col_width = (self.width - 2 * margin_x - col_gap) // 2
        left_x = self.x + margin_x
        right_x = left_x + col_width + col_gap
        input_height = 35  # 输入框高度
        
        self.input_boxes = {}
        
        # 左列 - 基本信息
        self.input_boxes['name'] = InputBox(
            left_x, self.y + margin_y, col_width, input_height, 
            '', '员工姓名:'
        )
        self.input_boxes['gender'] = InputBox(
            left_x, self.y + margin_y + row_gap, col_width, input_height, 
            '', '性别:'
        )
        self.input_boxes['position'] = InputBox(
            left_x, self.y + margin_y + row_gap * 2, col_width, input_height, 
            '', '职位:'
        )
        self.input_boxes['department'] = InputBox(
            left_x, self.y + margin_y + row_gap * 3, col_width, input_height, 
            '', '部门:'
        )
        
        # 右列 - API配置
        self.input_boxes['api_url'] = InputBox(
            right_x, self.y + margin_y, col_width, input_height,
            '', 'API URL:'
        )
        self.input_boxes['api_key'] = InputBox(
            right_x, self.y + margin_y + row_gap, col_width, input_height,
            '', 'API Key:', password=True
        )
        self.input_boxes['model_name'] = InputBox(
            right_x, self.y + margin_y + row_gap * 2, col_width, input_height,
            '', '模型名称:'
        )
        
        # 底部 - 技能文件路径（横跨两列）
        skill_y = self.y + margin_y + row_gap * 4 + 20  # 额外间距
        skill_width = self.width - 2 * margin_x - 140  # 留出按钮空间
        self.input_boxes['skill_file'] = InputBox(
            left_x, skill_y, skill_width, input_height,
            '', '技能文件路径:'
        )
        
        # 加载技能文件按钮位置
        self.load_skill_btn = pygame.Rect(
            left_x + skill_width + 10, skill_y, 130, input_height
        )
    
    def _load_employee_config(self):
        """加载员工配置"""
        self.input_boxes['name'].text = getattr(self.employee, 'name', '')
        self.input_boxes['gender'].text = getattr(self.employee, 'gender', '')
        self.input_boxes['position'].text = getattr(self.employee, 'position', '')
        self.input_boxes['department'].text = getattr(self.employee, 'department', '')
        self.input_boxes['api_url'].text = getattr(self.employee, 'api_url', '')
        self.input_boxes['api_key'].text = getattr(self.employee, 'api_key', '')
        self.input_boxes['model_name'].text = getattr(self.employee, 'model_name', '')
        skill_path = getattr(self.employee, 'skill_file', f"skill/skill{self.employee.id}.md")
        self.input_boxes['skill_file'].text = skill_path
    
    def open(self):
        """打开弹窗"""
        self.active = True
        self._save_original_data()
        self._load_employee_config()
    
    def _save_original_data(self):
        """保存原始数据"""
        self.original_data = {
            'name': self.input_boxes['name'].text,
            'gender': self.input_boxes['gender'].text,
            'position': self.input_boxes['position'].text,
            'department': self.input_boxes['department'].text,
            'api_url': self.input_boxes['api_url'].text,
            'api_key': self.input_boxes['api_key'].text,
            'model_name': self.input_boxes['model_name'].text,
            'skill_file': self.input_boxes['skill_file'].text,
        }
    
    def close(self):
        """关闭弹窗"""
        self.active = False
        for box in self.input_boxes.values():
            box.active = False
            box.color = (130, 115, 95)
    
    def save(self):
        """保存修改"""
        self.employee.name = self.input_boxes['name'].text
        self.employee.gender = self.input_boxes['gender'].text
        self.employee.position = self.input_boxes['position'].text
        self.employee.department = self.input_boxes['department'].text
        
        # 处理API URL，确保是base_url格式（去掉/chat/completions等路径）
        api_url = self.input_boxes['api_url'].text.strip()
        if api_url.endswith('/chat/completions'):
            api_url = api_url[:-17]  # 移除末尾的 /chat/completions
        self.employee.api_url = api_url
        
        self.employee.api_key = self.input_boxes['api_key'].text
        self.employee.model_name = self.input_boxes['model_name'].text
        self.employee.skill_file = self.input_boxes['skill_file'].text
        
        if self.employee.api_url and self.employee.api_key and self.employee.model_name:
            if hasattr(self.employee, 'ai_client'):
                self.employee.ai_client.set_api_config(
                    self.employee.api_url,
                    self.employee.api_key,
                    self.employee.model_name
                )
            print(f"[员工{self.employee.id}] API配置已保存: {self.employee.api_url}")
        
        self.close()
    
    def cancel(self):
        """取消修改"""
        for key, value in self.original_data.items():
            if key in self.input_boxes:
                self.input_boxes[key].text = value
        self.close()
    
    def handle_event(self, event):
        """处理事件"""
        if not self.active:
            return
        
        for box in self.input_boxes.values():
            box.handle_event(event)
        
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.save_btn.collidepoint(event.pos):
                self.save()
            elif self.close_btn.collidepoint(event.pos):
                self.cancel()
            elif self.load_skill_btn.collidepoint(event.pos):
                self._load_skill_file()
        
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.cancel()
            elif event.key == pygame.K_RETURN and pygame.key.get_mods() & pygame.KMOD_CTRL:
                self.save()
    
    def _load_skill_file(self):
        """加载技能文件内容"""
        skill_path = self.input_boxes['skill_file'].text
        if not skill_path:
            skill_path = f"skill/skill{self.employee.id}.md"
            self.input_boxes['skill_file'].text = skill_path
        
        os.makedirs(os.path.dirname(skill_path), exist_ok=True)
        
        if not os.path.exists(skill_path):
            try:
                with open(skill_path, 'w', encoding='utf-8') as f:
                    f.write(f"# 员工{self.employee.id} 技能定义\n\n")
                print(f"[员工{self.employee.id}] 已创建技能文件: {skill_path}")
            except Exception as e:
                print(f"[员工{self.employee.id}] 创建技能文件失败: {e}")
        else:
            print(f"[员工{self.employee.id}] 技能文件已存在: {skill_path}")
    
    def update(self, dt):
        """更新弹窗"""
        if not self.active:
            return
        for box in self.input_boxes.values():
            box.update(dt)
    
    def draw(self, surface):
        """绘制弹窗 - 优化布局"""
        if not self.active:
            return
        
        # 半透明背景
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 200))
        surface.blit(overlay, (0, 0))
        
        # 主窗口
        dialog_rect = pygame.Rect(self.x, self.y, self.width, self.height)
        pygame.draw.rect(surface, (40, 35, 30), dialog_rect, border_radius=10)
        pygame.draw.rect(surface, (120, 100, 80), dialog_rect, width=3, border_radius=10)
        
        # 标题
        title = self.font_title.render(f"[员工 {self.employee.id} 配置]", True, (255, 220, 150))
        title_y = self.y + 20
        surface.blit(title, (self.x + (self.width - title.get_width()) // 2, title_y))
        
        # 分隔线
        line_y = title_y + 45
        pygame.draw.line(surface, (100, 85, 70), 
                        (self.x + 40, line_y), 
                        (self.x + self.width - 40, line_y), 2)
        

        
        # 绘制输入框
        for box in self.input_boxes.values():
            box.draw(surface)
        
        # 技能文件加载按钮
        pygame.draw.rect(surface, (70, 90, 70), self.load_skill_btn, border_radius=5)
        pygame.draw.rect(surface, (100, 140, 100), self.load_skill_btn, 2, border_radius=5)
        load_text = self.font_normal.render("加载/创建", True, (255, 255, 255))
        text_x = self.load_skill_btn.centerx - load_text.get_width() // 2
        text_y = self.load_skill_btn.centery - load_text.get_height() // 2
        surface.blit(load_text, (text_x, text_y))
        
        # 技能说明
        skill_hint_y = self.input_boxes['skill_file'].rect.bottom + 10
        skill_hint = self.font_normal.render(
            "技能文件: 程序会自动读取该文件内容作为AI提示词", True, (150, 150, 150)
        )
        surface.blit(skill_hint, (self.x + 40, skill_hint_y))
        
        # 按钮
        mouse_pos = pygame.mouse.get_pos()
        
        # 保存按钮
        save_hover = self.save_btn.collidepoint(mouse_pos)
        save_color = (90, 160, 90) if save_hover else (75, 140, 75)
        pygame.draw.rect(surface, save_color, self.save_btn, border_radius=6)
        pygame.draw.rect(surface, (130, 200, 130), self.save_btn, 2, border_radius=6)
        save_text = self.font_normal.render("保存", True, (255, 255, 255))
        text_x = self.save_btn.centerx - save_text.get_width() // 2
        text_y = self.save_btn.centery - save_text.get_height() // 2
        surface.blit(save_text, (text_x, text_y))
        
        # 取消按钮
        close_hover = self.close_btn.collidepoint(mouse_pos)
        close_color = (170, 90, 90) if close_hover else (150, 70, 70)
        pygame.draw.rect(surface, close_color, self.close_btn, border_radius=6)
        pygame.draw.rect(surface, (210, 130, 130), self.close_btn, 2, border_radius=6)
        close_text = self.font_normal.render("取消", True, (255, 255, 255))
        text_x = self.close_btn.centerx - close_text.get_width() // 2
        text_y = self.close_btn.centery - close_text.get_height() // 2
        surface.blit(close_text, (text_x, text_y))
        
        # 底部提示
        hint_y = self.y + self.height - 30
        hint = self.font_normal.render("ESC取消 | Ctrl+Enter保存", True, (140, 130, 120))
        surface.blit(hint, (self.x + (self.width - hint.get_width()) // 2, hint_y))
