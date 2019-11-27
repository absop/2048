#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>
#include <wx/wxprec.h>
#ifndef WX_PRECOMP
#include <wx/wx.h>
#endif
#include <wx/dcbuffer.h>
#include "2048.xpm"


typedef struct Grid Grid;
typedef int Cells[4][4];
typedef int (*Move)(Grid *);
typedef struct Score {
    int current;
    int highest;
    void increase(int delta) {
        current += delta;
        if (current > highest)
            highest = current;
    }
} Score;

struct Grid {
    int maxnum;
    int ncell;
    Score score;
    Cells cells;

    bool movable() { return ncell > 0 || movable(cells); }
    bool movable(Cells cells) {
        for (int i = 0; i < 4; ++i) {
            for (int j = 1; j < 4; ++j) {
                // unnecessary judgement for number 0,
                // cause we have known that ncell == 0
                if (cells[i][j - 1] == 0 || cells[i][j] == 0 ||
                    cells[i][j - 1] == cells[i][j])
                    return true;
                if (cells[j - 1][i] == 0 || cells[j][i] == 0 ||
                    cells[j - 1][i] == cells[j][i])
                    return true;
            }
        }
        return false;
    }

    int add_random() {
        int randnum, randxy;
        randnum = (rand() % 100) >= 80 ? 4 : 2;
        randxy = rand() % ncell;
        ncell -= 1;
        if (randnum > maxnum) maxnum = randnum;
        int i, j, icell = 0;
        for (i = 0; i < 4; ++i) {
            for (j = 0; j < 4; ++j) {
                if (cells[i][j] == 0) {
                    // the i-th blank cell
                    if (icell == randxy) {
                        cells[i][j] = randnum;
                        return icell;
                    }
                    icell++;
                }
            }
        }
        return -1;
    }
};


#define MAKE_MOVE(key, inc, begin, end, x1, y1, x2, y2) \
    int move##key(Grid *grid)                           \
    {                                                   \
        int moved = 0, score = 0, ncell = 0;            \
        int i, j, k, (*cells)[4] = grid->cells;         \
        for (i = 0; i < 4; ++i) {                       \
            for (j = k = begin; j != end; inc j) {      \
                if (j == k || cells[x2][y2] == 0)       \
                    continue;                           \
                if (cells[x1][y1] == cells[x2][y2]) {   \
                    cells[x1][y1] <<= 1;                \
                    if (cells[x1][y1] > grid->maxnum)   \
                        grid->maxnum = cells[x1][y1];   \
                    score += cells[x1][y1];             \
                    ncell++;                            \
                    inc k;                              \
                }                                       \
                else {                                  \
                    if (cells[x1][y1] && inc k == j)    \
                        continue;                       \
                    cells[x1][y1] = cells[x2][y2];      \
                }                                       \
                cells[x2][y2] = 0;                      \
                moved = 1;                              \
            }                                           \
        }                                               \
        if (score > 0) {                                \
            grid->ncell += ncell;                       \
            grid->score.increase(score);                \
            return score;                               \
        }                                               \
        return moved;                                   \
    }

MAKE_MOVE(0, ++, 0, +4, k, i, j, i) // Up
MAKE_MOVE(1, --, 3, -1, k, i, j, i) // Down
MAKE_MOVE(2, ++, 0, +4, i, k, i, j) // Left
MAKE_MOVE(3, --, 3, -1, i, k, i, j) // Right


class Board {
  private:
    Grid grid;
    Move moves[4] = { move0, move1, move2, move3 };
    wxColour backgrounds[16] = {
        wxColour("#EEE4DA"), wxColour("#EFD385"),
        wxColour("#E8BE8B"), wxColour("#F4A460"),
        wxColour("#F48D4A"), wxColour("#FF7F50"),
        wxColour("#F5725B"), wxColour("#F86048"),
        wxColour("#D85C4c"), wxColour("#CD5C5C"),
        wxColour("#C9413C"), wxColour("#B53835"),
        wxColour("#A52A2A"), wxColour("#A13A3A"),
        wxColour("#B4122A"), wxColour("#B02031")
    };

  public:
    Board() { grid.score.highest = 0; reset(); }
    ~Board() {}

    int best() { return grid.score.highest; }
    int score() { return grid.score.current; }
    int ncell() { return grid.ncell; }
    int move(int key) { return (moves[key])(&grid); }
    int add_random() { return grid.ncell > 0 ? grid.add_random() : -1; }
    bool isalive() { return grid.movable(); }
    bool iswon() { return grid.maxnum >= 2048; }

    void reset() {
        grid.maxnum = 0;
        grid.ncell = 16;
        grid.score.current = 0;
        memset(grid.cells, 0, sizeof (Cells));
        add_random();
    }

    void save(const char *record) {
        FILE *pf = fopen(record, "wb+");
        if (!pf) return;
        fwrite(&grid, sizeof (Grid), 1, pf);
        fclose(pf);
    }

    void load(const char *record) {
        FILE *pf = fopen(record, "rb");
        if (!pf) return;
        fseek(pf, 0L, SEEK_END);
        if (ftell(pf) == sizeof (Grid)) {
            rewind(pf);
            fread(&grid, sizeof (Grid), 1, pf);
        }
        fclose(pf);
    }

    wxColour GetCellBackground(int row, int col) {
        int i = 0;
        while ((1 << i) < grid.cells[row][col])
            ++i;
        return backgrounds[i];
    }

    void DrawCells(wxBufferedPaintDC &dc) {
        for (int row = 0; row < 4; ++row) {
            for (int col = 0; col < 4; ++col) {
                wxRect rect(col * 120, row * 120, 120, 120);
                dc.SetBrush(GetCellBackground(row, col));
                dc.DrawRoundedRectangle(rect, 10.0);

                if (grid.cells[row][col]) {
                    wxString number;
                    number << grid.cells[row][col];
                    dc.SetFont(wxFontInfo(number.Length() < 5 ? 20 : 16));
                    dc.DrawLabel(number, rect, wxALIGN_CENTER);
                }
            }
        }
    }
};


class TabBar {
  private:
    wxRect boundary = wxRect(wxPoint(0, 0), wxPoint(480, 100));
    wxRect score_caption = wxRect(wxPoint(8, 0), wxPoint(120, 50));
    wxRect score_content = wxRect(wxPoint(8, 50), wxPoint(120, 100));
    wxRect best_caption = wxRect(wxPoint(120, 0), wxPoint(240, 50));
    wxRect best_content = wxRect(wxPoint(120, 50), wxPoint(240, 100));
    wxRect arrow_caption = wxRect(wxPoint(240, 0), wxPoint(360, 50));
    wxRect arrow_content = wxRect(wxPoint(240, 50), wxPoint(360, 100));
    wxColour title_name_color = wxColour("#FF5370");
    wxColour title_value_color = wxColour("#7C4DFF");

  public:
    TabBar() {};
    ~TabBar() {};

    void DrawTabs(wxBufferedPaintDC &dc,
                  wxString &score, wxString &best, wxString &arrow) {
        dc.DrawRoundedRectangle(boundary, 8.0);

        dc.SetFont(wxFontInfo(20).Bold(2));
        dc.SetTextForeground(title_name_color);
        dc.DrawLabel("SCORE", score_caption, wxALIGN_CENTER);
        dc.DrawLabel("BEST", best_caption, wxALIGN_CENTER);
        dc.DrawLabel("KEY", arrow_caption, wxALIGN_CENTER);

        dc.SetFont(wxFontInfo(16).Bold(2));
        dc.SetTextForeground(title_value_color);
        dc.DrawLabel(score, score_content, wxALIGN_CENTER);
        dc.DrawLabel(best, best_content, wxALIGN_CENTER);
        dc.DrawLabel(arrow, arrow_content, wxALIGN_CENTER);
    }
};


class GameWindow : public wxFrame {
  private:
    bool gameover = false;
    wxString arrow;
    wxColour background = wxColour("#FAFAFA");

    TabBar tabbar = TabBar();
    Board board = Board();

  public:
    GameWindow() : wxFrame(
            NULL, wxID_ANY, "2048",
            wxDefaultPosition, wxSize(480 + 20, 640 + 20),
            wxDEFAULT_FRAME_STYLE ^ wxMAXIMIZE_BOX ^ wxRESIZE_BORDER) {

        SetIcons(wxIconBundle(wxIcon(xpm2048)));

        SetTransparent(235);
        CentreOnScreen();
        SetBackgroundColour(background);
        CreateStatusBar();
        SetStatusText("Welcome to Game 2048!");

        Bind(wxEVT_PAINT, &OnPaint, this);
        Bind(wxEVT_KEY_DOWN, &OnKeyDown, this);
    }

    void OnPaint( wxPaintEvent &event ) {
        wxBufferedPaintDC dc(this);
        dc.Clear();

        wxString score, best;
        best << board.best();
        score << board.score();

        dc.SetPen(wxPen(background, 4));
        dc.SetBrush(wxColour("#EEE4DA"));

        dc.SetDeviceOrigin(7, 0);
        tabbar.DrawTabs(dc, score, best, arrow);

        dc.SetTextForeground(background);
        dc.SetDeviceOrigin(7, 100);
        board.DrawCells(dc);
    }

    void OnKeyDown( wxKeyEvent &event ) {
        int kcode = -1;
        switch (event.GetKeyCode()) {
            case WXK_UP:
            case 'w':
                arrow = wxT("↑");
                kcode = 0;
                break;
            case WXK_DOWN:
            case 's':
                arrow = wxT("↓");
                kcode = 1;
                break;
            case WXK_LEFT:
            case 'a':
                arrow = wxT("←");
                kcode = 2;
                break;
            case WXK_RIGHT:
            case 'd':
                arrow = wxT("→");
                kcode = 3;
                break;
            case WXK_F5:
                GameResart();
                return;

            default: ;
        }
        if (gameover) return;
        if (0 <= kcode && kcode <= 3) {
            int moved = board.move(kcode);
            if (moved) {
                wxString status;
                if (moved > 1) {
                    status << "+" << moved;
                    if (board.iswon()) {
                        GameWon();
                    }
                }
                SetStatusText(status);

                board.add_random();
                if (!board.isalive())
                    GameOver();

                Refresh();
            }
        }
    }
    void Setup() {
        LoadRecord();
        if (!board.isalive())
            GameOver();
        else
            GameStart();
        Show(true);
    }
    void GameWon() {}
    void GameFailed() {}
    void GameResart() {
        board.reset();
        GameStart();
        Refresh();
    }
    void GameStart() {
        // printf("GameStart: ncell(%d)\n", board.ncell());
        gameover = false;
        srand((unsigned)time(NULL));
    }
    void GameOver() {
        gameover = true;
        // printf("GameOver: score(%d)\n", board.score());
        SetStatusText(wxString("Game Over!\tPress F5 to restart"));
        if (!board.iswon()) {
            GameFailed();
        }
    }
    void SaveRecord() { board.save("RECORD"); }
    void LoadRecord() { board.load("RECORD"); }
};


class wx2048 : public wxApp {
  private:
    GameWindow *game;
  public:
    virtual bool OnInit() {
        game = new GameWindow();
        game->Setup();
        return true;
    }

    virtual int OnExit() {
        game->SaveRecord();
        return 0;
    }

};

wxIMPLEMENT_APP(wx2048);
