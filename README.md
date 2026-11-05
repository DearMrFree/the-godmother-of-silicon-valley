# The Godmother of Silicon Valley

An independent research archive of work by, with and about Esther Wojcicki. It is not an official site. It holds citations and original summaries, not the source works.

- `site/index.html`: standalone website. Open it in a browser or host it anywhere.
- `corpus/corpus.json`, `corpus/corpus.csv`: the dataset, one record per item, with WOJ IDs.
- `corpus/entries_manual.py`: hand-compiled records. Add new records here.
- `corpus/build_corpus.py`: merges records and HuffPost columns.
- `site/build_site.py`: rebuilds the site from the corpus.

To rebuild after adding records:

    python3 corpus/build_corpus.py && python3 site/build_site.py

IDs are assigned by date order, so adding records can renumber them. Freeze the IDs before citing them externally.

The archive holds citations and original summaries only. It does not republish source text.

## Source check

`corpus/verification.py` holds the results of checking the 67 records that began as search hits, keyed by each record's original URL. `build_corpus.py` applies it and stops if a search-hit record has no entry. Add new search hits there once they have been checked.
