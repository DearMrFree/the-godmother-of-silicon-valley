#!/usr/bin/env python3
"""Build cheteni.json, cheteni.csv and photos.json from entries_cheteni.py."""
import csv, json, os
from collections import Counter
HERE = os.path.dirname(os.path.abspath(__file__))
ns = {}
exec(open(os.path.join(HERE, "entries_cheteni.py"), encoding="utf8").read(), ns)
C, P = ns["C"], ns["P"]
dup = [u for u, n in Counter(e["url"] for e in C).items() if n > 1 and "sof.ai" not in u]
assert not dup, dup
C.sort(key=lambda e: (e["date"] or "0000", e["title"]), reverse=True)
for n, e in enumerate(sorted(C, key=lambda e: (e["date"] or "9999", e["title"])), 1):
    e["id"] = f"FC-{n:04d}"
P.sort(key=lambda e: (-e["both"], e["date"]))
for n, e in enumerate(P, 1):
    e["id"] = f"IMG-{n:03d}"
json.dump(C, open(os.path.join(HERE, "cheteni.json"), "w", encoding="utf8"), ensure_ascii=False, indent=1)
json.dump(P, open(os.path.join(HERE, "photos.json"), "w", encoding="utf8"), ensure_ascii=False, indent=1)
with open(os.path.join(HERE, "cheteni.csv"), "w", newline="", encoding="utf8") as f:
    w = csv.writer(f); w.writerow("id date role type title venue url status woj ai topics summary note".split())
    for e in C: w.writerow([e["id"], e["date"], e["role"], e["type"], e["title"], e["venue"], e["url"], e["status"], e["woj"], e["ai"], ";".join(e["topics"]), e["summary"], e["note"]])
print(len(C), "records", dict(Counter(e["role"] for e in C)), "woj", sum(e["woj"] for e in C), "ai", sum(e["ai"] for e in C), "|", len(P), "photos", dict(Counter(e["both"] for e in P)))
