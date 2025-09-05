#include <cs50.h>
#include <stdio.h>

int calculate_quarters(int change);
int calculate_dimes(int change);
int calculate_nickels(int change);

int main(void)
{
    int change;
    do
    {
        change = get_int("Change owed: ");
    }while(change<0);

    int quarters = calculate_quarters(change);

    change = change - (quarters * 25);


    int dimes = calculate_dimes(change);

    change = change - (dimes * 10);


    int nickels = calculate_nickels(change);

    change = change - (nickels * 5);


    int pennies = change;

    change = quarters + dimes + nickels + pennies;
    printf("%i\n",change);
}

int calculate_quarters(int change)
{
    int quarters = 0;
    while (change >= 25)
    {
        quarters++;
        change = change - 25;
    }
    return quarters;
}

int calculate_dimes(int change)
{
    int dimes = 0;
    while (change >= 10)
    {
        dimes++;
        change = change - 10;
    }
    return dimes;
}

int calculate_nickels(int change)
{
    int nickels = 0;
    while (change >= 5)
    {
        nickels++;
        change = change - 5;
    }
    return nickels;
}
