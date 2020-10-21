import json
import time
import threading
from random import randint

import wx
from wx import Point, FontInfo, Font


class Score():
    def __init__(self):
        self.current = 0
        self.highest = 0

    def increase(self, delta):
        self.current += delta
        self.highest = max(self.current, self.highest)


class Grid():
    def __init__(self):
        self.score = Score()
        self.reset()

    def reset(self):
        self.cells = [[0 for j in range(4)] for i in range(4)]
        self.ncell = 16
        self.maxnum = 0
        self.score.current = 0
        self.add_randnum()

    def save(self, record):
        data = {
            "time": time.strftime("%Y%m%d %H:%M:%S"),
            "cells": self.cells,
            "score": {
                "highest": self.score.highest,
                "current": self.score.current
            }
        }
        with open(record, "w+") as file:
            json.dump(data, file)

    def load(self, record):
        try:
            with open(record, "r") as file:
                data = json.load(file)
                self.cells = data["cells"]
                self.score.highest = data["score"]["highest"]
                self.score.current = data["score"]["current"]
                self.ncell = len([i for r in self.cells for i in r if i == 0])
                self.maxnum = max(max(self.cells))
        except:
            self.reset()
            self.score.highest = 0

    def add_randnum(self):
        # 控制数字2和4的概率,此时2出现概率是80%
        randidx = randint(0, 100) % self.ncell
        randnum = (2, 4)[randint(1, 100) // 80]
        self.maxnum = max(randnum, self.maxnum)

        count = 0
        for i in range(4):
            for j in range(4):
                if self.cells[i][j] == 0:
                    if count == randidx:
                        self.cells[i][j] = randnum
                        self.ncell -= 1
                        return (i, j)
                    count += 1

    def movable(self):
        if self.ncell > 0:
            return True
        for i in range(4):
            for j in range(1, 4):
                if (self.cells[i][j - 1] == self.cells[i][j] or
                    self.cells[j - 1][i] == self.cells[j][i]):
                    return True
        return False


def genmove(inc, begin, end, index):
    def move(grid):
        cells = grid.cells
        ncell, score, moved = 0, 0, 0
        for i in range(4):
            k = begin
            for j in range(begin, end, inc(0) - 0):
                x1, y1 = index(i, k)
                x2, y2 = index(i, j)
                if j == k or cells[x2][y2] == 0:
                    continue
                if cells[x1][y1] == cells[x2][y2]:
                    cells[x1][y1] <<= 1
                    grid.maxnum = max(cells[x1][y1], grid.maxnum)
                    score += cells[x1][y1]
                    ncell += 1
                    k = inc(k)
                else:
                    if cells[x1][y1]:
                        k = inc(k)
                        if k == j:
                            continue
                    x1, y1 = index(i, k)
                    cells[x1][y1] = cells[x2][y2]

                cells[x2][y2] = 0
                moved = 1

        if score > 0:
            grid.ncell += ncell
            grid.score.increase(score)
            return score

        return moved

    return move


class Board():
    def __init__(self):
        self.grid = Grid()
        self.moves = {
            "↑": genmove(lambda n: n + 1, 0, +4, lambda x, y: (y, x)),
            "↓": genmove(lambda n: n - 1, 3, -1, lambda x, y: (y, x)),
            "←": genmove(lambda n: n + 1, 0, +4, lambda x, y: (x, y)),
            "→": genmove(lambda n: n - 1, 3, -1, lambda x, y: (x, y))
        }
        self.backgrounds = [
            wx.Colour("#C9C9C9"), wx.Colour("#D3D385"),
            wx.Colour("#E8BE8B"), wx.Colour("#F4A460"),
            wx.Colour("#F48D4A"), wx.Colour("#FF7F50"),
            wx.Colour("#F5725B"), wx.Colour("#F86048"),
            wx.Colour("#D85C4c"), wx.Colour("#CD5C5C"),
            wx.Colour("#C9413C"), wx.Colour("#B53835"),
            wx.Colour("#A52A2A"), wx.Colour("#A13A3A"),
            wx.Colour("#B4122A"), wx.Colour("#B02031")
        ]

    def best(self):
        return self.grid.score.highest

    def score(self):
        return self.grid.score.current

    def add_randnum(self):
        if self.grid.ncell > 0:
            self.grid.add_randnum()

    def background(self, x, y):
        i = 0
        while (1 << i) < self.grid.cells[x][y]:
            i += 1
        return self.backgrounds[i]

    def move(self, direction):
        return self.moves[direction](self.grid)

    def isalive(self):
        return self.grid.movable()

    def iswon(self):
        return self.grid.maxnum >= 2048

    def DrawCells(self, dc):
        for row in range(4):
            for col in range(4):
                rect = wx.Rect(col * 120, row * 120, 120, 120)
                dc.SetBrush(wx.Brush(self.background(row, col)))
                dc.DrawRoundedRectangle(rect, 10.0)
                if self.grid.cells[row][col]:
                    number = "%d" % self.grid.cells[row][col]
                    dc.SetFont(Font(FontInfo([16, 20][len(number) < 5])))
                    dc.DrawLabel(number, rect, wx.ALIGN_CENTER)


class Tabbar():
    def __init__(self):
        self.boundary = wx.Rect(Point(0, 0), Point(480, 100))
        self.score_caption = wx.Rect(Point(8, 0), Point(120, 50))
        self.score_content = wx.Rect(Point(8, 50), Point(120, 100))
        self.best_caption = wx.Rect(Point(120, 0), Point(240, 50))
        self.best_content = wx.Rect(Point(120, 50), Point(240, 100))
        self.arrow_caption = wx.Rect(Point(240, 0), Point(360, 50))
        self.arrow_content = wx.Rect(Point(240, 50), Point(360, 100))
        self.title_name_color = wx.Colour("#FF5370")
        self.title_value_color = wx.Colour("#7C4DFF")

    def DrawTabs(self, dc, score, best, arrow):
        dc.DrawRoundedRectangle(self.boundary, 8.0)

        dc.SetFont(Font(FontInfo(20).Bold(2)))
        dc.SetTextForeground(self.title_name_color)
        dc.DrawLabel("SCORE", self.score_caption, wx.ALIGN_CENTER)
        dc.DrawLabel("BEST", self.best_caption, wx.ALIGN_CENTER)
        dc.DrawLabel("KEY", self.arrow_caption, wx.ALIGN_CENTER)

        dc.SetFont(Font(FontInfo(16).Bold(2)))
        dc.SetTextForeground(self.title_value_color)
        dc.DrawLabel(score, self.score_content, wx.ALIGN_CENTER)
        dc.DrawLabel(best, self.best_content, wx.ALIGN_CENTER)
        dc.DrawLabel(arrow, self.arrow_content, wx.ALIGN_CENTER)



class GameFrame(wx.Frame):
    def __init__(self, parent, title):
        super(GameFrame, self).__init__(parent,
            title=title,
            size=wx.Size(480+20, 640+20),
            style=wx.DEFAULT_FRAME_STYLE ^ wx.MAXIMIZE_BOX ^ wx.RESIZE_BORDER)

        self.arrow = ""
        self.background = wx.Colour("#FAFAFA")
        self.tabbar = Tabbar()
        self.board = Board()
        self.directions = {
            wx.WXK_UP:    "↑",
            wx.WXK_DOWN:  "↓",
            wx.WXK_LEFT:  "←",
            wx.WXK_RIGHT: "→"
        }

        self.SetIcons(wx.IconBundle(wx.Icon("2048.ico")))

        self.SetTransparent(235)
        self.CentreOnScreen()
        self.SetBackgroundColour(self.background)
        self.CreateStatusBar()
        self.SetStatusText("Welcome to Game 2048!")

        self.Bind(wx.EVT_PAINT, self.OnPaint)
        self.Bind(wx.EVT_KEY_DOWN, self.OnKeyDown)

        self.GameStart()

    def OnPaint(self, event):
        dc = wx.BufferedPaintDC(self)
        dc.Clear()

        score = "%d" % self.board.score()
        best = "%d" % self.board.best()

        dc.SetPen(wx.Pen(self.background, 4))
        dc.SetBrush(wx.Brush(wx.Colour("#EEE4DA")))

        dc.SetDeviceOrigin(7, 0)
        self.tabbar.DrawTabs(dc, score, best, self.arrow)

        dc.SetTextForeground(self.background)
        dc.SetDeviceOrigin(7, 100)
        self.board.DrawCells(dc)

    def OnKeyDown(self, event):
        code = event.GetKeyCode()
        if code in self.directions:
            self.arrow = self.directions[code]
            if not self.gameover:
                moved = self.board.move(self.arrow)
                if moved:
                    status = ""
                    if moved > 1:
                        status += "+%d" % moved
                        if self.board.iswon():
                            self.GameWon()
                    self.SetStatusText(status)

                    self.board.add_randnum()
                    if not self.board.isalive():
                        self.GameOver()

                    self.Refresh()

        elif code == wx.WXK_F5:
            self.GameRestart()

    def setup(self):
        self.LoadRecord()
        if (self.board.isalive()):
            self.GameStart()
        else:
            self.GameOver()
        self.Show()

    def GameRestart(self):
        self.board.grid.reset()
        self.GameStart()
        self.Refresh()

    def GameStart(self):
        self.gameover = False

    def GameOver(self):
        self.gameover = True
        self.SetStatusText("Game Over!\tPress F5 to restart")
        if (not self.board.iswon()):
            self.GameFailed()

    def LoadRecord(self):
        self.board.grid.load(".RECORD")

    def SaveRecord(self):
        self.board.grid.save(".RECORD")

    def GameWon(self):
        pass

    def GameFailed(self):
        pass



class Game(wx.App):
    def __init__(self):
        super(Game, self).__init__()
        self.game = GameFrame(None, "2048")
        self.game.setup()

    def OnExit(self):
        self.game.SaveRecord()
        return 0


if __name__ == "__main__":
    app = Game()
    app.MainLoop()

