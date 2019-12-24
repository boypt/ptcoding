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
	"sort"
	"sync"

	"github.com/mmcdole/gofeed"
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
	goodch := make(chan *VmessLink)
	consem := make(chan struct{}, conn)
	var w sync.WaitGroup

	for _, v := range *sub {
		w.Add(1)
		go func(lnk *VmessLink) {
			consem <- struct{}{}
			cmd := exec.Command("vmessping", "-c", "3")
			cmd.Env = []string{"VMESS=" + lnk.OrigLink}
			if verbose {
				cmd.Stdout = os.Stdout
				cmd.Stderr = os.Stderr
			}
			cmd.Run()
			if cmd.ProcessState.ExitCode() == 0 {
				goodch <- lnk
			}
			w.Done()
			<-consem
		}(v)
	}

	go func() {
		w.Wait()
		close(goodch)
	}()

	for v := range goodch {
		log.Println("goodlink: ", v.Ps)
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
		out.Write([]byte(v.OrigLink))
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

	vmr := regexp.MustCompile(`vmess://[^ <\n]+`)

	sort.Slice(feed.Items, func(i, j int) bool {
		return feed.Items[i].PublishedParsed.After(*(feed.Items[j].PublishedParsed))
	})

	var vmess []string
	for _, item := range feed.Items {
		for _, link := range vmr.FindAllString(item.Description, -1) {
			vmess = append(vmess, link)
		}
	}

	subs := &VmSubs{}
	for _, item := range vmess {
		if unique {
			if !subs.HasVM(item) {
				if err := subs.Add(item); err != nil {
					log.Println(err, item)
				}
			}
		} else {
			if err := subs.Add(item); err != nil {
				log.Println(err, item)
			}
		}
	}

	log.Printf("found %d links from feed\n", len(vmess))
	if validate {
		writeLink(runVmessPing(subs))
	} else {
		writeLink(subs)
	}
}
