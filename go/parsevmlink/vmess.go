package main

import (
	"encoding/base64"
	"encoding/json"
	"fmt"
	"strings"
)

type VmessLink struct {
	Add      string      `json:"add,omitempty"`
	Aid      string      `json:"aid,omitempty"`
	Host     string      `json:"host,omitempty"`
	ID       string      `json:"id,omitempty"`
	Net      string      `json:"net,omitempty"`
	Path     string      `json:"path,omitempty"`
	Port     interface{} `json:"port,omitempty"`
	Ps       string      `json:"ps,omitempty"`
	TLS      string      `json:"tls,omitempty"`
	Type     string      `json:"type,omitempty"`
	OrigLink string      `json:"-"`
}

func (v VmessLink) String() string {
	return fmt.Sprintf("%s|%s|%s  (%s)", v.Net, v.Add, v.Port, v.Ps)
}

func (v *VmessLink) IsEqual(c *VmessLink) bool {
	return v.Add == c.Add && v.Aid == c.Aid &&
		v.Host == c.Host && v.ID == c.ID &&
		v.Net == c.Net && v.Path == c.Path &&
		v.Port == c.Port && v.TLS == c.TLS &&
		v.Type == c.Type
}

type VmSubs []*VmessLink

func (s *VmSubs) Add(vmess string) error {
	p, err := parseVmess(vmess)
	if err != nil {
		return err
	}
	p.OrigLink = vmess

	*s = append(*s, p)
	return nil
}

func (s *VmSubs) HasVM(vmess string) bool {
	if len(*s) == 0 {
		return false
	}
	p, err := parseVmess(vmess)
	if err != nil {
		return false
	}

	for _, o := range *s {
		if o.IsEqual(p) {
			return true
		}
	}

	return false
}

func parseVmess(vmess string) (*VmessLink, error) {

	b64 := vmess[8:]
	if len(b64)/4 != 0 {
		b64 += strings.Repeat("=", len(b64)%4)
	}

	b, err := base64.StdEncoding.DecodeString(b64)
	if err != nil {
		return nil, err
	}

	v := &VmessLink{}
	if err := json.Unmarshal(b, v); err != nil {
		return nil, err
	}

	return v, nil
}
