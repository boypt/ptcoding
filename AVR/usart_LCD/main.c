/*
 * =====================================================================================
 *
 *       Filename:  main.c
 *
 *    Description:  
 *
 *        Version:  1.0
 *        Created:  04/16/2009 04:23:37 PM
 *       Revision:  none
 *       Compiler:  gcc
 *
 *         Author:  PT_SWing (Man), pentie@gmail.com
 *        Company:  Nowhere, Earth
 *
 * =====================================================================================
 */

#include "main.h"

void init_device( void )
{
    LCD_Init();
    usart_init();
}
/*
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
*/
int main()
{
    init_device();
    char tmp;
    register uint8_t addr = 0x80;
    LCD_Send(1, 0x80);

    while(1){
        if(addr & (1 << 4)){
            addr &= (3 << 6);
            addr ^= (1 << 6);
            LCD_Send(1, addr);
        }
        tmp = usart_getchar();
        switch(tmp){
        case 0x08:            //Back Space,
            if(addr == 0x80)
                break;
            LCD_Send(1, --addr);
            LCD_Send(0, ' ');
            LCD_Send(1, addr);
            break;
        case 0x1b:            //ESC, reset all
            LCD_Send(1, 01);
            addr = 0x80;
            break;
        case 0x0d:            //Return
            addr &= (3 << 6);
            LCD_Send(1, addr);
            break;
        default:
            uart_putchar (tmp);
            LCD_Send(0, tmp);
            addr++;
        }
    }
}



