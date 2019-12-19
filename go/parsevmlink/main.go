package main

import (
	"flag"
	"fmt"
	"log"
	"net/http"
	"regexp"
	"sort"

	"github.com/mmcdole/gofeed"
)

var (
	feedurl string
)

func main() {

	flag.StringVar(&feedurl, "f", "", "feed")
	flag.Parse()

	fp := gofeed.NewParser()
	fp.Client = &http.Client{}
	feed, err := fp.ParseURL(feedurl)
	if err != nil {
		log.Fatalln("parse feed err", err)
	}

	vmr := regexp.MustCompile(`vmess://[^ <\n]+`)

	sort.Slice(feed.Items, func(i, j int) bool {
		return feed.Items[i].PublishedParsed.After(*(feed.Items[j].PublishedParsed))
	})

	for _, item := range feed.Items {
		for _, link := range vmr.FindAllString(item.Description, -1) {
			fmt.Println(link)
		}
	}
	fmt.Println()
}
