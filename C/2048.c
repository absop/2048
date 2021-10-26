#include <conio.h>
#include <stdio.h>
#include <stdlib.h>
#include <time.h>
#include <windows.h>

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

typedef struct Direc Direc;
typedef struct Matrix Matrix;
typedef int Grids[4][4];

struct Direc {
    int score;
    int ngrid;
    int movable;
    Grids cache;
    int (*check)(Matrix *);
    char *bufptr;
    char buffer[1024];
};

struct Matrix {
    int score;
    int ngrid;
    char *bufptr;
    Grids grids;
    Direc direcs[4];
};

void random_add42(Matrix *m)
{
    int randnum, randxy;
    randnum = (rand() % 100) >= 80 ? 4 : 2;
    randxy = rand();
#if 0
    printf("randxy = %d\n", randxy);
#endif
    randxy %= m->ngrid;
    m->ngrid -= 1;
    int i, j, igrid = 0;
    for (i = 0; i < 4; ++i) {
        for (j = 0; j < 4; ++j) {
            if (m->grids[i][j] == 0) {
                // the i-th blank grid
                if (igrid == randxy) {
                    m->grids[i][j] = randnum;
                    return;
                }
                igrid++;
            }
        }
    }
}

#define MAKE_CHECK(key, inc, begin, end, x1, y1, x2, y2)            \
int check##key(Matrix *m)                                           \
{                                                                   \
    Direc *direc = &m->direcs[key];                                 \
    char *bufptr = direc->bufptr;                                   \
    int i, j, k, (*cache)[4] = direc->cache;                        \
    int ngrid = 0, score = 0, movable = 0;                          \
    memcpy(cache, m->grids, sizeof m->grids);                       \
    for (i = 0; i < 4; ++i) {                                       \
        for (j = k = begin; j != end; inc j) {                      \
            if (j == k || cache[x2][y2] == 0)                       \
                continue;                                           \
            if (cache[x1][y1] == cache[x2][y2]) {                   \
                cache[x1][y1] <<= 1;                                \
                score += cache[x1][y1];                             \
                bufptr += sprintf(bufptr,                           \
                    "Morge: (%d, %d)->(%d, %d)\n",                  \
                    (x2 + 1), (y2 + 1), (x1 + 1), (y1 + 1));        \
                ngrid++;                                            \
                inc k;                                              \
            }                                                       \
            else {                                                  \
                if (cache[x1][y1]) {                                \
                    if (inc k == j)                                 \
                        continue;                                   \
                }                                                   \
                cache[x1][y1] = cache[x2][y2];                      \
                bufptr += sprintf(bufptr,                           \
                    " Move: (%d, %d)->(%d, %d)\n",                  \
                    (x2 + 1), (y2 + 1), (x1 + 1), (y1 + 1));        \
            }                                                       \
            cache[x2][y2] = 0;                                      \
            movable = 1;                                            \
        }                                                           \
    }                                                               \
    direc->ngrid = ngrid;                                           \
    direc->score = score;                                           \
    direc->movable = movable;                                       \
    return movable;                                                 \
}

MAKE_CHECK(0, ++, 0, +4, k, i, j, i)
MAKE_CHECK(1, --, 3, -1, k, i, j, i)
MAKE_CHECK(2, ++, 0, +4, i, k, i, j)
MAKE_CHECK(3, --, 3, -1, i, k, i, j)

static int isalive(Matrix *m)
{
    int movable = 0;
    for (int i = 0; i < 4; ++i) {
        m->direcs[i].bufptr[0] = 0;
        if (m->direcs[i].check(m))
            movable = 1;
    }
    return movable || (m->ngrid > 0);
}

int move(Matrix *m, char key)
{
    Direc *direc = &m->direcs[key];
    memcpy(m->grids, direc->cache, sizeof m->grids);
    m->ngrid += direc->ngrid;
    m->score += direc->score;
    m->bufptr = direc->buffer;
    return direc->movable;
}

#define BOUND "  +-------------+-------------+-------------+-------------+\n"
#define BLANK "  |             |             |             |             |\n"

void show_grids(Matrix *m)
{
    char buffer[4096], *ptr = buffer;
    for (int i = 0; i < 4; ++i) {
        ptr += sprintf(ptr, BOUND BLANK BLANK "  ");
        for (int j = 0; j < 4; ++j) {
            if (m->grids[i][j])
                ptr += sprintf(ptr, "|  %7d    ", m->grids[i][j]);
            else
                ptr += sprintf(ptr, "|             ");
        }
        ptr += sprintf(ptr, "|\n" BLANK BLANK);
    }
    ptr += sprintf(ptr, BOUND);
    ptr += sprintf(ptr, "grids: %d\n", m->ngrid);
    ptr += sprintf(ptr, "score: %d\n", m->score);
    if (m->bufptr)
        sprintf(ptr, "%s\n", m->bufptr);
    puts(title_card_2048);
    puts(buffer);
}

char convkey(char key)
{
    if (key == 72) return 0;
    if (key == 80) return 1;
    if (key == 75) return 2;
    if (key == 77) return 3;
    if (key == 0x1B) return -1;
    return -2;  // for unknown key
}

Matrix *new_matrix()
{
    Matrix *m = (Matrix *)malloc(sizeof(Matrix));
    int (*checks[4])(Matrix*) = {check0, check1, check2, check3};
    char *keystrs[4] = {"Up", "Down", "Left", "Right"};
    m->ngrid = 16;
    m->score = 0;
    m->bufptr = 0;
    Direc *direc;
    memset(m->grids, 0, sizeof m->grids);
    for (int i = 0; i < 4; ++i) {
        direc = &m->direcs[i];
        direc->bufptr = direc->buffer;
        direc->bufptr += sprintf(direc->bufptr, "direction: %s\n", keystrs[i]);
        direc->check = checks[i];
    }
    random_add42(m);
    return m;
}

int main()
{
    char key, moved;
    CONSOLE_CURSOR_INFO cci;
    cci.bVisible = 0;
    cci.dwSize = 1;
    SetConsoleCursorInfo(GetStdHandle(STD_OUTPUT_HANDLE), &cci);

    srand((unsigned)time(NULL));

    Matrix *m = new_matrix();
    show_grids(m);
    for (; isalive(m);) {
        key = convkey(_getch());
        if (key == -1) {
            printf("exit...\n");
            break;
        }
        if (key == -2) continue;
        Sleep(50);
        system("cls");
        moved = move(m, key);
        if (moved) random_add42(m);
        show_grids(m);
    }
    printf("%s\n", "Game over!");
    free(m);

    return 0;
}
