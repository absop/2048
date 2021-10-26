/* * File : myRetroSnaker.cpp * Author : weixinhum * Date : 2017.5.16 * Function : Snake game of overcoming the splash screen */

#include <stdio.h>
#include <stdlib.h>
#include <Windows.h>
#define LENGTH 15

HANDLE hOutput, hOutBuf;//控制台屏幕缓冲区句柄
COORD coord = { 0, 0 };
//双缓冲处理显示
DWORD bytes = 0;
char data[LENGTH][LENGTH];

void show()
{
    int i, j;
    for (i = 0; i < LENGTH; i++) {
        for (j = 0; j < LENGTH; j++)
            data[i][j] = '*';
    }
    for (i = 0; i < LENGTH; i++) {
        coord.Y = i;
        WriteConsoleOutputCharacterA(hOutBuf, data[i], LENGTH, coord, &bytes);
    }
    //设置新的缓冲区为活动显示缓冲
    SetConsoleActiveScreenBuffer(hOutBuf);
    Sleep(500);
    for (i = 0; i < LENGTH; i++) {
        for (j = 0; j < LENGTH; j++)
            data[i][j] = '-';
    }
    for (i = 0; i < LENGTH; i++) {
        coord.Y = i;
        WriteConsoleOutputCharacterA(hOutput, data[i], LENGTH, coord, &bytes);
    }
    //设置新的缓冲区为活动显示缓冲
    SetConsoleActiveScreenBuffer(hOutput);
    Sleep(500);
}

void main()
{
    //创建新的控制台缓冲区
    hOutBuf = CreateConsoleScreenBuffer(
                  GENERIC_WRITE,//定义进程可以往缓冲区写数据
                  FILE_SHARE_WRITE,//定义缓冲区可共享写权限
                  NULL,
                  CONSOLE_TEXTMODE_BUFFER,
                  NULL
              );
    hOutput = CreateConsoleScreenBuffer(
                  GENERIC_WRITE,//定义进程可以往缓冲区写数据
                  FILE_SHARE_WRITE,//定义缓冲区可共享写权限
                  NULL,
                  CONSOLE_TEXTMODE_BUFFER,
                  NULL
              );
    //隐藏两个缓冲区的光标
    CONSOLE_CURSOR_INFO cci;
    cci.bVisible = 0;
    cci.dwSize = 1;
    SetConsoleCursorInfo(hOutput, &cci);
    SetConsoleCursorInfo(hOutBuf, &cci);

    while (1)
        show();
}
