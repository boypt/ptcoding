package main

import (
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

func torrentDecode(fn string) (string, string) {
	var f torrentFile
	content, err := ioutil.ReadFile(fn)
	if err != nil {
		log.Fatal(err)
	}

	//decode
	err = bencode.Unmarshal([]byte(content), &f)
	if err != nil {
		log.Fatal(err)
	}

	metainfo, err := bencode.Marshal(f.Info)
	if err != nil {
		log.Fatal(err)
	}

	sha1sum := fmt.Sprintf("xt=urn:btih:%x", sha1.Sum(metainfo))
	dn := fmt.Sprintf("dn=%s", url.QueryEscape(f.Info.Name))
	maglink := fmt.Sprintf("magnet:?%s&%s", sha1sum, dn)
	return f.Info.Name, maglink
}

func mag2cloud(maglink string, idx int, wg *sync.WaitGroup) {
	defer wg.Done()
	magapi := fmt.Sprintf("%s/api/magnet", os.Getenv("CLDTORRENT"))
	req, err := http.NewRequest("POST", magapi, strings.NewReader(maglink))
	if err != nil {
		log.Fatal(err)
	}

	client := &http.Client{}
	req.Header.Set("Content-Type", "application/x-www-form-urlencoded")
	req.Header.Set("Cookie", strings.TrimPrefix(os.Getenv("CLDCOOKIE"), "cookie: "))

	resp, err := client.Do(req)
	if err != nil {
		log.Fatal(err)
	}

	body, err := ioutil.ReadAll(resp.Body)
	if err != nil {
		log.Fatal(err)
	}

	fmt.Printf("[ %d] %s\n", idx, string(body))
	defer resp.Body.Close()
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
	for i, torf := range tors {
		_, base := path.Split(torf)
		name, mag := torrentDecode(torf)
		fmt.Printf("[%d] %s --> %s\n    %s\n\n", i+1, base, name, mag)
		wg.Add(1)
		go mag2cloud(mag, i+1, &wg)
	}

	fmt.Println("===================================")
	wg.Wait()
}
