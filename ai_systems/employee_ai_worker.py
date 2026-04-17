# 员工AI工作处理器 - 管理AI调用和进度显示（支持云端API流式输出）
import threading
import time
from typing import Dict, Optional, Callable
from ai_systems.prompts import get_employee_prompt
from ai_systems.output_parser import parse_employee_output


class EmployeeAIWorker:
    """员工AI工作处理器 - 在后台线程执行AI任务，支持流式输出（仅并行模式）"""

    def __init__(self, ollama_client=None):
        # ollama_client 保留用于兼容，但实际使用员工的ai_client
        self.ollama_client = ollama_client
        self.active_tasks: Dict[int, 'TaskInfo'] = {}  # employee_id -> TaskInfo
        self.result_callbacks: Dict[int, Callable] = {}  # employee_id -> callback
        self.employees = []  # 员工列表引用，需要在main中设置

    def set_employees(self, employees):
        """设置员工列表引用"""
        self.employees = employees

    def start_task(self,
                   employee_id: int,
                   employee_name: str,
                   role: str,
                   responsibility: str,
                   task_description: str,
                   project_goal: str,
                   on_progress: Callable = None,
                   on_complete: Callable = None,
                   on_token: Callable = None):
        """
        启动AI任务（仅并行模式）

        Args:
            employee_id: 员工ID
            employee_name: 员工名称
            role: 角色
            responsibility: 职责
            task_description: 任务描述
            project_goal: 项目目标
            on_progress: 进度回调函数(progress_percent)
            on_complete: 完成回调函数(result_content)
        """
        # 如果该员工已有任务在运行，先停止
        if employee_id in self.active_tasks:
            print(f"[AI工作器] 员工{employee_name}已有任务在运行，跳过")
            return False

        # 获取员工对象
        employee = None
        for emp in self.employees:
            if emp.id == employee_id:
                employee = emp
                break

        if not employee:
            print(f"[AI工作器] 错误: 找不到员工 {employee_id}")
            return False

        # 检查员工是否配置了AI
        if not hasattr(employee, 'ai_client') or not employee.ai_client.is_available():
            print(f"[AI工作器] 错误: 员工 {employee_name} 未配置有效的AI API")
            if on_complete:
                on_complete(f"[错误: 员工 {employee_name} 未配置有效的AI API]")
            return False

        # 创建任务信息
        task_info = TaskInfo(
            employee_id=employee_id,
            employee_name=employee_name,
            role=role,
            start_time=time.time()
        )
        self.active_tasks[employee_id] = task_info
        self.result_callbacks[employee_id] = on_complete

        # 构建提示词
        prompt = get_employee_prompt(
            role=role,
            responsibility=responsibility,
            task_description=task_description,
            project_goal=project_goal
        )

        # 启动后台线程执行AI任务
        thread = threading.Thread(
            target=self._worker_thread_stream,
            args=(employee, prompt, on_progress, on_complete, on_token)
        )
        thread.daemon = True
        thread.start()

        print(f"[AI工作器] 启动任务: {employee_name} - {role}")
        return True

    def _worker_thread_stream(self,
                              employee,
                              prompt: str,
                              on_progress: Callable,
                              on_complete: Callable,
                              on_token: Callable = None):
        """工作线程 - 执行AI调用（流式输出）"""
        employee_id = employee.id
        try:
            task_info = self.active_tasks.get(employee_id)
            if not task_info:
                print(f"[AI工作器] 错误: 找不到任务信息 for employee {employee_id}")
                return

            print(f"[AI工作器] 开始AI调用: {task_info.employee_name} - {task_info.role}")
            print(f"[AI工作器] 提示词长度: {len(prompt)} 字符")

            # 模拟进度更新
            progress_steps = [10, 25, 40, 55, 70, 85, 95]
            step_delay = 0.5
            progress_idx = 0
            last_update_time = time.time()

            # 启动AI流式生成
            full_response = ""
            token_count = 0

            print(f"[AI工作器] 使用员工AI客户端: {employee.name}")
            print(f"[AI工作器] API: {employee.api_url}")
            print(f"[AI工作器] 模型: {employee.model_name}")

            # 使用员工的ai_client进行流式生成
            for chunk in employee.ai_client.generate_stream(prompt):
                if employee_id not in self.active_tasks:
                    # 任务被取消
                    print(f"[AI工作器] 任务被取消: {task_info.employee_name}")
                    return

                full_response += chunk
                token_count += 1
                
                # 实时更新token数
                if on_token and token_count % 10 == 0:  # 每10个token更新一次
                    on_token(token_count)

                # 更新进度
                current_time = time.time()
                if current_time - last_update_time > step_delay and progress_idx < len(progress_steps):
                    progress = progress_steps[progress_idx]
                    if on_progress:
                        on_progress(progress)
                    print(f"[AI工作器] {task_info.employee_name} 进度: {progress}%")
                    progress_idx += 1
                    last_update_time = current_time

            print(f"[AI工作器] 接收完成，共 {token_count} 个token，响应长度: {len(full_response)}")

            # 完成100%
            if on_progress:
                on_progress(100)

            # 解析结果
            print(f"[AI工作器] 开始解析响应...")
            result_content = self._parse_ai_response(full_response)
            print(f"[AI工作器] 解析完成")

            # 调用完成回调
            if on_complete:
                on_complete(result_content)

            print(f"[AI工作器] 任务完成: {task_info.employee_name}")

        except Exception as e:
            print(f"[AI工作器] 任务失败: {e}")
            import traceback
            traceback.print_exc()
            if on_complete:
                on_complete(f"[错误: {str(e)}]")
        finally:
            # 清理任务信息
            if employee_id in self.active_tasks:
                del self.active_tasks[employee_id]
            if employee_id in self.result_callbacks:
                del self.result_callbacks[employee_id]

    def _parse_ai_response(self, response: str) -> Dict:
        """解析AI响应，提取结构化工作结果"""
        # 使用 output_parser 解析严格格式的输出
        parsed = parse_employee_output(response)

        # 构建结果字典
        result = {
            'stage_name': parsed.get('stage_name', ''),
            'completed_content': parsed.get('completed_content', ''),
            'key_outputs': parsed.get('key_outputs', []),
            'quality_check': parsed.get('quality_check', {}),
            'handoff': parsed.get('handoff', ''),
            'output_files': parsed.get('output_files', ''),
            'raw_text': response
        }

        return result

    def get_task_progress(self, employee_id: int) -> float:
        """获取任务进度"""
        task_info = self.active_tasks.get(employee_id)
        if task_info:
            return task_info.progress
        return 0.0

    def is_task_active(self, employee_id: int) -> bool:
        """检查任务是否在进行中"""
        return employee_id in self.active_tasks

    def cancel_task(self, employee_id: int):
        """取消任务"""
        if employee_id in self.active_tasks:
            del self.active_tasks[employee_id]


class TaskInfo:
    """任务信息"""

    def __init__(self, employee_id: int, employee_name: str, role: str, start_time: float):
        self.employee_id = employee_id
        self.employee_name = employee_name
        self.role = role
        self.start_time = start_time
        self.progress = 0.0
        self.output = ""
