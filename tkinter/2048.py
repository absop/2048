import copy
import json
import os
import time

from random import randint

import threading
import tkinter as tk

FOREGROUND = {
    "button_down":  "#ADD817",
    "button":       "#FFFFFF",
    "new_num":      "#FFFFFF",
    "number":       "#282828",
    "scorebar":     "#9554E0",
}
BACKGROUND = {
    0:              "#EDEDED",
    2:              "#C9C9C9",
    4:              "#D3D385",
    8:              "#E8BE8B",
    16:             "#F4A460",
    32:             "#F48D4A",
    64:             "#FF7F50",
    128:            "#F5725B",
    256:            "#F86048",
    512:            "#D85C4c",
    1024:           "#CD5C5C",
    2048:           "#C9413C",
    4096:           "#B53835",
    8192:           "#A52A2A",
    16384:          "#A13A3A",
    32768:          "#B4122A",
    65536:          "#B02031",
    "end":          "#F6415D",
    "button":       "#9ACD32",
    "scorebar":     "#EDEDED"
}


class Grid():
    DIRECTIONS = ["U", "D", "L", "R"]

    def blanks(self):
        return [(i, j) for i in range(4)
            for j in range(4) if self.matrix[i][j] == 0]

    def add_rand_num(self):
        # 控制数字2和4的概率,此时2出现概率是80%
        rand_num = (2, 4)[randint(1, 100) // 80]

        blanks = self.blanks()
        randxy = randint(0, len(blanks) - 1)
        x, y = blanks[randxy]
        self.matrix[x][y] = rand_num
        return (x, y)

    def init_matrix(self):
        self.matrix = [[0 for i in range(4)] for j in range(4)]
        self.score = 0
        rand_num = (2, 4)[randint(1, 100) // 80]
        x = randint(0, 3)
        y = randint(0, 3)
        self.matrix[x][y] = rand_num
        return (x, y)

    # 像‘冒泡’一样把‘0’冒出来放到一边，非零在一边
    def bubble(self, direction):
        # 如果是上下方向的，先转置一下矩阵，bubble之后再转置回去
        if direction == "U" or direction == "D":
            self.matrix = list(map(list, zip(*self.matrix)))

        forward = direction in ("D", "R")
        for i in range(len(self.matrix)):
            array = [a for a in self.matrix[i] if a != 0]
            zeros = [0] * (4 - len(array))
            self.matrix[i] = zeros + array if forward else array + zeros

        if direction == "U" or direction == "D":
            self.matrix = list(map(list, zip(*self.matrix)))

    # 变换矩阵： 合并可以合并的格子，并冒泡处理
    def transform_matrix(self, ways):
        pairs, score, direction = ways
        for pair in pairs:
            move, goal = pair[0], pair[1]
            self.matrix[goal[0]][goal[1]] *= 2
            self.matrix[move[0]][move[1]]  = 0
        self.bubble(direction)

    # 搜索往某一方向变换的方法并返回，没有可行的方法则返回None
    def search_ways(self, direction):
        def within_bounds(index):
            return index > end if step == -1 else index < end

        coord_pairs, addable_score, moveable = [], 0, False
        begin, end, step = ((3, -1, -1), (0, 4, 1))[direction in ("U", "L")]
        if direction in ("L", "R"):
            for row in range(begin, end, step):
                column = begin
                while within_bounds(column):
                    number = self.matrix[row][column]
                    k = column + step
                    while within_bounds(k) and self.matrix[row][k] == 0:
                        k += step
                    if within_bounds(k):
                        if number != 0 and self.matrix[row][k] == number:
                            coord_pairs.append(((row, column), (row, k)))
                            addable_score += 2 * number
                            column = k
                        elif number == 0:
                            moveable = True
                    column += step
        else:
            for column in range(begin, end, step):
                row = begin
                while within_bounds(row):
                    number = self.matrix[row][column]
                    k = row + step
                    while within_bounds(k) and self.matrix[k][column] == 0:
                        k += step
                    if within_bounds(k):
                        if number != 0 and self.matrix[k][column] == number:
                            coord_pairs.append(((row, column), (k, column)))
                            addable_score += 2 * number
                            row = k
                        elif number == 0:
                            moveable = True
                    row += step
        if addable_score > 0 or moveable:
            return (coord_pairs, addable_score, direction)
        return None

    def has_ways(self):
        for direction in self.DIRECTIONS:
            if self.search_ways(direction) is not None:
                return True
        return False

    def search_best_way(self):
        def score_key(grid, direction, ways, depth):
            possible_ways[direction][1] += ways[1] * (depth + 1)
            if depth > 0:
                temp = Grid()
                temp.matrix = copy.deepcopy(grid.matrix)
                temp.transform_matrix(ways)
                # self.add_rand_num(temp)
                subways = []
                for direc in self.DIRECTIONS:
                    way = temp.search_ways(direc)
                    if way is not None:
                        subways.append(way)
                if subways:
                    best_subway = max(subways, key=lambda x: x[1])
                    if best_subway[1] != 0:
                        score_key(temp, direction, best_subway, depth - 1)
                    else:
                        for subway in subways:
                            score_key(temp, direction, subway, depth - 1)

        possible_ways = {}
        for direction in self.DIRECTIONS:
            ways = self.search_ways(direction)
            if ways is not None:
                possible_ways.update({direction: [ways, 0]})
                score_key(self, direction, ways, 3)
        if possible_ways:
            best_direc = max(possible_ways, key=lambda k: possible_ways[k][1])
            return possible_ways[best_direc][0]
        return None


class Game2048(Grid):
    RECORD_PATH = os.path.join(os.path.dirname(__file__), "RECORD")
    WINDOW_NAME = os.path.splitext(os.path.basename(__file__))[0]
    KEY_BINDINGS = {
        "U": ("W", "UP"),   "D": ("S", "DOWN"),
        "L": ("A", "LEFT"), "R": ("D", "RIGHT")
    }

    def __init__(self):
        self.setup()

        self.window.bind("<KeyPress>", self.run_call_back)
        self.window.protocol("WM_DELETE_WINDOW", self.on_close)
        self.window.mainloop()

    def init_profile(self):
        self.call_backs = {
            self.new_game:  ["F1"],
            self.game_help: ["F3"],
            self.auto_run:  ["F5"]
        }
        self.gfont = ('Monaco', 17, "bold")
        self.bfont = ('Monaco', 15, "bold")

    def create_button(self, text, command, width):
        return tk.Button(self.status_bar, font=self.bfont,
                         width=width, text=text, command=command,
                         bg=BACKGROUND["button"], fg=FOREGROUND["button"],
                         relief=tk.GROOVE, overrelief=tk.RAISED,
                         activeforeground=FOREGROUND["button_down"])

    def create_scorebar(self):
        return tk.Button(self.status_bar, bg=BACKGROUND["scorebar"],
                         disabledforeground=FOREGROUND["scorebar"],
                         state=tk.DISABLED, relief=tk.GROOVE,
                         width=9, font=self.bfont)

    def init_window(self):
        self.window = tk.Tk()
        self.window.attributes("-alpha", 0.9)
        self.window.geometry("+300+100")
        # True: 数值可变, False: 不可变
        self.window.resizable(width=False, height=False)
        self.window.title(self.WINDOW_NAME)

        self.status_bar = tk.Label(self.window)
        self.status_bar.grid(row=0, column=0)

        self.scorebar = self.create_scorebar()
        self.bestbar = self.create_scorebar()
        self.new_game_button = self.create_button("新游戏", self.new_game, 9)
        self.help_button = self.create_button("帮助", self.game_help, 4)
        self.auto_button = self.create_button("自动", self.auto_run, 4)
        self.bestbar.grid(row=0, column=1)
        self.scorebar.grid(row=0, column=0)
        self.new_game_button.grid(row=0, column=2)
        self.help_button.grid(row=0, column=3)
        self.auto_button.grid(row=0, column=4)

        self.gridsbar = tk.Label(self.window)
        self.gridsbar.grid(row=1, column=0, columnspan=3)
        self.grids = [([0] * 4) for j in range(4)]
        for i in range(4):
            for j in range(4):
                self.grids[i][j] = tk.Label(self.gridsbar, width=8, height=3,
                                            font=self.gfont, relief=tk.GROOVE)
                self.grids[i][j].grid(row=i + 1, column=j)

    # 涮新格子的显示，xy为新添加的数字的坐标，将其显示为另一颜色
    def flush_window(self, xy):
        self.best = max(self.best, self.score)
        self.bestbar.config(text=self.best)
        self.scorebar.config(text=self.score)
        for i in range(4):
            for j in range(4):
                number = self.matrix[i][j]
                bg = BACKGROUND[number]
                fg = FOREGROUND[("number", "new_num")[(i, j) == xy]]
                self.grids[i][j].config(text=number or "", bg=bg, fg=fg)

    def on_close(self):
        just_best = not (self.score > 0 and self.has_ways())
        self.save_record(just_best)
        self.window.destroy()

    def save_record(self, just_best=False):
        record = {
            "best": self.best,
            "time": time.strftime("%Y%m%d %H:%M:%S")
        }
        if not just_best:
            record.update({"matrix": self.matrix, "score": self.score})
        with open(self.RECORD_PATH, "w+") as file:
            file.write(json.dumps(record))

    def load_record(self):
        try:
            with open(self.RECORD_PATH, "r") as file:
                record = json.load(file)
                return record
        except:
            return {}

    def setup(self):
        record = self.load_record()
        self.best = record.get("best", 0)
        self.score = record.get("score", 0)
        self.matrix = record.get("matrix", [])
        self.init_profile()
        self.init_window()
        self.start_game()
        try:
            self.flush_window(self.add_rand_num())
        except:
            self.flush_window(self.init_matrix())

    def start_game(self):
        self.auto = False
        self.game_over = False
        self.auto_button["text"] = "自动"
        self.help_button["text"] = "帮助"
        self.auto_button["bg"] = BACKGROUND["button"]
        self.help_button["bg"] = BACKGROUND["button"]

    def end_game(self):
        if not self.game_over:
            self.game_over = True
            self.auto_button["text"] = "结束"
            self.help_button["text"] = "结束"
            self.auto_button["bg"] = BACKGROUND["end"]
            self.help_button["bg"] = BACKGROUND["end"]

    def new_game(self):
        self.save_record(just_best=True)
        self.flush_window(self.init_matrix())
        self.start_game()

    # 定时器，单开一个线程在延迟一定时间后执行function
    def timer(self, interval, function):
        thread = threading.Timer(interval, function)
        thread.setDaemon(True)
        thread.start()

    # 自动开启新游戏，自动模式使用，用来达到某一目标分数
    def auto_resart(self):
        max_score = 0
        for i in range(4):
            for j in range(4):
                if self.matrix[i][j] > max_score:
                    max_score = self.matrix[i][j]
        if not max_score >= 2048:
            self.timer(1, self.new_game)
            self.timer(2, self.auto_run)
        else:
            won_time = time.strftime("%Y%m%d %H:%M:%S")
            self.window.title("%s(%s)" % (self.WINDOW_NAME, won_time))

    def flush_grids(self, ways):
        self.score += ways[1]
        self.transform_matrix(ways)
        self.flush_window(self.add_rand_num())
        if not self.has_ways():
            self.end_game()
            self.auto_resart()

    def run_call_back(self, event):
        keysym = event.keysym.upper()

        for call_back in self.call_backs:
            if keysym in self.call_backs[call_back]:
                call_back()
                return
        if not self.game_over:
            for direction in self.DIRECTIONS:
                if keysym in self.KEY_BINDINGS[direction]:
                    ways = self.search_ways(direction)
                    if ways is not None:
                        self.flush_grids(ways)
                    return

    def game_help(self):
        if not self.game_over:
            ways = self.search_best_way()
            if ways is not None:
                self.flush_grids(ways)

    def auto_run(self):
        def run_help():
            if self.auto is True:
                self.game_help()
            if not self.game_over and self.auto is True:
                self.timer(delay, run_help)
        delay = 0.01
        if not self.game_over:
            self.auto = not self.auto
            self.auto_button["text"] = ("自动", "停止")[self.auto]
            run_help()


if __name__ == "__main__":
    Game2048()
