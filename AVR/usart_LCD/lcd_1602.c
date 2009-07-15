#include "lcd_1602.h"

void
LCD_Busy_Wait(void)
{
    LCD_CTRL_PORT |= LCD_RW;    //RW = 1
    LCD_CTRL_PORT &= ~LCD_RS;   //RS = 0
    
//    _delay_loop_1(10);
    
    LCD_DATA_DDR = 0;           //Set Port to input
//    LCD_DATA_PORT = 0xff;

    LCD_CTRL_PORT |= LCD_E;     //E=1
//    _delay_loop_1(100);
    _delay_us(60);
    while(LCD_DATA_PIN & _BV(LCD_DATA_BF)); //busy wait

    LCD_CTRL_PORT &= ~LCD_E;    //E=0
}


void 
LCD_Send (uint8_t command, char data)
{
    LCD_Busy_Wait();
//    while(LCD_Read_Static() & LCD_DATA_BF);
    if(command)
        LCD_CTRL_PORT &= ~LCD_RS; //Command, RS=0
    else
        LCD_CTRL_PORT |= LCD_RS;  //Data, RS=1

    LCD_CTRL_PORT &= ~LCD_RW;     //RW = 0

    LCD_DATA_DDR = LCD_DATA;    //Set Port to Output
    LCD_DATA_PORT = data;         //Send data

    LCD_CTRL_PORT |= LCD_E;       //Enable Signal
//    _delay_loop_1(100);
    _delay_us(10);
    LCD_CTRL_PORT &= ~LCD_E;
    LCD_CTRL_PORT |= LCD_RW;     //RW = 1
    LCD_CTRL_PORT &= ~LCD_RS;    //RS = 0
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
    register uint8_t i = 20;
    while(i--){  
//        _delay_us(10);               //make sure the device fully initial.
        LCD_CTRL_PORT |= LCD_E;
        _delay_us(10);
        LCD_CTRL_PORT &= ~LCD_E;
    }

    LCD_Send(1,0x0e);           //Display On, No Cursor, No Blinking
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

