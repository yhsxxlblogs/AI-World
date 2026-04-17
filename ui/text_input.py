# AI World - 文本输入组件
# 支持中文输入、连续删除、复制粘贴

import pygame
from pygame.locals import *
from pygame.time import get_ticks
from pygame.key import get_mods


class TextInput:
    """文本输入组件 - 支持中文输入和连续删除（优化版）"""
    
    def __init__(self, max_length=100, allow_chinese=True):
        self.max_length = max_length
        self.allow_chinese = allow_chinese
        self.text = ""
        
        # 输入法组合文本（拼音/候选）
        self.composition_text = ""
        self.composition_cursor = 0
        
        # 按键重复处理
        self.key_repeat_delay = 400  # 首次重复延迟（毫秒）
        self.key_repeat_interval = 50  # 重复间隔（毫秒）
        self.key_timers = {}  # 记录按键按下的时间
        self.key_repeat_states = {}  # 记录按键是否已开始重复
        
        # 新增：防止输入法干扰的状态跟踪
        self.last_textinput_time = 0  # 上次文本输入时间
        self.textinput_cooldown = 50  # 文本输入冷却时间（毫秒）
        self.last_backspace_time = 0  # 上次Backspace时间
        self.backspace_cooldown = 100  # Backspace冷却时间（毫秒）
        self.ime_active = False  # 输入法是否处于活动状态
        self.last_event_text = ""  # 上次输入的文本（用于去重）
        
    def enable_text_input(self):
        """启用文本输入事件（用于中文输入）"""
        try:
            pygame.key.start_text_input()
            print("[TextInput] 文本输入已启用")
        except Exception as e:
            print(f"[TextInput] 启用文本输入失败: {e}")
            
    def disable_text_input(self):
        """禁用文本输入事件"""
        try:
            pygame.key.stop_text_input()
            print("[TextInput] 文本输入已禁用")
        except Exception as e:
            print(f"[TextInput] 禁用文本输入失败: {e}")
    
    def set_text(self, text):
        """设置文本"""
        self.text = text[:self.max_length]
        
    def get_full_text(self):
        """获取完整文本（已确认 + 组合中）"""
        return self.text + self.composition_text
    
    def get_confirmed_text(self):
        """获取已确认的文本"""
        return self.text
    
    def handle_event(self, event) -> bool:
        """
        处理输入事件（优化版，更好的输入法兼容性）
        返回: 文本是否发生变化
        """
        text_changed = False
        current_time = get_ticks()
        
        # 处理文本输入事件（关键！这是接收中文的主要方式）
        if event.type == TEXTINPUT:
            # 防抖动：检查冷却时间
            if current_time - self.last_textinput_time < self.textinput_cooldown:
                return False
            
            # 防重复：检查是否与上次输入相同
            if event.text == self.last_event_text:
                return False
            
            if event.text:
                # 检查是否为中文字符
                has_chinese = any(ord(c) > 127 for c in event.text)
                
                if has_chinese and self.allow_chinese:
                    # 中文字符直接添加到主文本
                    if len(self.text) + len(event.text) <= self.max_length:
                        self.text += event.text
                        text_changed = True
                        self.last_textinput_time = current_time
                        self.last_event_text = event.text
                        self.ime_active = False  # 中文输入完成，IME不活跃
                        self.composition_text = ""  # 清空组合文本，防止重复
                        print(f"[TextInput] 中文输入: {event.text}")
                elif event.text.isprintable():
                    # 英文/数字/标点直接添加
                    if len(self.text) + len(event.text) <= self.max_length:
                        self.text += event.text
                        text_changed = True
                        self.last_textinput_time = current_time
                        self.last_event_text = event.text
                        print(f"[TextInput] 文本输入: {event.text}")
            return text_changed
        
        # 处理文本编辑事件（输入法组合状态）
        if event.type == TEXTEDITING:
            # 更新组合文本（显示输入法的候选/拼音）
            old_composition = self.composition_text
            self.composition_text = event.text
            self.composition_cursor = event.start
            
            # 检测IME状态
            if event.text:
                self.ime_active = True
                print(f"[TextInput] 编辑中: {event.text}, 光标: {event.start}")
            else:
                # 组合文本为空，可能是IME提交完成或取消
                if old_composition and not event.text:
                    self.ime_active = False
                    print("[TextInput] IME组合完成")
            return False
        
        # 处理按键事件
        if event.type == KEYDOWN:
            current_time = get_ticks()
            
            # 记录按键按下时间（用于重复删除）
            self.key_timers[event.key] = current_time
            self.key_repeat_states[event.key] = False
            
            # 处理特殊键
            if event.key == K_BACKSPACE:
                # 防抖动：检查Backspace冷却时间
                if current_time - self.last_backspace_time < self.backspace_cooldown:
                    return False
                
                if self.composition_text:
                    # 如果有组合文本，让输入法处理
                    pass
                elif self.text:
                    # 删除已确认的文本
                    self.text = self.text[:-1]
                    text_changed = True
                    self.last_backspace_time = current_time
                    self.last_event_text = ""  # 清除上次输入记录
                    print(f"[TextInput] 删除后: {self.text}")
                    
            elif event.key == K_DELETE:
                # Delete键暂不支持
                pass
                
            elif event.key == K_RETURN or event.key == K_KP_ENTER:
                # 确认组合文本（仅当IME活跃且组合文本不为空时）
                # 注意：现代输入法通常通过TEXTINPUT事件自动提交中文，这里作为后备
                if self.ime_active and self.composition_text:
                    # 检查是否已经通过TEXTINPUT添加过（避免重复）
                    if not self.text.endswith(self.composition_text):
                        if len(self.text) + len(self.composition_text) <= self.max_length:
                            self.text += self.composition_text
                            text_changed = True
                            print(f"[TextInput] 回车确认: {self.composition_text}")
                    self.composition_text = ""
                    self.ime_active = False
                    
            elif event.key == K_ESCAPE:
                # 取消组合
                self.composition_text = ""
                
            elif event.key == K_SPACE:
                # 空格直接添加（输入法通常会处理空格确认）
                if not self.composition_text and len(self.text) < self.max_length:
                    self.text += " "
                    text_changed = True
                    
            elif event.key == K_v and (get_mods() & KMOD_CTRL):
                # Ctrl+V 粘贴 - 尝试使用pyperclip
                try:
                    import pyperclip
                    pasted_text = pyperclip.paste()
                    if pasted_text:
                        remaining = self.max_length - len(self.text)
                        self.text += pasted_text[:remaining]
                        text_changed = True
                        print(f"[TextInput] 粘贴: {pasted_text[:remaining]}")
                except ImportError:
                    print("[TextInput] 粘贴失败: 未安装pyperclip模块")
                except Exception as e:
                    print(f"[TextInput] 粘贴失败: {e}")
                    
            elif event.key == K_c and (get_mods() & KMOD_CTRL):
                # Ctrl+C 复制
                try:
                    import pyperclip
                    if self.text:
                        pyperclip.copy(self.text)
                        print(f"[TextInput] 复制: {self.text}")
                except ImportError:
                    print("[TextInput] 复制失败: 未安装pyperclip模块")
                except Exception as e:
                    print(f"[TextInput] 复制失败: {e}")
                    
            elif event.key == K_a and (get_mods() & KMOD_CTRL):
                # Ctrl+A 全选（暂不实现，仅阻止默认行为）
                pass
                
            else:
                # 其他按键：尝试从unicode获取字符
                # 这用于某些系统TEXTINPUT不工作的情况
                if hasattr(event, 'unicode') and event.unicode:
                    char = event.unicode
                    is_chinese = ord(char) > 127
                    is_printable = char.isprintable()
                    
                    # 只处理非ASCII的可打印字符（中文等）
                    if is_chinese and self.allow_chinese:
                        if len(self.text) + len(char) <= self.max_length:
                            self.text += char
                            text_changed = True
                            print(f"[TextInput] 字符输入: {char}")
        
        elif event.type == KEYUP:
            # 清除按键状态
            if event.key in self.key_timers:
                del self.key_timers[event.key]
            if event.key in self.key_repeat_states:
                del self.key_repeat_states[event.key]
                
        return text_changed
    
    def update(self, dt):
        """更新按键重复状态（用于连续删除，优化版）"""
        current_time = get_ticks()
        
        # 检查Backspace键的重复
        # 注意：只有当没有组合文本（输入法候选）且IME不活跃时才处理删除
        if K_BACKSPACE in self.key_timers and not self.composition_text and not self.ime_active:
            elapsed = current_time - self.key_timers[K_BACKSPACE]
            
            # 如果超过2秒没有KEYUP事件，强制清除Backspace状态（防止输入法干扰）
            if elapsed > 2000:
                print("[TextInput] Backspace状态超时，强制清除")
                del self.key_timers[K_BACKSPACE]
                if K_BACKSPACE in self.key_repeat_states:
                    del self.key_repeat_states[K_BACKSPACE]
                self.last_backspace_time = current_time
                return
            
            # 检查冷却时间
            if current_time - self.last_backspace_time < self.backspace_cooldown:
                return
            
            if not self.key_repeat_states.get(K_BACKSPACE, False):
                # 首次重复
                if elapsed >= self.key_repeat_delay:
                    self.key_repeat_states[K_BACKSPACE] = True
                    self.key_timers[K_BACKSPACE] = current_time
                    if self.text:
                        self.text = self.text[:-1]
                        self.last_backspace_time = current_time
                        print(f"[TextInput] 连续删除: {self.text}")
            else:
                # 后续重复
                if elapsed >= self.key_repeat_interval:
                    self.key_timers[K_BACKSPACE] = current_time
                    if self.text:
                        self.text = self.text[:-1]
                        self.last_backspace_time = current_time
                        print(f"[TextInput] 连续删除: {self.text}")
