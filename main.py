# AI World - AI公司模拟器
# 2D俯视视角游戏 - 剧情类风格

import pygame
import sys
import random
import threading
import time
from core.config import SCREEN_WIDTH, SCREEN_HEIGHT, FPS, TITLE, COLORS, AREAS, GRID_SIZE, get_font
from areas.work_area import WorkArea
from areas.entertainment_area import EntertainmentArea
from core.ai_employee import AIEmployee
from core.pathfinding import PathFinder
from core.boss import Boss
from core.particle_system import ParticleSystem
from ui.employee_info_dialog import EmployeeInfoDialog

# 新功能导入
from ui.workflow_system import WorkflowEngine, WorkflowUI, TaskStatus
from ui.workflow_editor import WorkflowEditor
from ai_systems.cloud_ai_client import cloud_ai_client
from utils.localization import get_text, toggle_lang, Language
from utils.result_manager import ResultManager
from ai_systems.employee_ai_worker import EmployeeAIWorker
from ai_systems.employee_dialogue_system import dialogue_system
from ui.loading_screen import LoadingScreen, ConfigManager
from ui.planner_chat import PlannerChat
from ai_systems.agent_planner import agent_planner

class Game:
    """游戏主类 - 剧情类风格"""
    
    def __init__(self, skip_loading=False):
        pygame.init()
        pygame.display.set_caption(TITLE)
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.clock = pygame.time.Clock()
        self.running = True
        
        # 启动界面
        self.loading_screen = None
        if not skip_loading:
            self.loading_screen = LoadingScreen(SCREEN_WIDTH, SCREEN_HEIGHT)
        
        # 初始化区域
        self.work_area = WorkArea()
        self.ent_area = EntertainmentArea()
        
        # 初始化寻路
        self.pathfinder = PathFinder()
        self._setup_obstacles()
        
        # 员工列表
        self.employees = []
        self.selected_employee = None
        
        # 当前模式：True=工作模式，False=休息模式
        self.work_mode = False
        
        # 鼠标位置
        self.mouse_pos = (0, 0)
        
        # 字体 - 像素风字体
        self.font_large = get_font(26)
        self.font_medium = get_font(18)
        self.font_small = get_font(14)
        
        # 初始化员工
        self._init_employees()
        
        # 初始化老板（玩家角色）
        rest_spots = self.ent_area.get_all_rest_spots()
        if rest_spots:
            spawn_x, spawn_y = rest_spots[0]
        else:
            spawn_x = AREAS['entertainment']['x'] + 80
            spawn_y = AREAS['entertainment']['y'] + 220
        self.boss = Boss(spawn_x, spawn_y)
        
        # 初始化粒子系统
        self.particles = ParticleSystem()
        
        # 工位位置记录系统
        self.recorded_work_positions = []
        self.recording_enabled = True
        
        # 对话框系统
        self.dialog_box = None
        self.dialog_employee = None
        self.dialog_text = ""
        self.dialog_timer = 0
        
        # 员工信息弹窗
        self.employee_info_dialog = None
        
        # ========== 新功能初始化 ==========
        
        # 工作流系统
        self.workflow_engine = WorkflowEngine(None)  # 不再使用ai_planner
        self.workflow_ui = WorkflowUI(self.font_large, self.font_medium, self.font_small)
        
        # 流程编辑器（替代AI规划师）
        self.workflow_editor = WorkflowEditor(
            self.font_large, self.font_medium, self.font_small, self.employees
        )
        self.workflow_editor.on_config_complete = self._on_workflow_config_complete
        
        # AI规划师聊天界面
        self.planner_chat = PlannerChat(SCREEN_WIDTH, SCREEN_HEIGHT)
        self.planning_in_progress = False
        self.pending_config = None
        
        # 结果管理器
        self.result_manager = ResultManager()
        
        # 员工AI工作器 - 管理AI任务执行（每个员工有自己的客户端）
        self.employee_ai_worker = EmployeeAIWorker()  # 创建worker
        self.employee_ai_worker.set_employees(self.employees)  # 设置员工列表
        
        # 员工AI任务状态 {employee_id: {'task': task_obj, 'progress': 0, 'result': None}}
        self.employee_ai_tasks = {}
        
        # 游戏状态
        self.game_state = "playing"  # playing, workflow_editor
        self.work_order_issued = False  # 是否已发布号令
        
        # 消息气泡
        self.message_bubble_text = ""
        self.message_bubble_timer = 0
        self.message_bubble_show = False
        
        # 召回确认对话框
        self.recall_dialog_active = False
        
        # 退出确认对话框
        self.exit_confirm_dialog_active = False
        self.exit_confirm_selection = 0  # 0=取消, 1=确认
        
        # 检查云端AI服务状态
        self.ai_available = False  # 初始状态为未配置，等待员工设置API
        print("[系统] 等待配置云端AI API（请在员工面板中设置）")
        
        # 初始检查一次AI可用性（可能从保存的数据中加载了配置）
        self._check_ai_availability()
        if self.ai_available:
            print("[系统] 检测到已配置的员工API")
        
        # 设置工作流回调
        self.workflow_engine.on_task_complete = self._on_task_complete
        self.workflow_engine.on_project_complete = self._on_project_complete
        
        # 工作流配置（由用户手动设置）
        self.workflow_config = None
        self.current_working_employee_idx = 0  # 单程模式下当前工作的员工索引
    
    def _setup_obstacles(self):
        """设置寻路障碍物"""
        work_collisions = self.work_area.get_collision_objects()
        ent_collisions = self.ent_area.get_collision_objects()
        
        for obj in work_collisions + ent_collisions:
            if obj['blocking']:
                rect = obj['rect']
                self.pathfinder.add_obstacle_rect(rect)
    
    def _init_employees(self):
        """初始化AI员工"""
        names = ['小明', '小红', '阿强', '小丽', '大伟', '晓晓']
        
        # 加载保存的API配置
        api_configs = ConfigManager.load_configs()
        
        for i, name in enumerate(names):
            rest_spots = self.ent_area.get_all_rest_spots()
            if i < len(rest_spots):
                x, y = rest_spots[i]
            else:
                x = random.randint(self.ent_area.area['x'] + 40, 
                                 self.ent_area.area['x'] + self.ent_area.area['width'] - 40)
                y = random.randint(self.ent_area.area['y'] + 60, 
                                 self.ent_area.area['y'] + self.ent_area.area['height'] - 60)
            
            employee = AIEmployee(i, name, x, y)
            
            # 应用保存的API配置
            if i < len(api_configs):
                config = api_configs[i]
                if config.is_configured():
                    employee.api_url = config.api_url
                    employee.api_key = config.api_key
                    employee.model_name = config.model_name
                    employee.ai_client.set_api_config(config.api_url, config.api_key, config.model_name)
                    print(f"[员工{i}] 已加载保存的API配置: {config.model_name}")
            
            if i < len(self.work_area.desks):
                desk = self.work_area.desks[i]
                self.work_area.assign_employee(i, employee)
                employee.assign_task(f"任务{i+1}")
            
            self.employees.append(employee)
    
    def handle_events(self):
        """处理输入事件"""
        for event in pygame.event.get():
            # 处理规划师聊天界面
            if self.planner_chat.visible:
                result = self.planner_chat.handle_event(event)
                if result == "CLOSE":
                    # ESC关闭聊天界面
                    pass
                elif result == "START_TASK":
                    # 空格开始任务
                    self._start_workflow_after_planning()
                if event.type == pygame.QUIT:
                    self.running = False
                continue
            
            # 处理流程编辑器
            if self.workflow_editor.active:
                self.workflow_editor.handle_event(event)
                if event.type == pygame.QUIT:
                    self.running = False
                continue
            
            # 处理员工信息弹窗
            if self.employee_info_dialog and self.employee_info_dialog.active:
                self.employee_info_dialog.handle_event(event)
                if event.type == pygame.QUIT:
                    self.running = False
                continue
            
            # 处理工作流UI事件（拖动、滚动）
            if self.workflow_ui.handle_event(event):
                if event.type == pygame.QUIT:
                    self.running = False
                continue
            
            # 处理召回确认对话框
            if self.recall_dialog_active:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_y:
                        self._handle_recall_confirm(True)
                    elif event.key == pygame.K_n or event.key == pygame.K_ESCAPE:
                        self._handle_recall_confirm(False)
                continue
            
            # 处理消息气泡（按任意键关闭）
            if self.message_bubble_show:
                if event.type == pygame.KEYDOWN or event.type == pygame.MOUSEBUTTONDOWN:
                    self.message_bubble_show = False
                    self.message_bubble_timer = 0
                continue
            
            if event.type == pygame.QUIT:
                self.running = False
            
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    # ESC显示退出确认对话框
                    self._show_exit_confirm_dialog()
                    return  # 退出当前事件处理
                elif event.key == pygame.K_SPACE:
                    self._issue_work_order()
                elif event.key == pygame.K_e:
                    self._handle_interact()
                elif event.key == pygame.K_r:
                    self._record_work_position()
                elif event.key == pygame.K_p:
                    # P键 - 打开流程编辑器
                    self._open_workflow_editor()
                elif event.key == pygame.K_t:
                    # T键 - 切换工作流UI
                    self.workflow_ui.toggle()
                elif event.key == pygame.K_l:
                    # L键 - 切换语言
                    self._toggle_language()

                # WASD移动控制
                elif event.key == pygame.K_w:
                    self.boss.moving_up = True
                elif event.key == pygame.K_s:
                    self.boss.moving_down = True
                elif event.key == pygame.K_a:
                    self.boss.moving_left = True
                elif event.key == pygame.K_d:
                    self.boss.moving_right = True
            
            elif event.type == pygame.KEYUP:
                if event.key == pygame.K_w:
                    self.boss.moving_up = False
                elif event.key == pygame.K_s:
                    self.boss.moving_down = False
                elif event.key == pygame.K_a:
                    self.boss.moving_left = False
                elif event.key == pygame.K_d:
                    self.boss.moving_right = False
            
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    self._handle_mouse_click(event.pos)
            
            elif event.type == pygame.MOUSEMOTION:
                self.mouse_pos = event.pos
    
    def _handle_mouse_click(self, pos):
        """处理鼠标点击"""
        print(f"[COORD] 点击坐标: ({pos[0]}, {pos[1]})")
        
        for employee in self.employees:
            rect = employee.get_rect()
            if rect.collidepoint(pos):
                self.selected_employee = employee
                return
        self.selected_employee = None
    
    def _record_work_position(self):
        """按R键记录当前老板位置作为工位位置"""
        if not self.recording_enabled:
            return
        
        pos_x = int(self.boss.x)
        pos_y = int(self.boss.y)
        
        self.recorded_work_positions.append((pos_x, pos_y))
        
        employee_id = len(self.recorded_work_positions) - 1
        print(f"\n[工位记录] 员工{employee_id} 工位位置: ({pos_x}, {pos_y})")
        print(f"[进度] 已记录 {len(self.recorded_work_positions)}/6 个工位")
        
        if len(self.recorded_work_positions) >= 6:
            print("\n" + "="*50)
            print("所有工位位置已记录完毕！")
            print("="*50)
            print("work_positions = [")
            for i, (x, y) in enumerate(self.recorded_work_positions):
                print(f"    ({x}, {y}),   # 员工{i}工作位置")
            print("]")
            print("="*50 + "\n")
            self.recording_enabled = False
    
    def _handle_interact(self):
        """处理与员工的交互"""
        boss_rect = self.boss.get_interact_rect()
        
        for employee in self.employees:
            emp_rect = employee.get_rect()
            if boss_rect.colliderect(emp_rect):
                self._open_employee_info(employee)
                return
    
    def _open_employee_info(self, employee):
        """打开员工信息弹窗"""
        self.employee_info_dialog = EmployeeInfoDialog(
            employee, self.font_large, self.font_medium
        )
        self.employee_info_dialog.open()
    
    def _check_ai_availability(self):
        """检查有多少员工配置了有效的API"""
        connected_count = 0
        for employee in self.employees:
            if hasattr(employee, 'ai_client') and employee.ai_client.is_available():
                connected_count += 1
        self.ai_available = connected_count > 0
        return connected_count
    
    def _open_workflow_editor(self):
        """打开流程编辑器"""
        self.workflow_editor.show()
    
    def _on_workflow_config_complete(self, config):
        """流程配置完成回调 - 启动AI规划师聊天界面"""
        self.pending_config = config

        print(f"\n{'='*60}")
        print(f"[配置完成] 工作流程已配置，启动AI规划师...")
        print(f"[工作人数] {len(config.get('selected_employees', []))}人")
        print(f"{'='*60}\n")

        # 显示规划师聊天界面
        self.planner_chat.show()
        self.planning_in_progress = True

        # 启动aider规划
        selected_employees = config.get('selected_employee_objects', [])
        user_requirement = config.get('initial_prompt', '')

        # 配置agent planner - 使用智谱API
        if selected_employees:
            first_emp = selected_employees[0]
            agent_planner.set_config(
                api_key=first_emp.api_key,
                api_url=first_emp.api_url if hasattr(first_emp, 'api_url') else "https://open.bigmodel.cn/api/paas/v4",
                model=first_emp.model_name if first_emp.model_name else "glm-4"
            )

        # 异步启动规划
        agent_planner.generate_plan(
            selected_employees=selected_employees,
            user_requirement=user_requirement,
            on_token=self._on_planner_token,
            on_complete=self._on_planner_complete
        )
    
    def _on_planner_token(self, token: str):
        """接收AI规划师的流式输出"""
        if self.planner_chat.visible:
            self.planner_chat.on_streaming_token(token)
    
    def _on_planner_complete(self, plan):
        """AI规划师完成规划"""
        self.planning_in_progress = False
        
        if self.planner_chat.visible:
            self.planner_chat.on_plan_complete(plan)
        
        if plan:
            # 生成skill文件
            agent_planner.generate_skill_files(plan)
            
            # 保存规划结果
            self.workflow_config = {
                **self.pending_config,
                'plan': plan
            }
            
            print(f"\n[AI规划] 项目目标: {plan.get('project_goal', 'N/A')}")
            print(f"[AI规划] 工作模式: {plan.get('project_mode', '并行')}")
            print("[AI规划] 员工分工:")
            for emp_plan in plan['employees']:
                print(f"  - {emp_plan['employee_name']}: {emp_plan['role']}")
    
    def _start_workflow_after_planning(self):
        """规划完成后开始工作流"""
        if not self.workflow_config:
            return
        
        config = self.workflow_config
        
        # 显示工作流UI
        self.workflow_ui.show()
        
        print(f"\n{'='*60}")
        print(f"[准备就绪] 工作流程已配置")
        print(f"[提示] 按 空格键 发布号令开始执行")
        print(f"{'='*60}\n")
    
    def _assign_tasks_to_employees(self):
        """分配任务给员工"""
        if not self.workflow_engine.current_project:
            return
        
        project = self.workflow_engine.current_project
        
        # 为每个任务分配一个员工
        for i, task in enumerate(project.tasks):
            if i < len(self.employees):
                employee = self.employees[i]
                self.workflow_engine.assign_task_to_employee(task, employee.id)
                print(f"[分配] {task.name} -> {employee.name}")
    
    def _on_task_complete(self, task):
        """任务完成回调"""
        print(f"[完成] 任务完成: {task.name}")
        
        # 找到完成任务的员工
        employee = None
        for emp in self.employees:
            if emp.id == task.assignee_id:
                employee = emp
                break
        
        if employee:
            # 给员工增加满意度
            employee.happiness = min(100, employee.happiness + 10)
            
            # 保存工作结果
            if self.work_order_issued:
                result_content = f"## {task.name}\n\n{task.description}\n\n任务已完成。"
                self.result_manager.save_task_result(
                    task_id=task.id,
                    employee_name=employee.name,
                    role=task.assignee_role,
                    content=result_content,
                    mode=task.mode.value
                )
                
    def _find_employee_by_task(self, task):
        """根据任务查找员工"""
        for emp in self.employees:
            if emp.id == task.assignee_id:
                return emp
        return None
    
    def _show_message_bubble(self, message: str, duration: int = 3000):
        """显示消息气泡"""
        self.message_bubble_text = message
        self.message_bubble_timer = duration
        self.message_bubble_show = True
        print(f"[提示] {message}")
    
    def _show_recall_confirm_dialog(self):
        """显示召回确认对话框"""
        self.recall_dialog_active = True
        self.recall_dialog_result = None
        print("\n[召回] 是否确认结束当前工作流？")
        print("[Y] 确认结束  [N] 取消")
    
    def _handle_recall_confirm(self, confirmed: bool):
        """处理召回确认结果"""
        self.recall_dialog_active = False
        if confirmed:
            print("[召回] 确认结束工作，召回所有员工...")
            # 结束当前项目
            if self.workflow_engine.current_project:
                # 生成报告（即使未完成）
                self.result_manager.generate_final_report()
            
            # 让所有员工返回休息区
            self._send_all_to_rest()
            self.work_order_issued = False
            self.work_mode = False
            
            # 清空当前项目
            self.workflow_engine.current_project = None
            
            print("[召回] 所有员工已返回休息区")
        else:
            print("[召回] 取消召回，继续工作")
    
    def _on_project_complete(self, project):
        """项目完成回调"""
        print(f"\n{'='*60}")
        print(f"[完成] 项目完成: {project.name}")
        print(f"{'='*60}\n")
        
        # 生成最终报告
        report_file = self.result_manager.generate_final_report()
        if report_file:
            print(f"[报告] 已生成: {report_file}")
        
        # 让所有员工返回休息区
        print("\n[休息] 所有员工返回休息区...")
        self._send_all_to_rest()
        self.work_order_issued = False
    
    def _toggle_language(self):
        """切换语言"""
        new_lang = toggle_lang()
        lang_name = "中文" if new_lang == Language.CHINESE else "English"
        print(f"[语言] 已切换至: {lang_name}")
    
    def _issue_work_order(self):
        """发布号令 - 根据流程编辑器配置开始工作"""
        # 如果员工正在工作，显示召回确认对话框
        if self.work_order_issued and self.workflow_engine.current_project:
            has_incomplete = any(
                t.status != TaskStatus.COMPLETED 
                for t in self.workflow_engine.current_project.tasks
            )
            if has_incomplete:
                self._show_recall_confirm_dialog()
                return
        
        # 检查是否有流程配置
        if self.workflow_config and not self.work_order_issued:
            config = self.workflow_config
            
            print(f"\n{'='*60}")
            print(f"[号令] 老板发布工作号令！")
            # 获取选中的员工
            selected_ids = config.get('selected_employees', [])
            selected_employees = [self.employees[eid] for eid in selected_ids if eid < len(self.employees)]
            
            if not selected_employees:
                print("[错误] 没有选中的员工")
                self._show_message_bubble("请先选择配置了有效API的员工（按P键）")
                return
            
            selected_names = [e.name for e in selected_employees]
            
            print(f"[选中员工] {', '.join(selected_names)}")
            print(f"[工作模式] 并行(多AI独立工作)")
            print(f"{'='*60}\n")
            
            # 创建项目（任务已在创建时分配给员工）
            self._create_project_from_config(config, selected_employees)
            
            # 初始化结果管理器
            self.result_manager.start_project("用户自定义项目", "AI World公司")
            
            # 标记已发布号令
            self.work_order_issued = True
            self.work_mode = True
            
            # 并行模式：所有选中的员工一起去工位
            self._send_selected_workers_to_work(selected_employees)
            
            # 并行模式：立即启动所有员工的AI任务（不需要等待坐下）
            self._start_all_employee_ai_tasks(selected_employees)
            
        elif self.work_order_issued:
            print("[号令] 工作正在进行中...")
        else:
            # 未配置时显示提示气泡
            self._show_message_bubble("请先配置工作流程（按P键打开流程编辑器）")
    
    def _create_project_from_config(self, config, selected_employees):
        """根据用户配置创建项目 - 使用AI规划结果"""
        from ui.workflow_system import Project, Task, WorkflowMode
        import time

        # 检查是否有AI规划结果
        plan = config.get('plan')

        # 创建项目
        project_name = "用户自定义项目"
        project_goal = config['initial_prompt']

        if plan:
            project_goal = plan.get('project_goal', config['initial_prompt'])
            project_name = f"AI规划项目: {project_goal[:20]}..."

        project = Project(
            id=f"proj_{int(time.time())}",
            name=project_name,
            description=project_goal,
            requirement=config['initial_prompt'],
            detailed_requirement=config['initial_prompt'],
            company_name="AI World公司"
        )

        # 根据是否有AI规划结果创建任务
        if plan and plan.get('employees'):
            # 使用AI规划的分工
            print("[项目创建] 使用AI规划的分工方案")
            print(f"[项目创建] AI规划员工数: {len(plan['employees'])}")
            print(f"[项目创建] 选中员工数: {len(selected_employees)}")
            
            # 创建一个映射，确保每个选中的员工都有任务
            assigned_employee_ids = set()

            for emp_plan in plan['employees']:
                emp_id = emp_plan['employee_id']
                assigned_employee_ids.add(emp_id)
                # 找到对应的员工对象
                employee = None
                for emp in selected_employees:
                    if emp.id == emp_id:
                        employee = emp
                        break

                if not employee:
                    print(f"[警告] 找不到员工ID {emp_id}")
                    continue

                # 创建任务 - 仅支持并行模式
                task = Task(
                    id=f"task_{project.id}_{emp_id}",
                    name=f"{emp_plan['role']}",
                    description=emp_plan.get('skill_definition', f"{employee.name}负责的工作部分")[:200],
                    assignee_role=emp_plan['role'],
                    mode=WorkflowMode.PARALLEL,
                    assignee_id=employee.id
                )
                project.tasks.append(task)
                print(f"[任务创建] {employee.name} (ID:{emp_id}) -> {emp_plan['role']}")
            
            # 为没有被AI规划覆盖的员工创建默认任务
            for employee in selected_employees:
                if employee.id not in assigned_employee_ids:
                    print(f"[警告] 员工 {employee.name} (ID:{employee.id}) 未被AI规划覆盖，创建默认任务")
                    task = Task(
                        id=f"task_{project.id}_{employee.id}",
                        name=f"{employee.name}的任务",
                        description=f"员工{employee.name}负责的工作部分",
                        assignee_role=employee.position or "执行专员",
                        mode=WorkflowMode.PARALLEL,
                        assignee_id=employee.id
                    )
                    project.tasks.append(task)
                    print(f"[任务创建] {employee.name} (ID:{employee.id}) -> 默认任务")
        else:
            # 没有AI规划，使用默认分配
            print("[项目创建] 使用默认任务分配")
            mode = WorkflowMode.PARALLEL

            for i, employee in enumerate(selected_employees):
                task = Task(
                    id=f"task_{project.id}_{i}",
                    name=f"{employee.name}的任务",
                    description=f"员工{employee.name}负责的工作部分",
                    assignee_role=employee.position or "执行专员",
                    mode=mode,
                    assignee_id=employee.id
                )
                project.tasks.append(task)
        
        self.workflow_engine.projects.append(project)
        self.workflow_engine.current_project = project
        
        print(f"[工作流] 已创建项目，共 {len(project.tasks)} 个任务")
    
    def _send_selected_workers_to_work(self, selected_employees):
        """发送选中的员工去工作"""
        work_positions = [
            (152, 216), (292, 216), (428, 216),
            (152, 380), (288, 380), (428, 380),
        ]
        
        project = self.workflow_engine.current_project
        if not project:
            print("[派遣] 错误: 没有当前项目")
            return
        
        # 获取项目中有任务的员工ID列表
        assigned_employee_ids = set()
        for task in project.tasks:
            if task.assignee_id is not None:
                assigned_employee_ids.add(task.assignee_id)
        
        print(f"[派遣] 项目任务数: {len(project.tasks)}")
        print(f"[派遣] 已分配任务的员工ID: {assigned_employee_ids}")
        print(f"[派遣] 选中的员工数: {len(selected_employees)}")
        
        # 只派遣有任务的员工
        employees_with_tasks = []
        for emp in selected_employees:
            if emp.id in assigned_employee_ids:
                employees_with_tasks.append(emp)
            else:
                print(f"[派遣] 跳过 {emp.name} (ID:{emp.id}) - 没有分配任务")
        
        print(f"[派遣] 实际派遣员工数: {len(employees_with_tasks)}")
        
        for i, employee in enumerate(employees_with_tasks):
            if i < len(work_positions):
                employee.state = AIEmployee.STATE_WORK
                employee.substate = AIEmployee.SUBSTATE_WALKING
                employee.is_sitting = False
                
                target_x, target_y = work_positions[i]
                
                self.pathfinder.update_employee_positions(self.employees, employee)
                path = self.pathfinder.find_path(
                    employee.x, employee.y,
                    target_x, target_y,
                    exclude_employee=employee,
                    random_factor=0.3,
                    exact_end=True
                )
                
                if path and len(path) > 0:
                    employee.set_target_exact(target_x, target_y, path)
                    employee.final_work_pos = (target_x, target_y)
                    print(f"[派遣] {employee.name} (ID:{employee.id}) -> 工位{i+1}")
                else:
                    print(f"[派遣] 警告: {employee.name} 找不到路径")
    
    def _toggle_all_employees(self):
        """切换所有员工的状态"""
        self.work_mode = not self.work_mode
        
        if self.work_mode:
            self._send_all_to_work()
        else:
            self._send_all_to_rest()
    
    def _send_all_to_work(self):
        """让需要的员工去工作，其余留在休息区"""
        work_positions = [
            (152, 216), (292, 216), (428, 216),
            (152, 380), (288, 380), (428, 380),
        ]
        
        # 获取需要工作的员工数量（根据项目任务数）
        needed_count = 0
        if self.workflow_engine.current_project:
            needed_count = len(self.workflow_engine.current_project.tasks)
        
        needed_count = min(needed_count, 6)  # 最多6人
        
        print(f"[号令] 派遣 {needed_count} 名员工去工作，其余员工留在休息区")
        
        for i, employee in enumerate(self.employees):
            if i < needed_count:
                # 需要工作的员工
                employee.state = AIEmployee.STATE_WORK
                employee.substate = AIEmployee.SUBSTATE_WALKING
                employee.is_sitting = False
                
                if i < len(work_positions):
                    target_x, target_y = work_positions[i]
                    
                    self.pathfinder.update_employee_positions(self.employees, employee)
                    
                    path = self.pathfinder.find_path(
                        employee.x, employee.y,
                        target_x, target_y,
                        exclude_employee=employee,
                        random_factor=0.3,
                        exact_end=True
                    )
                    
                    if path and len(path) > 0:
                        employee.set_target_exact(target_x, target_y, path)
                        employee.final_work_pos = (target_x, target_y)
                        print(f"[派遣] {employee.name} -> 工位{i+1}")
            else:
                # 不需要工作的员工留在休息区
                print(f"[留守] {employee.name} 留在休息区")
    
    def _send_all_to_rest(self):
        """让所有员工去休息"""
        ent = AREAS['entertainment']
        margin = 60
        
        for employee in self.employees:
            employee.state = AIEmployee.STATE_REST
            employee.substate = AIEmployee.SUBSTATE_WALKING
            employee.is_sitting = False
            
            if hasattr(employee, 'final_work_pos'):
                delattr(employee, 'final_work_pos')
            
            target_x = random.randint(ent['x'] + margin, ent['x'] + ent['width'] - margin)
            target_y = random.randint(ent['y'] + margin, ent['y'] + ent['height'] - margin)
            
            self.pathfinder.update_employee_positions(self.employees, employee)
            
            path = self.pathfinder.find_path(
                employee.x, employee.y,
                target_x, target_y,
                exclude_employee=employee,
                random_factor=0.3
            )
            
            if path and len(path) > 0:
                employee.set_target(target_x, target_y, path)
    
    def update(self, dt):
        """更新游戏状态"""
        # 更新规划师聊天界面
        if self.planner_chat.visible:
            self.planner_chat.update(dt)
            return
        
        # 更新流程编辑器
        if self.workflow_editor.active:
            self.workflow_editor.update(dt)
            return
        
        # 检查员工信息对话框是否刚关闭（从active变为inactive）
        if self.employee_info_dialog:
            was_active = self.employee_info_dialog.active
            self.employee_info_dialog.update(dt)
            # 如果对话框刚关闭，检查AI可用性
            if was_active and not self.employee_info_dialog.active:
                self._check_ai_availability()
        
        # 更新区域
        self.work_area.update(dt)
        self.ent_area.update(dt)
        
        # 更新老板
        self.boss.update(dt, self.pathfinder, self.work_area, self.ent_area, self.particles)
        
        # 获取当前时间（用于消息气泡系统）
        current_time = pygame.time.get_ticks()
        
        # 检查是否有对话在进行
        dialogue_active = len(dialogue_system.active_dialogues) > 0
        
        # 更新员工
        for employee in self.employees:
            self.pathfinder.update_employee_positions(self.employees, employee)
            
            # 更新工作流任务进度
            self._update_employee_task_progress(employee, dt)
            
            employee.update(dt, self.particles, current_time, dialogue_active)
            
            # 为休息区需要路径的员工计算随机走动路径
            if employee.state == AIEmployee.STATE_REST and employee.needs_path and employee.target_pos:
                path = self.pathfinder.find_path(
                    employee.x, employee.y,
                    employee.target_pos[0], employee.target_pos[1],
                    exclude_employee=employee,
                    random_factor=0.3
                )
                if path and len(path) > 0:
                    employee.set_target(employee.target_pos[0], employee.target_pos[1], path)
                employee.needs_path = False
        
        # 更新对话框计时器
        if self.dialog_timer > 0:
            self.dialog_timer -= dt
            if self.dialog_timer <= 0:
                self.dialog_employee = None
                self.dialog_text = ""
        
        # 更新粒子系统
        self.particles.update(dt)
        
        # 更新消息气泡计时器
        if self.message_bubble_timer > 0:
            self.message_bubble_timer -= dt
            if self.message_bubble_timer <= 0:
                self.message_bubble_show = False
        
        # 更新工作流UI动画
        self.workflow_ui.update(dt)
        
        # 更新员工对话系统
        dialogue_system.update(self.employees, current_time)
    
    def _update_employee_task_progress(self, employee, dt):
        """更新员工任务进度 - 使用AI工作器"""
        if not self.workflow_engine.current_project:
            return
        
        # 获取员工当前任务
        task = self.workflow_engine.get_employee_task(employee.id)
        
        if task:
            # 如果员工刚坐下且任务等待中，启动AI任务
            if employee.state == AIEmployee.STATE_WORK and employee.substate == AIEmployee.SUBSTATE_SITTING:
                if task.status == TaskStatus.PENDING:
                    self._start_employee_ai_task(employee, task)
                elif task.status == TaskStatus.IN_PROGRESS:
                    # 从AI工作器获取真实进度
                    if employee.id in self.employee_ai_tasks:
                        ai_progress = self.employee_ai_tasks[employee.id]['progress']
                        # 更新任务进度
                        if ai_progress > task.progress:
                            self.workflow_engine.update_task_progress(task, ai_progress)
                            
                            # 每10%打印一次进度
                            new_progress = int(task.progress / 10)
                            old_progress_int = int(self.employee_ai_tasks[employee.id].get('last_printed_progress', 0) / 10)
                            if new_progress > old_progress_int:
                                print(f"[进度] {employee.name} - {task.name}: {task.progress:.0f}%")
                                self.employee_ai_tasks[employee.id]['last_printed_progress'] = task.progress
    
    def _start_all_employee_ai_tasks(self, selected_employees):
        """并行启动所有员工的AI任务"""
        if not self.workflow_engine.current_project:
            print("[并行启动] 错误: 没有当前项目")
            return
        
        project = self.workflow_engine.current_project
        
        # 获取项目中有任务的员工ID列表
        assigned_employee_ids = set()
        for task in project.tasks:
            if task.assignee_id is not None:
                assigned_employee_ids.add(task.assignee_id)
        
        # 只启动有任务的员工
        employees_with_tasks = []
        for emp in selected_employees:
            if emp.id in assigned_employee_ids:
                employees_with_tasks.append(emp)
        
        print(f"\n{'='*60}")
        print(f"[并行启动] 同时启动 {len(employees_with_tasks)} 个员工的AI任务")
        print(f"[并行启动] 项目任务数: {len(project.tasks)}")
        print(f"{'='*60}\n")
        
        # 为每个有任务的员工启动AI任务
        for employee in employees_with_tasks:
            # 找到分配给该员工的任务
            task = None
            for t in project.tasks:
                if t.assignee_id == employee.id:
                    task = t
                    break
            
            if task:
                # 立即启动AI任务（不等待员工坐下）
                self._start_employee_ai_task(employee, task)
            else:
                print(f"[警告] 员工 {employee.name} (ID:{employee.id}) 找不到对应任务")
    
    def _start_employee_ai_task(self, employee, task):
        """启动员工AI任务"""
        # 标记任务开始
        self.workflow_engine.start_task(task, employee.id)
        
        # 重置该员工的token计数
        self.workflow_ui.update_token_count(employee.id, 0)
        
        print(f"\n{'='*60}")
        print(f"[开始] {employee.name} 开始执行: {task.name}")
        print(f"[角色] {task.assignee_role}")
        print(f"[模式] {task.mode.value}")
        print(f"{'='*60}\n")
        
        # 初始化AI任务状态
        self.employee_ai_tasks[employee.id] = {
            'task': task,
            'progress': 0,
            'result': None,
            'last_printed_progress': 0
        }
        
        # 获取项目信息
        project = self.workflow_engine.current_project
        project_goal = project.description if project else "完成分配的任务"
        
        # 构建并打印提示词（用于调试）
        from ai_systems.prompts import get_employee_prompt
        prompt = get_employee_prompt(
            role=task.assignee_role,
            responsibility=task.description,
            task_description=task.description,
            project_goal=project_goal
        )
        print(f"[提示词] 已生成提示词，长度: {len(prompt)} 字符")
        print(f"[提示词预览] {prompt[:200]}...")
        
        # 启动AI工作器
        print(f"[AI] 启动AI工作器...")
        success = self.employee_ai_worker.start_task(
            employee_id=employee.id,
            employee_name=employee.name,
            role=task.assignee_role,
            responsibility=task.description,
            task_description=task.description,
            project_goal=project_goal,
            on_progress=lambda progress: self._on_ai_progress(employee.id, progress),
            on_complete=lambda result: self._on_ai_complete(employee.id, result),
            on_token=lambda tokens: self._on_ai_token(employee.id, tokens)
        )
        
        if success:
            print(f"[AI] AI工作器启动成功")
        else:
            print(f"[AI] AI工作器启动失败")
    
    def _on_ai_progress(self, employee_id: int, progress: float):
        """AI进度回调 - 实时更新任务进度"""
        if employee_id in self.employee_ai_tasks:
            self.employee_ai_tasks[employee_id]['progress'] = progress
            
            # 实时更新工作流任务进度（用于UI显示）
            task = self.employee_ai_tasks[employee_id]['task']
            if task and task.status == TaskStatus.IN_PROGRESS:
                self.workflow_engine.update_task_progress(task, progress)
    
    def _on_ai_token(self, employee_id: int, token_count: int):
        """AI Token消耗回调 - 实时更新工作流UI"""
        # 更新工作流UI的token计数
        self.workflow_ui.update_token_count(employee_id, token_count)
    
    def _on_ai_complete(self, employee_id: int, result):
        """AI完成回调"""
        if employee_id not in self.employee_ai_tasks:
            return
        
        task_info = self.employee_ai_tasks[employee_id]
        task = task_info['task']
        employee = self.employees[employee_id]
        
        # 处理结果 - 如果是字典则提取raw_text，否则直接使用
        if isinstance(result, dict):
            content = result.get('raw_text', '')
            if not content:
                # 如果没有raw_text，尝试构建内容
                content_parts = []
                if result.get('stage_name'):
                    content_parts.append(f"# {result['stage_name']}\n")
                if result.get('completed_content'):
                    content_parts.append(result['completed_content'])
                if result.get('key_outputs'):
                    content_parts.append("\n## 关键产出\n" + "\n".join(result['key_outputs']))
                content = "\n\n".join(content_parts)
        else:
            content = str(result)
        
        # 保存结果
        task_info['result'] = content
        task.output = content
        
        # 完成任务
        self.workflow_engine.complete_task(task)
        
        # 保存到结果管理器
        self.result_manager.save_task_result(
            task_id=task.id,
            employee_name=employee.name,
            role=task.assignee_role,
            content=content,
            mode=task.mode.value
        )
        
        print(f"[完成] {employee.name} 完成任务: {task.name}")
        
        # 让员工返回休息区
        self._send_employee_to_rest(employee)
        
        # 检查是否是最后一个任务
        project = self.workflow_engine.current_project
        if project and all(t.status == TaskStatus.COMPLETED for t in project.tasks):
            self._on_all_tasks_complete(project)
    
    def _send_employee_to_rest(self, employee):
        """发送员工返回休息区"""
        employee.state = AIEmployee.STATE_REST
        employee.substate = AIEmployee.SUBSTATE_WALKING
        employee.is_sitting = False
        
        # 随机选择休息区位置
        ent = AREAS['entertainment']
        margin = 60
        target_x = random.randint(ent['x'] + margin, ent['x'] + ent['width'] - margin)
        target_y = random.randint(ent['y'] + margin, ent['y'] + ent['height'] - margin)
        
        self.pathfinder.update_employee_positions(self.employees, employee)
        path = self.pathfinder.find_path(
            employee.x, employee.y,
            target_x, target_y,
            exclude_employee=employee,
            random_factor=0.3
        )
        
        if path and len(path) > 0:
            employee.set_target(target_x, target_y, path)
        
        print(f"[休息] {employee.name} 返回休息区")
    
    def _on_all_tasks_complete(self, project):
        """所有任务完成时调用"""
        print(f"\n{'='*60}")
        print(f"[项目完成] 所有员工已完成工作")
        print(f"{'='*60}\n")

        # 生成最终报告
        report_file = self.result_manager.generate_final_report()
        if report_file:
            print(f"[报告] 已生成: {report_file}")

        # 合并所有结果
        merged_file = self.result_manager.merge_all_results()
        if merged_file:
            print(f"[合并] 已生成完整成果文档: {merged_file}")

        # 重置工作状态
        self.work_order_issued = False
        self.work_mode = False
    
    def draw_corridor(self, surface):
        """绘制通道"""
        corridor = AREAS['corridor']
        rect = pygame.Rect(corridor['x'], corridor['y'], corridor['width'], corridor['height'])
        
        pygame.draw.rect(surface, COLORS['corridor'], rect)
        
        tile_size = GRID_SIZE
        for x in range(rect.x, rect.right, tile_size):
            for y in range(rect.y, rect.bottom, tile_size):
                grid_x = (x - rect.x) // tile_size
                grid_y = (y - rect.y) // tile_size
                
                if (grid_x + grid_y) % 2 == 0:
                    color = COLORS['floor_light']
                else:
                    color = COLORS['floor_dark']
                
                tile_rect = pygame.Rect(x, y, min(tile_size, rect.right - x), min(tile_size, rect.bottom - y))
                pygame.draw.rect(surface, color, tile_rect)
                pygame.draw.rect(surface, COLORS['floor_grid_line'], tile_rect, 1)
    
    def draw(self):
        """绘制游戏画面"""
        self.screen.fill(COLORS['ui_bg'])
        
        # 绘制区域
        self.work_area.draw(self.screen)
        self.draw_corridor(self.screen)
        self.ent_area.draw(self.screen)
        
        # 绘制员工和老板
        all_characters = self.employees + [self.boss]
        sorted_characters = sorted(all_characters, key=lambda c: getattr(c, 'visual_y', c.y))
        for character in sorted_characters:
            character.draw(self.screen)
            if isinstance(character, AIEmployee):
                character.draw_interact_effect(self.screen)
                character.draw_message_bubble(self.screen)
        
        # 绘制粒子效果
        self.particles.draw(self.screen)
        
        # 绘制对话框
        self._draw_dialog()
        
        # 绘制UI
        self._draw_ui()
        
        # 绘制工作流UI
        self.workflow_ui.draw(self.screen, self.workflow_engine.current_project)
        
        # 绘制员工信息弹窗
        if self.employee_info_dialog:
            self.employee_info_dialog.draw(self.screen)
        
        # 绘制公司创建对话框
        # 绘制流程编辑器
        if self.workflow_editor.active:
            self.workflow_editor.draw(self.screen)
        
        # 绘制规划师聊天界面（最上层）
        if self.planner_chat.visible:
            self.planner_chat.draw(self.screen)
        
        # 绘制消息气泡
        self._draw_message_bubble()
        
        # 绘制员工对话气泡
        dialogue_system.draw(self.screen, self.employees)
        
        # 绘制召回确认对话框
        self._draw_recall_dialog()
        
        pygame.display.flip()
    
    def _draw_ui(self):
        """绘制UI界面"""
        # 底部信息栏
        ui_rect = pygame.Rect(0, SCREEN_HEIGHT - 60, SCREEN_WIDTH, 60)
        pygame.draw.rect(self.screen, COLORS['ui_bg'], ui_rect)
        pygame.draw.line(self.screen, COLORS['ui_border'], (0, SCREEN_HEIGHT - 60), 
                        (SCREEN_WIDTH, SCREEN_HEIGHT - 60), 2)
        
        # 员工状态统计
        work_count = sum(1 for e in self.employees if e.state == AIEmployee.STATE_WORK)
        rest_count = sum(1 for e in self.employees if e.state == AIEmployee.STATE_REST)
        walking_count = sum(1 for e in self.employees if e.substate == AIEmployee.SUBSTATE_WALKING)
        sitting_count = sum(1 for e in self.employees if e.substate == AIEmployee.SUBSTATE_SITTING)
        
        # 显示当前模式
        mode_text = "工作模式" if self.work_mode else "休息模式"
        mode_color = COLORS['ui_highlight'] if self.work_mode else (150, 200, 150)
        mode_surface = self.font_medium.render(f"当前: {mode_text}", True, mode_color)
        self.screen.blit(mode_surface, (20, SCREEN_HEIGHT - 55))
        
        stats_text = f"工作中: {work_count} | 休息中: {rest_count} | 行走中: {walking_count} | 坐着: {sitting_count}"
        stats = self.font_medium.render(stats_text, True, COLORS['ui_text'])
        self.screen.blit(stats, (20, SCREEN_HEIGHT - 35))
        
        # 项目信息
        if self.workflow_engine.current_project:
            project = self.workflow_engine.current_project
            progress = project.get_progress()
            project_text = f"项目进度: {progress:.0f}%"
            project_surface = self.font_small.render(project_text, True, (150, 255, 150))
            self.screen.blit(project_surface, (250, SCREEN_HEIGHT - 15))
        
        # 快捷键提示
        hints = self.font_small.render("[P]" + get_text("open_planner") +
                                      " [T]" + get_text("toggle_workflow") + " [L]" + get_text("switch_language") +
                                      " [SPACE]" + get_text("toggle_mode"), True, (150, 150, 150))
        self.screen.blit(hints, (SCREEN_WIDTH - hints.get_width() - 20, SCREEN_HEIGHT - 35))
        
        # 鼠标坐标
        coord_text = f"鼠标: ({self.mouse_pos[0]}, {self.mouse_pos[1]})"
        coord_surface = self.font_small.render(coord_text, True, (200, 200, 200))
        self.screen.blit(coord_surface, (SCREEN_WIDTH - coord_surface.get_width() - 20, SCREEN_HEIGHT - 55))
        
        # AI状态指示 - 显示已连接的员工数量
        connected_count = self._check_ai_availability()
        if connected_count > 0:
            ai_status = f"● AI已连接 ({connected_count}/{len(self.employees)})"
            ai_color = (100, 255, 100)
        else:
            ai_status = "○ AI未连接 (0/6)"
            ai_color = (255, 100, 100)
        ai_surface = self.font_small.render(ai_status, True, ai_color)
        self.screen.blit(ai_surface, (SCREEN_WIDTH - ai_surface.get_width() - 20, 10))
    
    def _draw_dialog(self):
        """绘制对话框"""
        if self.dialog_timer <= 0 or not self.dialog_text:
            return
        
        dialog_width = min(600, len(self.dialog_text) * 18 + 40)
        dialog_height = 60
        dialog_x = (SCREEN_WIDTH - dialog_width) // 2
        dialog_y = SCREEN_HEIGHT - 120
        
        dialog_rect = pygame.Rect(dialog_x, dialog_y, dialog_width, dialog_height)
        
        pygame.draw.rect(self.screen, (40, 40, 50), dialog_rect)
        pygame.draw.rect(self.screen, (100, 200, 255), dialog_rect, 3)
        
        inner_rect = dialog_rect.inflate(-6, -6)
        pygame.draw.rect(self.screen, (60, 60, 75), inner_rect)
        
        text_surface = self.font_medium.render(self.dialog_text, True, (255, 255, 255))
        text_x = dialog_x + (dialog_width - text_surface.get_width()) // 2
        text_y = dialog_y + (dialog_height - text_surface.get_height()) // 2
        self.screen.blit(text_surface, (text_x, text_y))
        
        hint_text = "按 E 继续对话"
        hint_surface = self.font_small.render(hint_text, True, (150, 150, 160))
        self.screen.blit(hint_surface, (dialog_x + dialog_width - hint_surface.get_width() - 10, dialog_y + dialog_height - 18))
    
    def _draw_message_bubble(self):
        """绘制消息气泡提示"""
        if not self.message_bubble_show or not self.message_bubble_text:
            return
        
        # 计算气泡尺寸
        max_width = 500
        words = self.message_bubble_text
        text_surface = self.font_medium.render(words, True, (255, 255, 255))
        
        # 如果文字太长，需要换行
        lines = []
        current_line = ""
        for char in words:
            test_line = current_line + char
            test_surface = self.font_medium.render(test_line, True, (255, 255, 255))
            if test_surface.get_width() > max_width - 40:
                lines.append(current_line)
                current_line = char
            else:
                current_line = test_line
        if current_line:
            lines.append(current_line)
        
        if not lines:
            lines = [words]
        
        # 计算气泡尺寸
        line_height = self.font_medium.get_height() + 5
        bubble_width = max_width
        bubble_height = len(lines) * line_height + 30
        bubble_x = (SCREEN_WIDTH - bubble_width) // 2
        bubble_y = 100
        
        # 绘制半透明背景遮罩
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 100))
        self.screen.blit(overlay, (0, 0))
        
        # 绘制气泡背景 - 剧情类游戏风格
        bubble_rect = pygame.Rect(bubble_x, bubble_y, bubble_width, bubble_height)
        
        # 渐变效果背景
        pygame.draw.rect(self.screen, (60, 50, 40), bubble_rect, border_radius=15)
        pygame.draw.rect(self.screen, (120, 100, 80), bubble_rect, width=3, border_radius=15)
        
        # 内部装饰线
        inner_rect = bubble_rect.inflate(-10, -10)
        pygame.draw.rect(self.screen, (80, 70, 60), inner_rect, width=1, border_radius=10)
        
        # 绘制文字
        y_offset = bubble_y + 20
        for line in lines:
            line_surface = self.font_medium.render(line, True, (255, 240, 200))
            line_x = bubble_x + (bubble_width - line_surface.get_width()) // 2
            self.screen.blit(line_surface, (line_x, y_offset))
            y_offset += line_height
        
        # 绘制提示
        hint_text = "按任意键关闭"
        hint_surface = self.font_small.render(hint_text, True, (180, 160, 140))
        hint_x = bubble_x + bubble_width - hint_surface.get_width() - 20
        hint_y = bubble_y + bubble_height - 25
        self.screen.blit(hint_surface, (hint_x, hint_y))
    
    def _draw_recall_dialog(self):
        """绘制召回确认对话框"""
        if not self.recall_dialog_active:
            return
        
        # 绘制半透明背景遮罩
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150))
        self.screen.blit(overlay, (0, 0))
        
        # 对话框尺寸
        dialog_width = 400
        dialog_height = 200
        dialog_x = (SCREEN_WIDTH - dialog_width) // 2
        dialog_y = (SCREEN_HEIGHT - dialog_height) // 2
        
        # 绘制对话框背景 - 剧情类游戏风格
        dialog_rect = pygame.Rect(dialog_x, dialog_y, dialog_width, dialog_height)
        pygame.draw.rect(self.screen, (50, 45, 40), dialog_rect, border_radius=10)
        pygame.draw.rect(self.screen, (150, 120, 100), dialog_rect, width=3, border_radius=10)
        
        # 内部装饰
        inner_rect = dialog_rect.inflate(-15, -15)
        pygame.draw.rect(self.screen, (70, 65, 60), inner_rect, width=1, border_radius=5)
        
        # 标题
        title_text = "确认召回"
        title_surface = self.font_large.render(title_text, True, (255, 200, 150))
        title_x = dialog_x + (dialog_width - title_surface.get_width()) // 2
        title_y = dialog_y + 25
        self.screen.blit(title_surface, (title_x, title_y))
        
        # 提示文字
        message_text = "是否确认结束当前工作流？"
        message_surface = self.font_medium.render(message_text, True, (220, 220, 220))
        message_x = dialog_x + (dialog_width - message_surface.get_width()) // 2
        message_y = dialog_y + 75
        self.screen.blit(message_surface, (message_x, message_y))
        
        # 按钮
        button_width = 100
        button_height = 40
        button_y = dialog_y + 130
        
        # 确认按钮 (Y)
        confirm_x = dialog_x + 60
        confirm_rect = pygame.Rect(confirm_x, button_y, button_width, button_height)
        pygame.draw.rect(self.screen, (100, 150, 100), confirm_rect, border_radius=5)
        pygame.draw.rect(self.screen, (150, 200, 150), confirm_rect, width=2, border_radius=5)
        confirm_text = self.font_medium.render("[Y] 确认", True, (255, 255, 255))
        confirm_text_x = confirm_x + (button_width - confirm_text.get_width()) // 2
        confirm_text_y = button_y + (button_height - confirm_text.get_height()) // 2
        self.screen.blit(confirm_text, (confirm_text_x, confirm_text_y))
        
        # 取消按钮 (N)
        cancel_x = dialog_x + dialog_width - 60 - button_width
        cancel_rect = pygame.Rect(cancel_x, button_y, button_width, button_height)
        pygame.draw.rect(self.screen, (150, 100, 100), cancel_rect, border_radius=5)
        pygame.draw.rect(self.screen, (200, 150, 150), cancel_rect, width=2, border_radius=5)
        cancel_text = self.font_medium.render("[N] 取消", True, (255, 255, 255))
        cancel_text_x = cancel_x + (button_width - cancel_text.get_width()) // 2
        cancel_text_y = button_y + (button_height - cancel_text.get_height()) // 2
        self.screen.blit(cancel_text, (cancel_text_x, cancel_text_y))
    
    def run_loading_screen(self):
        """运行启动界面"""
        if not self.loading_screen:
            return True  # 跳过启动界面
        
        print("[启动] 显示启动界面...")
        
        while self.running:
            dt = self.clock.tick(FPS)
            
            # 处理事件
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                    return False
                
                result = self.loading_screen.handle_event(event)
                if result == "EXIT":
                    self.running = False
                    return False
                elif result == "START_GAME":
                    return True
            
            # 更新
            result = self.loading_screen.update(dt)
            if result == "START_GAME":
                return True
            
            # 绘制
            self.loading_screen.draw(self.screen)
            pygame.display.flip()
        
        return False
    
    def _show_exit_confirm_dialog(self):
        """显示退出确认对话框"""
        self.exit_confirm_dialog_active = True
        self.exit_confirm_selection = 0
        
        # 检查是否有正在进行的任务
        active_tasks = len(self.employee_ai_tasks) > 0
        
        # 进入对话框事件循环
        while self.exit_confirm_dialog_active and self.running:
            dt = self.clock.tick(FPS)
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                    return
                
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_LEFT or event.key == pygame.K_a:
                        self.exit_confirm_selection = 0  # 取消
                    elif event.key == pygame.K_RIGHT or event.key == pygame.K_d:
                        self.exit_confirm_selection = 1  # 确认
                    elif event.key == pygame.K_RETURN or event.key == pygame.K_KP_ENTER:
                        if self.exit_confirm_selection == 1:
                            # 确认退出
                            self.exit_confirm_dialog_active = False
                            self._return_to_loading_screen()
                            return
                        else:
                            # 取消
                            self.exit_confirm_dialog_active = False
                            return
                    elif event.key == pygame.K_ESCAPE:
                        # ESC取消
                        self.exit_confirm_dialog_active = False
                        return
                
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        mouse_pos = pygame.mouse.get_pos()
                        # 检查点击按钮
                        dialog_width = 450
                        dialog_height = 220 if active_tasks else 180
                        dialog_x = (SCREEN_WIDTH - dialog_width) // 2
                        dialog_y = (SCREEN_HEIGHT - dialog_height) // 2
                        
                        button_width = 100
                        button_height = 40
                        button_y = dialog_y + dialog_height - 70
                        
                        # 取消按钮
                        cancel_x = dialog_x + 80
                        cancel_rect = pygame.Rect(cancel_x, button_y, button_width, button_height)
                        if cancel_rect.collidepoint(mouse_pos):
                            self.exit_confirm_dialog_active = False
                            return
                        
                        # 确认按钮
                        confirm_x = dialog_x + dialog_width - 80 - button_width
                        confirm_rect = pygame.Rect(confirm_x, button_y, button_width, button_height)
                        if confirm_rect.collidepoint(mouse_pos):
                            self.exit_confirm_dialog_active = False
                            self._return_to_loading_screen()
                            return
            
            # 绘制游戏画面
            self.draw()
            
            # 绘制退出确认对话框
            self._draw_exit_confirm_dialog(active_tasks)
            
            pygame.display.flip()
    
    def _draw_exit_confirm_dialog(self, has_active_tasks):
        """绘制退出确认对话框"""
        dialog_width = 450
        dialog_height = 220 if has_active_tasks else 180
        dialog_x = (SCREEN_WIDTH - dialog_width) // 2
        dialog_y = (SCREEN_HEIGHT - dialog_height) // 2
        
        # 半透明背景遮罩
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        self.screen.blit(overlay, (0, 0))
        
        # 对话框背景
        dialog_rect = pygame.Rect(dialog_x, dialog_y, dialog_width, dialog_height)
        pygame.draw.rect(self.screen, (40, 38, 36), dialog_rect, border_radius=12)
        pygame.draw.rect(self.screen, (80, 75, 70), dialog_rect, width=2, border_radius=12)
        
        # 标题
        title = self.font_large.render("返回主菜单", True, (255, 220, 180))
        title_x = dialog_x + (dialog_width - title.get_width()) // 2
        self.screen.blit(title, (title_x, dialog_y + 20))
        
        # 警告信息
        if has_active_tasks:
            warning_text = "[警告] 有任务正在进行中，退出将中断任务进度！"
            warning = self.font_small.render(warning_text, True, (255, 150, 120))
            warning_x = dialog_x + (dialog_width - warning.get_width()) // 2
            self.screen.blit(warning, (warning_x, dialog_y + 60))
            
            confirm_text = "确定要返回主菜单吗？"
        else:
            confirm_text = "确定要返回主菜单吗？"
        
        confirm = self.font_medium.render(confirm_text, True, (200, 200, 200))
        confirm_x = dialog_x + (dialog_width - confirm.get_width()) // 2
        confirm_y = dialog_y + 95 if has_active_tasks else dialog_y + 70
        self.screen.blit(confirm, (confirm_x, confirm_y))
        
        # 按钮
        button_width = 100
        button_height = 40
        button_y = dialog_y + dialog_height - 70
        
        # 取消按钮
        cancel_x = dialog_x + 80
        cancel_rect = pygame.Rect(cancel_x, button_y, button_width, button_height)
        cancel_color = (80, 80, 85) if self.exit_confirm_selection != 0 else (120, 120, 130)
        pygame.draw.rect(self.screen, cancel_color, cancel_rect, border_radius=6)
        pygame.draw.rect(self.screen, (150, 150, 160), cancel_rect, width=2, border_radius=6)
        cancel_text = self.font_medium.render("取消", True, (255, 255, 255))
        cancel_text_x = cancel_x + (button_width - cancel_text.get_width()) // 2
        cancel_text_y = button_y + (button_height - cancel_text.get_height()) // 2
        self.screen.blit(cancel_text, (cancel_text_x, cancel_text_y))
        
        # 确认按钮
        confirm_x = dialog_x + dialog_width - 80 - button_width
        confirm_rect = pygame.Rect(confirm_x, button_y, button_width, button_height)
        confirm_color = (140, 70, 70) if self.exit_confirm_selection != 1 else (180, 90, 90)
        pygame.draw.rect(self.screen, confirm_color, confirm_rect, border_radius=6)
        pygame.draw.rect(self.screen, (200, 120, 120), confirm_rect, width=2, border_radius=6)
        confirm_text = self.font_medium.render("确认", True, (255, 255, 255))
        confirm_text_x = confirm_x + (button_width - confirm_text.get_width()) // 2
        confirm_text_y = button_y + (button_height - confirm_text.get_height()) // 2
        self.screen.blit(confirm_text, (confirm_text_x, confirm_text_y))
        
        # 提示
        hint = self.font_small.render("使用 ← → 选择，Enter 确认，ESC 取消", True, (120, 120, 120))
        hint_x = dialog_x + (dialog_width - hint.get_width()) // 2
        self.screen.blit(hint, (hint_x, dialog_y + dialog_height - 25))
    
    def _return_to_loading_screen(self):
        """返回启动界面"""
        print("[游戏] 返回启动界面...")
        
        # 重置启动界面状态
        if self.loading_screen:
            self.loading_screen.state = "MENU"
            self.loading_screen.loading_progress = 0
            self.loading_screen.target_progress = 0
            self.loading_screen.loading_complete = False
            self.loading_screen.quote_alpha = 0
            # 清除预渲染的表面
            if hasattr(self.loading_screen, '_quote_surface'):
                delattr(self.loading_screen, '_quote_surface')
        
        # 重新运行启动界面
        result = self.run_loading_screen()
        
        if not result:
            self.running = False
    
    def run(self):
        """游戏主循环"""
        # 运行启动界面
        if not self.run_loading_screen():
            return  # 用户退出
        
        # 启动界面完成，进入游戏
        print("=" * 60)
        print(get_text("game_title"))
        print("=" * 60)
        print(get_text("controls") + ":")
        print("  [WASD]    - " + get_text("move_boss"))
        print("  [E]       - " + get_text("interact_employee"))
        print("  [C]       - " + get_text("create_company"))
        print("  [P]       - " + get_text("open_planner"))
        print("  [T]       - " + get_text("toggle_workflow"))
        print("  [L]       - " + get_text("switch_language"))
        print("  [SPACE]   - " + get_text("toggle_mode"))
        print("  [ESC]     - " + get_text("exit_game"))
        print("  [鼠标左键] - " + get_text("click_employee"))
        print("=" * 60)
        
        if not self.ai_available:
            print("\n[!] " + get_text("ai_service_error"))
            print("    " + get_text("please_start_ollama"))
            print("")
        
        while self.running:
            dt = self.clock.tick(FPS)
            
            self.handle_events()
            self.update(dt)
            self.draw()
        
        pygame.quit()
        sys.exit()


def main():
    """主函数"""
    game = Game()
    game.run()


if __name__ == '__main__':
    main()
