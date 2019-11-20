package main

import (
	"flag"
	"fmt"
	"io/ioutil"
	"log"
	"os"
	"path"
	"strings"
	"syscall"
	"time"
)

var (
	inteval    int
	fileSuffix string
	watchPid   int
)

func findfd() (string, error) {

	procDir := fmt.Sprintf("/proc/%d", watchPid)
	fdDir := path.Join(procDir, "fd")
	fns, err := ioutil.ReadDir(fdDir)
	if err != nil {
		return "", err
	}

	var watchfd string
	for _, f := range fns[3:] {
		fd := path.Join(fdDir, f.Name())
		info, err := os.Readlink(fd)
		if err != nil {
			return "", err
		}
		if !strings.HasPrefix(info, "/") {
			continue
		}
		if strings.HasSuffix(info, fileSuffix) {
			watchfd = f.Name()
			break
		}
	}
	if watchfd == "" {
		return "", fmt.Errorf("can not find correct fd to `%s` suffix", fileSuffix)
	}

	return path.Join(procDir, "fdinfo", watchfd), nil
}

func main() {
	flag.StringVar(&fileSuffix, "s", "opus", "the file suffix to find fd")
	flag.IntVar(&watchPid, "p", -1, "the pid to watch")
	flag.IntVar(&inteval, "i", 5, "inteval")
	flag.Parse()
	if watchPid <= 0 {
		log.Println("need pid")
		return
	}

	fdinfo, err := findfd()
	if err != nil {
		log.Fatal(err)
	}

	log.Printf("watching %s\n", fdinfo)
	var pos string
	for {
		fc, err := ioutil.ReadFile(fdinfo)
		if err != nil {
			break
		}
		firstline := strings.SplitN(string(fc), "\n", 2)[0]
		if pos == firstline {
			break
		}
		pos = firstline
		time.Sleep(time.Second * time.Duration(inteval))
	}

	log.Printf("watching exit, killing %d\n", watchPid)
	syscall.Kill(watchPid, syscall.SIGINT)
}
