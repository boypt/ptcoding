package main

import (
	"github.com/v2fly/vmessping/vmess"
)

type VmSubs []*vmess.VmessLink

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
