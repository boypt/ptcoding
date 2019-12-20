package main

import (
	"flag"
	"io"
	"log"
	"net/http"
	"os"
	"regexp"
	"sort"

	"github.com/mmcdole/gofeed"
)

var (
	feedurl string
	output  string
)

func main() {

	flag.StringVar(&feedurl, "f", "", "feed")
	flag.StringVar(&output, "o", "", "output")
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

	for _, item := range feed.Items {
		for _, link := range vmr.FindAllString(item.Description, -1) {
			out.Write([]byte(link))
			out.Write([]byte("\n"))
		}
	}
	out.Write([]byte("\n"))
	out.Close()
}
