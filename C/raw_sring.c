#include <stdio.h>
#include <string.h>


const char *s = R"("123")";

int main()
{
    printf("%s\n", s);
    printf("%d\n", strlen(s));
    return 0;
}
