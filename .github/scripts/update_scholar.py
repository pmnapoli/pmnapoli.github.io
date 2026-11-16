"""Refresh the Google Scholar figures on index.html (citations, h-index, date checked).

Reads Philip M. Napoli's public Scholar profile. If Scholar can't be read or the numbers look
wrong, the page is left as it is, so a blocked request never blanks or lowers the figures.
"""
import datetime
import re
import sys
import urllib.request

PROFILE = "https://scholar.google.com/citations?user=Uft1VUYAAAAJ&hl=en"
PAGE = sys.argv[1] if len(sys.argv) > 1 else "index.html"


def fetch():
    req = urllib.request.Request(PROFILE, headers={
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 "
                      "(KHTML, like Gecko) Version/17.0 Safari/605.1.15",
        "Accept-Language": "en-US,en;q=0.9",
    })
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.read().decode("utf-8", "replace")


def main():
    try:
        html = fetch()
    except Exception as e:  # blocked, rate-limited or offline: keep the current figures
        print(f"::warning::Google Scholar could not be read ({e}); figures left unchanged")
        return
    cells = re.findall(r'class="gsc_rsb_std">(\d+)<', html)
    if len(cells) < 3:
        print("::warning::Google Scholar returned no citation table (possibly a CAPTCHA); figures left unchanged")
        return
    citations, h_index = int(cells[0]), int(cells[2])
    if citations < 1000 or not 10 <= h_index <= 500:
        print(f"::warning::Implausible figures ({citations}, {h_index}); figures left unchanged")
        return

    page = open(PAGE, encoding="utf-8").read()
    today = datetime.date.today()
    label = f"{today:%B} {today.day}, {today.year}"
    new = re.sub(r'(<strong id="scholar-citations">)[^<]*(</strong>)', rf"\g<1>{citations:,}\g<2>", page)
    new = re.sub(r'(<strong id="scholar-h">)[^<]*(</strong>)', rf"\g<1>{h_index}\g<2>", new)
    new = re.sub(r'<time id="scholar-date" datetime="[^"]*">[^<]*</time>',
                 f'<time id="scholar-date" datetime="{today.isoformat()}">{label}</time>', new)
    if new == page:
        print("No change")
        return
    open(PAGE, "w", encoding="utf-8").write(new)
    print(f"Updated: {citations:,} citations, h-index {h_index}, checked {label}")


if __name__ == "__main__":
    main()
