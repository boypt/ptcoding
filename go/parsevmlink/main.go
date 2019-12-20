package main

import (
	"flag"
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
)

func runVmessPing(vmess []string) []string {

	var good []string
	goodch := make(chan string)
	var w sync.WaitGroup

	for _, v := range vmess {
		w.Add(1)
		go func(lnk string) {
			cmd := exec.Command("vmessping", "-c", "3", lnk)
			cmd.Run()
			if cmd.ProcessState.ExitCode() == 0 {
				goodch <- lnk
			}
			w.Done()
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
}

func main() {

	flag.StringVar(&feedurl, "f", "", "feed")
	flag.StringVar(&output, "o", "", "output")
	flag.BoolVar(&validate, "v", false, "validate available")
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

	if validate {
		goodv := runVmessPing(vmess)
		writeLink(goodv)
	} else {
		writeLink(vmess)
	}
}
