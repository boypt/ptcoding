/*
 * =====================================================================================
 *
 *       Filename:  1602_lcd.c
 *
 *    Description:  A AVR Driver for 1602A LCD.
 *
 *        Version:  1.0
 *        Created:  04/10/2009 04:20:38 PM
 *       Revision:  none
 *       Compiler:  avr-gcc
 *
 *         Author:  PT (Man), pentie@gmail.com
 *        Company:  Nowhere, Earth
 *
 * =====================================================================================
 */

#define F_CPU 8000000UL  /* 1 MHz CPU clock */
#include <util/delay.h>
#include <avr/io.h>

/* Define LCD Data Ports (8bit). */
#define LCD_DATA_PIN    PINB
#define LCD_DATA_DDR    DDRB
#define LCD_DATA_PORT   PORTB
#define LCD_DATA_BF     _BV(PB7)
#define LCD_DATA        0xff

/* Define LCD Control Ports. */
#define LCD_CTRK_DDR    DDRC
#define LCD_CTRL_PORT   PORTC
#define LCD_E           _BV(PC0)
#define LCD_RW          _BV(PC1)
#define LCD_RS          _BV(PC2)

/*
 * You may replace the LCD_Busy_Wait() 
 * with _delay_ms(5), with 36 byte program decrease,
 * but the device works a little slowly.
 */
void 
LCD_Busy_Wait(void)
{
    LCD_DATA_PORT = 0xff;
    LCD_DATA_DDR = 0;           //Set Port to input

    LCD_CTRL_PORT &= ~LCD_RS;   //RS = 0
    LCD_CTRL_PORT |= LCD_RW;    //RW = 1
    LCD_CTRL_PORT |= LCD_E;     //E=1
    _delay_us(200);
    while (LCD_DATA_PIN & LCD_DATA_BF); //busy wait
    LCD_CTRL_PORT &= ~LCD_E;    //E=0
    LCD_DATA_DDR = LCD_DATA;    //Set Port to Output
}

/* Function LCD_Send:
 * argument 'command' defind data is a control
 * word or a charactor data.
 */
void 
LCD_Send (uint8_t command, unsigned char data)
{
    LCD_Busy_Wait();
    if(command)
        LCD_CTRL_PORT &= ~LCD_RS; //Command, RS=0
    else
        LCD_CTRL_PORT |= LCD_RS;  //Data, RS=1

    LCD_CTRL_PORT &= ~LCD_RW;     //RW = 0

    LCD_DATA_PORT = data;         //Send data

    LCD_CTRL_PORT |= LCD_E;       //Enable Signal
    _delay_us(100);
    LCD_CTRL_PORT &= ~LCD_E;
}

void 
LCD_Init(void)
{
    LCD_DATA_DDR = LCD_DATA;    //Data port to output
    LCD_CTRK_DDR = LCD_E|LCD_RW|LCD_RS;    //Ctrl port to output

    _delay_ms(50);              //Initializing wait

    LCD_CTRL_PORT &= ~LCD_RW;   //RW = 0
    LCD_CTRL_PORT &= ~LCD_RS;   //RS = 0

    LCD_DATA_PORT = 0x38;       //Initial signal. 8bit data,
                                //2 line display, 5*8 dot fonts.
    register uint8_t i = 5;
    while(i--){                 //make sure the device fully initial.
        LCD_CTRL_PORT |= LCD_E;
        _delay_us(100);
        LCD_CTRL_PORT &= ~LCD_E;
        _delay_us(100);
    }

    LCD_Send(1,0x0c);           //Display On, No Cursor, No Blinking
    LCD_Send(1,0x01);           //Display Clear
}

void 
LCD_Write_String (const char ptr[])
{
    while(*ptr){
        LCD_Send(0, *ptr);
        ptr++;
    }
}


int
main (void)
{
    LCD_Init();
//    while(1){
        LCD_Send(1,0x80);
        LCD_Write_String("Testing!!!");
        LCD_Send(1,0xc0);
        LCD_Write_String("PT from Mars -.-");
        LCD_Send(1,0x01);
        LCD_Write_String("The Only Survived...");
//        LCD_Send(1,0xff);
//        _delay_ms(10);
//    }
    while(1);
    return 0;
}
