package main

import (
	"flag"
	"fmt"
	"io"
	"io/ioutil"
	"log"
	"os"
	"os/exec"
	"regexp"
	"strconv"
	"strings"
	"sync"

	"github.com/mmcdole/gofeed"
)

var (
	feedfile    string
	extsubsfile string
	output      string
	validate    bool
	unique      bool
	conn        int
	goodth      int
	verbose     bool
	vmr         = regexp.MustCompile(`vmess://[^ ]+`)
)

const (
	prefxNode = "Node Outbound:"
	prefxRTT  = "rtt min/avg/max"
	pxnLen    = len(prefxNode)
)

func runVmessPing(sub *vmSubs) *vmSubs {

	good := &vmSubs{}
	goodch := make(chan *vmessLinkP)
	consem := make(chan struct{}, conn)
	var w sync.WaitGroup

	for _, v := range *sub {
		w.Add(1)
		go func(lnk *vmessLinkP) {
			consem <- struct{}{}
			defer func() {
				w.Done()
				<-consem
			}()

			args := []string{"-n", "-c", "5", "-q", "2"}
			if verbose {
				args = append(args, "-v")
			}
			cmd := exec.Command("vmessping", args...)
			cmd.Env = []string{"VMESS=" + lnk.OrigLink}

			if out, err := cmd.CombinedOutput(); err == nil {
				for _, l := range strings.Split(string(out), "\n") {
					if strings.HasPrefix(l, prefxNode) {
						lnk.nodeline = l
					}
					if strings.HasPrefix(l, prefxRTT) {
						lnk.rttline = l
						if tl := strings.Split(l, " "); len(tl) == 5 {
							ts := strings.Split(tl[3], "/")
							if v, err := strconv.Atoi(ts[1]); err == nil && v > 0 {
								lnk.Delay = v
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
		if v.nodeline != "" {
			loc := v.nodeline[pxnLen : pxnLen+3]
			v.Ps = loc + " - " + strings.TrimSpace(v.Ps)
		}
		log.Println("--->", v, v.nodeline, v.rttline)
		good.Append(v)
	}

	return good
}

func writeLink(s *vmSubs) {
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
		out.Write([]byte(v.LinkStr("n")))
		out.Write([]byte("\n"))
	}
	out.Write([]byte("\n"))
	out.Close()
	fmt.Fprintf(os.Stderr, "output %d links\n", len(*s))
}

func readFeeds() []string {
	var vmess []string
	fp := gofeed.NewParser()
	bm, err := ioutil.ReadFile(feedfile)
	if err != nil {
		return vmess
	}

	for _, furl := range strings.Split(string(bm), "\n") {
		furl = strings.TrimSpace(furl)
		if furl == "" {
			continue
		}
		if strings.HasPrefix(furl, "http") {
			feed, err := fp.ParseURL(furl)
			if err != nil {
				log.Println("parse feed err", err)
				continue
			}

			if len(feed.Items) == 0 {
				continue
			}

			for _, item := range feed.Items {
				desc := trimDescription(item.Description)
				desc = strings.ReplaceAll(desc, "\n", " ")
				for _, link := range vmr.FindAllString(desc, -1) {
					vmess = append(vmess, link)
				}
			}
		}
	}
	return vmess
}

func readExtSus() []string {
	bm, err := ioutil.ReadFile(extsubsfile)
	if err != nil {
		return nil
	}
	return vmr.FindAllString(string(bm), -1)
}

func saveExtSus(s *vmSubs) {
	if output != "" {
		out, err := os.Create(output)
		if err != nil {
			log.Fatal(err)
		}
		for _, v := range *s {
			out.Write([]byte(v.LinkStr("n")))
			out.Write([]byte("\n"))
		}
		out.Write([]byte("\n"))
		out.Close()
	}
}

func main() {

	flag.StringVar(&feedfile, "f", "", "feed url file")
	flag.StringVar(&extsubsfile, "e", "", "ext subs file")
	flag.StringVar(&output, "o", "", "output")
	flag.BoolVar(&validate, "v", false, "validate available")
	flag.BoolVar(&unique, "u", false, "remove duplicated results")
	flag.IntVar(&goodth, "good", 2000, "good avg threshold")
	flag.BoolVar(&verbose, "verb", false, "verbose")
	flag.IntVar(&conn, "conn", 5, "conncurency")
	flag.Parse()

	var vmesses []string
	vmesses = append(vmesses, readExtSus()...)
	vmesses = append(vmesses, readFeeds()...)
	subs := &vmSubs{}
	for _, item := range vmesses {
		if err := subs.Add(item, unique); err != nil {
			log.Println(err, item)
		}
	}

	log.Printf("found %d links \n", len(*subs))
	var final *vmSubs
	if validate {
		gd := runVmessPing(subs)
		gd.Sort()
		for _, i := range *gd {
			fmt.Println(i.Ps, i.Delay, "ms")
		}
		final = gd
	} else {
		final = subs
	}

	writeLink(final)
	saveExtSus(final)
}
