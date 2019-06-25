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

func torrent2Magnet(fn string) (*metainfo.Magnet, error) {

	mi, err := metainfo.LoadFromFile(fn)
	if err != nil {
		return nil, err
	}

	info, err := mi.UnmarshalInfo()
	if err != nil {
		return nil, err
	}

	m := mi.Magnet(info.Name, mi.HashInfoBytes())
	return &m, nil
}

func mag2cloud(m *metainfo.Magnet) (string, error) {
	magapi := fmt.Sprintf("%s/api/magnet", os.Getenv("CLDTORRENT"))
	req, err := http.NewRequest("POST", magapi, strings.NewReader(m.String()))
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

	var wg sync.WaitGroup
	resCh := make(chan string)

	for i, torf := range tors {
		_, base := path.Split(torf)
		m, err := torrent2Magnet(torf)
		if err != nil {
			fmt.Println(err)
			continue
		}
		fmt.Printf("(%d)%s -> %s\n%s\n\n", i+1, base, m.DisplayName, m.String())
		resInfo := fmt.Sprintf("(%d)%s:", i+1, m.DisplayName)

		wg.Add(1)
		go func() {
			defer wg.Done()
			ret, err := mag2cloud(m)
			if err != nil {
				ret = err.Error()
			}
			resCh <- resInfo + ret
		}()
	}

	go func() {
		wg.Wait()
		close(resCh)
	}()

	fmt.Println("===================================")
	// printer in main goroutine
	for r := range resCh {
		fmt.Println(r)
	}

	if runtime.GOOS == "windows" {
		fmt.Println("===================================")
		fmt.Println("\nPress 'Enter' to continue...")
		bufio.NewReader(os.Stdin).ReadBytes('\n')
	}

}
