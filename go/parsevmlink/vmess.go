package main

import (
	"sort"
	"strconv"

	"github.com/v2fly/vmessping/vmess"
)

type vmessLinkP struct {
	vmess.VmessLink
	Delay    int
	rttline  string
	nodeline string
}

type vmSubs []*vmessLinkP

func (s *vmSubs) Sort() {
	sort.SliceStable(*s, func(i, j int) bool {
		return (*s)[i].Delay < (*s)[j].Delay
	})
}

func (s *vmSubs) Append(v *vmessLinkP) {
	*s = append(*s, v)
}

func (s *vmSubs) Add(vm string, uniq bool) error {
	p, err := vmess.ParseVmess(vm)
	if err != nil {
		return err
	}
	p.OrigLink = vm

	// attr amends
	switch aid := p.Aid.(type) {
	case int:
		if aid > 2 {
			p.Aid = 2
		}
	case string:
		if i, err := strconv.Atoi(aid); err == nil && i > 2 {
			p.Aid = "2"
		}
	}
	if p.Ps == "" {
		p.Ps = p.Add
	}

	if uniq && s.hasVM(p) {
		return nil
	}

	s.Append(&vmessLinkP{*p, -1, "", ""})
	return nil
}

func (s *vmSubs) hasVM(v *vmess.VmessLink) bool {
	for _, o := range *s {
		if o.IsEqual(v) {
			return true
		}
	}

	return false
}
