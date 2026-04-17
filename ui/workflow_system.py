# AI工作流系统 - 剧情类游戏风格
# 管理任务分配、并行执行、状态追踪

import pygame
import json
import time
import math
from typing import List, Dict, Optional, Callable
from enum import Enum
from dataclasses import dataclass, field
from ui.text_input import TextInput

class TaskStatus(Enum):
    """任务状态"""
    PENDING = "等待中"
    ANALYZING = "分析中"
    IN_PROGRESS = "进行中"
    REVIEWING = "审核中"
    COMPLETED = "已完成"
    FAILED = "失败"

class WorkflowMode(Enum):
    """工作流模式 - 仅支持并行"""
    PARALLEL = "并行"      # 同时执行

@dataclass
class Task:
    """任务数据类"""
    id: str
    name: str
    description: str
    assignee_role: str  # 分配的角色
    assignee_id: Optional[int] = None  # 分配的员工ID
    status: TaskStatus = TaskStatus.PENDING
    mode: WorkflowMode = WorkflowMode.PARALLEL
    output: str = ""  # 任务输出
    start_time: Optional[float] = None
    end_time: Optional[float] = None
    progress: float = 0.0  # 0-100
    
    def to_dict(self) -> Dict:
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'assignee_role': self.assignee_role,
            'assignee_id': self.assignee_id,
            'status': self.status.value,
            'mode': self.mode.value,
            'output': self.output,
            'progress': self.progress,
        }

@dataclass
class Project:
    """项目数据类"""
    id: str
    name: str
    description: str
    requirement: str  # 原始需求
    detailed_requirement: str  # AI细化后的需求
    company_name: str
    tasks: List[Task] = field(default_factory=list)
    status: str = "规划中"
    created_at: float = field(default_factory=time.time)
    completed_at: Optional[float] = None
    
    def get_progress(self) -> float:
        """获取整体进度"""
        if not self.tasks:
            return 0.0
        completed = sum(1 for t in self.tasks if t.status == TaskStatus.COMPLETED)
        return (completed / len(self.tasks)) * 100
    
    def get_task_by_id(self, task_id: str) -> Optional[Task]:
        """通过ID获取任务"""
        for task in self.tasks:
            if task.id == task_id:
                return task
        return None


class WorkflowEngine:
    """工作流引擎 - 管理项目执行"""
    
    def __init__(self, ai_planner):
        self.ai_planner = ai_planner
        self.projects: List[Project] = []
        self.current_project: Optional[Project] = None
        self.task_callbacks: Dict[str, List[Callable]] = {}
        
    def create_project(self, name: str, requirement: str, company) -> Project:
        """
        创建新项目 - 仅支持并行模式
        """
        print(f"[工作流] 创建项目: {name}")
        
        # 创建项目
        project = Project(
            id=f"proj_{int(time.time())}",
            name=name,
            description=requirement,
            requirement=requirement,
            detailed_requirement=requirement,
            company_name=company.name if company else "AI World公司"
        )
        
        self.projects.append(project)
        self.current_project = project
        
        print(f"[工作流] 项目创建完成")
        return project
    
    def add_task_to_project(self, project: Project, task: Task):
        """添加任务到项目"""
        project.tasks.append(task)
        print(f"[工作流] 添加任务: {task.name}")
    
    def start_task(self, task: Task, employee_id: int) -> bool:
        """开始执行任务"""
        if task.status != TaskStatus.PENDING:
            return False
        
        task.assignee_id = employee_id
        task.status = TaskStatus.IN_PROGRESS
        task.start_time = time.time()
        task.progress = 0
        
        print(f"[工作流] 任务开始: {task.name} -> 员工{employee_id}")
        return True
    
    def update_task_progress(self, task: Task, progress: float):
        """更新任务进度"""
        task.progress = min(100, max(0, progress))
        
    def complete_task(self, task: Task, output: str = ""):
        """完成任务"""
        task.status = TaskStatus.COMPLETED
        task.output = output
        task.end_time = time.time()
        task.progress = 100
        
        print(f"[工作流] 任务完成: {task.name}")
        
        # 触发回调
        if task.id in self.task_callbacks:
            for callback in self.task_callbacks[task.id]:
                callback(task)
    
    def assign_task_to_employee(self, task: Task, employee_id: int):
        """分配任务给员工"""
        task.assignee_id = employee_id
        print(f"[工作流] 分配任务: {task.name} -> 员工{employee_id}")
    
    def get_employee_task(self, employee_id: int) -> Optional[Task]:
        """获取员工的当前任务"""
        if not self.current_project:
            return None
        
        for task in self.current_project.tasks:
            if task.assignee_id == employee_id:
                return task
        return None
    
    def register_task_callback(self, task_id: str, callback: Callable):
        """注册任务完成回调"""
        if task_id not in self.task_callbacks:
            self.task_callbacks[task_id] = []
        self.task_callbacks[task_id].append(callback)


class WorkflowUI:
    """工作流UI - 显示项目进度（支持拖动、ESC关闭和实时进度条）"""
    
    def __init__(self, font_large, font_medium, font_small):
        self.font_large = font_large
        self.font_medium = font_medium
        self.font_small = font_small
        self.visible = False
        self.x = 10
        self.y = 100
        self.width = 320
        self.height = 450
        
        # 拖动相关
        self.is_dragging = False
        self.drag_offset_x = 0
        self.drag_offset_y = 0
        self.title_bar_height = 35
        
        # 滚动相关
        self.scroll_y = 0
        self.max_scroll = 0
        self.content_height = 0
        
        # 动画效果
        self.pulse_animation = 0
        self.animation_speed = 0.1
        
        # 缓存表面
        self.bg_surface = None
        self.need_redraw_bg = True
        
        # Token消耗统计
        self.token_counts = {}  # employee_id -> token_count
        self.total_tokens = 0
        
    def show(self):
        """显示UI"""
        self.visible = True
        self.need_redraw_bg = True
        
    def hide(self):
        """隐藏UI"""
        self.visible = False
        
    def toggle(self):
        """切换显示状态"""
        self.visible = not self.visible
        if self.visible:
            self.need_redraw_bg = True
    
    def handle_event(self, event):
        """处理鼠标和键盘事件"""
        if not self.visible:
            return False
            
        mouse_pos = pygame.mouse.get_pos()
        panel_rect = pygame.Rect(self.x, self.y, self.width, self.height)
        title_bar_rect = pygame.Rect(self.x, self.y, self.width, self.title_bar_height)
        
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # 左键
                # 检查是否点击标题栏（拖动）
                if title_bar_rect.collidepoint(mouse_pos):
                    self.is_dragging = True
                    self.drag_offset_x = mouse_pos[0] - self.x
                    self.drag_offset_y = mouse_pos[1] - self.y
                    return True
                # 检查是否点击面板内部（消费事件）
                elif panel_rect.collidepoint(mouse_pos):
                    return True
                    
        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:
                self.is_dragging = False
                
        elif event.type == pygame.MOUSEMOTION:
            if self.is_dragging:
                self.x = mouse_pos[0] - self.drag_offset_x
                self.y = mouse_pos[1] - self.drag_offset_y
                # 限制在屏幕内（使用正确的屏幕尺寸）
                from core.config import SCREEN_WIDTH, SCREEN_HEIGHT
                self.x = max(0, min(self.x, SCREEN_WIDTH - self.width))
                self.y = max(0, min(self.y, SCREEN_HEIGHT - self.height))
                self.need_redraw_bg = True
                return True
            
        elif event.type == pygame.MOUSEWHEEL:
            # 鼠标滚轮滚动
            if panel_rect.collidepoint(mouse_pos):
                self.scroll_y += event.y * 30
                self.scroll_y = max(0, min(self.scroll_y, self.max_scroll))
                return True
        
        elif event.type == pygame.KEYDOWN:
            # ESC键关闭面板
            if event.key == pygame.K_ESCAPE:
                self.hide()
                return True
                
        return False
    
    def update(self, dt):
        """更新动画"""
        if not self.visible:
            return
            
        # 脉冲动画
        self.pulse_animation += self.animation_speed
        if self.pulse_animation > 3.14159 * 2:
            self.pulse_animation = 0
    
    def _create_blur_background(self, surface):
        """创建虚化背景效果（更透明）"""
        if not self.need_redraw_bg or self.bg_surface is None:
            return
            
        # 创建更透明的背景
        self.bg_surface.fill((30, 28, 25, 180))
        
        # 添加渐变效果
        for i in range(self.height):
            alpha = int(180 - (i / self.height) * 30)
            pygame.draw.line(self.bg_surface, (30, 28, 25, alpha), 
                           (0, i), (self.width, i))
        
        self.need_redraw_bg = False
    
    def draw(self, surface, project: Project):
        """绘制工作流UI"""
        if not self.visible or not project:
            return
        
        # 初始化背景表面
        if self.bg_surface is None or self.bg_surface.get_size() != (self.width, self.height):
            self.bg_surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
            self.need_redraw_bg = True
        
        # 创建虚化背景
        self._create_blur_background(surface)
        
        # 绘制主面板背景
        panel_rect = pygame.Rect(self.x, self.y, self.width, self.height)
        
        # 使用带透明度的背景
        if self.bg_surface:
            surface.blit(self.bg_surface, (self.x, self.y))
        else:
            pygame.draw.rect(surface, (40, 38, 35, 240), panel_rect, border_radius=8)
        
        # 绘制边框（发光效果）
        glow_intensity = int(100 + 30 * abs(math.sin(self.pulse_animation)))
        pygame.draw.rect(surface, (glow_intensity, 90, 70), panel_rect, width=2, border_radius=8)
        
        # 绘制标题栏
        title_bar_rect = pygame.Rect(self.x, self.y, self.width, self.title_bar_height)
        pygame.draw.rect(surface, (60, 55, 50, 200), title_bar_rect, border_radius=8)
        pygame.draw.rect(surface, (80, 75, 70, 200), 
                        (self.x, self.y + self.title_bar_height - 2, self.width, 2))
        
        # 标题 - 自动换行处理
        title_text = f"[项目] {project.name}"
        max_title_width = self.width - 50  # 留出拖动提示的空间
        
        # 计算是否需要换行
        title_surface = self.font_medium.render(title_text, True, (255, 220, 150))
        if title_surface.get_width() > max_title_width:
            # 需要换行，逐字添加直到超出宽度
            lines = []
            current_line = "[项目] "
            for char in project.name:
                test_line = current_line + char
                test_surface = self.font_medium.render(test_line, True, (255, 220, 150))
                if test_surface.get_width() > max_title_width and len(current_line) > 2:
                    lines.append(current_line)
                    current_line = char
                else:
                    current_line = test_line
            if current_line:
                lines.append(current_line)
            
            # 绘制多行标题
            line_height = self.font_medium.get_height()
            for i, line in enumerate(lines[:2]):  # 最多显示2行
                title_surf = self.font_medium.render(line, True, (255, 220, 150))
                surface.blit(title_surf, (self.x + 10, self.y + 5 + i * (line_height - 2)))
        else:
            # 单行标题
            surface.blit(title_surface, (self.x + 10, self.y + 8))
        
        # 拖动提示
        drag_hint = self.font_small.render("≡", True, (150, 150, 150))
        surface.blit(drag_hint, (self.x + self.width - 25, self.y + 10))
        
        # 整体进度条
        progress = project.get_progress()
        bar_x = self.x + 10
        bar_y = self.y + 45
        bar_width = self.width - 20
        bar_height = 22
        
        # 进度条背景
        pygame.draw.rect(surface, (50, 48, 45), (bar_x, bar_y, bar_width, bar_height), border_radius=4)
        
        # 进度条填充（带渐变效果）
        fill_width = int(bar_width * progress / 100)
        if fill_width > 0:
            # 渐变色
            for i in range(fill_width):
                progress_ratio = i / bar_width
                r = int(80 + 40 * progress_ratio)
                g = int(160 + 40 * progress_ratio)
                b = int(80 + 20 * progress_ratio)
                pygame.draw.line(surface, (r, g, b), 
                               (bar_x + i, bar_y + 1), 
                               (bar_x + i, bar_y + bar_height - 2))
        
        # 进度条边框
        pygame.draw.rect(surface, (120, 110, 100), (bar_x, bar_y, bar_width, bar_height), width=1, border_radius=4)
        
        # 进度文字
        progress_text = self.font_small.render(f"{progress:.0f}%", True, (255, 255, 255))
        text_x = bar_x + bar_width // 2 - progress_text.get_width() // 2
        surface.blit(progress_text, (text_x, bar_y + 3))
        
        # 任务列表区域（带裁剪）
        list_start_y = bar_y + 35
        list_height = self.height - (list_start_y - self.y) - 10
        
        # 创建裁剪区域
        clip_rect = pygame.Rect(self.x + 5, list_start_y, self.width - 10, list_height)
        
        # 保存原始裁剪区域
        old_clip = surface.get_clip()
        surface.set_clip(clip_rect)
        
        # 计算内容高度
        task_item_height = 50
        self.content_height = len(project.tasks) * task_item_height
        self.max_scroll = max(0, self.content_height - list_height)
        
        # 绘制任务列表
        task_y = list_start_y - self.scroll_y
        
        for task in project.tasks:
            # 跳过超出可视区域的任务
            if task_y + task_item_height < list_start_y or task_y > list_start_y + list_height:
                task_y += task_item_height
                continue
            
            # 任务项背景
            item_rect = pygame.Rect(self.x + 8, task_y, self.width - 16, task_item_height - 5)
            
            # 根据状态设置背景色
            if task.status == TaskStatus.COMPLETED:
                bg_color = (45, 70, 45)
                border_color = (80, 150, 80)
            elif task.status == TaskStatus.IN_PROGRESS:
                bg_color = (65, 60, 40)
                border_color = (180, 160, 80)
            else:
                bg_color = (50, 48, 45)
                border_color = (80, 78, 75)
            
            pygame.draw.rect(surface, bg_color, item_rect, border_radius=4)
            pygame.draw.rect(surface, border_color, item_rect, width=1, border_radius=4)
            
            # 任务图标和名称
            if task.status == TaskStatus.COMPLETED:
                icon = "[OK]"
                name_color = (120, 220, 120)
            elif task.status == TaskStatus.IN_PROGRESS:
                icon = "[>"
                name_color = (220, 200, 120)
            else:
                icon = "[ ]"
                name_color = (180, 180, 180)
            
            task_name = self.font_small.render(f"{icon} {task.name}", True, name_color)
            surface.blit(task_name, (self.x + 15, task_y + 5))
            
            # 实时进度条（仅进行中任务）
            if task.status == TaskStatus.IN_PROGRESS:
                mini_bar_x = self.x + 15
                mini_bar_y = task_y + 28
                mini_bar_width = self.width - 50
                mini_bar_height = 12
                
                # 迷你进度条背景
                pygame.draw.rect(surface, (40, 40, 40), 
                               (mini_bar_x, mini_bar_y, mini_bar_width, mini_bar_height), 
                               border_radius=2)
                
                # 迷你进度条填充（动画效果）
                mini_fill_width = int(mini_bar_width * task.progress / 100)
                if mini_fill_width > 0:
                    # 动态颜色
                    pulse = abs(math.sin(self.pulse_animation * 2))
                    r = int(100 + 50 * pulse)
                    g = int(180 + 40 * pulse)
                    b = int(100 + 30 * pulse)
                    pygame.draw.rect(surface, (r, g, b), 
                                   (mini_bar_x, mini_bar_y, mini_fill_width, mini_bar_height), 
                                   border_radius=2)
                
                # 进度百分比
                progress_text = self.font_small.render(f"{task.progress:.0f}%", True, (200, 200, 200))
                surface.blit(progress_text, (mini_bar_x + mini_bar_width + 5, mini_bar_y - 1))
            
            # 完成时间（仅已完成任务）
            elif task.status == TaskStatus.COMPLETED and task.end_time:
                duration = task.end_time - task.start_time if task.start_time else 0
                time_text = self.font_small.render(f"⏱ {duration:.1f}s", True, (150, 200, 150))
                surface.blit(time_text, (self.x + 15, task_y + 28))
            
            task_y += task_item_height
        
        # 恢复裁剪区域
        surface.set_clip(old_clip)
        
        # 绘制滚动条（如果需要）
        if self.max_scroll > 0:
            scrollbar_x = self.x + self.width - 12
            scrollbar_y = list_start_y
            scrollbar_height = list_height
            
            # 滚动条背景
            pygame.draw.rect(surface, (50, 50, 50), 
                           (scrollbar_x, scrollbar_y, 8, scrollbar_height), 
                           border_radius=4)
            
            # 滚动条滑块
            thumb_height = max(30, scrollbar_height * list_height / self.content_height)
            thumb_y = scrollbar_y + (self.scroll_y / self.max_scroll) * (scrollbar_height - thumb_height)
            pygame.draw.rect(surface, (120, 120, 120), 
                           (scrollbar_x, thumb_y, 8, thumb_height), 
                           border_radius=4)
        
        # 绘制Token消耗统计（底部）
        token_y = self.y + self.height - 28
        token_bg_rect = pygame.Rect(self.x + 5, token_y - 2, self.width - 10, 24)
        pygame.draw.rect(surface, (40, 38, 35, 200), token_bg_rect, border_radius=4)
        pygame.draw.rect(surface, (80, 75, 70, 200), token_bg_rect, width=1, border_radius=4)
        
        # Token图标和总数
        token_text = f"[Token] {self.total_tokens:,}"
        token_surface = self.font_small.render(token_text, True, (180, 180, 200))
        surface.blit(token_surface, (self.x + 12, token_y))
        
        # 显示各员工Token消耗（简版）
        if self.token_counts:
            active_tokens = [(emp_id, count) for emp_id, count in self.token_counts.items() if count > 0]
            if active_tokens:
                details = " | ".join([f"{self._get_employee_name(emp_id)}:{count:,}" for emp_id, count in active_tokens[:3]])
                details_surface = self.font_small.render(details, True, (140, 140, 160))
                surface.blit(details_surface, (self.x + 12, token_y + 12))
    
    def _get_employee_name(self, employee_id: int) -> str:
        """根据ID获取员工名称简写"""
        names = {0: "明", 1: "红", 2: "强", 3: "丽", 4: "伟", 5: "晓"}
        return names.get(employee_id, f"E{employee_id}")
    
    def update_token_count(self, employee_id: int, token_count: int):
        """更新员工Token消耗"""
        self.token_counts[employee_id] = token_count
        # 重新计算总数
        self.total_tokens = sum(self.token_counts.values())
    
    def reset_token_counts(self):
        """重置Token统计"""
        self.token_counts = {}
        self.total_tokens = 0
