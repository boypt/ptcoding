package main

import (
	"bufio"
	"crypto/sha1"
	"fmt"
	"io/ioutil"
	"log"
	"net/http"
	"net/url"
	"os"
	"os/user"
	"path"
	"path/filepath"
	"runtime"
	"strings"
	"sync"

	"github.com/anacrolix/torrent/bencode"
	"github.com/joho/godotenv"
)

type torrentFile struct {
	Info struct {
		Name        string `bencode:"name"`
		Length      int64  `bencode:"length"`
		MD5Sum      string `bencode:"md5sum,omitempty"`
		PieceLength int64  `bencode:"piece length"`
		Pieces      string `bencode:"pieces"`
		Private     bool   `bencode:"private,omitempty"`
	} `bencode:"info"`

	Announce     string      `bencode:"announce"`
	AnnounceList [][]string  `bencode:"announce-list,omitempty"`
	CreationDate int64       `bencode:"creation date,omitempty"`
	Comment      string      `bencode:"comment,omitempty"`
	CreatedBy    string      `bencode:"created by,omitempty"`
	URLList      interface{} `bencode:"url-list,omitempty"`
}

type magnetInfo struct {
	Name    string
	MagLink string
}

func torrentDecode(fn string) (*magnetInfo, error) {
	var f torrentFile
	content, err := ioutil.ReadFile(fn)
	if err != nil {
		return nil, err
	}

	//decode
	err = bencode.Unmarshal([]byte(content), &f)
	if err != nil {
		return nil, err
	}

	metainfo, err := bencode.Marshal(f.Info)
	if err != nil {
		return nil, err
	}

	maglink := fmt.Sprintf(
		"magnet:?xt=urn:btih:%x&dn=%s",
		sha1.Sum(metainfo),
		url.QueryEscape(f.Info.Name),
	)

	return &magnetInfo{
		Name:    f.Info.Name,
		MagLink: maglink,
	}, nil
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

	var wg sync.WaitGroup
	resCh := make(chan string)

	for i, torf := range tors {
		_, base := path.Split(torf)
		m, err := torrentDecode(torf)
		if err != nil {
			fmt.Println(err)
			continue
		}
		fmt.Printf("[%d] %s --> %s\n%s\n\n", i+1, base, m.Name, m.MagLink)
		resInfo := fmt.Sprintf("[%d]%s:", i+1, m.Name)

		wg.Add(1)
		go func() {
			ret, err := mag2cloud(m.MagLink)
			if err != nil {
				ret = err.Error()
			}
			resCh <- resInfo + ret
			wg.Done()
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
