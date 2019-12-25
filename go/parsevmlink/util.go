package main

import (
	"regexp"
	"strings"

	strip "github.com/grokify/html-strip-tags-go"
)

func trimDescription(desc string) string {
	return strings.Trim(
		strip.StripTags(
			regexp.MustCompile(`\n+`).ReplaceAllLiteralString(
				strings.ReplaceAll(
					regexp.MustCompile(`<br(| /)>`).ReplaceAllString(desc, "<br>"),
					"<br>", "\n"),
				"\n")),
		"\n")
}
