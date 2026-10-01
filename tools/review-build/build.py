"""Build the review site "Home Page Redesign" — V2 alone, on its own Vercel project.

Copies index.html + js/ + assets/ (minus the icon archive) into OUT, then:
  1. pins the page to V2 before either `?v=` reader runs (any other v, or none, becomes 2);
  2. swaps the menu's "Home page" version rows for a "Header style" pick (Climate / Plain),
     so reviewers cannot leave V2 but can choose the header;
  3. retitles the tab;
  4. layers review.css (Figma 816:3 header, 829:595 site chips, 816:143 View all) on top,
     and swaps both "View all" chevrons for the node's double chevron.
The main app (antz-module-selection-home) is untouched.
Usage: python3 tools/review-build/build.py OUT_DIR
"""
import re, shutil, sys, pathlib
ROOT = pathlib.Path(__file__).resolve().parents[2]
OUT = pathlib.Path(sys.argv[1]).resolve()
# keep .vercel (the project link) and .env.local; everything else is rebuilt
OUT.mkdir(parents=True, exist_ok=True)
for k in OUT.iterdir():
    if k.name in ('.vercel', '.env.local'): continue
    shutil.rmtree(k) if k.is_dir() else k.unlink()
shutil.copytree(ROOT / 'js', OUT / 'js')
shutil.copytree(ROOT / 'assets', OUT / 'assets', ignore=shutil.ignore_patterns('icon.zip', '.DS_Store'))
html = (ROOT / 'index.html').read_text()

def sub(old, new, count=1):
    global html
    assert html.count(old) == count, (old[:60], html.count(old))
    html = html.replace(old, new)

sub('<title>ANTZ Command Centre · Home</title>', '<title>Home Page Redesign · ANTZ</title>')
PIN = ("<script>document.documentElement.dataset.review='1';document.documentElement.dataset.profileDrawer='1';try{var u=new URL(location.href);if(u.searchParams.get('v')!=='2'){"
       "u.searchParams.set('v','2');history.replaceState(null,'',u.pathname+u.search+u.hash)}}catch(e){}"
       # the header style: plain by default, climate when the reader chose it (kept per device)
       "try{if(localStorage.getItem('rv-hdr')==='climate')document.documentElement.dataset.hdrStyle='climate'}catch(e){}"
       "window.__rvHdr=function(v){var r=document.documentElement;if(v==='climate')r.dataset.hdrStyle='climate';else delete r.dataset.hdrStyle;"
       "try{localStorage.setItem('rv-hdr',v)}catch(e){}dispatchEvent(new Event('resize'))};</script>\n")
m = re.search(r'<head[^>]*>\n?', html); html = html[:m.end()] + PIN + html[m.end():]
rows = re.search(r"\n\s*null,\n\s*\{ heading: 'Home page' \},.*?note: 'Version 2 under the tabbed header[^\n]*\n", html, re.S)
assert rows, 'version rows not found'
# in their place, the header style (the reader's choice; see review.css)
HDR = ("\n        null,\n        { heading: 'Background' },\n"
       "        { id: 'hdr:climate', label: 'Climate', checked: document.documentElement.dataset.hdrStyle === 'climate',\n"
       "          note: 'The live weather sky: sun, rain and cloud as they are now' },\n"
       "        { id: 'hdr:plain', label: 'Plain', checked: document.documentElement.dataset.hdrStyle !== 'climate',\n"
       "          note: 'A still cream-to-mint header' },\n")
html = html[:rows.start()] + HDR + html[rows.end():]
sub("    if (id.startsWith('ver:')) { setPageVersion(id.slice(4)); return }",
    "    if (id.startsWith('ver:')) { setPageVersion(id.slice(4)); return }\n    if (id.startsWith('hdr:')) { window.__rvHdr(id.slice(4)); return }")
HERE = pathlib.Path(__file__).resolve().parent
shutil.copy(HERE / 'assets' / 'rv-chevron2.svg', OUT / 'assets' / 'icon' / 'rv-chevron2.svg')
shutil.copy(HERE / 'review.css', OUT / 'review.css')
CHEV = 'assets/icon/rv-chevron2.svg'
sub('View all<img src="assets/icon/adeck-chevron.svg" alt="" width="14" height="14">',
    f'View all<img class="rv-chev" src="{CHEV}" alt="" width="8" height="9">')
sub("arrow.src = 'assets/icon/v2-chevron-grey.svg'; arrow.width = 16; arrow.height = 16",
    f"arrow.src = '{CHEV}'; arrow.width = 8; arrow.height = 9; arrow.className = 'rv-chev'")
sub('</head>', '<link rel="stylesheet" href="review.css">\n</head>')
# "Header label make it My species" (owner, 30 Sep 2026) — the favourites band's title
sub("if (isV2()) root.querySelector('.fav__title').textContent = 'My Favourites'",
    "if (isV2()) root.querySelector('.fav__title').textContent = 'My species'")
(OUT / 'index.html').write_text(html)
(OUT / 'vercel.json').write_text('{"cleanUrls": true}\n')
print('built', OUT)
