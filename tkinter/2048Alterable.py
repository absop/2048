import copy
import json
import os
import time
from random import randint

import threading
import tkinter as tk
from tkinter import messagebox

FOREGROUND = {
    "button_down":  "#ADD817",
    "new_game":     "#FFFFFF",
    "new_num":      "#FFFFFF",
    "number":       "#282828",
    "scorebar":    "#9554E0",
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
    16384:          "#A52A2A",
    32768:          "#A52A2A",
    65536:          "#A52A2A",
    "new_game":     "#9ACD32",
    "scorebar":    "#EDEDED"
}


class Game2048():
    RECORD_PATH = os.path.join(os.path.dirname(__file__), "RECORD")
    WINDOW_NAME = os.path.splitext(os.path.basename(__file__))[0]

    def __init__(self, scale=4):
        self.start_game(min(max(scale, 4), 8))

        self.window.bind("<KeyPress>", self.run_call_back)
        self.window.protocol("WM_DELETE_WINDOW", self.on_close)
        self.window.mainloop()

    def init_profile(self, scale):
        self.key_bindings = {
            "U": {"range": (0,    scale,  1), "keys": ("W", "UP")},
            "D": {"range": (scale-1, -1, -1), "keys": ("S", "DOWN")},
            "L": {"range": (0,    scale,  1), "keys": ("A", "LEFT")},
            "R": {"range": (scale-1, -1, -1), "keys": ("D", "RIGHT")}
        }

        self.call_backs = {
            self.new_game:  ["F1"],
            self.game_help: ["F3"],
            self.auto_run:  ["F5"]
        }

    def sent_message(self, msg):
        messagebox.showinfo("2048", msg)

    def on_close(self):
        just_best = (True, False)[self.score > 0 and self.has_ways(self.array)]
        self.save_record(just_best)
        self.window.destroy()

    def save_record(self, just_best=False):
        record = {
            "best": self.best,
            "time": time.strftime("%Y%m%d %H:%M:%S")
        }
        if not just_best:
            record.update({
                "array": self.array,
                "scale": self.scale,
                "score": self.score
            })
        with open(self.RECORD_PATH, "w+") as file:
            file.write(json.dumps(record))

    def load_record(self):
        try:
            with open(self.RECORD_PATH, "r") as file:
                record = json.load(file)
                return record
        except:
            return {"best": 0}

    def init_window(self):
        scale = self.scale
        new_game_width, dx, dy = (10, 8, 4)
        width, height = (dx * scale, dy * scale)
        scorebar_width = (width - new_game_width) // 2

        font_size = -min(max(360 // height, 12), 20)
        self.font = ('微软雅黑', font_size, "bold")
        self.window = tk.Tk()
        self.window.attributes("-alpha", 0.9)
        self.window.geometry("+300+100")
        # True: 数值可变, False: 不可变
        self.window.resizable(width=False, height=False)
        self.window.title("%s(%s)"%(self.WINDOW_NAME, scale))

        self.status_bar = tk.Label(self.window)
        self.status_bar.grid(row=0, column=0)

        def scorebar(text):
            return tk.Button(self.status_bar, bg=BACKGROUND["scorebar"],
                             state=tk.DISABLED, relief=tk.GROOVE, anchor=tk.W,
                             width=scorebar_width, font=self.font, text=text,
                             disabledforeground=FOREGROUND["scorebar"])
        self.scorebar = scorebar("score = %d"%self.score)
        self.bestbar = scorebar("best = %d"%self.best)
        self.button = tk.Button(self.status_bar, font=self.font,
                                command=self.new_game, text="New Game",
                                width=new_game_width,
                                bg=BACKGROUND["new_game"],
                                fg=FOREGROUND["new_game"],
                                relief=tk.GROOVE, overrelief=tk.RAISED,
                                activeforeground=FOREGROUND["button_down"])
        self.scorebar.grid(row=0, column=0)
        self.bestbar.grid(row=0, column=1)
        self.button.grid(row=0, column=2)

        self.gridsbar = tk.Label(self.window, width=width, height=height)
        self.gridsbar.grid(row=1, column=0, columnspan=3)
        self.grids = [[0 for i in range(scale)] for j in range(scale)]
        for i in range(scale):
            for j in range(scale):
                number = self.array[i][j]
                self.grids[i][j] = tk.Label(self.gridsbar, font=self.font,
                                            fg=FOREGROUND["number"],
                                            bg=BACKGROUND[number],
                                            text=number or "",
                                            width=dx, height=dy,
                                            relief=tk.GROOVE)
                self.grids[i][j].grid(row=i+1, column=j)

    # (x, y) 是新添加的数字的位置，我们可以给它一些特效
    def window_flush(self, coord):
        self.best = max(self.best, self.score)
        self.bestbar.config(text="best = %d"%self.best)
        self.scorebar.config(text="score = %d"%self.score)
        for i in range(self.scale):
            for j in range(self.scale):
                number = self.array[i][j]
                bg = BACKGROUND[number]
                fg = FOREGROUND[("number", "new_num")[(i, j) == coord]]
                self.grids[i][j].config(text=number or "", bg=bg, fg=fg)

    def add_rand_num(self, array):
        # 控制数字2和4的概率,此时2出现概率是80%
        rand_num = (2, 4)[randint(1, 100) // 80]

        blanks = self.find_blank(array)
        randxy = randint(0, len(blanks) - 1)
        x, y = blanks[randxy]
        array[x][y] = rand_num
        return (x, y)

    def start_game(self, scale):
        record = self.load_record()
        self.auto = False
        self.game_over = False
        self.best = record["best"]
        try:
            if scale == record["scale"]:
                self.array = record["array"]
                self.scale = record["scale"]
                self.score = record["score"]
            else:
                self.init_data(scale)
        except:
            self.init_data(scale)
        self.init_profile(self.scale)
        self.init_window()

    def end_game(self):
        if not self.game_over:
            self.game_over = True
            self.sent_message("Game Over!!!")

    def new_game(self):
        self.auto = False
        self.game_over = False
        self.save_record(just_best=True)
        self.window_flush(self.init_data(self.scale))

    def init_data(self, scale):
        self.array = [[0 for i in range(scale)] for j in range(scale)]
        self.scale = scale
        self.score = 0
        rand_num = (2, 4)[randint(1, 100) // 80]
        x = randint(0, scale - 1)
        y = randint(0, scale - 1)
        self.array[x][y] = rand_num
        return (x, y)

    def find_blank(self, array):
        blanks = []
        for i in range(self.scale):
            for j in range(self.scale):
                if array[i][j] == 0:
                    blanks.append((i, j))
        return blanks

    def transpose(self, array):
        for i in range(4):
            for j in range(i+1, 4):
                array[i][j], array[j][i] = array[j][i], array[i][j]

    def shift_array(self, array, key):
        if key == "U" or key == "D":
            self.transpose(array)

        forward = key in ("D", "R")
        for i in range(len(array)):
            temp = [a for a in array[i] if a != 0]
            zeros = [0] * (self.scale - len(temp))
            array[i] = zeros + temp if forward else temp + zeros

        if key == "U" or key == "D":
            self.transpose(array)

    def merge_array(self, array, merge):
        for pair in merge:
            src, des = pair[0], pair[1]
            array[des[0]][des[1]] *= 2
            array[src[0]][src[1]]  = 0

    def search_key_ways(self, array, key):
        def ref(i, j):
            return array[j][i] if transpose else array[i][j]

        def in_range(j):
            return j > end if step == -1 else j < end

        def coord_pair(i, j, k):
            return ((j, i), (k, i)) if transpose else ((i, j), (i, k))

        transpose = key in ("U", "D")
        items = self.key_bindings[key]
        begin, end, step = items["range"]
        merge, score, shift = [], 0, False
        for i in range(*items["range"]):
            j = begin
            while in_range(j):
                number = ref(i, j)
                k = j + step
                while in_range(k) and ref(i, k) == 0:
                    k += step
                if in_range(k):
                    if number != 0 and ref(i, k) == number:
                        merge.append(coord_pair(i, j, k))
                        score += number << 1
                        j = k
                    elif number == 0:
                        shift = True
                j += step
        if score or shift:
            return (merge, score, key)
        return None

    def has_ways(self, array):
        for key in self.key_bindings:
            if self.search_key_ways(array, key) is not None:
                return True
        return False

    def move(self, ways):
        self.score += ways[1]
        self.merge_array(self.array, ways[0])
        self.shift_array(self.array, ways[2])
        self.window_flush(self.add_rand_num(self.array))
        if not self.has_ways(self.array):
            self.end_game()

    def run_call_back(self, event):
        keysym = event.keysym.upper()

        for call_back in self.call_backs:
            if keysym in self.call_backs[call_back]:
                call_back()
                return
        if not self.game_over:
            for key in self.key_bindings:
                if keysym in self.key_bindings[key]["keys"]:
                    ways = self.search_key_ways(self.array, key)
                    if ways is not None:
                        self.move(ways)
                    return

    def game_help(self):
        if not self.game_over:
            ways = self.search_best_way(self.array)
            if ways is not None:
                self.move(ways)

    def auto_run(self):
        def run_help():
            if self.auto is True:
                self.game_help()
            if not self.game_over and self.auto is True:
                thread = threading.Timer(delay, run_help)
                thread.setDaemon(True)
                thread.start()
        delay = 0.01
        if not self.game_over:
            self.auto = not self.auto
            run_help()

    def search_best_way(self, array):
        def score_ways(array, skey, ways, depth):
            possible_ways[skey][1] += ways[1] ** 2 * (depth + 1)
            if depth > 0:
                temp = copy.deepcopy(array)
                self.merge_array(temp, ways[0])
                self.shift_array(temp, ways[2])
                possible_ways[skey][1] += ways[1] + len(self.find_blank(temp))
                # self.add_rand_num(temp)
                subways = []
                for key in self.key_bindings:
                    way = self.search_key_ways(temp, key)
                    if way is not None:
                        subways.append(way)
                if subways:
                    best_subway = max(subways, key=lambda x: x[1])
                    if best_subway[1] != 0:
                        score_ways(temp, skey, best_subway, depth - 1)
                    else:
                        for subway in subways:
                            score_ways(temp, skey, subway, depth - 1)

        possible_ways = {}
        for key in self.key_bindings:
            ways = self.search_key_ways(array, key)
            if ways is not None:
                possible_ways.update({key: [ways, 0]})
                score_ways(array, key, ways, 4)
        if possible_ways:
            mk = max(possible_ways, key=lambda k: possible_ways[k][1])
            return possible_ways[mk][0]
        return None


Game2048(7)
