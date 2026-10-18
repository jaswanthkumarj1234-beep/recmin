#!/usr/bin/env python3
"""Static checks for the recmin site. Standard library only, so it runs anywhere (CI, Docker, laptop).

Usage: python tests/check_site.py [site_dir]
Exit code is 0 when every check passes, 1 otherwise.
"""
import re
import sys
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).resolve().parent.parent
failures = []
passed = 0


def check(name, ok, detail=""):
    global passed
    if ok:
        passed += 1
        print(f"PASS  {name}")
    else:
        failures.append(name)
        print(f"FAIL  {name} {detail}")


class Tags(HTMLParser):
    VOID = {"meta", "link", "input", "br", "img", "hr"}

    def __init__(self):
        super().__init__()
        self.stack, self.errors, self.ids, self.scripts = [], [], [], []
        self._in_script = False

    def handle_starttag(self, tag, attrs):
        d = dict(attrs)
        if "id" in d:
            self.ids.append(d["id"])
        if tag == "script" and "src" not in d:
            self._in_script = True
            self.scripts.append("")
        if tag not in self.VOID:
            self.stack.append(tag)

    def handle_endtag(self, tag):
        if tag == "script":
            self._in_script = False
        if tag in self.VOID:
            return
        if self.stack and self.stack[-1] == tag:
            self.stack.pop()
        else:
            self.errors.append(f"unexpected </{tag}>")

    def handle_data(self, data):
        if self._in_script:
            self.scripts[-1] += data


index = ROOT / "index.html"
check("index.html exists", index.is_file())
if not index.is_file():
    sys.exit(1)
html = index.read_text(encoding="utf-8")

parser = Tags()
parser.feed(html)
check("HTML tags are balanced", not parser.errors and not parser.stack, f"{parser.errors} {parser.stack}")
dupes = {i for i in parser.ids if parser.ids.count(i) > 1}
check("no duplicate element ids", not dupes, str(dupes))

# every $('id') used by the script must exist in the markup
used = set(re.findall(r"\$\('([A-Za-z0-9_-]+)'\)", html))
missing_ids = sorted(used - set(parser.ids))
check("every $('id') in the script exists in the HTML", not missing_ids, str(missing_ids))

check("version label present", re.search(r'<div class="ver">v\d+</div>', html) is not None)
check("reload / close guard (beforeunload) present", "beforeunload" in html)
check("service worker registered", "serviceWorker" in html and (ROOT / "sw.js").is_file())

# voice clips: the same list the app builds in JS
names = ["start", "one", "done"] + [f"c{n}" for n in range(1, 31)]
names += [f"m{m}" for m in range(5, 181, 5)]
missing_clips = [n for n in names if not (ROOT / "clips" / f"{n}.wav").is_file()]
check(f"all {len(names)} voice clips exist", not missing_clips, str(missing_clips[:10]))
empty = [n for n in names if (ROOT / "clips" / f"{n}.wav").is_file() and (ROOT / "clips" / f"{n}.wav").stat().st_size < 1000]
check("no empty voice clips", not empty, str(empty))

check("offline voice library present", (ROOT / "vosk" / "vosk.js").is_file())
check("offline voice model present", (ROOT / "vosk" / "model.tar.gz").is_file())

# the script must be non-trivial and brackets must balance (cheap syntax sanity check)
js = max(parser.scripts, key=len) if parser.scripts else ""
check("inline script found", len(js) > 1000)
stripped = re.sub(r"//[^\n]*|/\*.*?\*/|'(?:\\.|[^'\\\n])*'|\"(?:\\.|[^\"\\\n])*\"|`(?:\\.|[^`\\])*`", "", js, flags=re.S)
stripped = re.sub(r"/(?![*/])(?:\\.|[^/\\\n])+/[gimsuy]*", "", stripped)
for a, b in ("()", "{}", "[]"):
    check(f"script brackets balanced {a}{b}", stripped.count(a) == stripped.count(b), f"{stripped.count(a)} vs {stripped.count(b)}")

print(f"\n{passed} passed, {len(failures)} failed")
sys.exit(1 if failures else 0)
