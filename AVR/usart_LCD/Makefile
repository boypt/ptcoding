CC=avr-gcc
CFLAGS=-g -Wall -Os -mcall-prologues -mmcu=atmega48
SRC=lcd_1602.c lcdtest.c
TARGET=uart

program:  $(TARGET).hex
	sudo avrdude -p m48 -e -V -U flash:w:$(TARGET).hex

%.hex : %.obj
	avr-objcopy -O ihex $< $@

%.obj: %.c
	$(CC) $(CFLAGS) $< -o $@

clean :$(SRC)
	rm -f *.hex *.obj *.o


