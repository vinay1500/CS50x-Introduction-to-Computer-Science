#include <cs50.h>
#include <stdio.h>

void pyramid(int spaces, int bricks);

int main(void)
{
    int n;
    do
    {
        n = get_int("Height: ");
    }while(n<0 || n>9);

    for (int i = 0; i<n; i++)
    {
        pyramid(n-(i+1),i+1);
    }

}

void pyramid(int spaces, int bricks)
{
    for (int i=spaces; i>0; i--)
    {
        printf(" ");
    }
    for (int j= 0; j< bricks; j++)
    {
        printf("#");
    }
    printf("  ");
    for (int k = 0; k < bricks; k++)
    {
        printf("#");
    }
    printf("\n");
}
