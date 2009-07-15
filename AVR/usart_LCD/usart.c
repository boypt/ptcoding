#define BAUD_RATE 9600
#include "usart.h"

void
uart_putchar( char c )
{
    loop_until_bit_is_set(UCSR0A, UDRE0);
    UDR0 = c;
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
