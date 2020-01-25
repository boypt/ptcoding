package main

import (
	"encoding/base64"
	"errors"
	"flag"
	"fmt"
	"io"
	"io/ioutil"
	"log"
	"net/http"
	"os"
	"os/exec"
	"regexp"
	"strconv"
	"strings"
	"sync"
	"time"

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
	httpClient  = &http.Client{
		Timeout: time.Second * 60,
	}
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

			args := []string{"-n", "-c", "5", "-q", "2", "-dest", "http://www.cloudflare.com/cdn-cgi/trace"}
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
			} else {
				log.Println("vmessping", err, "\n",string(out))
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
			if !strings.HasPrefix(v.Ps, loc) {
				v.Ps = loc + " - " + strings.TrimSpace(v.Ps)
			}
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

func readRemoteBase64(furl string) ([]string, error) {

	req, err := http.NewRequest("GET", furl, nil)
	if err != nil {
		return nil, err
	}
	resp, err := httpClient.Do(req)
	if err != nil {
		return nil, err
	}
	content, err := ioutil.ReadAll(resp.Body)
	if err != nil {
		return nil, err
	}
	defer resp.Body.Close()
	cnt, err := base64.StdEncoding.DecodeString(string(content))
	if err != nil {
		return nil, err
	}

	var vmesses []string
	for _, src := range strings.Split(string(cnt), "\n") {
		src = strings.TrimSpace(src)
		if src == "" {
			continue
		}
		if !strings.HasPrefix(src, "vmess://") {
			continue
		}
		vmesses = append(vmesses, src)
	}

	return vmesses, nil

}

func readFeeds(furl string) ([]string, error) {
	var vmess []string
	fp := gofeed.NewParser()
	fp.Client = httpClient

	feed, err := fp.ParseURL(furl)
	if err != nil {
		log.Println("parse feed err", err)
		return nil, err
	}

	if len(feed.Items) == 0 {
		return nil, errors.New("empty feed")
	}

	for _, item := range feed.Items {
		desc := trimDescription(item.Description)
		desc = strings.ReplaceAll(desc, "\n", " ")
		for _, link := range vmr.FindAllString(desc, -1) {
			if len(link) > 1000 {
				log.Fatalln(link)
			}
			vmess = append(vmess, link)
		}
	}
	return vmess, nil
}

func readLocalPlain(fn string) ([]string, error) {
	var vmesses []string
	cnt, err := ioutil.ReadFile(fn)
	if err != nil {
		return nil, err
	}

	for _, src := range strings.Split(string(cnt), "\n") {
		src = strings.TrimSpace(src)
		if src == "" {
			continue
		}
		vmesses = append(vmesses, src)
	}

	return vmesses, nil
}

func readSource() []string {
	var vmess []string
	bm, err := ioutil.ReadFile(feedfile)
	if err != nil {
		return vmess
	}

	for _, src := range strings.Split(string(bm), "\n") {
		src = strings.TrimSpace(src)
		if src == "" {
			continue
		}

		if strings.HasPrefix(src, "#") {
			continue
		}

		source := strings.SplitN(src, ":", 2)
		if len(source) != 2 {
			log.Println("skip line:", src)
			continue
		}
		dest := source[1]
		switch source[0] {
		case "feed":
			log.Println("read feed:", dest)
			vvms, err := readFeeds(dest)
			if err != nil {
				log.Println(err)
				break
			}
			log.Println("items:", len(vvms))
			vmess = append(vmess, vvms...)
		case "rbase64":
			log.Println("read remotebase64:", dest)
			vvms, err := readRemoteBase64(dest)
			if err != nil {
				log.Println(err)
				break
			}
			log.Println("items:", len(vvms))
			vmess = append(vmess, vvms...)
		case "lplain":
			log.Println("read lplain:", dest)
			vvms, err := readLocalPlain(dest)
			if err != nil {
				log.Println(err)
				break
			}
			log.Println("items:", len(vvms))
			vmess = append(vmess, vvms...)
		}
	}

	log.Println("parsed source complete: ", feedfile)
	return vmess
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
	flag.StringVar(&output, "o", "", "output")
	flag.BoolVar(&validate, "v", false, "validate available")
	flag.BoolVar(&unique, "u", false, "remove duplicated results")
	flag.IntVar(&goodth, "good", 2000, "good avg threshold")
	flag.BoolVar(&verbose, "verb", false, "verbose")
	flag.IntVar(&conn, "conn", 5, "conncurency")
	flag.Parse()

	vmesses := readSource()
	subs := &vmSubs{}
	for idx, item := range vmesses {
		if err := subs.Add(item, unique); err != nil {
			log.Println(err, idx, item)
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
	// saveExtSus(final)
}
