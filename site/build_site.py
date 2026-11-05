#!/usr/bin/env python3
"""Embed corpus.json in the template. Writes artifact.html (page body) and index.html (standalone site)."""
import json, os
H = os.path.dirname(os.path.abspath(__file__))
data = json.load(open(os.path.join(H, "..", "corpus", "corpus.json"), encoding="utf8"))
t = open(os.path.join(H, "template.html"), encoding="utf8").read()
m = json.load(open(os.path.join(H, "..", "corpus", "mentions.json"), encoding="utf8"))
m["mentions"] = [{**{k: e[k] for k in ("id", "date", "kind", "title", "site", "url")}, **({"corpus": 1} if e["corpus_id"] else {}), **({"nick": 1} if e["nickname"] else {})} for e in m["mentions"]]
cj = json.load(open(os.path.join(H, "..", "corpus", "cheteni.json"), encoding="utf8"))
pj = json.load(open(os.path.join(H, "..", "corpus", "photos.json"), encoding="utf8"))
t = t.replace("__CHETENI__", json.dumps(cj, ensure_ascii=False).replace("</", "<\\/")).replace("__PHOTOS__", json.dumps(pj, ensure_ascii=False).replace("</", "<\\/"))
page = t.replace("__DATA__", json.dumps(data, ensure_ascii=False).replace("</", "<\\/")).replace("__MENTIONS__", json.dumps(m, ensure_ascii=False).replace("</", "<\\/"))
open(os.path.join(H, "artifact.html"), "w", encoding="utf8").write(page)
open(os.path.join(H, "index.html"), "w", encoding="utf8").write(
    '<!doctype html>\n<html lang="en">\n<meta charset="utf-8">\n<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">\n'
    '<style>html{padding-top:env(safe-area-inset-top,0px);padding-bottom:env(safe-area-inset-bottom,0px)}body{margin:0}[hidden]{display:none!important}img{max-width:100%}</style>\n' + page)
print(len(page), "bytes,", len(data), "records")
