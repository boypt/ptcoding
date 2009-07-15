#ifndef  USART_H
#define  USART_H
#define F_CPU 8000000UL  
#define BAUD_RATE 9600
#include <avr/io.h>

void usart_init( void );
void uart_putchar( char c );
char usart_getchar( void );
void usart_putstr(char *str);

#endif   /* ----- #ifndef USART_H_INC  ----- */

