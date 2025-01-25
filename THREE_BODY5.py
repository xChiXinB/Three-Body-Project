"""
原创三体模拟系统（5.0重构版已完结）  作者：王之众
"""

print('三体系统正在加载中……')
import pygame, math, time

# 定义类
# 天体类
class Planets:
    def __init__(self, information, axis):
        # 接受一个嵌套字典的字典
        self.info = information
        self.reset(axis, 'rects')
        self.need_resetting = True

    def get_info(self):
        """获取天体信息"""
        return self.info

    def draw(self, screen, axis):
        """将所有天体渲染在屏幕上"""
        for planet in self.info.values(): # 遍历自己信息
            pygame.draw.circle(screen, planet['color'], axis.calculate_pos(planet['pos_x'], planet['pos_y']), 5, 0)

    def run(self, fps):
        """物理计算自己的位置"""
        for num in range(1, 4):
            # 计算其他天体的编号
            other_num = [1, 2, 3]
            other_num.remove(num)
            # 调用函数（感觉这个函数可以写到类里面，但是懒得算了）
            a_x1, a_y1 = calculate_acceleration(
                x_origin=self.info[num]['pos_x'],
                y_origin=self.info[num]['pos_y'],
                x_target=self.info[other_num[0]]['pos_x'],
                y_target=self.info[other_num[0]]['pos_y'],
                mass_target=self.info[other_num[0]]['mass'],
                G=6.6743e-11,
                minimum_d=22
            )
            a_x2, a_y2 = calculate_acceleration(
                x_origin=self.info[num]['pos_x'],
                y_origin=self.info[num]['pos_y'],
                x_target=self.info[other_num[1]]['pos_x'],
                y_target=self.info[other_num[1]]['pos_y'],
                mass_target=self.info[other_num[1]]['mass'],
                G=6.6743e-11,
                minimum_d=22
            )
            # 更改自身加速度、速度、位置
            # 更新加速度
            self.info[num]['a_x'] = a_x1 + a_x2
            self.info[num]['a_y'] = a_y1 + a_y2
            # 帧位移=帧初速度*帧时间+½*加速度*帧时间²
            self.info[num]['pos_x'] += self.info[num]['v_x'] * 1/fps + 0.5 * self.info[num]['a_x'] * (1/fps) ** 2
            self.info[num]['pos_y'] += self.info[num]['v_y'] * 1/fps + 0.5 * self.info[num]['a_y'] * (1/fps) ** 2
            # 更新帧末速度作为下一帧初速度
            self.info[num]['v_x'] += self.info[num]['a_x'] * 1/fps
            self.info[num]['v_y'] += self.info[num]['a_y'] * 1/fps

    def highlight(self, num, screen, color, axis, information):
        """高亮天体num号"""
        information.show_planet_touch(self.info[num]['mass'], num, screen, color) # 展示接触到的天体信息
        x, y = axis.calculate_pos(self.info[num]['pos_x'], self.info[num]['pos_y']) # 获取天体实际位置
        pygame.draw.circle(screen, color, (x, y), 7, 2) # 为天体渲染高亮（白边）

    def move(self, axis, mouse_action, num):
        """移动天体"""
        if mouse_action == 'Moving planet':
            # 把天体位置设为鼠标位置
            self.info[num]['pos_x'], self.info[num]['pos_y'] = axis.calculate_mouse_pos() # 需要设定为鼠标实际位置
            self.need_resetting = True # rect对象未重置
        else:
            # 移动天体以后需要重置rect对象
            if self.need_resetting:
                self.reset(axis, 'rects')
                self.need_resetting = False # rect对象已重置

    def alter_mass(self, num):
        """更改天体num的质量"""
        print() # 换行
        print(f'将更改天体{num}的质量（必须为自然数）：')
        new_mass = input(f'原质量：{self.info[num]['mass']}kg ——> 更改为（单位：kg）：') # 接受玩家输入
        # 只有输入自然数（非负整数）时才允许更改质量
        try:
            new_mass = int(new_mass)
        except ValueError:
            # 不是整数，int抛出ValueError
            print('质量更改失败。输入非自然数。')
        else:
            if new_mass >= 0:
                print(f'成功地将天体{num}的质量更改为{new_mass}kg。')
                self.info[num]['mass'] = new_mass # 修改重量数据
            else:
                # 输入的质量小于0
                print('质量更改失败。输入非自然数。')

    def reset(self, axis, *args):
        """复位天体的参数*args"""
        for argument in args: # 遍历传入的不定长参数
            if argument == 'rects':
                # 复位所有的rect对象
                for num in range(1, 4):
                    self.info[num]['rect'].center = (axis.calculate_pos(self.info[num]['pos_x'], self.info[num]['pos_y']))
            elif argument == 'a&v':
                # 将所有天体的加速度和速度设为0
                for num in range(1, 4):
                    self.info[num]['a_x'] = self.info[num]['a_y'] = self.info[num]['v_x'] = self.info[num]['v_x'] = 0

# 按钮类
class Button:
    def __init__(self, font):
        self.rect = pygame.Rect(530, 620, 140, 50) # 碰撞箱
        self.font = font
        # 生成四个button
        self.start = Button.summon_button(self, '开始模拟', (255,255,255), (20,80,255))
        self.start_touched = Button.summon_button(self, '开始模拟', (0,0,0), (255,255,25))
        self.stop = Button.summon_button(self, '中断模拟', (255,255,255), (20,80,255))
        self.stop_touched = Button.summon_button(self, '中断模拟', (0,0,0), (255,255,25))

    def summon_button(self, text, text_color, bg_color):
        """渲染button的surface"""
        surface = pygame.Surface((140, 50))
        surface.fill(bg_color) # 填充底色
        text = self.font.render(text, True, text_color)
        surface.blit(text, (10, 10)) # 填充文字
        return surface

    def get_mouse_collision(self):
        """返回是否碰撞鼠标"""
        return self.rect.collidepoint(pygame.mouse.get_pos())

    def draw(self, stopping, screen):
        """在屏幕上绘制自己"""
        if stopping:
            # 中断模拟，绘制开始模拟
            if Button.get_mouse_collision(self): # 检测触碰鼠标
                screen.blit(self.start_touched, (530, 620))
            else:
                screen.blit(self.start, (530, 620))
        else:
            # 正在模拟，绘制中断模拟
            if Button.get_mouse_collision(self):
                screen.blit(self.stop_touched, (530, 620))
            else:
                screen.blit(self.stop, (530, 620))

# 右键列表类
class List:
    def __init__(self, font):
        self.font = font
        self.options = {
            '更改天体1的质量': False,
            '更改天体2的质量': False,
            '更改天体3的质量': False,
            '打开操作引导': False,
            '关闭操作引导': False,
            '打开深色模式': False,
            '关闭深色模式': False,
            '显示天体轨迹': False,
            '隐藏天体轨迹': False,
            '显示天体位置信息': False,
            '折叠天体位置信息': False,
            '加速':False,
            '恢复原速':False,
            '退出系统': False
        } # 存储列表选项内容
        """self.list_surface = None # 列表图层
        self.list_rects = None # 列表文字的碰撞箱
        self.todo = None # 列表的执行项
        self.todo_list = None # 可能的列表执行项
        self.highlighting = None # 高亮图层
        self.x = self.y = None # 列表位置"""
        self.list_surface = self.list_rects = self.todo = self.todo_list = self.highlighting = self.x = self.y = None # 同时初始化以上

    def refresh(self, target_planet, guide, color, track, information, speed_ctrl):
        """更新列表状态"""
        # 更改天体质量
        self.options['更改天体1的质量'] = target_planet == 1
        self.options['更改天体2的质量'] = target_planet == 2
        self.options['更改天体3的质量'] = target_planet == 3
        # 开关操作引导
        self.options['打开操作引导'] = not guide.get_mode()
        self.options['关闭操作引导'] = guide.get_mode()
        # 开关深色模式
        self.options['打开深色模式'] = color == (0,0,0)
        self.options['关闭深色模式'] = color == (255,255,255)
        # 显示轨迹与否
        self.options['显示天体轨迹'] = not track.get_mode()
        self.options['隐藏天体轨迹'] = track.get_mode()
        # 显示天体位置与否
        self.options['显示天体位置信息'] = not information.get_mode()
        self.options['折叠天体位置信息'] = information.get_mode()
        # 加速与否
        self.options['加速'] = speed_ctrl.ctrl()
        self.options['恢复原速'] = not speed_ctrl.ctrl()
        # 退出系统（永远是True）
        self.options['退出系统'] = True

        # 创建文字surface，并计算列表图层（surface）的宽高
        text_surfaces = [] # 储存每行文字surface
        self.todo_list = [] # 储存值为True的键
        width = 0 # 列表宽度
        for text in self.options: # 遍历键
            if self.options[text]:
                # 如果键对应的值是True
                surface = self.font.render(text, True, color) # 渲染文字surface
                text_surfaces.append(surface)
                self.todo_list.append(text) # 加入键（选项）
                width = max(width, surface.get_width()) # 迭代最大宽度
        width += 8 # 留出左右的缝隙
        """
        高度计算：   列表行数*16 ←--文字   +（列表行数+1)*4 ←--空隙
        =16l+4(l+1) =16l+4l+4 =20l+4
        """
        height = 20 * len(text_surfaces) + 4 # 计算右键列表高度（留出上下缝隙）

        # 根据宽高变量创建surface
        self.list_surface = pygame.Surface((width, height)) # 空surface
        self.highlighting = pygame.Surface((width-8, 16), pygame.SRCALPHA) # 高亮图层
        self.highlighting.fill((0, 0, 255, 51)) # 不透明红色
        if color == (255,255,255):
            self.list_surface.fill((45,45,45))
        else:
            self.list_surface.fill((210,210,210)) # 绘制surface背景色

        # 计算列表位置
        self.x, self.y = pygame.mouse.get_pos()  # 与鼠标位置一致
        # 判断窗口是否会溢出屏幕
        if self.x + width > 700:
            self.x = 700 - width
        if self.y + height > 700:
            self.y = 700 - height

        # 向空surface上渲染文字、并创建rect
        y = 4 # 纵坐标
        self.list_rects = []
        for text in text_surfaces:
            self.list_surface.blit(text, (4, y)) # 渲染文字
            self.list_rects.append(pygame.Rect(self.x + 4, self.y + y, width-8, 16)) # 创建文字rect
            y += 20

    def run(self, screen, mouse_action):
        if mouse_action == 'Activate list':
            # 绘制surface
            screen.blit(self.list_surface, (self.x, self.y))
            # 遍历rects
            n = 0
            self.todo = None
            for rect in self.list_rects:
                if rect.collidepoint(pygame.mouse.get_pos()):
                    # 若接触鼠标则高亮
                    screen.blit(self.highlighting, rect.topleft)
                    self.todo = self.todo_list[n] # 更新列表执行项
                n += 1
            """此时self.todo储存了被选中的操作"""

    def execute(self, planets, guide, color, main_color, track, information, run, speed_ctrl):
        if self.todo is None:
            pass # 无操作
        elif self.todo == '更改天体1的质量':
            planets.alter_mass(1)
        elif self.todo == '更改天体2的质量':
            planets.alter_mass(2)
        elif self.todo == '更改天体3的质量':
            planets.alter_mass(3)
        elif self.todo == '打开操作引导':
            guide.mode(True)
        elif self.todo == '关闭操作引导':
            guide.mode(False)
        elif self.todo == '打开深色模式':
            main_color.__init__((255,255,255))
            track.empty((255,255,255)) # 清空轨迹
        elif self.todo == '关闭深色模式':
            main_color.__init__((0,0,0))
            track.empty((0,0,0))
        elif self.todo == '显示天体轨迹':
            track.mode(True)
        elif self.todo == '隐藏天体轨迹':
            track.mode(False, color) # color用于清空已有轨迹
        elif self.todo == '显示天体位置信息':
            information.mode(True)
        elif self.todo == '折叠天体位置信息':
            information.mode(False)
        elif self.todo == '加速':
            speed_ctrl.__init__(False)
        elif self.todo == '恢复原速':
            speed_ctrl.__init__(True)
        else: # 退出系统
            run.__init__(False) # 退出系统

# 信息类
class Information:
    def __init__(self, font):
        self.text = None
        self.font = font
        self.show_pos = True
        self.planets_color = {
            1:'(红)',
            2:'(绿)',
            3:'(蓝)'
        }

    def show_mouse_pos(self, axis, screen, color):
        """展示鼠标坐标"""
        x, y = axis.calculate_mouse_pos() # 获取鼠标真实坐标
        self.text = self.font.render(f'鼠标位置：{(x, y)}', True, color)
        screen.blit(self.text, (10, 10))

    def show_planet_touch(self, mass, num, screen, color):
        """展示天体num的质量"""
        self.text = self.font.render(f'天体{num}：{mass}kg', True, color)
        screen.blit(self.text, (10, 36))

    def show_simulate(self, planets, color, screen, speed_ctrl):
        """展示正在模拟信息"""
        if speed_ctrl.ctrl():
            self.text = self.font.render('正在模拟中……', True, color)
        else:
            self.text = self.font.render('正在模拟中……（已加速）', True, color)
        screen.blit(self.text, (10, 36))
        if self.show_pos: # 展示天体位置
            y = 62
            for num in range(1, 4):
                self.text = self.font.render(
                    f'天体{num}{self.planets_color[num]}位置:({round(planets.get_info()[num]['pos_x'])},{round(planets.get_info()[num]['pos_y'])})',
                    True, color)
                screen.blit(self.text, (10, y))
                y += 26

    def get_mode(self):
        """返回是否展示天体位置"""
        return self.show_pos

    def mode(self, condition):
        self.show_pos = condition

# 鼠标类
class Mouse:
    def __init__(self):
        self.key = None
        self.action = None
        self.planet_touch = None
        self.target_planet = None # 这个参数受锁定影响
        self.lock = False

    def right_click(self):
        """按下鼠标右键进行的操作"""
        self.key = 'Right'

    def left_click(self, stopping, button, planets, axis, track, color):
        """按下鼠标左键进行的操作"""
        self.key = 'Left'
        # 与按钮对象互动
        if button.get_mouse_collision():
            # 如果碰到按钮，返回stopping的反值
            planets.reset(axis, 'a&v', 'rects') # 重置天体
            track.empty(color)
            return not stopping
        else:
            return stopping

    def none_click(self):
        """松开鼠标进行的操作"""
        self.key = None

    def refresh(self, stopping, planets, axis, information, guide, track, lst, screen, color, main_color, run, speed_ctrl):
        """确定自己的行为"""
        # 更新天体接触信息
        self.planet_touch = None
        for num in range(1, 4):
            if planets.get_info()[num]['rect'].collidepoint(pygame.mouse.get_pos()):
                # 如果鼠标接触到了num号天体
                self.planet_touch = num
                break # 一次只能接触一个天体
        # 高亮天体逻辑
        if stopping: # 只有停止时才高亮天体
            if self.action is None:
                if self.planet_touch is not None:
                    # 如果没有执行操作却触碰天体
                    planets.highlight(self.planet_touch, screen, color, axis, information)
            elif self.action == 'Moving planet':
                # 如果在移动天体，则高亮对应天体
                planets.highlight(self.target_planet, screen, color, axis, information)
            elif self.action == 'Activate list':
                if self.target_planet is not None:
                    # 如果对一个天体右键，高亮它
                    planets.highlight(self.target_planet, screen, color, axis, information)
        # 行为解锁逻辑
        if self.lock:
            if self.action == 'Activate list':
                if self.key == 'Left':
                    self.lock = False # 解锁
                    lst.execute(planets, guide, color, main_color, track, information, run, speed_ctrl) # 列表执行内容
            elif 'Moving' in self.action:
                if self.key is None:
                    self.lock = False  # 解锁
        # 行为判断逻辑
        """这里（下一行）不能用if...ELSE...！！！"""
        if not self.lock: # 只有未解锁才判断
            if self.key == 'Left':
                # 按下左键
                self.lock = True # 锁定
                if (self.planet_touch is None) or (not stopping): # 如果没有碰到天体或正在模拟
                    self.action = 'Moving axis'
                else: # 反之：停止模拟且碰到天体
                    self.action = 'Moving planet'
                    self.target_planet = self.planet_touch # 复制天体触碰信息，受锁定影响
            elif self.key == 'Right':
                # 按下右键
                self.lock = True # 锁定
                self.action = 'Activate list'
                self.target_planet = self.planet_touch
                lst.refresh(self.target_planet, guide, color, track, information, speed_ctrl) # 刷新列表内容
            elif self.key is None:
                # 没有按下鼠标时，无行为。不锁定。
                self.action = None

        # 返回行为
        return self.action, self.target_planet

# 轴类
class Axis:
    def __init__(self):
        self.dx = self.dy = self.add_dx = self.add_dy = self.init_x = self.init_y = 0
        self.not_inited = True
        self.not_compounded = True
        self.color = None

    def calculate_pos(self, x, y):
        """接受原始坐标，返回屏幕（渲染）坐标"""
        return x + self.dx + self.add_dx, y + self.dy + self.add_dy

    def calculate_mouse_pos(self):
        """返回鼠标原始坐标"""
        return pygame.mouse.get_pos()[0] - self.dx - self.add_dx, pygame.mouse.get_pos()[1] - self.dy - self.add_dy,

    def move(self, mouse_action, planets):
        # 移动轴（平面）
        if mouse_action == 'Moving axis':
            if self.not_inited:
                self.init_x, self.init_y = pygame.mouse.get_pos()
                self.not_compounded = True
                self.not_inited = False
            self.add_dx = pygame.mouse.get_pos()[0] - self.init_x
            self.add_dy = pygame.mouse.get_pos()[1] - self.init_y
        else:
            if self.not_compounded:
                self.dx += self.add_dx
                self.dy += self.add_dy
                self.add_dx = self.add_dy = 0
                planets.reset(self, 'rects')
                self.not_compounded = False
                self.not_inited = True

    def draw(self, screen, color):
        """绘制轴"""
        if color == (255,255,255):
            self.color = (185,185,185)
        else:
            self.color = (70,70,70)
        pygame.draw.circle(screen, self.color,(self.dx + self.add_dx, self.dy + self.add_dy),3, 0) # 原点
        pygame.draw.line(screen, self.color, (0, self.dy + self.add_dy), (700, self.dy + self.add_dy), 1) # x轴
        pygame.draw.line(screen, self.color, (self.dx + self.add_dx, 0), (self.dx + self.add_dx, 700), 1) # y轴

# 新手引导类
class Guide:
    def __init__(self, font):
        self.guide_on = False
        self.stop_step = 1
        self.start_step = 1
        self.font = font
        self.start_time = time.time()
        # 储存新手教程文字
        self.stop1_text = [
            '欢迎来到三体！',
            '引导即将开始。',
            '（点按c以继续）',
            'tip:若c键无响应，请尝试将系统输入法',
            '    切换为英文，或关闭正在运行的中文',
            '    输入法。'
        ]
        self.stop2_text = [
            '在空白处拖动鼠标，',
            '可以移动整个平面。',
            '来试试！',
            '（点按c以继续）'
        ]
        self.stop3_text = [
            '将鼠标放在天体上并拖动，',
            '可以拖曳天体，更改其位置。',
            '←尝试拖动这个蓝色的天体吧！',
            '（点按c以继续）'
        ]
        self.stop4_text = [
            '当一切准备就绪，',
            '点击这个按钮 “开始模拟”，',
            '就可以欣赏三体运动了！',
            '（点按按钮↓以继续）'
        ]
        self.stop5_text = [
            '当天体停止运行时，',
            '你可以右键天体以改变其质量。',
            '←尝试更改这个天体的质量！',
            '（点按c结束新手教程）'
        ]
        self.start1_text = [
            '电脑正在模拟三体运动。',
            '模拟时，你无法拖曳天体，但可以移动平面。',
            '                 （点按按钮↓以继续）'
        ]

    def guide_stop(self, screen, color, planets, axis):
        """展示停止模拟时的新手教程"""
        if self.guide_on:
            if self.stop_step == 1:
                self.show(350, 50, self.stop1_text, color, screen)
            elif self.stop_step == 2:
                x, y = axis.calculate_pos(400, 300) # 文字随屏幕移动
                self.show(x, y, self.stop2_text, color, screen)
            elif self.stop_step == 3:
                x, y = axis.calculate_pos(planets.get_info()[3]['pos_x'] + 10, planets.get_info()[3]['pos_y'] - 58) # 文字随天体移动
                self.show(x, y, self.stop3_text, color, screen)
            elif self.stop_step == 4:
                self.show(500, 516, self.stop4_text, color, screen)
            elif self.stop_step == 5:
                x, y = axis.calculate_pos(planets.get_info()[3]['pos_x'] + 10, planets.get_info()[3]['pos_y'] - 58)
                self.show(x, y, self.stop5_text, color, screen)

    def guide_start(self, screen, color):
        """展示开始模拟时的新手教程。"""
        if self.guide_on:
            if self.start_step == 1:
                self.show(370,540, self.start1_text, color, screen)
                if self.stop_step != 5:
                    self.stop_step = 5

    def show(self, x, init_y, texts, color, screen):
        """渲染文字"""
        y = init_y
        for text in texts:
            surface = self.font.render(text, True, color)
            screen.blit(surface, (x, y))
            y += 26

    def step_forward(self):
        if self.guide_on:
            if self.stop_step != 4:
                self.stop_step += 1
                if self.stop_step == 6:
                    self.guide_on = False
                    self.stop_step = 1

    def welcome(self, color, screen):
        """显示欢迎信息"""
        if time.time() < self.start_time + 3.5: # 信息展示持续3.5秒
            surface = self.font.render('欢迎来到三体！单击右键以打开操作引导。', True, color)
            screen.blit(surface, (198,500))

    def get_mode(self):
        """返回是否开启引导"""
        return self.guide_on

    def mode(self, condition):
        """开启或关闭教程"""
        if condition: # 开or关
            self.guide_on = True  # 开启教程
        else:
            self.guide_on = False
            self.stop_step = 1 # 关闭教程

# 天体轨迹类
class Track:
    def __init__(self):
        self.surface = pygame.Surface((700,700))
        self.mask = pygame.Surface((700,700), pygame.SRCALPHA)
        self.color = None
        self.count = 0
        self.track_on = True

    def render(self, planets, axis, screen, color):
        """根据天体的真实位置渲染轨迹"""
        if self.track_on: # 绘制模式开启才能绘制
            if color == (0,0,0):
                self.color = (255,255,255,1)
            else:
                self.color = (0,0,0,1)
            for num in range(1, 4):
                x, y = axis.calculate_pos(planets.get_info()[num]['pos_x'], planets.get_info()[num]['pos_y'])
                pygame.draw.circle(self.surface, planets.get_info()[num]['color'], (x, y), 2, 0) # 拖曳天体时会鬼畜，暂留
            if self.count % 4 == 0: # 防止蒙版覆盖过快
                self.mask.fill(self.color)
                self.surface.blit(self.mask, (0,0))
            self.count += 1
            screen.blit(self.surface, (0,0))

    def empty(self, color):
        """清空轨迹"""
        if color == (0,0,0):
            self.surface.fill((255,255,255))
        else:
            self.surface.fill((0,0,0))

    def get_mode(self):
        """返回是否显示轨迹"""
        return self.track_on

    def mode(self, condition, color=None):
        if condition:
            self.track_on = True
        else:
            self.track_on = False
            self.empty(color)

# 主颜色类
class MainColor:
    def __init__(self, color):
        """设置主颜色"""
        self.color = color

    def get_color(self):
        """返回主颜色"""
        return self.color

# 运行类
class Run:
    def __init__(self, condition):
        self.running = condition

    def run(self):
        return self.running

# 速度控制类
class SpeedCtrl:
    def __init__(self, condition):
        self.isCtrl = condition

    def ctrl(self):
        return self.isCtrl

# 定义函数
# 主程序
def main():
    # 初始化
    pygame.init()
    print('加载完成！')
    #time.sleep(0.5)
    # 字体
    simsun = pygame.font.SysFont('simsun', 16) # 宋体
    simhei = pygame.font.SysFont('simhei',30) # 黑体
    # 游戏窗口
    screen = pygame.display.set_mode((700, 700))
    pygame.display.set_caption('三体运动模拟系统')
    # 帧率
    fps_ctrl = pygame.time.Clock()
    fps = 60
    # 创建对象
    button = Button(simhei) # 按钮对象
    lst = List(simsun) # 列表对象
    information = Information(simsun) # 信息对象
    guide = Guide(simsun) #新手引导对象
    mouse = Mouse() # 鼠标对象
    axis = Axis() # 轴对象
    track = Track() # 轨迹对象
    main_color = MainColor((255,255,255)) # 主颜色对象
    run = Run(True) # 运行对象
    speed_ctrl = SpeedCtrl(True) # 速度控制对象
    planet1 = {
        'pos_x':100, # x坐标
        'pos_y':100, # y坐标
        'a_x':0, # x加速度
        'a_y':0, # y加速度
        'v_x':0, # x速度
        'v_y':0, # y速度
        'mass':10000000000000, # 质量
        'rect':pygame.Rect(0, 0, 10, 10), # rect对象
        'color':(255,0,0) # 颜色
    }
    planet2 = {
        'pos_x':150, # x坐标
        'pos_y':150, # y坐标
        'a_x':0, # x加速度
        'a_y':0, # y加速度
        'v_x':0, # x速度
        'v_y':0, # y速度
        'mass':15000000000000, # 质量
        'rect':pygame.Rect(0, 0, 10, 10), # rect对象
        'color':(0,255,0) # 颜色
    }
    planet3 = {
        'pos_x':278, # x坐标
        'pos_y':140, # y坐标
        'a_x':0, # x加速度
        'a_y':0, # y加速度
        'v_x':0, # x速度
        'v_y':0, # y速度
        'mass':8000000000000, # 质量
        'rect':pygame.Rect(0, 0, 10, 10), # rect对象
        'color':(0,0,255) # 颜色
    }
    planets = Planets({1:planet1, 2:planet2, 3:planet3}, axis) # 天体对象
    # 运行变量
    stopping = True
    # 游戏循环
    while run.run():
        color = main_color.get_color() # 颜色刷新

        # 事件遍历
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run.__init__(False) # 退出窗口
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                stopping = mouse.left_click(stopping, button, planets, axis, track, color)
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 3:
                mouse.right_click()
            elif event.type == pygame.MOUSEBUTTONUP:
                mouse.none_click()
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_c:
                guide.step_forward()

        # 其他任务
        if stopping:
            guide.guide_stop(screen, color, planets, axis) # 显示新手引导
        else:
            planets.run(fps) # 天体运行
            track.render(planets, axis, screen, color) # 绘制天体轨迹
            information.show_simulate(planets, color, screen, speed_ctrl) # 显示模拟信息
            guide.guide_start(screen, color) # 显示新手引导
        planets.draw(screen, axis) # 绘制天体
        button.draw(stopping, screen) # 绘制按钮
        axis.draw(screen, color) # 绘制轴
        guide.welcome(color, screen) # 显示欢迎信息
        mouse_action, mouse_target_num = mouse.refresh(stopping, planets, axis, information, guide, track, lst, screen, color, main_color, run, speed_ctrl)
        # 鼠标行动的执行
        axis.move(mouse_action, planets) # 移动轴
        planets.move(axis, mouse_action, mouse_target_num) # 移动天体
        lst.run(screen, mouse_action)

        information.show_mouse_pos(axis, screen, color) # 显示鼠标信息

        # 基本控制
        if speed_ctrl.ctrl():
            fps_ctrl.tick(8*fps)
        pygame.display.update()
        if color == (0,0,0):
            screen.fill((255,255,255))
        else:
            screen.fill((0,0,0))

    print()
    print('系统已退出，感谢您的体验。')
    pygame.quit() # 退出pygame

def calculate_acceleration(x_origin, y_origin, x_target, y_target, mass_target, G, minimum_d):
    """计算目标天体的万有引力作用在原天体上产生的加速度"""
    # 建立以原天体为中心的平面直角坐标系，计算目标天体的相应坐标
    x_coordinate = x_target - x_origin
    y_coordinate = y_target - y_origin
    # 计算目标天体与原天体的距离和角度
    distance = math.hypot(x_coordinate,y_coordinate)
    distance = max(distance, minimum_d) # 最小距离限制
    angle = math.atan2(y_coordinate, x_coordinate)
    # 根据万有引力定律计算加速度（F=G*m1*m2/r^2, a=F/m）
    acceleration = G * mass_target / distance ** 2
    # 分解加速度
    acceleration_x = acceleration * math.cos(angle)
    acceleration_y = acceleration * math.sin(angle)
    return acceleration_x, acceleration_y

# 运行主程序
if __name__ == '__main__':
    main()