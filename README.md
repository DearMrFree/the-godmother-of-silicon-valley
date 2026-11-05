# The Godmother of Silicon Valley

An independent research archive of work by, with and about Esther Wojcicki. It is not an official site. It holds citations and original summaries, not the source works.

- `site/index.html`: standalone website. Open it in a browser or host it anywhere.
- `corpus/corpus.json`, `corpus/corpus.csv`: the dataset, one record per item, with WOJ IDs.
- `corpus/mentions.json`, `corpus/mentions.csv`: separate database of pages that name her, with MEN IDs.
- `corpus/build_mentions.py`: filters checked pages into the mentions database. `corpus/harvest/` holds the scripts and the check results.
- `corpus/entries_manual.py`: hand-compiled records. Add new records here.
- `corpus/entries_cheteni.py`, `corpus/build_cheteni.py`: Freedom Cheteni's publications, talks, projects and code, plus photos of Esther Wojcicki and Freedom Cheteni. Builds `corpus/cheteni.json`, `corpus/cheteni.csv` and `corpus/photos.json`, gathered as source material for the planned book *Raising Humans in the Age of AI*.
- `corpus/build_troper.py`: builds `corpus/troper.json` and `corpus/troper.csv`, published pages about or mentioning Marco Troper, from `corpus/harvest/troper_checked.json` (made by `troper_gnews.py` and `troper_check.py`).
- `corpus/entries_wojway.py`: records focused on The Woj Way, with notes on who published each.
- `corpus/build_corpus.py`: merges records and HuffPost columns.
- `site/build_site.py`: rebuilds the site from the corpus.

To rebuild after adding records:

    python3 corpus/build_corpus.py && python3 corpus/build_cheteni.py && python3 corpus/build_troper.py && python3 corpus/build_mentions.py && python3 site/build_site.py

IDs are assigned by date order, so adding records can renumber them. Freeze the IDs before citing them externally.

The archive holds citations and original summaries only. It does not republish source text.

## Source check

`corpus/verification.py` holds the results of checking the 67 records that began as search hits, keyed by each record's original URL. `build_corpus.py` applies it and stops if a search-hit record has no entry. Add new search hits there once they have been checked.

## Mentions database

`corpus/harvest/` holds the collection scripts and `checked_pages.json`, the result of opening each candidate link on 2026-11-04. Candidates came from Google News, GDELT, DuckDuckGo, Bing, publisher site search, YouTube, Apple Podcasts, Wikipedia, Hacker News and links on pages already found. A page counts only if a script found her full name or the nickname "Godmother of Silicon Valley" (including translations) in its text and the page is not her own site or byline, a mirror, retailer, listing page, sidebar link or syndicated copy. It has not been read page by page by a person, a mention may be brief, and sites that block scripts are undercounted.

The nickname has also been applied to other people, so a page with the nickname but not her name is kept only if listed in `NICK_ONLY` in `build_mentions.py`. Every YouTube candidate was checked against its title and description, not its spoken content.
