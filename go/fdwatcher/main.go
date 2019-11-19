package main

import (
	"flag"
	"io/ioutil"
	"log"
	"os"
	"path"
	"strconv"
	"strings"
	"time"
)

var (
	inteval  int
	watchPid int
)

func watchPos() {

}

func main() {
	flag.IntVar(&watchPid, "p", -1, "the pid to watch")
	flag.IntVar(&inteval, "i", 5, "inteval")
	flag.Parse()

	if watchPid <= 0 {
		log.Println("need pid")
		return
	}

	procDir := path.Join("/proc", strconv.Itoa(watchPid))
	fdDir := path.Join(procDir, "fd")
	fns, err := ioutil.ReadDir(fdDir)
	if err != nil {
		log.Fatal(err)
	}

	var watchfd string
	for _, f := range fns {
		fd := path.Join(fdDir, f.Name())
		info, err := os.Readlink(fd)
		if err != nil {
			log.Fatal(err)
		}
		if !strings.HasPrefix(info, "/") {
			continue
		}
		if strings.HasPrefix(info, "/dev") {
			continue
		}

		watchfd = f.Name()
		break
	}

	if watchfd == "" {
		log.Fatal("cant find correct fd")
		return
	}

	fdinfo := path.Join(procDir, "fdinfo", watchfd)
	log.Println(fdinfo)
	var pos string
	for {
		time.Sleep(time.Second * time.Duration(inteval))

		fc, err := ioutil.ReadFile(fdinfo)
		if err != nil {
			break
		}
		firstline := strings.SplitN(string(fc), "\n", 2)[0]
		if pos != firstline {
			pos = firstline
		} else {
			os.Exit(1)
			return
		}
	}
}
