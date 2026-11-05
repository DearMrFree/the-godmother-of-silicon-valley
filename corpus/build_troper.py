#!/usr/bin/env python3
"""Build troper.json and troper.csv: published pages about or mentioning Marco Troper (2004-2024).
Input: harvest/troper_checked.json, made by harvest/troper_check.py on 2026-11-05."""
import csv, json, os, re, urllib.parse
from collections import Counter
HERE = os.path.dirname(os.path.abspath(__file__))
R = json.load(open(os.path.join(HERE, "harvest", "troper_checked.json"), encoding="utf8"))
host = lambda u: urllib.parse.urlsplit(u).netloc.lower().replace("www.", "").replace("m.economictimes", "economictimes")
ABOUT = re.compile(r"marco|troper|trooper|\bson\b|son's|hijo|filho|sohn|figlio|\bsyn\b|19-l|19歲|兒|grandson|fils|19-year|teen|student|19yo|tragedy", re.I)
LOW = {"naturalnews.com": "Natural News network site that mixes the report with unsupported claims.",
       "techgiants.news": "Natural News network site that mixes the report with unsupported claims.",
       "scallywagandvagabond.com": "Gossip site; its headline speculates about fentanyl, which the toxicology report did not find.",
       "ussanews.com": "Aggregator; the site could not be reached for this check."}
SKIP = re.compile(r"ilfattoquotidiano\.it/2024/02/19/filma|wikitree|aol\.com/news|bolnews|jiacaigang|marcosmission\.org/(team|what-we-do)")
def kind(h, u):
    if "youtube.com" in h or "tiktok.com" in h: return "Video"
    if "linkedin.com" in h: return "Social post"
    if h in ("marcosmission.org",): return "Memorial nonprofit"
    if h in ("findagrave.com",): return "Memorial page"
    if "berkeley.edu" in h: return "University"
    if h in ("menlocoa.org", "dailycal.org"): return "Student press"
    if "wikipedia" in h: return "Encyclopedia"
    return "News"
def clean(t):
    t = re.sub(r"\s+", " ", t or "").strip()
    t = re.sub(r"\s+[-|–]\s+(YouTube|The Almanac|Redwood City Pulse|Fortune|Business Insider|Los Angeles Times|Hindustan Times|Times Now|HuffPost Latest News|FOX 10 Phoenix|KTVU FOX 2|Dexerto|The Star|NBC Los Angeles|CBS San Francisco|Republic World|Fox Business|WSVN 7News.*|The Economic Times|Orange County Register|Palo Alto Online|Palo Alto Daily Post|Pa.*Post|Blesk\.cz|GALA\.de|TN|LA NACION|Primera Hora|Grupo Milenio|AhoraMismo\.com|Super Express.*|Dzień Dobry TVN|Pomponik w INTERIA\.PL|Viva\.pl|Bus.*|The M.*|ABC7.*|ABC11.*|Berkeley Inspire|Letters & Science|BILD\.de|FOCUS online|Today News|LINE TODAY|TVBS|The Coat of Arms|Yahoo News Canada|Daily Mail Online)$", "", t)
    return re.sub(r"\s*\|\s*(Leben & Wissen|Hindustan Times|Fox Business|TVBS)$", "", t).strip(" -|")
out, seen = [], set()
for r in R:
    u = r.get("final") or r["url"]; h = host(u)
    if SKIP.search(u): continue
    t = clean(r.get("page_title") or r.get("title") or "")
    if r.get("ok") and r.get("marco"):
        status = "opened"
    elif r.get("ok") and re.search(r"trooper|\bson\b|her son", t, re.I) and "youtube" not in h or (r.get("ok") and "youtube" in h and re.search(r"\bson\b", t, re.I)):
        status = "opened"
    elif not r.get("ok") and re.search(r"son|hijo|filho|fils|syn|Troper|19", r.get("title") or "", re.I) and not re.search(r"Dying of Cancer|Former CEO of YouTube, Dies|politico", (r.get("title") or "") + u):
        status = "listed"; t = clean(re.sub(r"\s+-\s+[^-]+$", "", r.get("title") or "")) or t
    else:
        continue
    if not t and "paloaltoonline.com/wp-content" in u: t = "Palo Alto Weekly print edition, March 29, 2024"
    key = re.sub(r"[^a-z0-9]", "", t.lower())[:70]
    if key in seen: continue
    seen.add(key)
    d = r.get("date") or ""
    if not d and r.get("gdate"):
        import email.utils; d = email.utils.parsedate_to_datetime(r["gdate"]).strftime("%Y-%m-%d")
    if "nypost.com/2024/02/20" in u: d = d or "2024-02-20"
    e = dict(date=d, kind=kind(h, u), title=t, site=(r.get("channel") + " on YouTube") if "youtube" in h and r.get("channel") else (r.get("source") or h) if status == "listed" else h,
             url=u, status=status, about=1 if ABOUT.search(t + " " + u) else 0, cheteni=1 if r.get("fc") else 0, esther=1 if r.get("esther") else 0,
             note=LOW.get(h, ""))
    if e["kind"] == "Social post": e["note"] = "Freedom Cheteni's own LinkedIn post."
    if status == "listed": e["note"] = (e["note"] + " " if e["note"] else "") + "The site refused the automated check; title and date are from Google News or search results."
    out.append(e)
# Added by hand: pages the name check missed.
for e in [dict(date="2024-02-17", kind="Social post", title="Marco and Benji Wojin. Love these kids and their liveliness. #DearMrFree #Kindness", site="linkedin.com", url="https://www.linkedin.com/posts/superintendents_marco-and-benji-wojin-love-these-kids-and-activity-7164448664772435968-siUC", status="opened", about=1, cheteni=1, esther=0, note="Freedom Cheteni's own LinkedIn post. It names Marco by first name only, so the automated check missed it."),
          dict(date="2024-05-30", kind="Video", title="Marco Troper, the 19-year-old son of former YouTube CEO Susan Wojcicki, has died of an accidental overdose", site="Daily Mail on TikTok", url="https://www.tiktok.com/@dailymail/video/7374854160891645227", status="listed", about=1, cheteni=0, esther=0, note="Title from search results; TikTok did not load for the check. The date is the day the cause of death was reported.")]:
    out.append(e)
for e in out:
    if e["title"].startswith("Palo Alto Weekly print edition"):
        e.update(title="Family, friends mourn Marco Troper (Palo Alto Weekly print edition, March 29, 2024)", date="2024-03-29", about=1)
out.sort(key=lambda e: (e["date"] or "0000", e["title"]), reverse=True)
for n, e in enumerate(sorted(out, key=lambda e: (e["date"] or "9999", e["title"])), 1): e["id"] = f"MT-{n:04d}"
json.dump(out, open(os.path.join(HERE, "troper.json"), "w", encoding="utf8"), ensure_ascii=False, indent=1)
with open(os.path.join(HERE, "troper.csv"), "w", newline="", encoding="utf8") as f:
    w = csv.writer(f); w.writerow("id date kind title site url status about cheteni esther note".split())
    for e in out: w.writerow([e[k] for k in "id date kind title site url status about cheteni esther note".split()])
print(len(out), "pages", dict(Counter(e["kind"] for e in out)), "about", sum(e["about"] for e in out), "cheteni", sum(e["cheteni"] for e in out), "esther", sum(e["esther"] for e in out), "listed", sum(e["status"] == "listed" for e in out))
