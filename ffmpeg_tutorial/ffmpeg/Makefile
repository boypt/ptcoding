CC = gcc
LIBS = -lavutil -lavformat -lavcodec -lswscale -lz -lavdevice 
CFLAGS = -Wall -O2
INC_DIR= "/home/boypt/ProgramProjects/ffmpeg-0.5"
LINK_DIR= 
OBJ  = ffmpeg.o cmdutils.o main.o
.PHONY: all
all: ffmpeg

ffmpeg: $(OBJ)
	$(CC) $(CFLAGS) -o $@ $(OBJ) $(LIBS) 

ffmpeg.o: ffmpeg.c
	$(CC) $(CFLAGS) -c $< -I$(INC_DIR)

cmdutils.o: cmdutils.c 
	$(CC) $(CFLAGS) -c $< -I$(INC_DIR)

main.o: main.c
	$(CC) $(CFLAGS) -c $< -I$(INC_DIR)

clean:
	rm $(OBJ) ffmpeg

