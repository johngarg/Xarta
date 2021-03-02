# Xarta

A work-in-progress command-line tool for organising papers from the arXiv.

This is a lightweight tool that I use to organise my reading. Almost all of the
papers I read are on the arXiv, and therefore there is no need for me to keep a
local copy of my library on my machine. I want to add a similar interface to the
CERN document server as well at some stage.

Suppose you want to keep the paper database in your Dropbox. Initialise it with
```
xarta init ~/Dropbox/xarta.db
```
and add a paper to your library with kebab-case tags by topic or project:
```
xarta add 1704.05849 neutrino-mass flavour-anomalies
```
Now, `xarta browse` lists all of the papers in your library.
Alternatively, you can browse by specific paper attributes, like
```
xarta browse neutrino-mass
xarta browse --author Weinberg
```
For complex queries, use the `--filter` option:
```
xarta browse --filter "'neutrino-mass' in tags and 'Weinberg' in authors"
```

The `xarta choose` command is similar to browse but allows you to open the paper
in your browser with a key press.

You can also export your whole library to a bibtex file, or just a subset of
papers filtered by tags, authors, category, etc.

A summary of the options that are working now:
```
Usage:
  xarta open <ref> [--pdf]
  xarta init [<database-file>]
  xarta add <ref> [--alias=<alias>] [<tag> ...]
  xarta delete <ref>
  xarta info <ref>
  xarta browse [--author=<auth>] [--title=<ttl>] [--ref=<ref>]
               [--category=<cat>] [--filter=<fltr>] [<tag> ...]
  xarta choose [--author=<auth>] [--title=<ttl>] [--ref=<ref>]
               [--category=<cat>] [--filter=<fltr>] [--pdf] [<tag> ...]
  xarta export (arxiv|inspire) <bibtex-file> [--export-alias] [--author=<auth>]
               [--title=<ttl>] [--ref=<ref>] [--category=<cat>]
               [--filter=<fltr>] [<tag> ...]
  xarta list (authors|tags|aliases) [--sort=<order>] [--contains=<cont>]
  xarta lucky [--author=<auth>] [--title=<ttl>] [--pdf] [<tag> ...]
  xarta tags (set|add|remove) <ref> [<tag> ...]
  xarta alias <ref> [<alias>]
  xarta rename <tag> [<tag>]
  xarta refresh <ref>
  xarta -h | --help
  xarta --version
```

Pronounce the "x" as a voiceless velar fricative or plosive, as you like.
