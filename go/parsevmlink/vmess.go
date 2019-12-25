package main

import (
	"sort"
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
