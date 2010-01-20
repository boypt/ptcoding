
from subprocess import Popen, PIPE
import threading
import time

Pipe = None

def main():
	global Pipe
	Pipe = Popen(["ping", "127.0.0.1", '-t'], stdout = PIPE)
	read = threading.Thread(target=run)
	read.start()
	read.join()
	
def run():
	global Pipe
	outfile = Pipe.stdout
	line = outfile.readline(40)
	while line:
		print line
		time.sleep(0.1)
		line = outfile.readline(40)


if __name__ == "__main__":
	main()

