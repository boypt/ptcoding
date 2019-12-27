package main

import (
	"sort"
	"strconv"
	"strings"

	"github.com/v2fly/vmessping/vmess"
)

type VmSubs []*vmess.VmessLink

func (s *VmSubs) Sort() {
	sort.SliceStable(*s, func(i, j int) bool {
		return strings.Compare((*s)[i].Ps, (*s)[j].Ps) < 0
	})
}

func (s *VmSubs) Append(v *vmess.VmessLink) {
	*s = append(*s, v)
}

func (s *VmSubs) Add(vm string, uniq bool) error {
	p, err := vmess.ParseVmess(vm)
	if err != nil {
		return err
	}
	p.OrigLink = vm

	// attr amends
	if i, err := strconv.Atoi(p.Aid); err == nil && i > 2 {
		p.Aid = "2"
	}
	if p.Ps == "" {
		p.Ps = p.Add
	}

	if uniq && s.hasVM(p) {
		return nil
	}

	s.Append(p)
	return nil
}

func (s *VmSubs) hasVM(v *vmess.VmessLink) bool {
	for _, o := range *s {
		if o.IsEqual(v) {
			return true
		}
	}

	return false
}
