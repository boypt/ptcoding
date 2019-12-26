package main

import (
	"flag"
	"fmt"
	"io"
	"log"
	"net/http"
	"os"
	"os/exec"
	"regexp"
	"strconv"
	"strings"
	"sync"

	"github.com/mmcdole/gofeed"
	"github.com/v2fly/vmessping/vmess"
)

var (
	feedurl  string
	output   string
	validate bool
	unique   bool
	conn     int
	verbose  bool
)

func runVmessPing(sub *VmSubs) *VmSubs {

	good := &VmSubs{}
	goodch := make(chan *vmess.VmessLink)
	consem := make(chan struct{}, conn)
	var w sync.WaitGroup

	for _, v := range *sub {
		w.Add(1)
		go func(lnk *vmess.VmessLink) {
			consem <- struct{}{}
			defer func() {
				w.Done()
				<-consem
			}()

			args := []string{"-i", "0", "-c", "5"}
			if verbose {
				args = append(args, "-v")
			}
			cmd := exec.Command("vmessping", args...)
			cmd.Env = []string{"VMESS=" + lnk.OrigLink}

			if out, err := cmd.CombinedOutput(); err == nil {
				for _, l := range strings.Split(string(out), "\n") {
					if strings.HasPrefix(l, "rtt min/avg/max") {
						if tl := strings.Split(l, " "); len(tl) == 5 {
							ts := strings.Split(tl[3], "/")
							if v, err := strconv.Atoi(ts[1]); err == nil && v > 0 && v < 1500 {
								fmt.Println(lnk.Ps, l)
								goodch <- lnk
							}
							return
						}
					}
				}
			}
		}(v)
	}

	go func() {
		w.Wait()
		close(goodch)
	}()

	for v := range goodch {
		log.Println("goodlink: ", v.Ps, "/", v.Add)
		good.Append(v)
	}

	return good
}

func writeLink(s *VmSubs) {
	var out io.WriteCloser
	if output != "" {
		f, err := os.Create(output)
		if err != nil {
			log.Fatal(err)
		}
		out = f
	} else {
		out = os.Stdout
	}

	for _, v := range *s {
		out.Write([]byte(v.LinkStr()))
		out.Write([]byte("\n"))
	}
	out.Write([]byte("\n"))
	out.Close()
	fmt.Fprintf(os.Stderr, "output %d links\n", len(*s))
}

func main() {

	flag.StringVar(&feedurl, "f", "", "feed")
	flag.StringVar(&output, "o", "", "output")
	flag.BoolVar(&validate, "v", false, "validate available")
	flag.BoolVar(&unique, "u", false, "remove duplicated results")
	flag.BoolVar(&verbose, "verb", false, "verbose")
	flag.IntVar(&conn, "conn", 5, "conncurency")
	flag.Parse()

	fp := gofeed.NewParser()
	fp.Client = &http.Client{}
	feed, err := fp.ParseURL(feedurl)
	if err != nil {
		log.Fatalln("parse feed err", err)
	}

	if len(feed.Items) == 0 {
		return
	}

	vmr := regexp.MustCompile(`vmess://[a-zA-Z0-9\+/-]+`)

	var vmess []string
	for _, item := range feed.Items {
		desc := trimDescription(item.Description)
		for _, link := range vmr.FindAllString(desc, -1) {
			vmess = append(vmess, link)
		}
	}

	subs := &VmSubs{}
	for _, item := range vmess {
		if err := subs.Add(item, unique); err != nil {
			log.Println(err, item)
		}
	}

	log.Printf("found %d links from feed\n", len(vmess))

	subs.Sort()

	// attr amends
	for _, v := range *subs {
		if i, err := strconv.Atoi(v.Aid); err == nil && i > 4 {
			v.Aid = "2"
		} else {
			v.Aid = "0"
		}

		if v.Ps == "" {
			v.Ps = v.Add
		}
	}

	if validate {
		writeLink(runVmessPing(subs))
	} else {
		writeLink(subs)
	}
}
