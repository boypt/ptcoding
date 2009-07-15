CC=avr-gcc
CFLAGS=-g -Wall -Os -mcall-prologues -mmcu=atmega48
TARGET=1602_lcd

program:  $(TARGET).hex
	sudo avrdude -p m48 -e -V -U flash:w:$(TARGET).hex

%.hex : %.obj
	avr-objcopy -O ihex $< $@

%.obj: %.c
	$(CC) $(CFLAGS) $< -o $@

clean :
	rm -f *.hex *.obj *.o


