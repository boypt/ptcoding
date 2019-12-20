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

func runVmessPing(vmess []string) []string {

	var good []string
	goodch := make(chan string)
	consem := make(chan struct{}, conn)
	var w sync.WaitGroup

	for _, v := range vmess {
		consem <- struct{}{}
		w.Add(1)
		go func(lnk string) {
			log.Println("pinging")
			cmd := exec.Command("vmessping", "-c", "3", lnk)
			if verbose {
				cmd.Stdout = os.Stdout
				cmd.Stderr = os.Stderr
			}
			cmd.Run()
			if cmd.ProcessState.ExitCode() == 0 {
				goodch <- lnk
			}
			w.Done()
			log.Println("pingdone")
			<-consem
		}(v)
	}

	go func() {
		w.Wait()
		close(goodch)
	}()

	for v := range goodch {
		log.Println("goodlink: ", v)
		good = append(good, v)
	}

	return good
}

func writeLink(vmess []string) {
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

	for _, v := range vmess {
		out.Write([]byte(v))
		out.Write([]byte("\n"))
	}
	out.Write([]byte("\n"))
	out.Close()
	fmt.Fprintf(os.Stderr, "output %d links\n", len(vmess))
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

	if unique {
		subs := &VmSubs{}
		for _, item := range vmess {
			if !subs.HasVM(item) {
				if err := subs.Add(item); err != nil {
					log.Println(err, item)
				}
			}
		}
		vmess = subs.Link
	}

	log.Printf("found %d links from feed\n", len(vmess))
	if validate {
		goodv := runVmessPing(vmess)
		writeLink(goodv)
	} else {
		writeLink(vmess)
	}
}
