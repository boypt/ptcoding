#ifndef  LCD_1602_H
#define  LCD_1602_H
#define F_CPU 8000000UL  
#include <avr/io.h>
#include <util/delay.h>
/* Define LCD Data Ports (8bit). */
#define LCD_DATA_PIN    PINB
#define LCD_DATA_DDR    DDRB
#define LCD_DATA_PORT   PORTB
#define LCD_DATA_BF     PB7
#define LCD_DATA        0xff

/* Define LCD Control Ports. */
#define LCD_CTRK_DDR    DDRC
#define LCD_CTRL_PORT   PORTC
#define LCD_E           _BV(PC0)
#define LCD_RW          _BV(PC1)
#define LCD_RS          _BV(PC2)

void LCD_Busy_Wait(void);
void LCD_Send (uint8_t command, char data);
void LCD_Init(void);
void LCD_Write_String (const char ptr[]);

#endif
