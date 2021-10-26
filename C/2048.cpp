#include <iostream>
#include <vector>
#include <random>
#include <cstdlib>
#include <ctime>
#include <conio.h>
#include <windows.h>

const char *coord_pair = "Merge: (%d, %d)-(%d, %d)\n";
const char *title_card_2048 = R"(
   /\\\\\\\\\          /\\\\\\\                /\\\         /\\\\\\\\\
  /\\\///////\\\      /\\\/////\\\            /\\\\\       /\\\///////\\\
  \///      \//\\\    /\\\    \//\\\         /\\\/\\\      \/\\\     \/\\\
             /\\\/    \/\\\     \/\\\       /\\\/\/\\\      \///\\\\\\\\\/
           /\\\//      \/\\\     \/\\\     /\\\/  \/\\\       /\\\///////\\\
         /\\\//         \/\\\     \/\\\   /\\\\\\\\\\\\\\\\   /\\\      \//\\\
        /\\\/            \//\\\    /\\\   \///////////\\\//   \//\\\      /\\\
        /\\\\\\\\\\\\\\\   \///\\\\\\\/              \/\\\      \///\\\\\\\\\/
        \///////////////      \///////                \///         \/////////
)";

class Matrix {
  private:
    int score = 0;
    int ngrid = 16;
    int grids[4][4] = {0};
    char *bufptr;
    const char *direc = nullptr;

    inline void bubble_ud(int b, int e, int d) {
        int i, j, k;
        for (i = 0; i < 4; ++i) {
            for (j = k = b; j != e; j += d) {
                if (grids[j][i] != 0) {
                    if (k != j) {
                        grids[k][i] = grids[j][i];
                        grids[j][i] = 0;
                    }
                    k += d;
                }
            }
        }
    }

    inline void bubble_lr(int b, int e, int d) {
        int i, j, k;
        for (i = 0; i < 4; ++i) {
            for (j = k = b; j != e; j += d) {
                if (grids[i][j] != 0) {
                    if (k != j) {
                        grids[i][k] = grids[i][j];
                        grids[i][j] = 0;
                    }
                    k += d;
                }
            }
        }
    }

    inline void merge_ud(int b, int e, int d) {
        int i, j, k;
        for (i = 0; i < 4; ++i) {
            for (j = k = b; j != e; j += d) {
                if (k == j) continue;
                if (grids[j][i] != 0) {
                    if (grids[k][i] == grids[j][i]) {
                        grids[k][i] <<= 1;
                        score += grids[k][i];
                        bufptr += sprintf(bufptr, coord_pair, k, i, j, i);
                        k += d;
                        ngrid += 1;
                    }
                    else {
                        if (grids[k][i] != 0) {
                            k += d;
                            if (k == j) continue;
                        }
                        grids[k][i] = grids[j][i];
                    }
                    grids[j][i] = 0;
                }
            }
        }
    }

    inline void merge_lr(int b, int e, int d) {
        int i, j, k;
        for (i = 0; i < 4; ++i) {
            for (j = k = b; j != e; j += d) {
                if (k == j) continue;
                if (grids[i][j] != 0) {
                    if (grids[i][k] == grids[i][j]) {
                        grids[i][k] <<= 1;
                        score += grids[i][k];
                        bufptr += sprintf(bufptr, coord_pair, i, k, i, j);
                        k += d;
                        ngrid += 1;
                    }
                    else {
                        if (grids[i][k] != 0) {
                            k += d;
                            if (k == j) continue;
                        }
                        grids[i][k] = grids[i][j];
                    }
                    grids[i][j] = 0;
                }
            }
        }
    }

  public:
    Matrix() {
        add42();
    }

    int isalive() {
        return ngrid > 0;
    }

    void bubble(char dir) {
        if (dir == 'U') { bubble_ud(0, 4, 1); return; }
        if (dir == 'L') { bubble_lr(0, 4, 1); return; }
        if (dir == 'D') { bubble_ud(3, -1, -1); return; }
        if (dir == 'R') { bubble_lr(3, -1, -1); return; }
    }
    void transform(char dir, char *buffer) {
        direc = dir == 'U' ? "Up" :
                dir == 'D' ? "Down" :
                dir == 'L' ? "Left" : "Right";
        bufptr = buffer;
        if (dir == 'U') { merge_ud(0, 4, 1); return; }
        if (dir == 'L') { merge_lr(0, 4, 1); return; }
        if (dir == 'D') { merge_ud(3, -1, -1); return; }
        if (dir == 'R') { merge_lr(3, -1, -1); return; }
    }

    void add42();
    void show();
    ~Matrix() {};
};


void Matrix::add42()
{
    int randnum, randxy;
    // srand((unsigned)time(NULL));
    randnum = (rand() % 100) >= 80 ? 4 : 2;
    randxy = rand();
#if 0
    printf("randxy = %d\n", randxy);
#endif
    randxy %= ngrid;
    ngrid -= 1;
    int i, j, igrid = 0;
    for (i = 0; i < 4; ++i) {
        for (j = 0; j < 4; ++j) {
            if (grids[i][j] == 0) {
                // the i-th blank grid
                if (igrid == randxy) {
                    grids[i][j] = randnum;
                    return;
                }
                igrid++;
            }
        }
    }
}

#define BOUNDARIES "+---------+---------+---------+---------+\n"
#define WHITESPACE "|         |         |         |         |\n"

void Matrix::show()
{
    char buffer[1024], *ptr = buffer;
    for (int i = 0; i < 4; ++i) {
        ptr += sprintf(ptr, BOUNDARIES WHITESPACE);
        for (int j = 0; j < 4; ++j) {
            if (grids[i][j])
                ptr += sprintf(ptr, "|  %5d  ", grids[i][j]);
            else
                ptr += sprintf(ptr, "|         ");
        }
        ptr += sprintf(ptr, "|\n" WHITESPACE);
    }
    sprintf(ptr, BOUNDARIES);
    puts(title_card_2048);
    puts(buffer);
    printf("grids: %d\n", ngrid);
    printf("score: %d\n", score);
    if (direc)
        printf("direction: %s\n", direc);

}


char gettask(char key)
{
    if (key == 72) return 'U';
    if (key == 80) return 'D';
    if (key == 75) return 'L';
    if (key == 77) return 'R';
    if (key == 0x1B) return 0;
    return 1;
}


int main()
{
    char key;
    char buffer[2048];
    CONSOLE_CURSOR_INFO cci;
    cci.bVisible = 0;
    cci.dwSize = 1;
    SetConsoleCursorInfo(GetStdHandle(STD_OUTPUT_HANDLE), &cci);

    Matrix m = Matrix();
    m.show();
    for (;;) {
        key = gettask(_getch());
        if (key == 0) break;
        if (key == 1) continue;
        Sleep(50);
        system("cls");
        buffer[0] = 0;
        m.transform(key, buffer);
        if (m.isalive()) {
            m.add42();
            m.show();
            printf("%s\n", buffer);
        }
        else {
            printf("%s\n", "Game over!");
            return 0;
        }
    }

    return 0;
}
