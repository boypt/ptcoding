#!/usr/bin/perl -w
#
# Written by AutumnCat.
#

use strict;
use Getopt::Long;
require LWP::UserAgent;

my $help_message = <<HELP;
upaste: Paste text and images to http://paste.ubuntu.org.cn.

Usage:
    upaste [OPTION]... [FILES]...

Options:
    -lang LANGUAGE  set the language used for highlighting.
    -image FILE     screenshot image to upload.
    -name NAME      poster's name.
    -verbose        also print the urls of image and text files.
    -help           show this message.

If FILES is not specified or FILES is - , message will be read from standard input.

Available languages for the LANGUAGE argument:
    actionscript            ActionScript
    actionscript-french     ActionScript (French Doc Links)
    ada                     Ada
    apache                  Apache Log File
    applescript             AppleScript
    asm                     ASM (NASM based)
    asp                     ASP
    autoit                  AutoIT
    bash                    Bash
    blitzbasic              BlitzBasic
    c                       C
    c_mac                   C for Macs
    caddcl                  CAD DCL
    cadlisp                 CAD Lisp
    cfdg                    CFDG
    cpp                     C++
    csharp                  C#
    css                     CSS
    d                       D
    delphi                  Delphi
    diff                    Diff
    div                     DIV
    dos                     DOS
    eiffel                  Eiffel
    fortran                 Fortran
    freebasic               FreeBasic
    gml                     GML
    html4strict             HTML (4.0.1)
    inno                    Inno
    java                    Java
    java5                   Java 5
    javascript              Javascript
    lisp                    Lisp
    lua                     Lua
    matlab                  Matlab
    mpasm                   MPASM
    mysql                   MySQL
    nsis                    NullSoft Installer
    objc                    Objective C
    ocaml                   OCaml
    ocaml-brief             OCaml (Brief)
    oobas                   Openoffice.org BASIC
    oracle8                 Oracle 8
    pascal                  Pascal
    perl                    Perl
    php                     PHP
    php-brief               PHP (Brief version)
    python                  Python
    qbasic                  QBasic/QuickBASIC
    robots                  robots.txt
    ruby                    Ruby
    sas                     SAS
    scheme                  Scheme
    sdlbasic                SDLBasic
    smarty                  Smarty
    sql                     SQL
    tsql                    T-SQL
    vb                      VisualBasic
    vbnet                   VB.NET
    vhdl                    VHDL
    visualfoxpro            VisualFoxPro
    xml                     XML
HELP

my $poster="";
my $class="actionscript";
my $screenshot="";
my $verbose=0;
my $help=0;
my $optresult = GetOptions (
    "lang=s" => \$class,
    "image=s" => \$screenshot,
    "name=s" => \$poster,
    "verbose" => \$verbose,
    "help" => \$help
);

if ($help) {
    print $help_message;
    exit 0;
}

if (! $optresult) {
    print STDERR $help_message;
    exit 1;
}

# if ( $#ARGV == -1) {
#     print "Reading message from standard input, press CTRL-D to finish.\n";
# }

my @text = <> ;
chomp @text;
my $paste_url = 'http://paste.ubuntu.org.cn/';

my $ua = LWP::UserAgent -> new;
push @{ $ua->requests_redirectable }, 'POST';

my $r = $ua -> post(
    $paste_url,
    Content_Type => 'form-data',
    Content      => [
        paste       => "Send",    
        code2       => join("\n",@text) ,
        class       => $class ,
        screenshot  => [$screenshot] ,
        poster      => $poster
    ]
);
if ($r -> is_success ) {
    exit 1 if ( $paste_url eq ($r -> base) ) ;
    print $r -> base ."\n";
    if ($verbose) {
        if (($r -> content) =~ m'a class="alt" href="/(d\d+)"') {
            print "text:\t".$paste_url.$1."\n";
        }
        if (($r -> content) =~ m'a class="scr" href="/(i\d+)"') {
            print "image:\t".$paste_url.$1.".png\n";
        }
    }
} else {
    print STDERR "ERROR:\t".$r->status_line ."\n";
}