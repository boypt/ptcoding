/*
 * =====================================================================================
 *
 *       Filename:  uart.c
 *
 *    Description:  
 *
 *        Version:  1.0
 *        Created:  04/15/2009 03:00:30 PM
 *       Revision:  none
 *       Compiler:  gcc
 *
 *         Author:  PT_SWing (Man), pentie@gmail.com
 *        Company:  Nowhere, Earth
 *
 * =====================================================================================
 */
#define F_CPU 8000000UL  /* 1 MHz CPU clock */
#define BAUD_RATE 9600
#include <avr/io.h>
#include <stdio.h>
//#include <utils/delay.h>


void
uart_putchar( char c )
{
    loop_until_bit_is_set(UCSR0A, UDRE0);
    UDR0 = c;
    if( c == '\r')
        uart_putchar('\n');
}

char usart_getchar()
{
    loop_until_bit_is_set(UCSR0A, RXC0);
    return UDR0;
}

void usart_putstr(char *str)
{
    while(*str){
        loop_until_bit_is_set(UCSR0A, UDRE0);
        UDR0 = *(str++);
    }
}

void usart_init( void )
{
    /* 设置波特率 (计算公式)*/
    UBRR0 = F_CPU / 16 / BAUD_RATE - 1;

    /* 接收器与发送器使能 */
    UCSR0B |= _BV(RXEN0) | _BV(TXEN0);
    /* 设置帧格式 :异步、无校验、1停止、 8 数据位 */

    UCSR0C |= _BV(UCSZ01) | _BV(UCSZ00);
}

int main(void)
{
    usart_init();
    char tmp;
    usart_putstr("Hello World...\r\n");
    while(1){
        tmp = usart_getchar();
        uart_putchar(tmp);
    }
}


