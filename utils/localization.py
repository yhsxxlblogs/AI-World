# 语言本地化系统 - 支持中英文切换
# 为AI World游戏提供多语言支持

from enum import Enum
from typing import Dict, Any

class Language(Enum):
    """语言枚举"""
    CHINESE = "zh"
    ENGLISH = "en"

class Localization:
    """本地化管理器"""
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        
        self.current_language = Language.CHINESE  # 默认中文
        self._initialized = True
        
        # 翻译字典
        self._translations = self._load_translations()
    
    def _load_translations(self) -> Dict[str, Dict[str, str]]:
        """加载所有翻译文本"""
        return {
            # ==================== 通用文本 ====================
            "game_title": {
                Language.CHINESE: "AI World - AI公司模拟器",
                Language.ENGLISH: "AI World - AI Company Simulator"
            },
            "confirm": {
                Language.CHINESE: "确认",
                Language.ENGLISH: "Confirm"
            },
            "cancel": {
                Language.CHINESE: "取消",
                Language.ENGLISH: "Cancel"
            },
            "save": {
                Language.CHINESE: "保存",
                Language.ENGLISH: "Save"
            },
            "close": {
                Language.CHINESE: "关闭",
                Language.ENGLISH: "Close"
            },
            "back": {
                Language.CHINESE: "返回",
                Language.ENGLISH: "Back"
            },
            "next": {
                Language.CHINESE: "下一步",
                Language.ENGLISH: "Next"
            },
            "create": {
                Language.CHINESE: "创建",
                Language.ENGLISH: "Create"
            },
            "input_hint": {
                Language.CHINESE: "按回车确认",
                Language.ENGLISH: "Press Enter to confirm"
            },
            
            # ==================== 游戏控制 ====================
            "controls": {
                Language.CHINESE: "控制说明",
                Language.ENGLISH: "Controls"
            },
            "move_boss": {
                Language.CHINESE: "控制老板移动",
                Language.ENGLISH: "Move boss character"
            },
            "interact_employee": {
                Language.CHINESE: "与附近的员工对话",
                Language.ENGLISH: "Talk to nearby employee"
            },
            "create_company": {
                Language.CHINESE: "创建新公司",
                Language.ENGLISH: "Create new company"
            },
            "open_planner": {
                Language.CHINESE: "打开AI规划师",
                Language.ENGLISH: "Open AI Planner"
            },
            "toggle_workflow": {
                Language.CHINESE: "切换工作流面板",
                Language.ENGLISH: "Toggle workflow panel"
            },
            "toggle_mode": {
                Language.CHINESE: "切换工作/休息模式",
                Language.ENGLISH: "Toggle work/rest mode"
            },
            "exit_game": {
                Language.CHINESE: "退出游戏",
                Language.ENGLISH: "Exit game"
            },
            "click_employee": {
                Language.CHINESE: "点击员工查看详情",
                Language.ENGLISH: "Click employee for details"
            },
            "switch_language": {
                Language.CHINESE: "切换语言(中/英)",
                Language.ENGLISH: "Switch Language(CN/EN)"
            },
            
            # ==================== 状态文本 ====================
            "work_mode": {
                Language.CHINESE: "工作模式",
                Language.ENGLISH: "Work Mode"
            },
            "rest_mode": {
                Language.CHINESE: "休息模式",
                Language.ENGLISH: "Rest Mode"
            },
            "current_mode": {
                Language.CHINESE: "当前",
                Language.ENGLISH: "Current"
            },
            "working": {
                Language.CHINESE: "工作中",
                Language.ENGLISH: "Working"
            },
            "resting": {
                Language.CHINESE: "休息中",
                Language.ENGLISH: "Resting"
            },
            "walking": {
                Language.CHINESE: "行走中",
                Language.ENGLISH: "Walking"
            },
            "sitting": {
                Language.CHINESE: "坐着",
                Language.ENGLISH: "Sitting"
            },
            "idle": {
                Language.CHINESE: "空闲",
                Language.ENGLISH: "Idle"
            },
            
            # ==================== 公司系统 ====================
            "create_new_company": {
                Language.CHINESE: "[创建新公司]",
                Language.ENGLISH: "[Create New Company]"
            },
            "select_company_type": {
                Language.CHINESE: "[选择公司类型]",
                Language.ENGLISH: "[Select Company Type]"
            },
            "confirm_create": {
                Language.CHINESE: "[确认创建]",
                Language.ENGLISH: "[Confirm Creation]"
            },
            "create_success": {
                Language.CHINESE: "[创建成功!]",
                Language.ENGLISH: "[Creation Successful!]"
            },
            "input_company_name": {
                Language.CHINESE: "请输入公司名称：",
                Language.ENGLISH: "Enter company name:"
            },
            "company_name": {
                Language.CHINESE: "公司名称",
                Language.ENGLISH: "Company Name"
            },
            "company_type": {
                Language.CHINESE: "公司类型",
                Language.ENGLISH: "Company Type"
            },
            "company_description": {
                Language.CHINESE: "公司简介",
                Language.ENGLISH: "Description"
            },
            "initial_team": {
                Language.CHINESE: "初始团队",
                Language.ENGLISH: "Initial Team"
            },
            "max_chars_hint": {
                Language.CHINESE: "按回车确认，最多20个字符",
                Language.ENGLISH: "Press Enter, max 20 chars"
            },
            "congrats_company": {
                Language.CHINESE: "恭喜！{name} 正式成立！",
                Language.ENGLISH: "Congratulations! {name} is established!"
            },
            "press_continue": {
                Language.CHINESE: "按回车或空格键继续",
                Language.ENGLISH: "Press Enter or Space to continue"
            },
            
            # ==================== 公司类型 ====================
            "software_company": {
                Language.CHINESE: "软件开发公司",
                Language.ENGLISH: "Software Dev Company"
            },
            "content_company": {
                Language.CHINESE: "内容创作公司",
                Language.ENGLISH: "Content Creation Co."
            },
            "data_company": {
                Language.CHINESE: "数据分析公司",
                Language.ENGLISH: "Data Analytics Co."
            },
            "game_company": {
                Language.CHINESE: "游戏开发公司",
                Language.ENGLISH: "Game Dev Company"
            },
            "consulting_company": {
                Language.CHINESE: "咨询公司",
                Language.ENGLISH: "Consulting Firm"
            },
            "custom_company": {
                Language.CHINESE: "自定义公司",
                Language.ENGLISH: "Custom Company"
            },
            
            # ==================== 公司类型描述 ====================
            "software_desc": {
                Language.CHINESE: "专注于软件产品开发，拥有完整的开发团队",
                Language.ENGLISH: "Focus on software development with complete team"
            },
            "content_desc": {
                Language.CHINESE: "创作优质内容，包括文章、视频、图文等",
                Language.ENGLISH: "Create quality content: articles, videos, graphics"
            },
            "data_desc": {
                Language.CHINESE: "提供专业的数据分析和可视化服务",
                Language.ENGLISH: "Professional data analysis and visualization"
            },
            "game_desc": {
                Language.CHINESE: "开发有趣的游戏作品，从概念到成品",
                Language.ENGLISH: "Develop games from concept to finished product"
            },
            "consulting_desc": {
                Language.CHINESE: "为企业提供专业的咨询服务",
                Language.ENGLISH: "Professional consulting services for enterprises"
            },
            "custom_desc": {
                Language.CHINESE: "自由组合团队成员，创建独特的公司",
                Language.ENGLISH: "Freely combine team members, create unique company"
            },
            
            # ==================== AI规划师 ====================
            "ai_planner_title": {
                Language.CHINESE: "◈ AI规划师 ◈",
                Language.ENGLISH: "◈ AI Planner ◈"
            },
            "planner_welcome": {
                Language.CHINESE: "你好！我是你的AI规划师。请告诉我你想完成什么任务？简单描述即可，我会帮你完善细节并规划团队。",
                Language.ENGLISH: "Hello! I'm your AI Planner. Tell me what task you want to accomplish? A simple description is enough, I'll help refine details and plan the team."
            },
            "thinking": {
                Language.CHINESE: "规划师正在思考",
                Language.ENGLISH: "Planner is thinking"
            },
            "start_project": {
                Language.CHINESE: "按回车键开始项目",
                Language.ENGLISH: "Press Enter to start project"
            },
            "input_requirement": {
                Language.CHINESE: "输入需求后按回车发送",
                Language.ENGLISH: "Enter requirement and press Enter"
            },
            
            # ==================== 规划结果 ====================
            "task_type": {
                Language.CHINESE: "【任务类型】",
                Language.ENGLISH: "[Task Type]"
            },
            "complexity": {
                Language.CHINESE: "【复杂度】",
                Language.ENGLISH: "[Complexity]"
            },
            "core_goal": {
                Language.CHINESE: "【核心目标】",
                Language.ENGLISH: "[Core Goal]"
            },
            "team_plan": {
                Language.CHINESE: "我为你规划了{count}人的团队：",
                Language.ENGLISH: "I've planned a team of {count} members:"
            },
            "sequential": {
                Language.CHINESE: "顺序",
                Language.ENGLISH: "Sequential"
            },
            "parallel": {
                Language.CHINESE: "并行",
                Language.ENGLISH: "Parallel"
            },
            
            # ==================== 工作流UI ====================
            "workflow_title": {
                Language.CHINESE: "◈ 项目工作流",
                Language.ENGLISH: "◈ Project Workflow"
            },
            "no_project": {
                Language.CHINESE: "暂无进行中的项目",
                Language.ENGLISH: "No active projects"
            },
            "project_progress": {
                Language.CHINESE: "项目进度",
                Language.ENGLISH: "Project Progress"
            },
            "task_progress": {
                Language.CHINESE: "任务进度",
                Language.ENGLISH: "Task Progress"
            },
            
            # ==================== 任务状态 ====================
            "status_pending": {
                Language.CHINESE: "等待中",
                Language.ENGLISH: "Pending"
            },
            "status_in_progress": {
                Language.CHINESE: "进行中",
                Language.ENGLISH: "In Progress"
            },
            "status_completed": {
                Language.CHINESE: "已完成",
                Language.ENGLISH: "Completed"
            },
            "status_failed": {
                Language.CHINESE: "失败",
                Language.ENGLISH: "Failed"
            },
            
            # ==================== 员工信息 ====================
            "employee_info_title": {
                Language.CHINESE: "◈ 员工信息编辑 ◈",
                Language.ENGLISH: "◈ Employee Info Edit ◈"
            },
            "badge": {
                Language.CHINESE: "工牌",
                Language.ENGLISH: "Badge"
            },
            "name": {
                Language.CHINESE: "姓名",
                Language.ENGLISH: "Name"
            },
            "gender": {
                Language.CHINESE: "性别",
                Language.ENGLISH: "Gender"
            },
            "position": {
                Language.CHINESE: "职能",
                Language.ENGLISH: "Position"
            },
            "department": {
                Language.CHINESE: "部门",
                Language.ENGLISH: "Department"
            },
            "employee_id": {
                Language.CHINESE: "工牌号",
                Language.ENGLISH: "Employee ID"
            },
            "entry_date": {
                Language.CHINESE: "入职日期",
                Language.ENGLISH: "Entry Date"
            },
            "mood": {
                Language.CHINESE: "心情",
                Language.ENGLISH: "Mood"
            },
            "energy": {
                Language.CHINESE: "能量",
                Language.ENGLISH: "Energy"
            },
            
            # ==================== AI状态 ====================
            "ai_connected": {
                Language.CHINESE: "● AI已连接",
                Language.ENGLISH: "● AI Connected"
            },
            "ai_disconnected": {
                Language.CHINESE: "○ AI未连接",
                Language.ENGLISH: "○ AI Disconnected"
            },
            "ai_service_error": {
                Language.CHINESE: "Ollama服务未启动，无法使用AI规划师",
                Language.ENGLISH: "Ollama service not running, AI Planner unavailable"
            },
            "please_start_ollama": {
                Language.CHINESE: "请先启动Ollama服务",
                Language.ENGLISH: "Please start Ollama service first"
            },
            "please_create_company_first": {
                Language.CHINESE: "请先创建公司（按C键）",
                Language.ENGLISH: "Please create company first (Press C)"
            },
            
            # ==================== 快捷键提示 ====================
            "shortcuts": {
                Language.CHINESE: "快捷键",
                Language.ENGLISH: "Shortcuts"
            },
            
            # ==================== 消息提示 ====================
            "company_created": {
                Language.CHINESE: "[公司] 创建成功: {name}",
                Language.ENGLISH: "[Company] Created: {name}"
            },
            "company_type_info": {
                Language.CHINESE: "[公司] 类型: {type}",
                Language.ENGLISH: "[Company] Type: {type}"
            },
            "team_size_info": {
                Language.CHINESE: "[公司] 团队: {count}人",
                Language.ENGLISH: "[Company] Team: {count} members"
            },
            "project_created": {
                Language.CHINESE: "[项目] 创建成功: {name}",
                Language.ENGLISH: "[Project] Created: {name}"
            },
            "task_count_info": {
                Language.CHINESE: "[项目] 任务数: {count}",
                Language.ENGLISH: "[Project] Tasks: {count}"
            },
            "task_assigned": {
                Language.CHINESE: "[分配] {task} -> {employee}",
                Language.ENGLISH: "[Assigned] {task} -> {employee}"
            },
            "task_completed": {
                Language.CHINESE: "[完成] 任务完成: {name}",
                Language.ENGLISH: "[Complete] Task: {name}"
            },
            "project_completed": {
                Language.CHINESE: "[完成] 项目完成: {name}",
                Language.ENGLISH: "[Complete] Project: {name}"
            },
        }
    
    def set_language(self, language: Language):
        """设置当前语言"""
        self.current_language = language
    
    def toggle_language(self):
        """切换语言"""
        if self.current_language == Language.CHINESE:
            self.current_language = Language.ENGLISH
        else:
            self.current_language = Language.CHINESE
        return self.current_language
    
    def get(self, key: str, **kwargs) -> str:
        """
        获取翻译文本
        
        Args:
            key: 翻译键
            **kwargs: 格式化参数
        
        Returns:
            翻译后的文本
        """
        if key not in self._translations:
            return key
        
        translation = self._translations[key].get(
            self.current_language, 
            self._translations[key].get(Language.ENGLISH, key)
        )
        
        # 格式化参数
        if kwargs:
            try:
                translation = translation.format(**kwargs)
            except KeyError:
                pass
        
        return translation
    
    def get_current_language(self) -> Language:
        """获取当前语言"""
        return self.current_language
    
    def is_chinese(self) -> bool:
        """是否当前为中文"""
        return self.current_language == Language.CHINESE


# 全局本地化实例
_ = Localization()

# 便捷函数
def get_text(key: str, **kwargs) -> str:
    """获取翻译文本的便捷函数"""
    return _.get(key, **kwargs)

def toggle_lang() -> Language:
    """切换语言的便捷函数"""
    return _.toggle_language()

def set_lang(lang: Language):
    """设置语言的便捷函数"""
    _.set_language(lang)

def get_lang() -> Language:
    """获取当前语言的便捷函数"""
    return _.get_current_language()
