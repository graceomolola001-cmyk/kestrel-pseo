#!/usr/bin/env python3
"""
QA for the built site. Reads the HTML in dist/, not the spreadsheet.

Usage:
    python qa.py            check dist/
    python qa.py path/to/dist

Checks (per page and across pages):
  title        exactly one, present, unique across pages
  description  present, unique, 60 to 160 characters
  h1           exactly one, unique across pages
  canonical    present and pointing to the page's own address
  placeholders no {, }, None, nan or "undefined" left in visible text
  links        every internal link points to a file that exists
  faq markup   if FAQPage JSON-LD exists, every question and answer is visible on the page
  duplicates   no two pages share 4 or more of the 5 data fields
  sitemap      if present, lists exactly the built pages

Exit code 1 if any FAIL. WARN items need a person to look.
Standard library only.
"""
import json
import os
import re
import sys
from urllib.parse import urlparse
from collections import defaultdict
from html.parser import HTMLParser

FIELDS = ["fees", "duration", "intake", "entry", "suits"]


class P(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.title = []; self.in_title = False
        self.meta = {}; self.canonical = None
        self.h1 = []; self.in_h1 = False
        self.hrefs = []; self.fields = {}; self.cur = None
        self.ld = []; self.in_ld = False
        self.text = []; self.skip = 0

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == "title": self.in_title = True
        if tag == "h1": self.in_h1 = True; self.h1.append("")
        if tag == "meta" and a.get("name"): self.meta[a["name"]] = a.get("content", "")
        if tag == "link" and a.get("rel") == "canonical": self.canonical = a.get("href")
        if tag == "a" and a.get("href"): self.hrefs.append(a["href"])
        if "data-field" in a: self.cur = a["data-field"]; self.fields[self.cur] = ""
        if tag == "script" and a.get("type") == "application/ld+json": self.in_ld = True; self.ld.append("")
        if tag in ("script", "style"): self.skip += 1

    def handle_endtag(self, tag):
        if tag == "title": self.in_title = False
        if tag == "h1": self.in_h1 = False
        if tag in ("dd", "p") and self.cur: self.cur = None
        if tag == "script": self.in_ld = False
        if tag in ("script", "style"): self.skip -= 1

    def handle_data(self, d):
        if self.in_title: self.title.append(d)
        if self.in_h1 and self.h1: self.h1[-1] += d
        if self.cur: self.fields[self.cur] += d
        if self.in_ld and self.ld: self.ld[-1] += d
        if not self.skip: self.text.append(d)


def main(dist):
    pages = []
    for root, _, files in os.walk(dist):
        for f in files:
            if f.endswith(".html"):
                pages.append(os.path.join(root, f))
    if not pages:
        print("FAIL  no HTML files found in " + dist)
        return 1
    fails, warns = [], []

    prefix = ""
    home = os.path.join(dist, "index.html")
    if os.path.isfile(home):
        hp = P(); hp.feed(open(home, encoding="utf-8").read())
        if hp.canonical:
            prefix = urlparse(hp.canonical).path.rstrip("/")

    def rel(p): return "/" + os.path.relpath(p, dist).replace(os.sep, "/").replace("index.html", "")
    data = {}
    for p in sorted(pages):
        ps = P(); ps.feed(open(p, encoding="utf-8").read()); data[p] = ps

    titles, descs, h1s = defaultdict(list), defaultdict(list), defaultdict(list)
    for p, ps in data.items():
        u = rel(p)
        t = "".join(ps.title).strip()
        if not t: fails.append(f"{u}: missing title")
        titles[t].append(u)
        d = ps.meta.get("description", "").strip()
        if not d: fails.append(f"{u}: missing meta description")
        elif not 60 <= len(d) <= 160: warns.append(f"{u}: description is {len(d)} characters")
        descs[d].append(u)
        if len(ps.h1) != 1: fails.append(f"{u}: expected one h1, found {len(ps.h1)}")
        else: h1s[ps.h1[0].strip()].append(u)
        if not ps.canonical: fails.append(f"{u}: missing canonical")
        elif urlparse(ps.canonical).path != (prefix + u):
            fails.append(f"{u}: canonical {ps.canonical} does not match the page address")
        if "robots" not in ps.meta: warns.append(f"{u}: no robots meta tag")
        visible = " ".join(ps.text)
        if re.search(r"[{}]|\bNone\b|\bnan\b|undefined", visible):
            fails.append(f"{u}: placeholder text left on page")
        for h in ps.hrefs:
            if h.startswith(("http://", "https://", "mailto:", "#")): continue
            if prefix and h.startswith(prefix + "/"):
                h = h[len(prefix):]
            elif prefix and h.startswith("/"):
                fails.append(f"{u}: link {h} ignores the base path {prefix}"); continue
            target = os.path.join(dist, *h.split("#")[0].strip("/").split("/"))
            if not (os.path.isfile(target) or os.path.isfile(os.path.join(target, "index.html"))):
                fails.append(f"{u}: broken internal link {h}")
        for block in ps.ld:
            try:
                j = json.loads(block)
            except Exception:
                fails.append(f"{u}: JSON-LD is not valid JSON"); continue
            if j.get("@type") == "FAQPage":
                norm = lambda s: re.sub(r"\s+", " ", s).strip()
                vis = norm(visible)
                for q in j.get("mainEntity", []):
                    if norm(q["name"]) not in vis or norm(q["acceptedAnswer"]["text"]) not in vis:
                        fails.append(f"{u}: FAQ markup text is not visible on the page: {q['name']}")

    for label, bucket in (("title", titles), ("description", descs), ("h1", h1s)):
        for val, urls in bucket.items():
            if val and len(urls) > 1:
                fails.append(f"duplicate {label} on {len(urls)} pages: {urls[0]} and others")

    prog = [(rel(p), ps) for p, ps in data.items() if all(f in ps.fields for f in FIELDS)]
    for i in range(len(prog)):
        for j in range(i + 1, len(prog)):
            same = [f for f in FIELDS if prog[i][1].fields[f].strip() == prog[j][1].fields[f].strip()]
            if len(same) >= 4:
                warns.append(f"near-duplicate pages: {prog[i][0]} and {prog[j][0]} share {', '.join(same)}")

    sm = os.path.join(dist, "sitemap.xml")
    if os.path.isfile(sm):
        locs = re.findall(r"<loc>(.*?)</loc>", open(sm, encoding="utf-8").read())
        listed = sorted(urlparse(l).path[len(prefix):].strip("/") if urlparse(l).path.startswith(prefix) else urlparse(l).path.strip("/") for l in locs)
        built = sorted(rel(p).strip("/") for p, ps in data.items() if all(f in ps.fields for f in FIELDS))
        if listed != built:
            fails.append(f"sitemap lists {len(listed)} URLs but {len(built)} programme pages were built")
        for p, ps in data.items():
            if "noindex" in ps.meta.get("robots", ""):
                fails.append(f"{rel(p)}: page is noindex but a sitemap exists")
    elif any("noindex" not in ps.meta.get("robots", "noindex") for ps in data.values()):
        warns.append("pages are indexable but there is no sitemap.xml")

    for w in warns: print("WARN  " + w)
    for f in fails: print("FAIL  " + f)
    print(f"\n{len(pages)} pages checked. {len(fails)} FAIL, {len(warns)} WARN.")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1] if len(sys.argv) > 1 else "dist"))
