package main

import (
	"bufio"
	"fmt"
	"io/ioutil"
	"log"
	"net/http"
	"os"
	"os/user"
	"path"
	"path/filepath"
	"runtime"
	"strings"
	"sync"

	"github.com/anacrolix/torrent/metainfo"
	"github.com/joho/godotenv"
)

type tItem struct {
	Index    int
	FileName string
	DispName string
	MagLink  string
	RetInfo  string
}

func (t tItem) printMag() {
	_, base := path.Split(t.FileName)
	fmt.Printf("(%d)%s -> %s\n%s\n\n", t.Index, base, t.DispName, t.MagLink)
}
func (t tItem) printRet() {
	fmt.Printf("(%d)%s: %s\n", t.Index, t.DispName, t.RetInfo)
}

func torrent2Magnet(fn string) (*tItem, error) {

	mi, err := metainfo.LoadFromFile(fn)
	if err != nil {
		return nil, err
	}

	info, err := mi.UnmarshalInfo()
	if err != nil {
		return nil, err
	}

	m := mi.Magnet(info.Name, mi.HashInfoBytes())
	i := &tItem{FileName: fn,
		DispName: info.Name,
		MagLink:  m.String(),
	}
	return i, nil
}

func mag2cloud(maglink string) (string, error) {
	magapi := fmt.Sprintf("%s/api/magnet", os.Getenv("CLDTORRENT"))
	req, err := http.NewRequest("POST", magapi, strings.NewReader(maglink))
	if err != nil {
		return "", err
	}

	client := &http.Client{}
	req.Header.Set("Content-Type", "application/x-www-form-urlencoded")
	req.Header.Set("Cookie", strings.TrimPrefix(os.Getenv("CLDCOOKIE"), "cookie: "))

	resp, err := client.Do(req)
	if err != nil {
		return "", err
	}
	defer resp.Body.Close()

	body, err := ioutil.ReadAll(resp.Body)
	if err != nil {
		return "", err
	}

	return string(body), nil
}

func main() {

	cur, err := user.Current()
	if err != nil {
		log.Fatal(err)
	}
	_ = godotenv.Load(filepath.Join(cur.HomeDir, ".ptutils.config"))
	_ = godotenv.Load() // for .env

	tors, err := filepath.Glob(fmt.Sprintf("%s/*.torrent", os.Getenv("CLDTORRENTDIR")))
	if err != nil {
		return
	}

	wg := new(sync.WaitGroup)
	resCh := make(chan *tItem)

	for i, torf := range tors {
		item, err := torrent2Magnet(torf)
		if err != nil {
			fmt.Println(err)
			continue
		}
		item.Index = i + 1

		item.printMag()
		wg.Add(1)
		go func() {
			defer wg.Done()
			ret, err := mag2cloud(item.MagLink)
			if err != nil {
				ret = err.Error()
			}
			item.RetInfo = ret
			resCh <- item
		}()
	}

	go func() {
		wg.Wait()
		close(resCh)
	}()

	fmt.Println("===================================")
	// printer in main goroutine
	for r := range resCh {
		r.printRet()
		os.Remove(r.FileName)
	}

	if runtime.GOOS == "windows" {
		fmt.Println("===================================")
		fmt.Println("\nPress 'Enter' to continue...")
		bufio.NewReader(os.Stdin).ReadBytes('\n')
	}

}
