# 寻路系统 - A*算法实现，支持人物碰撞检测和随机路径

import heapq
import random
from core.config import PATHFINDING, AREAS, GRID_SIZE

class Node:
    def __init__(self, x, y, g=0, h=0):
        self.x = x
        self.y = y
        self.g = g
        self.h = h
        self.f = g + h
        self.parent = None
    
    def __lt__(self, other):
        return self.f < other.f
    
    def __eq__(self, other):
        return self.x == other.x and self.y == other.y
    
    def __hash__(self):
        return hash((self.x, self.y))

class PathFinder:
    def __init__(self, obstacles=None):
        # 使用与游戏相同的网格大小
        self.grid_size = GRID_SIZE
        self.diagonal = False
        self.static_obstacles = set()  # 存储网格坐标
        self.dynamic_obstacles = set()  # 动态障碍物（其他人物）
        self.work_area = AREAS['work']
        self.ent_area = AREAS['entertainment']
        self.corridor = AREAS['corridor']
        
        # 添加初始障碍物
        if obstacles:
            for obs in obstacles:
                self.add_obstacle_rect(obs['rect'])
    
    def world_to_grid(self, x, y):
        """将世界坐标转换为网格坐标"""
        return (int(x // self.grid_size), int(y // self.grid_size))
    
    def grid_to_world(self, gx, gy):
        """将网格坐标转换为世界坐标(中心点)"""
        return (gx * self.grid_size + self.grid_size // 2, 
                gy * self.grid_size + self.grid_size // 2)
    
    def align_to_grid(self, x, y):
        """将坐标对齐到网格中心"""
        grid_x = round(x / self.grid_size)
        grid_y = round(y / self.grid_size)
        return (grid_x * self.grid_size + self.grid_size // 2, 
                grid_y * self.grid_size + self.grid_size // 2)
    
    def is_valid(self, gx, gy, exclude_employee=None):
        """检查网格点是否可通行"""
        wx, wy = self.grid_to_world(gx, gy)
        
        # 检查是否在工作区、娱乐区或通道内
        # 不使用边距，确保边界位置也能通过
        in_work = (self.work_area['x'] <= wx <= self.work_area['x'] + self.work_area['width'] and
                   self.work_area['y'] <= wy <= self.work_area['y'] + self.work_area['height'])
        in_ent = (self.ent_area['x'] <= wx <= self.ent_area['x'] + self.ent_area['width'] and
                  self.ent_area['y'] <= wy <= self.ent_area['y'] + self.ent_area['height'])
        in_corridor = (self.corridor['x'] <= wx <= self.corridor['x'] + self.corridor['width'] and
                       self.corridor['y'] <= wy <= self.corridor['y'] + self.corridor['height'])
        
        if not (in_work or in_ent or in_corridor):
            return False
        
        # 检查静态障碍物 - 只检查当前网格
        if (gx, gy) in self.static_obstacles:
            return False
        
        # 检查动态障碍物（其他人物）
        if (gx, gy) in self.dynamic_obstacles:
            return False
        
        return True
    
    def heuristic(self, a, b):
        """曼哈顿距离启发式"""
        return abs(a.x - b.x) + abs(a.y - b.y)
    
    def get_neighbors(self, node, exclude_employee=None):
        """获取相邻节点"""
        neighbors = []
        directions = [(0, 1), (1, 0), (0, -1), (-1, 0)]
        
        for dx, dy in directions:
            nx, ny = node.x + dx, node.y + dy
            if self.is_valid(nx, ny, exclude_employee):
                neighbors.append(Node(nx, ny))
        
        return neighbors
    
    def find_path(self, start_x, start_y, end_x, end_y, exclude_employee=None, random_factor=0.2, exact_end=False):
        """A*寻路算法 - 支持随机路径
        
        Args:
            exact_end: 如果为True，路径终点使用精确坐标而不是网格对齐坐标
        """
        # 对齐到网格
        start_x, start_y = self.align_to_grid(start_x, start_y)
        if not exact_end:
            end_x, end_y = self.align_to_grid(end_x, end_y)
        
        start_node = Node(*self.world_to_grid(start_x, start_y))
        end_node = Node(*self.world_to_grid(end_x, end_y))
        
        if start_node == end_node:
            return [(end_x, end_y)]
        
        open_list = []
        closed_set = set()
        
        heapq.heappush(open_list, start_node)
        
        while open_list:
            current = heapq.heappop(open_list)
            
            if current == end_node:
                # 重建路径
                path = []
                while current:
                    path.append(self.grid_to_world(current.x, current.y))
                    current = current.parent
                
                # 如果要求精确终点，替换最后一个点为精确坐标
                if exact_end and path:
                    path[0] = (end_x, end_y)
                
                # 添加随机偏移使路径更自然
                if random_factor > 0 and len(path) > 2:
                    path = self._add_randomness_to_path(path, random_factor)
                
                return path[::-1]
            
            closed_set.add((current.x, current.y))
            
            for neighbor in self.get_neighbors(current, exclude_employee):
                if (neighbor.x, neighbor.y) in closed_set:
                    continue
                
                # 添加随机性到代价计算
                random_cost = random.uniform(0, random_factor) if random_factor > 0 else 0
                tentative_g = current.g + 1 + random_cost
                
                existing = None
                for node in open_list:
                    if node == neighbor:
                        existing = node
                        break
                
                if existing is None or tentative_g < existing.g:
                    if existing:
                        existing.g = tentative_g
                        existing.f = tentative_g + existing.h
                        existing.parent = current
                    else:
                        neighbor.g = tentative_g
                        neighbor.h = self.heuristic(neighbor, end_node)
                        neighbor.f = neighbor.g + neighbor.h
                        neighbor.parent = current
                        heapq.heappush(open_list, neighbor)
        
        # 无路径，返回空路径
        return []
    
    def _add_randomness_to_path(self, path, factor):
        """为路径添加随机偏移"""
        if len(path) <= 2:
            return path
        
        new_path = [path[0]]
        for i in range(1, len(path) - 1):
            x, y = path[i]
            # 添加小幅随机偏移
            offset_x = random.uniform(-self.grid_size * factor * 0.3, self.grid_size * factor * 0.3)
            offset_y = random.uniform(-self.grid_size * factor * 0.3, self.grid_size * factor * 0.3)
            new_path.append((x + offset_x, y + offset_y))
        new_path.append(path[-1])
        return new_path
    
    def add_obstacle(self, x, y, width, height):
        """添加矩形障碍物 - 严格覆盖所有相关网格"""
        # 使用较小的边距，避免阻塞通道
        margin = 2
        start_x = int(x - margin)
        start_y = int(y - margin)
        end_x = int(x + width + margin)
        end_y = int(y + height + margin)
        
        for ox in range(start_x, end_x, self.grid_size):
            for oy in range(start_y, end_y, self.grid_size):
                grid_x = ox // self.grid_size
                grid_y = oy // self.grid_size
                self.static_obstacles.add((grid_x, grid_y))
    
    def add_obstacle_rect(self, rect):
        """从Rect对象添加障碍物"""
        self.add_obstacle(rect.x, rect.y, rect.width, rect.height)
    
    def add_dynamic_obstacle(self, x, y):
        """添加动态障碍物（人物）"""
        grid_x, grid_y = self.world_to_grid(x, y)
        self.dynamic_obstacles.add((grid_x, grid_y))
    
    def remove_dynamic_obstacle(self, x, y):
        """移除动态障碍物"""
        grid_x, grid_y = self.world_to_grid(x, y)
        self.dynamic_obstacles.discard((grid_x, grid_y))
    
    def clear_dynamic_obstacles(self):
        """清除所有动态障碍物"""
        self.dynamic_obstacles.clear()
    
    def clear_obstacles(self):
        """清除所有障碍物"""
        self.static_obstacles.clear()
        self.dynamic_obstacles.clear()
    
    def update_employee_positions(self, employees, current_employee):
        """更新所有员工位置作为动态障碍物 - 严格碰撞检测"""
        self.clear_dynamic_obstacles()
        for emp in employees:
            if emp != current_employee:
                # 添加员工周围的安全区域，确保像素级不接触
                self._add_employee_safety_zone(emp.x, emp.y)
    
    def _add_employee_safety_zone(self, x, y):
        """添加员工周围的安全区域 - 确保严格不接触"""
        # 将员工位置转换为网格坐标
        center_gx, center_gy = self.world_to_grid(x, y)
        
        # 添加3x3区域作为障碍物（确保周围有一定安全距离）
        for dx in range(-1, 2):
            for dy in range(-1, 2):
                gx, gy = center_gx + dx, center_gy + dy
                self.dynamic_obstacles.add((gx, gy))
        
        # 额外添加对角线方向的障碍物，确保斜向也不接触
        diagonal_offsets = [(-2, -1), (-2, 1), (2, -1), (2, 1), (-1, -2), (1, -2), (-1, 2), (1, 2)]
        for dx, dy in diagonal_offsets:
            gx, gy = center_gx + dx, center_gy + dy
            # 检查是否在有效区域内
            wx, wy = self.grid_to_world(gx, gy)
            if self._is_in_valid_area(wx, wy):
                self.dynamic_obstacles.add((gx, gy))
    
    def _is_in_valid_area(self, x, y):
        """检查坐标是否在有效区域内"""
        in_work = (self.work_area['x'] <= x <= self.work_area['x'] + self.work_area['width'] and
                   self.work_area['y'] <= y <= self.work_area['y'] + self.work_area['height'])
        in_ent = (self.ent_area['x'] <= x <= self.ent_area['x'] + self.ent_area['width'] and
                  self.ent_area['y'] <= y <= self.ent_area['y'] + self.ent_area['height'])
        in_corridor = (self.corridor['x'] <= x <= self.corridor['x'] + self.corridor['width'] and
                       self.corridor['y'] <= y <= self.corridor['y'] + self.corridor['height'])
        return in_work or in_ent or in_corridor
