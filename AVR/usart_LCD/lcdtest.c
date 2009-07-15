/*
 * =====================================================================================
 *
 *       Filename:  lcdtest.c
 *
 *    Description:  
 *
 *        Version:  1.0
 *        Created:  04/17/2009 01:01:04 PM
 *       Revision:  none
 *       Compiler:  gcc
 *
 *         Author:  PT_SWing (Man), pentie@gmail.com
 *        Company:  Nowhere, Earth
 *
 * =====================================================================================
 */

#include "main.h"
/*
void LCD_Cursor(uint8_t x, uint8_t y)
{
    uint8_t pos = x << 7;
    pos |= 0x80;
    pos += y;
    LCD_Send(1, pos);
}
*/
void LCD_Full_Screen_Str(char *str)
{
    uint8_t addr = 0x80;
    LCD_Send(1, 0x80);
    while(*str){
        if(addr & (1 << 4)){
            addr &= (3 << 6);
            addr ^= (1 << 6);
            LCD_Send(1, addr);
        }
        LCD_Send(0, *str++);
        addr++;
    }
}

int main()
{
    LCD_Init();
    LCD_Full_Screen_Str("Hello From PT");
    _delay_ms(2000);
    LCD_Full_Screen_Str("ABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890");
    _delay_ms(2000);
    LCD_Full_Screen_Str("PT From Mars.+.+=.=||  - .- ....");
    while(1);
}

