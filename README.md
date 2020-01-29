# Xarta

A work-in-progress command-line tool for organising papers from the arXiv.

This is a lightweight tool that I use to organise my reading. Almost all of the
papers I read are on the arXiv, and therefore there is no need for me to keep a
local copy of my library on my machine. I want to add a similar interface to the
CERN document server as well at some stage.

Suppose you want to keep the paper database in your Dropbox. Initialise it with
```
xarta init ~/Dropbox/
```
and add a paper to your library with tags by topic or project:
```
xarta add 1704.05849 --tag neutrino-mass --tag flavour-anomalies
```
Now, `xarta browse --all` lists all of the papers in your library.
Alternatively, you can browse by specific paper attributes, taken to be
connected by logical disjunction. For example,
```
xarta browse --tag neutrino-mass --author Weinberg
```
will return all papers by Weinberg as well as those with the `neutrino-mass`
tag. For complex queries, use the `--filter` option:
```
xarta browse --filter "'neutrino-mass' in tags and 'Weinberg' in authors"
```

You can also export your library to a bibtex file.

A summary of the options that are working now:
```
Usage:
  xarta init <database-location>
  xarta open <ref> [--pdf]
  xarta add <ref> [--tag=<tg>]...
  xarta delete <ref>
  xarta edit <ref> [--tag=<tg>]...
  xarta browse [--all] [--author=<auth>] [--tag=<tg>]... [--title=<ttl>] [--ref=<ref>] [--category=<cat>] [--filter=<fltr>]
  xarta lucky [--author=<auth>] [--tag=<tg>]... [--title=<ttl>] [--pdf]
  xarta choose [--author=<auth>] [--tag=<tg>]... [--title=<ttl>] [--ref=<ref>] [--category=<cat>] [--filter=<fltr>] [--pdf]
  xarta info <ref>
  xarta list <obj> [--contains=<cont>]
  xarta export <export-path> [--tag=<tg>]... [--bibtex]
  xarta -h | --help
  xarta --version
```

Pronounce the "x" as a voiceless velar fricative or plosive, as you like.
