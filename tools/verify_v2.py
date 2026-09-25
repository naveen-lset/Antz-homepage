"""The second home page — Figma nodes 236:6669, 270:4176 and 280:3521 — and the
widgets on it.

    python3 tools/verify_v2.py                      # 1024, the app's own width
    python3 tools/verify_v2.py http://host/ 768     # another origin, another width

V2 is `?v=2`: the same application drawing the composition node 236:6669 draws —
no announcement deck, no observation rail, the gradient band re-parented onto
the module grid, and Notes and My Focus Hub seeded into it. 270:4176 set the
four columns and the frame's row order; 280:3521 added Key Insights beside
Hospital, moved Pharmacy and Lab to the foot of the page, and drew the chat
disc beside the Quick Actions pill.

THE INK FOCUS HUB IS NO LONGER SEEDED — the ruling of 8 Sep 2026, "Notes put in
the top, remove that dark blue one". The node drew both compositions of My Focus
Hub at once, which was the file offering a choice; the choice is the plate. The
ink card is still in the catalogue and still addable, so its own geometry is
still worth checking — but only when something has put it on the page, which
this suite no longer does. Those checks are therefore conditional, and the
ruling itself is asserted instead.

TWO KINDS OF CHECK LIVE HERE. The first is that V2 IS V2 and V1 is untouched:
the switch is a URL parameter read in two places, and the failure mode of
getting that wrong is a page that looks fine and is the wrong one. The second is
the three new cards, whose numbers come from the design file rather than from a
node measurement — 4:3 has no meaning here, so what is asserted is the geometry
the file states (a 72 and a 92 photograph, a 44 thumbnail, three updates, the
priority pill) and, at every width, that nothing clips. Clipping is the whole
risk with these two: they are 2x2 compositions and SPAN_TABLE hands them a
single column on a phone.
"""
import json, os, sys, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from cdp import Chrome

BASE = (sys.argv[1] if len(sys.argv) > 1 else "http://127.0.0.1:8000/").rstrip("/") + "/"
WIDTH = int(sys.argv[2]) if len(sys.argv) > 2 else 1024
fails = []

# THE PANEL'S SIXTEEN, IN NODE 635:21410'S OWN WORDING AND ORDER.
# Transcribed from the frame a second time and on purpose: reading the list out
# of index.html would make this assert that the file agrees with itself. The
# order is the node's reading order — down the left column, then the right —
# and it is the order the data states, because on a phone the columns collapse
# into exactly this sequence.
#
# IT REPLACED THE PHONE SHEET'S WORDING ON 23 SEP. "+ Medical" is "New Medical
# Record", "+ Hospitalize" is "Hospitalise" with the node's s, and the leading
# "+" is gone from all sixteen.
SHEET = [
    # Medical & Clinical Care
    "New Medical Record", "Dispense Medicine", "Hospitalise", "Add Fetal Death",
    # Animal Management
    "Transfer Animal", "Add Accession", "Add Eggs", "Report Missing / Escaped Animal",
    # Operations & Administration
    "New Request", "New Note", "New Announcement", "Add User",
    # Site & System Management
    "New Site", "New Section", "New Enclosure", "Master Settings",
]

# The four categories, in the node's own order and with its own fills. The ink
# is stated too — a category is one tone, and a chip that took a colour its
# group did not give it is the failure this is here to catch.
CATS = [
    ("Medical & Clinical Care",     "rgb(232, 244, 242)",  "rgb(31, 81, 91)"),
    ("Animal Management",           "rgb(239, 245, 242)",  "rgb(0, 109, 53)"),
    ("Operations & Administration", "rgba(0, 0, 0, 0.05)", "rgb(68, 84, 74)"),
    ("Site & System Management",    "rgb(225, 249, 237)",  "rgb(0, 109, 53)"),
]


def check(name, ok, detail=""):
    print(f"  {'PASS' if ok else 'FAIL'}  {name}{('  — ' + detail) if detail else ''}")
    if not ok:
        fails.append(name)


def near(a, b, tol=1.0):
    return a is not None and abs(a - b) <= tol


def _sample_tile_separation(chrome):
    """How many levels darker a tile renders than the panel beside it.

    The launcher's tiles were set to `rgba(0, 0, 0, 0.2)` and rendered
    IDENTICAL to the panel — every style check passed and the tiles were
    invisible, because the tile's own `backdrop-filter` made it composite over
    the page rather than over the panel. A declared colour is not a rendered
    one once translucency and backdrop roots are involved, so this samples
    both grounds: inside the first tile, and the gutter between it and the
    second. Returns the mean drop in levels, or None if it cannot sample.
    """
    try:
        from PIL import Image
    except ImportError:
        return None
    import tempfile, os as _os

    box = json.loads(chrome.eval("""(()=>{const b=e=>e.getBoundingClientRect();
      const t=[...document.querySelectorAll('.qa-mod')];
      if(t.length<2) return 'null';
      const r0=b(t[0]), r1=b(t[1]);
      /* only when the two are side by side — at one column t[1] is a row down
         and the "gutter" between them is the whole panel */
      if(Math.abs(r1.top-r0.top)>2) return 'null';
      return JSON.stringify({
        tile:[Math.round(r0.left)+8, Math.round(r0.top)+10,
              Math.round(r0.left)+50, Math.round(r0.bottom)-10],
        gut:[Math.round(r0.right)+3, Math.round(r0.top)+10,
             Math.round(r1.left)-3, Math.round(r0.bottom)-10]})})()"""))
    if not box:
        return None
    fd, path = tempfile.mkstemp(suffix=".png", prefix="qa-sep-")
    _os.close(fd)
    try:
        chrome.screenshot(path)
        im = Image.open(path).convert("RGB")

        def avg(r):
            px = [im.getpixel((x, y))
                  for x in range(max(0, r[0]), min(im.width, r[2]))
                  for y in range(max(0, r[1]), min(im.height, r[3]))]
            if not px:
                return None
            return [sum(p[i] for p in px) / len(px) for i in range(3)]

        tile, gut = avg(box["tile"]), avg(box["gut"])
        if not tile or not gut:
            return None
        return round(sum(g - t for g, t in zip(gut, tile)) / 3)
    finally:
        try:
            _os.unlink(path)
        except OSError:
            pass


def _sample_ink_contrast(chrome, boxes):
    """White label against a TRANSLUCENT tile, measured off the render.

    The launcher's tiles stopped being opaque on 15 Sep (node 371:5441), and a
    translucent ground cannot be measured from `getComputedStyle`: the tile
    reports `rgba(0, 0, 0, 0.2)` whatever it is actually sitting on. The only
    honest read is the composited pixel, so this screenshots the page and
    samples each tile's ground in the strip between the label's right edge and
    the tile's own — clear of the chip, the ink and the rounded corners.

    Returns (worst, best, under_aa, under_3, worst_name), or None if the
    sample cannot be taken. None is reported as a FAILURE by the caller rather
    than skipped: a contrast check that quietly does nothing is how the debt
    got lost the first time.
    """
    try:
        from PIL import Image
    except ImportError:
        return None
    import tempfile, os as _os

    fd, path = tempfile.mkstemp(suffix=".png", prefix="qa-ink-")
    _os.close(fd)
    try:
        chrome.screenshot(path)
        im = Image.open(path).convert("RGB")

        def lin(v):
            v /= 255.0
            return v / 12.92 if v <= 0.04045 else ((v + 0.055) / 1.055) ** 2.4

        def lum(rgb):
            r, g_, b_ = (lin(c) for c in rgb)
            return 0.2126 * r + 0.7152 * g_ + 0.0722 * b_

        out = []
        for t in boxes:
            xs = range(max(0, t["lr"] + 4), min(im.width, t["x"] + t["w"] - 6))
            ys = range(max(0, t["y"] + 10), min(im.height, t["y"] + t["h"] - 10))
            px = [im.getpixel((x, y)) for x in xs for y in ys]
            if not px:
                continue
            avg = tuple(sum(p[i] for p in px) // len(px) for i in range(3))
            lo, hi = sorted((lum(avg) + 0.05, lum((255, 255, 255)) + 0.05))
            out.append((hi / lo, t["name"]))
        if not out:
            return None
        out.sort()
        return (out[0][0], out[-1][0],
                sum(1 for r, _ in out if r < 4.5),
                sum(1 for r, _ in out if r < 3.0),
                out[0][1], len(out))
    finally:
        try:
            _os.unlink(path)
        except OSError:
            pass


PROBE = """(()=>{
  const q=(s)=>document.querySelector(s);
  const shown=(s)=>{const e=q(s); return e ? getComputedStyle(e).display!=='none' : null};
  const cards=[...document.querySelectorAll('#moduleGrid .card')];
  const of=(id)=>cards.find(e=>e.dataset.variant===id) || null;
  const box=(e)=>{if(!e)return null;const r=e.getBoundingClientRect();
    return {w:+r.width.toFixed(1),h:+r.height.toFixed(1)}};
  const sub=(card,s)=>card?box(card.querySelector(s)):null;
  /* THE PAGE ON SCREEN, NOT ALL OF THEM. These cards now hold one element per
     item, so a naive `querySelectorAll` counts three pages' worth of updates
     and compares nine against three. Everything per-item is asked of the
     current page. */
  const at=(card)=>card?card.querySelector('.is-page[data-pos="at"]'):null;
  const nAt=(card,s)=>{const p=at(card); return p?p.querySelectorAll(s).length:0};
  const hub=of('focus.hub'), lite=of('focus.light'), note=of('notes.recent');
  const band=(()=>{const m=q('.modules-band'); if(!m) return null;
    const cs=getComputedStyle(m,'::before'); const r=m.getBoundingClientRect();
    const page=q('.page').getBoundingClientRect();
    return {img:cs.backgroundImage, radius:cs.borderRadius,
            left:+(r.left-page.left).toFixed(1)}})();
  return {
    stamp:document.documentElement.dataset.pageVersion,
    deckShown:shown('.hero-stage'), railShown:shown('.obs-band'),
    deckMounted:document.querySelectorAll('.hero--slide').length,
    railMounted:document.querySelectorAll('.obs').length,
    band,
    /* the section head: gone at rest on V2, back in edit mode */
    head:(()=>{const h=document.getElementById('modulesHead'); if(!h) return null;
      const b=h.querySelector('.link-btn'); if(b) b.focus();
      return {h:+h.getBoundingClientRect().height.toFixed(1),
              vis:getComputedStyle(h).visibility,
              /* a clipped control is still tabbable unless visibility says
                 otherwise — this is the check that caught it */
              focusable:!!b&&document.activeElement===b}})(),
    n:cards.length,
    ids:cards.map(e=>e.dataset.variant),
    /* the LIVE column count, read off the grid rather than off a media query,
       and the rows as drawn — cards grouped by their rendered top edge, which
       is the only place the packer's answer is visible */
    gridCols:getComputedStyle(q('#moduleGrid')).gridTemplateColumns.split(' ').length,
    rows:(()=>{const g=q('#moduleGrid').getBoundingClientRect(); const by=new Map();
      for(const e of cards){const t=Math.round(e.getBoundingClientRect().top-g.top);
        if(!by.has(t)) by.set(t, []); by.get(t).push(e.dataset.variant)}
      return [...by.entries()].sort((a,b)=>a[0]-b[0]).map(([,v])=>v)})(),
    /* KEY INSIGHTS · node 286:3940, the card node 280:3521 added. Everything
       here is either a number the frame states or a relationship the layout
       exists to hold — the ramp reaching the card at all, the figure in the
       library colour it names, and the two tiles carrying two DIFFERENT
       library colours, which is the whole reason they are not one tone. */
    ki:(()=>{const k=of('insights.key'); if(!k) return null;
      const cs=getComputedStyle(k);
      const v=k.querySelector('.l-headline__value');
      const lb=k.querySelector('.l-headline__label');
      const gl=k.querySelector('.c-head__icon img');
      const tiles=[...k.querySelectorAll('.l-headline__tile')];
      const tb=tiles[0]&&getComputedStyle(tiles[0]);
      return {fill:k.dataset.fill, size:k.dataset.size, layout:k.dataset.layout,
        w:+k.getBoundingClientRect().width.toFixed(1),
        h:+k.getBoundingClientRect().height.toFixed(1),
        ramp:cs.backgroundImage.slice(0, 40),
        title:k.querySelector('.c-head__text').textContent,
        glyph:!!gl&&gl.complete&&gl.naturalWidth>0,
        value:v&&v.textContent, valueColor:v&&getComputedStyle(v).color,
        label:lb&&lb.textContent,
        n:tiles.length,
        tiles:tiles.map(t=>({
          label:t.querySelector('.l-headline__tile-label').textContent,
          value:t.querySelector('.l-headline__tile-value').textContent,
          color:getComputedStyle(t.querySelector('.l-headline__tile-value')).color})),
        /* NOT A PLATE · 5% black under a blur, so the ramp still reads */
        tileBg:tb&&tb.backgroundColor,
        tileBlur:tb&&(tb.backdropFilter||tb.webkitBackdropFilter),
        /* the tiles reach half the card's padding from its edge and the head
           reaches a whole one — the frame's own asymmetry */
        tileRight:tiles[0]&&+(k.getBoundingClientRect().right
                              - tiles[0].getBoundingClientRect().right).toFixed(1),
        headLeft:+(k.querySelector('.c-head').getBoundingClientRect().left
                   - k.getBoundingClientRect().left).toFixed(1)}})(),
    three:[hub,lite,note].filter(Boolean).length,
    fills:{hub:hub&&hub.dataset.fill, lite:lite&&lite.dataset.fill, note:note&&note.dataset.fill},
    sizes:{hub:hub&&hub.dataset.size, lite:lite&&lite.dataset.size, note:note&&note.dataset.size},
    hubPhoto:box(at(hub)&&at(hub).querySelector('.l-focus__photo')),
    litePhoto:box(at(lite)&&at(lite).querySelector('.l-focus__photo')),
    noteThumb:box(at(note)&&at(note).querySelector('.l-note__thumb')),
    hubUpdates:nAt(hub,'.l-focus__update'),
    liteUpdates:nAt(lite,'.l-focus__update'),
    hubDots:hub?hub.querySelectorAll('.dots__dot').length:0,
    liteDots:lite?lite.querySelectorAll('.dots__dot').length:0,
    noteDots:note?note.querySelectorAll('.dots__dot').length:0,
    noteRun:note?!!note.querySelector('.dots--run'):false,
    hubBadges:nAt(hub,'.l-focus__tag'),
    /* the badges are ON the photograph here and in the flow there */
    hubBadgesOnPhoto:!!(at(hub)&&at(hub).querySelector('.l-focus__shot .l-focus__badges')),
    liteBadgesInFlow:!!(at(lite)&&at(lite).querySelector('.l-focus__facts .l-focus__badges')),
    /* the ink card's enclosure line, which the plate card does not draw */
    hubRefs:nAt(hub,'.l-focus__ref'),
    liteRefs:nAt(lite,'.l-focus__ref'),
    pri:at(note)?getComputedStyle(at(note).querySelector('.l-note__pri')).backgroundColor:null,
    tint:at(note)?getComputedStyle(at(note).querySelector('.l-note__plate')).backgroundColor:null,
    /* THE CLAMP AND THE BOX HAVE TO AGREE. `-webkit-line-clamp` draws its
       ellipsis at the line it clamps at; a flex parent that compresses the box
       below that never reaches it, so the text is cut mid-line with nothing to
       say so. Reading both means a squeezed box cannot pass as a clamped one. */
    noteClamp:at(note)?+getComputedStyle(at(note).querySelector('.l-note__text')).webkitLineClamp:0,
    noteTextH:at(note)?+box(at(note).querySelector('.l-note__text')).h.toFixed(1):0,
    noteTextSH:at(note)?at(note).querySelector('.l-note__text').scrollHeight:0,
    imgs:[...document.querySelectorAll('#moduleGrid .l-focus__photo,#moduleGrid .l-note__thumb')]
      .every(i=>i.complete&&i.naturalWidth>0),
    /* THE CARD CAN NO LONGER OVERFLOW, so asking whether it does is no longer
       a check. Focus Hub and Notes stack their items absolutely inside a
       `__pages` box, which means content taller than the card grows the PAGE
       and the card's own scrollHeight never moves — the check that caught the
       squeezed note would now pass on a card losing half its content. So every
       page is measured against the box it is absolutely positioned in. */
    clipped:(()=>{const out=[];
      for(const e of cards){
        if(e.scrollHeight>e.clientHeight+1) out.push(e.dataset.variant+'@'+e.dataset.size);
        for(const box of e.querySelectorAll('.l-focus__pages,.l-note__pages'))
          for(const pg of box.querySelectorAll('.is-page'))
            if(pg.scrollHeight>box.clientHeight+1)
              out.push(e.dataset.variant+' page '+pg.scrollHeight+'>'+box.clientHeight);
      }
      return out})(),
    zero:(()=>{const out=[];
      for(const card of [hub,lite,note].filter(Boolean))
        for(const n of card.querySelectorAll('span,b,time,img'))
          {const r=n.getBoundingClientRect();
           if((r.width<0.5||r.height<0.5)&&n.className&&!String(n.className).includes('sr-only'))
             out.push(card.dataset.variant+' '+String(n.className))}
      return out.slice(0,6)})(),
    hOverflow:document.documentElement.scrollWidth-document.documentElement.clientWidth,
    /* ── paging ── */
    pager:(()=>{const out={};
      for(const [k,e] of [['hub',hub],['lite',lite],['note',note]]){
        if(!e){out[k]=null;continue}
        const dots=[...e.querySelectorAll('.dots__dot')];
        out[k]={tag:e.tagName, role:e.getAttribute('role'),
          pages:e.querySelectorAll('.is-page').length,
          dots:dots.length,
          buttons:dots.filter(b=>b.tagName==='BUTTON').length,
          dwell:!!e.querySelector('.pager-dwell'),
          at:dots.findIndex(b=>b.getAttribute('aria-current')==='true'),
          /* one tab stop, not five: only the current dot is reachable */
          tabbable:dots.filter(b=>b.tabIndex===0).length,
          /* nothing inside an off-screen page may be focusable */
          inertOff:[...e.querySelectorAll('.is-page')].every(p=>p.inert===(p.dataset.pos!=='at')),
          /* a passive card must not be a control itself */
          clickable:e.tagName==='BUTTON'||e.tagName==='A'}}
      return out})(),
    /* the two kinds of item the hub carries */
    /* across ALL pages here, deliberately: the point is that the LIST holds
       both kinds, which one page cannot show */
    kinds:hub?{latin:hub.querySelectorAll('.l-focus__latin').length,
               sub:hub.querySelectorAll('.l-focus__sub').length}:null,
  }})()"""

# THE MODE'S CONTROLS ARE IN THE BOTTOM BAR SINCE 10 SEP, not in the head:
# "Edit module has to come down like quick actions & chat are there". So this
# reads the head for the thing the head still owns — that it comes back at all,
# carrying the mode's title — and looks for Add Module and Done in the row.
# Both are still reached by FOCUS rather than by presence, which is the point
# of the check: a control that is in the DOM and cannot be focused is not a
# control, and `visibility: hidden` on the collapse was how that happened once.
EDIT_HEAD = """(()=>{const h=document.getElementById('modulesHead');
  const bar=document.querySelector('.qa-row');
  const done=bar.querySelector('.link-btn--done'), add=bar.querySelector('.add-module-btn');
  if(done) done.focus(); const d=!!done&&document.activeElement===done;
  if(add) add.focus(); const a=!!add&&document.activeElement===add;
  return {h:+h.getBoundingClientRect().height.toFixed(1), vis:getComputedStyle(h).visibility,
          done:d, add:a,
          /* …and the two the mode replaces are gone from the bar */
          pill:getComputedStyle(document.querySelector('.qa-pill')).display,
          chat:getComputedStyle(document.querySelector('.qa-chat')).display}})()"""

HEAD_AWAY = """(()=>({editing:document.body.classList.contains('is-editing'),
  h:+document.getElementById('modulesHead').getBoundingClientRect().height.toFixed(1)}))()"""

# what V2 seeds, in V2_LAYOUT's order — which is node 280:3521's own order, row
# by row, since 8 Sep 2026. The ink Focus Hub is off the page; everything else
# the frame draws is on it.
#
# WHAT CHANGED AGAINST 270:4176 and is therefore what this list is now guarding:
# Key Insights takes the 2-wide cell beside Hospital, and Pharmacy and Lab —
# which used to be that cell's two smalls — are at the foot beside My Focus Hub.
WANT = ['medical.default', 'housing.default', 'species.stats',
        'hospital.photo', 'insights.key',
        'notes.recent', 'diet.photo', 'administer.default', 'mortality.default',
        'eggs.default', 'audit.default', 'users.default', 'security.default',
        'focus.light', 'pharmacy.default', 'lab.default', 'approvals.pending']

# and the rows those seventeen pack into at the frame's four columns. Each entry
# is one row of the grid: the cards on it, in order, with the column span the
# frame gives them. A 2x2 appears on the row it starts.
WANT_ROWS = [
    ['medical.default', 'housing.default', 'species.stats'],
    ['hospital.photo', 'insights.key'],
    ['notes.recent', 'diet.photo'],
    ['administer.default', 'mortality.default'],
    ['eggs.default', 'audit.default', 'users.default', 'security.default'],
    ['focus.light', 'pharmacy.default', 'lab.default'],
    ['approvals.pending'],
]


PILL = """(()=>{
  const p=document.querySelector('.qa-pill'), t=document.querySelector('.qa-pill__t');
  const row=document.querySelector('.qa-row'), ch=document.querySelector('.qa-chat');
  const r=p&&p.getBoundingClientRect(), cs=p&&getComputedStyle(p);
  const rr=row&&row.getBoundingClientRect(), cr=ch&&ch.getBoundingClientRect();
  const chs=ch&&getComputedStyle(ch);
  const img=ch&&ch.querySelector('img');
  return {pill:!!p, fab:!!document.querySelector('.qa-fab'),
    band:!!document.querySelector('.qa-band'),
    w:r&&Math.round(r.width), h:r&&Math.round(r.height),
    /* THE ROW IS WHAT IS CENTRED SINCE NODE 286:3988, not the pill — see the
       note in the stylesheet. Measuring the pill here would fail on a page
       that is drawn exactly as the frame draws it. */
    centred:rr&&Math.abs((rr.left+rr.right)/2 - innerWidth/2)<2,
    fromFoot:rr&&Math.round(innerHeight-rr.bottom),
    label:t&&t.textContent, labelW:t&&Math.round(t.getBoundingClientRect().width),
    /* THE TWO CENTRES AND THE GAP BETWEEN THEM. Which of the three is
       allowed to move is the whole question this row keeps being re-ruled
       on; see the checks. `--qa-pill-open-w` was read here while the
       reservation existed and is gone with it. */
    pillCentre:r&&Math.round(r.left+r.width/2),
    discCentre:cr&&Math.round(cr.left+cr.width/2),
    gapToDisc:cr&&r&&Math.round(cr.left-r.right),
    radius:cs&&cs.borderRadius, borderW:cs&&cs.borderTopWidth,
    bg:cs&&cs.backgroundImage, bgColor:cs&&cs.backgroundColor,
    /* THE MATERIAL, since node 295:5561 took the pair to glass. `ink` is read
       because the label went black with the fill, and `backdrop` because a
       40% fill with no filter behind it is not glass — it is a pale pill. */
    ink:cs&&cs.color, backdrop:cs&&(cs.backdropFilter||cs.webkitBackdropFilter),
    shadow:cs&&cs.boxShadow,
    /* the grid mark is MASKED now, not an <img>: one asset, coloured off the
       pill's own `color`, so `currentColor` moves it and the × together */
    gridMask:(()=>{const g=document.querySelector('.qa-pill__grid');
      if(!g)return null; const gs=getComputedStyle(g); const b=g.getBoundingClientRect();
      return {mask:(gs.maskImage||gs.webkitMaskImage||'none'), ink:gs.backgroundColor,
              size:(gs.maskSize||gs.webkitMaskSize||''),
              pos:(gs.maskPosition||gs.webkitMaskPosition||''),
              box:[Math.round(b.width),Math.round(b.height)]}})(),
    /* the chat disc */
    chat:!!ch, chatW:cr&&Math.round(cr.width), chatH:cr&&Math.round(cr.height),
    chatGap:(cr&&r)&&Math.round(cr.left-r.right),
    chatGlyph:!!img&&img.complete&&img.naturalWidth>0,
    chatGlyphW:img&&Math.round(img.getBoundingClientRect().width),
    chatLabel:ch&&ch.getAttribute('aria-label'),
    chatBgColor:chs&&chs.backgroundColor, chatBgImage:chs&&chs.backgroundImage,
    chatBackdrop:chs&&(chs.backdropFilter||chs.webkitBackdropFilter),
    chatShadow:chs&&chs.boxShadow, chatBorderW:chs&&chs.borderTopWidth,
    scrolled:document.querySelector('.qa').classList.contains('is-scrolled')}})()"""

MENU = """(()=>{
  const m=document.querySelector('.qa-menu'), r=m.getBoundingClientRect();
  const cs=getComputedStyle(m), v=getComputedStyle(document.querySelector('.qa-veil'));
  return {open:document.querySelector('.qa').classList.contains('is-open'),
    cells:m.querySelectorAll('.qa-chip').length,
    tiles:m.querySelectorAll('.qa-mod').length,
    head:(m.querySelector('.qa-menu__head b')||{}).textContent,
    isModules:document.querySelector('.qa').classList.contains('qa--modules'),
    clip:cs.clipPath,
    panelBlur:cs.backdropFilter||cs.webkitBackdropFilter,
    w:Math.round(r.width), h:Math.round(r.height),
    onScreen:r.top>=-0.5 && r.bottom<=innerHeight+0.5,
    material:cs.backgroundColor, radius:cs.borderRadius,
    veilBlur:v.backdropFilter||v.webkitBackdropFilter, veilOpacity:v.opacity,
    /* the dim itself, and the blur's radius — read as numbers so the check can
       name a range rather than say "there is a blur of some sort" */
    veilColor:v.backgroundColor,
    veilAlpha:(()=>{const m=/rgba?\([^)]*?([\d.]+)\s*\)$/.exec(v.backgroundColor);
      return m?+m[1]:1})(),
    veilPx:(()=>{const m=/blur\(([\d.]+)px\)/.exec(v.backdropFilter||v.webkitBackdropFilter||'');
      return m?+m[1]:0})(),
    labelW:Math.round(document.querySelector('.qa-pill__t').getBoundingClientRect().width)}})()"""

# ── THE OPENING, RESOLVED INTO NUMBERS ────────────────────────────────────
# The clip-path is the whole animation, and its computed value is a string of
# calc()s — `inset(calc(63.07% - 54.95px) … round 24.52px)`. Rather than assert
# anything about that string, this resolves each side against the panel's own
# box and reports the WINDOW it describes: width, height, radius and centre, in
# pixels, panel-relative. That is what the eye sees, and it is comparable
# directly against the pill's box.
STATE = """(()=>{
  const qa=document.querySelector('.qa'), m=document.querySelector('.qa-menu');
  const p=document.querySelector('.qa-pill');
  const cs=getComputedStyle(m), r=m.getBoundingClientRect(), pr=p.getBoundingClientRect();
  const W=r.width, H=r.height;
  /* one <length-percentage> or calc() of the two, against its own axis */
  const len=(v,base)=>{
    v=String(v).trim();
    let x=/^calc\((-?[\d.]+)%\s*([-+])\s*([\d.]+)px\)$/.exec(v);
    if(x) return base*(+x[1])/100 + (x[2]==='-'?-(+x[3]):+(+x[3]));
    x=/^(-?[\d.]+)px$/.exec(v); if(x) return +x[1];
    x=/^(-?[\d.]+)%$/.exec(v);  if(x) return base*(+x[1])/100;
    return NaN;
  };
  /* split on top-level spaces only — the arguments contain calc(a - b) */
  const args=(str)=>{
    const out=[]; let d=0, cur='';
    for(const ch of str){
      if(ch==='(') d++; if(ch===')') d--;
      if(ch===' '&&d===0){ if(cur) out.push(cur); cur=''; } else cur+=ch;
    }
    if(cur) out.push(cur); return out;
  };
  const win=(()=>{
    const s=/^inset\((.*)\)$/.exec(cs.clipPath.replace(/\s+/g,' ').trim());
    if(!s) return null;
    let a=args(s[1]), rad=null;
    const i=a.indexOf('round');
    if(i>=0){ rad=len(a[i+1], W); a=a.slice(0,i); }
    const t=len(a[0],H),
          rt=len(a.length>1?a[1]:a[0],W),
          b=len(a.length>2?a[2]:a[0],H),
          l=len(a.length>3?a[3]:(a.length>1?a[1]:a[0]),W);
    return {t,rt,b,l,rad};
  })();
  const rows={}, spread={}, cellByRow={};
  const dly=(k)=>{const c=cellByRow[k]; if(!c) return null;
    return Math.round(parseFloat(getComputedStyle(c).transitionDelay)*1000)};
  for(const cell of document.querySelectorAll('.qa-search, .qa-bind, .qa-cat, .qa-foot')){
    const k=cell.style.getPropertyValue('--qa-row').trim()||'0';
    const o=+(+getComputedStyle(cell).opacity).toFixed(2);
    if(!(k in rows)){ rows[k]=o; cellByRow[k]=cell }
    (spread[k]=spread[k]||[]).push(o);
  }
  /* the clip's own endpoints, so progress is a number and not a guess */
  const closedTop=H-52, openTop=-60;
  const prog=win?Math.max(0,Math.min(1,(closedTop-win.t)/(closedTop-openTop))):null;
  return JSON.stringify({
    winW:win&&+(W-win.l-win.rt).toFixed(1),
    winH:win&&+(H-win.t-win.b).toFixed(1),
    winR:win&&+win.rad.toFixed(1),
    winCx:win&&+(win.l+(W-win.l-win.rt)/2).toFixed(1),
    menuCx:+(W/2).toFixed(1),
    pillW:+pr.width.toFixed(1),
    pillCx:+(pr.left+pr.width/2-r.left).toFixed(1),
    progress:prog===null?null:+prog.toFixed(3),
    opacity:+(+cs.opacity).toFixed(2),
    grid:+(+getComputedStyle(document.querySelector('.qa-pill__grid')).opacity).toFixed(2),
    x:+(+getComputedStyle(document.querySelector('.qa-pill__x')).opacity).toFixed(2),
    rows,
    rowSpread:+Math.max(...Object.values(spread).map(v=>Math.max(...v)-Math.min(...v))).toFixed(3),
    /* THE DELAYS THEMSELVES, which is the only thing that PROVES the close is
       the open reversed. Opacity ordering cannot: in both directions the row
       nearest the FAB is the more opaque one, so "bottom leads" is true while
       opening and while closing. What differs is which row waits — so read the
       resolved transition-delay off the top and bottom cells and let the check
       compare them. */
    delayBottom:dly('0'),
    delayTop:dly(String(Math.max(...Object.keys(rows).map(Number)))),
  })})()"""

TILES = """(()=>{
  const grid=document.querySelector('.qa-menu__grid');
  const menu=document.querySelector('.qa-menu');
  const t=[...menu.querySelectorAll('.qa-mod')];
  const gcs=getComputedStyle(grid), mcs=getComputedStyle(menu);
  const uniq=(a)=>[...new Set(a)];
  const b=(e)=>e.getBoundingClientRect();
  /* THE SECOND ROW IS FOUND, NOT COUNTED TO. This was `t[4]`, which is the
     middle of row two at three columns and the middle of row THREE at two —
     so on a phone the row gutter measured 102 and a correct 16px grid failed
     its own check. The first tile that starts below row one is the second
     row at any column count. */
  const b0=b(t[0]), b1=b(t[1]);
  const bRow2=b(t.find((x)=>b(x).top>b0.bottom-1)||t[t.length-1]);

  /* THE INK IS WHITE ON ALL NINETEEN · ruled 10 Sep. What is checked is no
     longer WHICH ink each colour favours but that every tile actually got
     white, plus the honest cost of that: the white-on-tile contrast, per
     tile, recomputed from the resolved background. WCAG relative luminance
     against white's 1.05. */
  const lum=(css)=>{
    const m=/rgba?\(\s*([\d.]+)[,\s]+([\d.]+)[,\s]+([\d.]+)/.exec(css);
    if(!m) return null;
    const ch=[1,2,3].map(i=>{const v=+m[i]/255;
      return v<=0.04045? v/12.92 : Math.pow((v+0.055)/1.055,2.4)});
    return 0.2126*ch[0]+0.7152*ch[1]+0.0722*ch[2];
  };
  /* THE LABEL AGAINST ITS CARD · reworked 10 Sep 2026. This was white
     against the TILE, when the tile carried the module's colour and the ink
     was white on all nineteen. The card is white now and the ink is dark, so
     the pair being measured is the real one either way: whatever the label
     is, against whatever it sits on. */
  const ratioOf=(fg,bg)=>{const a=lum(fg)+0.05, b2=lum(bg)+0.05;
    return a>b2 ? a/b2 : b2/a};
  const ratio=(x)=>{const cs=getComputedStyle(x);
    return ratioOf(cs.color, cs.backgroundColor)};
  const nameOf=(x)=>x.querySelector('.qa-mod__t').textContent;
  const chip=(x)=>x.querySelector('.qa-mod__g');

  return JSON.stringify({
    n:t.length,
    visible:t.filter(x=>{const r=b(x);return r.width>1&&r.height>1}).length,
    /* ── ONE MATERIAL ON ALL NINETEEN · node 371:5441, 15 Sep 2026 ───────
       There is no per-module colour left on this surface at all. The fill
       went tile → chip on 10 Sep to settle a contrast debt, and the node
       empties the chip too, so what used to be a count of SIXTEEN distinct
       colours is now a requirement that there be exactly ONE ground and one
       unfilled chip. Asserted as a count rather than a value so that a stray
       `--qa-mod-c` coming back on one tile fails here rather than being
       absorbed. */
    grounds:uniq(t.map(x=>getComputedStyle(x).backgroundColor)),
    withGradient:t.filter(x=>getComputedStyle(x).backgroundImage!=='none').length,
    chipsFilled:t.filter(x=>{const c=getComputedStyle(chip(x)).backgroundColor;
      return c!=='rgba(0, 0, 0, 0)' && c!=='transparent'}).length,
    /* AND IT IS GLASS, NOT A SLAB. The 20% veil only reads as the node's
       material with the blur behind it; without it the tile is a flat grey
       rectangle that measures the same and looks nothing like the file. */
    tileBlur:uniq(t.map(x=>{const s=getComputedStyle(x);
      return s.backdropFilter||s.webkitBackdropFilter||'none'})),
    /* THE SHADOW IS GONE AND A HAIRLINE IS BACK, which is the exact reverse
       of the 10 Sep white card. A drop shadow under a translucent pane reads
       as dirt on the panel behind it. */
    withShadow:t.filter(x=>getComputedStyle(x).boxShadow!=='none').length,
    withBorder:t.filter(x=>parseFloat(getComputedStyle(x).borderTopWidth)>0).length,
    /* the chip's own geometry — a square with a squircle's radius, kept as a
       box even though it no longer carries a fill */
    chipW:Math.round(b(chip(t[0])).width), chipH:Math.round(b(chip(t[0])).height),
    chipR:Math.round(parseFloat(getComputedStyle(chip(t[0])).borderTopLeftRadius)),
    /* the tile's own layout — the node centres the chip and label as a pair
       rather than running them out from the left edge */
    justify:uniq(t.map(x=>getComputedStyle(x).justifyContent)),
    tileGap:uniq(t.map(x=>getComputedStyle(x).gap)),
    tilePad:uniq(t.map(x=>getComputedStyle(x).padding)),
    sizes:uniq(t.map(x=>getComputedStyle(x.querySelector('.qa-mod__t')).fontSize)),
    /* and the label's weight, which the ruling named outright */
    weights:uniq(t.map(x=>getComputedStyle(x.querySelector('.qa-mod__t')).fontWeight)),
    tileW:Math.round(b0.width), tileH:Math.round(b0.height),
    radius:Math.round(parseFloat(getComputedStyle(t[0]).borderTopLeftRadius)),
    gapX:Math.round(b1.left-b0.right), gapY:Math.round(bRow2.top-b0.bottom),
    cols:gcs.gridTemplateColumns.split(' ').length,
    panelPad:mcs.padding,
    panelW:Math.round(b(menu).width),
    clearOfRow:Math.round(b(document.querySelector('.qa-row')).top-b(menu).bottom),
    /* EVERY TILE'S RENDERED COLOUR, not the class that used to set it. The
       `--dark` class is gone; a stray one would show up as a non-white ink
       here rather than being counted. */
    inks:uniq(t.map(x=>getComputedStyle(x).color)),
    darkClass:t.filter(x=>x.classList.contains('qa-mod--dark')).length,
    /* THE CONTRAST IS NOT COMPUTABLE FROM STYLE ANY MORE, and pretending
       otherwise is worse than not checking. `ratioOf(color, backgroundColor)`
       used to be the real pair because the card was opaque white; the tile is
       now 20% black over a 40% white panel over a 30% black veil over
       whatever the page draws there, so `backgroundColor` returns
       `rgba(0, 0, 0, 0.2)` and a luminance read of it — which ignores alpha —
       reports 21:1 for a tile that actually measures 2.06. The measurement
       moved to the SCREENSHOT, below; what is exported here is only the boxes
       to sample and the ink that sits in them.

       ONLY THE TILES ACTUALLY INSIDE THE PANEL, which one column made
       necessary: nineteen rows overflow a phone, the panel scrolls, and a
       tile below the fold still reports its laid-out box. Sampling there
       reads the PAGE rather than the tile — it produced a 15.14:1 "best" off
       a dark card and a 1.66:1 "worst" off a pale corner, neither of which
       is a tile at all. */
    inkBoxes:t.map(x=>{const r=b(x), l=b(x.querySelector('.qa-mod__t')), p=b(menu);
      return {name:nameOf(x), x:Math.round(r.left), y:Math.round(r.top),
        w:Math.round(r.width), h:Math.round(r.height),
        lr:Math.round(l.right), lt:Math.round(l.top), lb:Math.round(l.bottom),
        inPanel: r.top>=p.top-1 && r.bottom<=p.bottom+1
                 && r.left>=p.left-1 && r.right<=p.right+1}})
      .filter(r=>r.inPanel),
    /* the text-shadow should be GONE — it existed to hold white ink off a
       pale tile, and there is no pale tile under the label any more */
    withShadowInk:t.filter(x=>getComputedStyle(x).textShadow!=='none').length,
    /* the glyphs are the modules' own exported files, loaded */
    glyphsLoaded:t.filter(x=>{const i=x.querySelector('.qa-mod__g img');
      return i && i.complete && i.naturalWidth>0}).length,
    /* and no label runs out of its tile */
    labelOverflow:t.filter(x=>{const l=x.querySelector('.qa-mod__t');
      return b(l).right>b(x).right-2 || b(l).bottom>b(x).bottom-1}).length,
    /* ── AND NO LABEL RUNS OUT OF ITS OWN BOX, which is a different question
       and the one that was being missed. `min-width: 0` is what lets the
       label wrap at all, and it also lets the BOX shrink under the text
       inside it: the box then sits happily within the tile while `overflow:
       hidden` cuts the word off. "Species Managemen" passed the check above
       at 390 while reading exactly like that on screen. Twelve of the
       nineteen were clipped this way at 360. `scrollWidth` against the
       measured box is what sees it. */
    labelClipped:t.map(x=>{const l=x.querySelector('.qa-mod__t');
        return [l.textContent.replace(/\\u00ad/g,''),
                l.scrollWidth-Math.round(b(l).width)]})
      .filter(r=>r[1]>1),
    /* ── AND NO WORD BREAKS IN THE MIDDLE OF ITSELF, which is the check that
       actually holds. `overflow-wrap: break-word` was added as a backstop
       against clipping and it has a sting: once it is on, `scrollWidth` never
       exceeds the box, so the clipping test above can never fail again. It
       went green at 360 while the panel read "Medica/l", "Hospit/al",
       "Specie/s Manag/ement" — twelve of the nineteen split mid-word. Nothing
       was hidden and everything was wrong.
       So what is measured is the longest UNBREAKABLE run — each label split
       on whitespace and on its own soft hyphens — against the box it has to
       sit in. If the run is wider, the backstop is carrying the layout, and
       the answer is a column fewer or a hyphen in MODULES, never the
       backstop. */
    wordBreaks:(()=>{const p=document.createElement('span');
      const c0=getComputedStyle(t[0].querySelector('.qa-mod__t'));
      p.style.cssText='position:absolute;visibility:hidden;white-space:nowrap;'+
        'font:'+c0.font+';letter-spacing:'+c0.letterSpacing;
      document.body.append(p);
      const runW=(s)=>Math.max(...s.split(/\\s+/).flatMap(w=>w.split('\\u00ad'))
        .map(w=>{p.textContent=w; return p.getBoundingClientRect().width}));
      const out=t.map(x=>{const l=x.querySelector('.qa-mod__t');
        const need=Math.round(runW(l.textContent)), has=Math.round(b(l).width);
        return [l.textContent.replace(/\\u00ad/g,''), need, has]})
        .filter(r=>r[1]>r[2]+1);
      p.remove(); return out})(),
    names:t.map(x=>x.querySelector('.qa-mod__t').textContent),
  })})()"""

OPEN_MENU = "(()=>{document.getElementById('avatarBtn').click(); return 1})()"

VER_GROUP = """(()=>{
  const m=document.querySelector('.pmenu');
  if(!m||m.hidden) return {open:false, ver:[], heads:[]};
  const rows=[...m.querySelectorAll('.pmenu__item')];
  const mr=m.getBoundingClientRect();
  return {open:true,
    heads:[...m.querySelectorAll('.pmenu__heading-text')].map(h=>h.textContent.trim()),
    ver:rows.filter(r=>r.dataset.id.startsWith('ver:')).map(r=>({
      id:r.dataset.id, role:r.getAttribute('role'), checked:r.getAttribute('aria-checked'),
      label:r.querySelector('.pmenu__label').textContent.trim(),
      note:r.querySelector('.pmenu__note').textContent.trim(),
      tick:!!r.querySelector('.pmenu__tick'),
      /* a row whose note wraps past its own box is a row that has lost half
         its second line — the menu is 304 wide and these notes are the
         longest in it */
      clipped:r.scrollHeight>r.clientHeight+1})),
    menuH:+mr.height.toFixed(1),
    onScreen: mr.top>=0 && mr.bottom<=innerHeight+.5 && mr.left>=0 && mr.right<=innerWidth+.5,
  }})()"""

PRESS_VER = """(()=>{const b=document.querySelector('.pmenu__item[data-id="ver:%s"]');
  if(!b) return 'no such row'; b.click(); return 'pressed'})()"""

WHERE = """(()=>({v:document.documentElement.dataset.pageVersion, search:location.search,
  cards:document.querySelectorAll('#moduleGrid .card').length,
  deck:document.querySelectorAll('.hero--slide').length}))()"""
# ── THE OPENING, RESOLVED INTO NUMBERS ────────────────────────────────────
# ONE SURFACE MOVES AND NOTHING ELSE DOES. Until 10 Sep each of the nineteen
# tiles flew out of the pill on its own measured vector, and this probe
# measured per-tile distances and launch ranks to prove the fan was a fan. The
# ruling — "Animation not at all good" — replaced all of it with a 220ms
# scale-and-fade of the panel from `50% 100%`, so what has to be measured now
# is the opposite claim: the PANEL is travelling, and NO TILE IS.
#
# THE ORIGIN IS CHECKED AS A POINT ON THE SCREEN, not as the string "50% 100%".
# A computed `transform-origin` of "356px 515px" tells you nothing on its own;
# what matters is whether that point lands on the pill, so it is resolved into
# viewport coordinates and compared with the pill's own centre. That is the
# check that would catch the panel growing from its middle, or from a corner,
# while the declaration still read plausibly.
SURFACE = """(()=>{
  const qa=document.querySelector('.qa'), m=document.querySelector('.qa-menu');
  const pill=document.querySelector('.qa-pill').getBoundingClientRect();
  const px=pill.left+pill.width/2, py=pill.top+pill.height/2;
  const t=[...m.querySelectorAll('.qa-mod')];
  const cs=(e)=>getComputedStyle(e);
  const mb=m.getBoundingClientRect();
  const scaleOfEl=(e)=>{const mt=/matrix\(([-\d.]+)/.exec(cs(e).transform);
    return mt? +mt[1] : 1};
  const scaleOf=(e)=>Math.round(scaleOfEl(e)*1000)/1000;
  /* THE ORIGIN, TURNED INTO A POINT IN THE VIEWPORT — and this is where the
     first version of this probe was wrong. `transform-origin` resolves in the
     element's UNTRANSFORMED coordinate space, while getBoundingClientRect()
     returns the box AFTER the scale. Adding one to the other reported the
     origin as 48px off the pill in a frame where the CSS was only 34px off,
     so the number was part artifact and part real bug. The scale is divided
     back out here: at scale s about origin o, a visual left edge sits at
     (trueLeft + o) - o*s, so trueLeft + o — the fixed point of the transform —
     is visualLeft + o*s. */
  const o=cs(m).transformOrigin.split(' ').map(parseFloat);
  const sc=scaleOfEl(m);
  return JSON.stringify({
    panelOpacity:+(+cs(m).opacity).toFixed(2),
    panelScale:scaleOf(m),
    clip:cs(m).clipPath,
    /* where the panel is actually growing FROM, against where the pill is —
       the fixed point of the scale, in viewport coordinates */
    originDX:Math.round((mb.left+o[0]*sc)-px),
    originDY:Math.round((mb.top+o[1]*sc)-py),
    /* NO TILE MOVES · every one of them full opacity, full size, in every
       frame, and — the real assertion — not one animation targeting a tile */
    tileOps:t.map(e=>+(+cs(e).opacity).toFixed(2)),
    tileScales:t.map(scaleOf),
    tileAnims:document.getAnimations().filter(a=>a.effect&&a.effect.target
      &&a.effect.target.classList
      &&a.effect.target.classList.contains('qa-mod')).length,
    /* and no tile carries the retired vectors or ranks */
    strayVectors:t.filter(e=>e.style.getPropertyValue('--qa-dx')
      ||e.style.getPropertyValue('--qa-i')).length,
    /* the pill's own morph is unchanged and still runs */
    grid:+(+cs(document.querySelector('.qa-pill__grid')).opacity).toFixed(2),
    x:+(+cs(document.querySelector('.qa-pill__x')).opacity).toFixed(2),
  })})()"""


# ── FREEZING WITHOUT GUESSING WHEN ────────────────────────────────────────
# Both measurements below used to be `sleep(0.004)` then pause, and both were
# a coin flip. `show()` clears `hidden`, measures its rows, and adds `is-open`
# only on the NEXT animation frame — so 4ms in, the transitions usually did not
# exist yet, `getAnimations()` came back EMPTY, nothing was paused, the real
# reveal then ran free, and every check below read whatever it happened to
# catch. That is why this file could pass twice and fail on a third run with
# no code change between them: observed 9 Sep 2026, PASS / PASS / 4 FAILED,
# reporting closed-state values (`0 of the way`, `grid=1 x=0`) for a panel
# that was opening correctly.
#
# Awaiting the state class AND a non-empty `getAnimations()` inside the page
# removes the guess entirely, and it is ONE round trip, so nothing can run
# between the wait and the pause.
#
# `hidden` IS NEUTRALISED HERE AND NOT BEFORE THE CLICK, which looks like it
# would be safer and is not: the override is a no-op SETTER over the IDL
# property, while `[hidden] { display: none }` matches the ATTRIBUTE. Installed
# before `show()` runs, it would swallow that method's own `hidden = false`,
# the attribute would never come off, and the panel would sit at
# `display: none` for the whole measurement.
def freeze_at(c, cls):
    c.eval("""(async()=>{
        await new Promise(res=>{const tick=()=>{
          const qa=document.querySelector('.qa');
          if(qa&&qa.classList.contains('%s')&&document.getAnimations().length)return res(1);
          requestAnimationFrame(tick)};tick()});
        const m=document.querySelector('.qa-menu');
        Object.defineProperty(m,'hidden',{get:()=>false,set:()=>{},configurable:true});
        document.getAnimations().forEach(a=>a.pause());
        return 1})()""" % cls, await_promise=True)


def main():
    print(f"V2 — V4 page redesigned, {WIDTH}px")

    # ── V1 is untouched by any of this ────────────────────────────────────
    print("\nV1 still V1")
    with Chrome(width=WIDTH, height=1200) as c:
        c.goto(BASE + "index.html", settle=2.0)
        v1 = c.eval(PROBE)
        check("no `?v=` means V1", v1["stamp"] == "1", str(v1["stamp"]))
        check("the deck is there and mounted", v1["deckShown"] and v1["deckMounted"] == 6,
              f"shown={v1['deckShown']} slides={v1['deckMounted']}")
        check("the observation rail is there and mounted",
              v1["railShown"] and v1["railMounted"] == 6,
              f"shown={v1['railShown']} cards={v1['railMounted']}")
        check("V1's module band carries NO band fill", v1["band"]["img"] == "none", v1["band"]["img"][:40])
        check("V1 seeds fifteen cards", v1["n"] == 15, str(v1["n"]))
        check("…and none of the three new ones", v1["three"] == 0, str(v1["three"]))
        errs = c.errors()
        check("no console errors on V1", not errs, "; ".join(str(e)[:90] for e in errs[:2]))

    # ── V2 IS V4'S PAGE, REDESIGNED (24 Sep 2026) ─────────────────────────
    # The owner: "instead of updating v4 can we do in v2" → "replace V2's
    # home". V2 now wears V4's whole composition (its stylesheet answers to
    # data-page-version="4") and adds, under data-home="v2": the stacked
    # announcement deck, the species shelf, a sliding notes filter and a
    # press-and-hold menu. The old node-280:3521 checks that stood here
    # retired with the page they described.
    print("\nV2 is V4's page, redesigned")
    with Chrome(width=WIDTH, height=1200) as c:
        c.goto(BASE + "index.html?v=2", settle=2.4)
        o = json.loads(c.eval("""JSON.stringify({
          pv: document.documentElement.dataset.pageVersion, home: document.documentElement.dataset.home || '',
          clock: !!document.querySelector('.clock')?.offsetParent,
          fav: !!document.querySelector('.fav-band')?.offsetParent,
          reports: !!document.querySelector('#reports')?.offsetParent,
          tiles: document.querySelectorAll('#moduleGrid .card').length,
          lists: document.querySelectorAll('#moduleGrid .card[data-variant$=".list"]').length,
          deck: document.querySelectorAll('.adeck__card').length,
          oldDeck: document.querySelectorAll('.hero-stage__deck').length,
          dots: document.querySelectorAll('.adeck__dots i').length,
          on: [...document.querySelectorAll('.adeck__dots i')].findIndex(i => i.classList.contains('on')),
          head: document.querySelector('#adeckTitle')?.textContent || '', headShown: !!document.querySelector('#adeckTitle:not(.sr-only)'), all: !!document.querySelector('.adeck__foot .adeck__all'),
          pager: document.querySelectorAll('.adeck__btn, .adeck__count, .adeck__index').length,
          seg: [...document.querySelectorAll('.v2seg__opt')].map(b => b.dataset.k),
          plate: getComputedStyle(document.querySelector('.fav__txt')).backdropFilter || getComputedStyle(document.querySelector('.fav__txt')).webkitBackdropFilter || '',
          ctx: document.querySelector('.qa').classList.contains('qa--ctx'),
          ovf: document.documentElement.scrollWidth - innerWidth})"""))
        check("<html> carries V4's stylesheet and V2's own scope", o["pv"] == "4" and o["home"] == "v2", f"{o['pv']} / {o['home']}")
        # NODE 718:17169 "V2 Design Figma" (24 Sep 2026): My Species, no clock,
        # no Site reports, and the frame's thirteen cards in its order
        check("the node's composition: My Species, no clock, no Site reports", o["fav"] and not o["clock"] and not o["reports"], str({k: o[k] for k in ('fav', 'clock', 'reports')}))
        want = ['medical.default', 'housing.default', 'species.stats', 'hospital.photo', 'insights.v3', 'species.newlist', 'diet.photo',
                'administer.default', 'mortality.default', 'eggs.default', 'species.newcount', 'users.default', 'security.default']
        got = c.eval("[...document.querySelectorAll('#moduleGrid .card')].map(x => x.dataset.variant)")
        check("…and the frame's thirteen cards, in its order", got == want, str(got))
        g2 = c.eval("""(()=>{const q=s=>document.querySelector(s);const R=e=>e.getBoundingClientRect();const r=v=>Math.round(v*10)/10;
          const cards=[...document.querySelectorAll('#moduleGrid .card')].map(x=>R(x));const grid=R(q('#moduleGrid'));
          const pad=parseFloat(getComputedStyle(q('.main-frame')).paddingLeft), col=innerWidth-2*pad;
          return {pad, col, mint:getComputedStyle(q('.home-header')).backgroundColor, page:getComputedStyle(document.documentElement).backgroundColor,
            climate:(()=>{const e=q('.climate'),h=q('.home-header'),f=q('#favSpecies');if(!e||!h||!f)return null;const a=R(e),b=R(h),c=R(f);return [r(a.top-b.top), r(a.bottom-c.bottom), getComputedStyle(e).zIndex]})(),
            greetY:r(R(q('.greeting__word')).top+scrollY), nameH:r(R(q('.greeting__name')).height), searchW:r(R(q('.search')).width), scanX:r(R(q('.search-btn')).left),
            favCard:[r(R(q('.fav__card')).width), r(R(q('.fav__card')).height)], plate:getComputedStyle(q('.fav__txt')).backgroundColor, favImg:r(R(q('.fav__card .fav__img')).height), favFade:getComputedStyle(q('.fav__card'),'::after').display, favRadius:getComputedStyle(q('#favSpecies')).borderBottomLeftRadius,
            bandsW:[r(R(q('#heroStage')).width), r(R(q('#recentObs')).width)], obs:[r(R(q('.obs')).width), r(R(q('.obs')).height)], obsHeadX:r(R(q('#recentObs .obs-head')).left),
            headH:r(R(q('#modulesHead')).height), heroH:r(R(q('.hero--estate')).height), row:r(cards[0].height), gridW:r(grid.width), banner:r(R(q('.hero--estate')).top-R(q('#modulesHead')).bottom),
            headTxt:[q('#obsTitle').textContent, q('#modulesTitle').textContent, q('#modulesHead .link-btn span')?.textContent]}})()""")
        # THE CLIMATE BACKGROUND replaced the mint on 25 Sep 2026 ("implement the
        # climate change"): the band goes clear and the scene behind it is measured
        # to exactly the header's top and My Species' foot, under the UI.
        check("a climate scene on a white page: the band clear, the scene fitted to it and behind it",
              g2["mint"] == "rgba(0, 0, 0, 0)" and g2["page"] == "rgb(255, 255, 255)" and g2["climate"] == [0, 0, "-1"],
              f"{g2['mint']} / {g2['page']} / {g2['climate']}")
        col, pad = g2["col"], g2["pad"]
        check("the greeting at 40, a 34px name line, the field the column less the scan and one gap", g2["greetY"] == 40 and g2["nameH"] == 34 and g2["searchW"] == col - 60 and g2["scanX"] == pad + col - 52, str(g2))
        # V4's card at V2's size since 25 Sep 2026 ("version 2 make like this
        # card, But Fix the card height same as v2"): the photograph fills the
        # 158 and the words sit on the dark fade, no black plate
        check("species cards 148×158, the photograph filling the card under the fade, the block's corners rounded 20",
              g2["favCard"] == [148, 158] and g2["favImg"] == 158 and g2["favFade"] == "block" and g2["plate"] == "rgba(0, 0, 0, 0)" and g2["favRadius"] == "20px", str(g2))
        check("both bands the column plus 8 a side; a 290×430 note card, the notes head 24 inside", g2["bandsW"] == [col + 16, col + 16] and g2["obs"] == [290, 430] and g2["obsHeadX"] == pad - 8 + 24, str(g2))
        row = round((col - 48) / 4 / 1.125, 1)   # 144 on the 744 artboard
        check("Modules: a 19px head, the banner 16 under it, banner and rows at the node's 162:144", g2["headH"] == 19 and g2["banner"] == 16 and g2["heroH"] == row and g2["row"] == row and g2["gridW"] == col, str(g2))
        check("the heads say Observation Notes, Modules and Edit", g2["headTxt"] == ["Observation Notes", "Modules", "Edit"], str(g2["headTxt"]))
        check("the announcements are the stacked deck, not V4's carousel", o["deck"] >= 5 and o["oldDeck"] == 0, f"{o['deck']} cards, old deck {o['oldDeck']}")
        check("…opening on the first, one dot per card and the first lit", o["dots"] == o["deck"] and o["on"] == 0, f"{o['dots']} dots, on={o['on']}")
        # NODE 753:20981 (25 Sep 2026): no visible head — the band keeps its
        # name for a screen reader — and View all sits in the foot row
        check("…named Announcements but with no visible head, View all in the foot, and no pager, counter or index", o["head"] == "Announcements" and not o["headShown"] and o["all"] and o["pager"] == 0, f"{o['head']!r} shown={o['headShown']} all={o['all']} pager={o['pager']}")

        # THE DECK IS NODE 718:18106's (24 Sep 2026): the band 8 wider than the
        # column each side, padded 16; the front card the stack less 32; the
        # two behind it out by 16 and 32; a 36px chip, a 180px photograph,
        # 8px dots with the lit one 20 wide; 36 under the species, 40 over
        # the next head. And since 25 Sep the card is the node's FIXED BOX —
        # 210 tall on every card, checked below by turning the whole deck.
        g = c.eval("""(()=>{const q=s=>document.querySelector(s);const R=e=>e.getBoundingClientRect();
          const band=R(q('#heroStage')), col=R(q('#panel-modules')), st=R(q('.adeck__stack')), f=R(q('.adeck__card[data-i="0"]')), p1=R(q('.adeck__card[data-i="1"]')), p2=R(q('.adeck__card[data-i="2"]'));
          const r=v=>Math.round(v*10)/10;
          return {bandW:r(band.width-col.width), bandPadL:r(st.left-band.left), bandPadT:r(st.top-band.top), bandH:r(band.height), foot:r(R(q('.adeck__foot')).height), footGap:r(R(q('.adeck__foot')).top-st.bottom), footPadB:r(band.bottom-R(q('.adeck__foot')).bottom), allRight:r(band.right-R(q('.adeck__all')).right),
            frontIn:r(st.width-f.width), p1out:r(p1.right-f.right), p2out:r(p2.right-f.right), p1down:r(p1.top-f.top),
            chip:r(R(q('.adeck__card[data-i="0"] .adeck__chip')).height), photo:q('.adeck__card[data-i="0"] .adeck__img')?r(R(q('.adeck__card[data-i="0"] .adeck__img')).width):180,
            dot:r(R(q('.adeck__dots i:not(.on)')).width), dotOn:r(R(q('.adeck__dots i.on')).width), dotsGap:r(R(q('.adeck__dots')).top-st.bottom), dotsCentre:(()=>{const ds=[...document.querySelectorAll('.adeck__dots i')].map(R),a=R(q('.adeck__all')),f=R(q('.adeck__foot'));return r((Math.min(...ds.map(x=>x.left))+Math.max(...ds.map(x=>x.right)))/2-(f.left+(a.left-f.left)/2))})(),
            above:r(band.top-R(q('#favSpecies')).bottom), below:r(R(q('#recentObs .obs-head')).top-band.bottom)}})()""")
        check("the band is the column plus 8 a side, padded 16, the stack straight under its top", g["bandW"] == 16 and g["bandPadL"] == 16 and g["bandPadT"] == 16, str(g))
        check("the node's 275: a 17px foot row 16 under the stack and 16 over the band's foot, View all 16 in", g["bandH"] == 275 and g["foot"] == 17 and g["footGap"] == 16 and g["footPadB"] == 16 and g["allRight"] == 16, str(g))
        check("the front card is the stack less 32; the peeks stand out 16 and 32, the first 10 down", g["frontIn"] == 32 and abs(g["p1out"] - 16) < .6 and abs(g["p2out"] - 32) < .6 and g["p1down"] == 10, str(g))
        check("a 36px chip and a 180px photograph", g["chip"] == 36 and g["photo"] == 180, f"{g['chip']} / {g['photo']}")
        check("8px dots, the lit one 20 wide, centred in the foot row left of View all", g["dot"] == 8 and g["dotOn"] == 20 and abs(g["dotsCentre"]) <= .5, str(g))
        check("16 under the species block, 40 to the notes head (16 to its band, 24 inside it)", g["above"] == 16 and g["below"] == 40, f"{g['above']} / {g['below']}")

        # THE CARD IS A FIXED BOX ("Announcement card has fixed size. Do not
        # reduce the Size", 25 Sep 2026): the node's 210 on EVERY card — the
        # title cut at its two lines, the body at its three, the photograph
        # the 186 column, the chip 12 from the top and the byline 12 from the
        # foot — so the band is one height whichever card is in front. The
        # deck is turned right round (reduced motion: each turn is instant)
        # and ends where it began, on the first card.
        key = lambda k: c.eval(f"document.querySelector('.adeck__stack').dispatchEvent(new KeyboardEvent('keydown', {{key: '{k}', bubbles: true}})); 1")
        box = lambda: c.eval("""(()=>{const q=s=>document.querySelector(s);const R=e=>e.getBoundingClientRect();const f=q('.adeck__card[data-i="0"]');const r=v=>Math.round(v*10)/10;
          return {ai:f.dataset.ai, card:r(R(f).height), stack:r(R(q('.adeck__stack')).height), hl:r(R(f.querySelector('.adeck__hl')).height), desc:r(R(f.querySelector('.adeck__desc')).height),
            chipTop:r(R(f.querySelector('.adeck__chip')).top-R(f).top), metaBot:r(R(f).bottom-R(f.querySelector('.adeck__meta')).bottom), img:f.querySelector('.adeck__img')?r(R(f.querySelector('.adeck__img')).height):186}})()""")
        hs = []
        for _ in range(o["deck"]):
            hs.append(box()); key("ArrowRight"); time.sleep(0.25)
        check("every card in front is the node's 210, and so is the stack", all(h["card"] == 210 and h["stack"] == 210 for h in hs) and len({h["ai"] for h in hs}) == o["deck"], str([(h["ai"], h["card"], h["stack"]) for h in hs]))
        check("…the title within two lines, the body within three, the photograph the 186 column", all(h["hl"] <= 39 and h["desc"] <= 60 and h["img"] == 186 for h in hs), str([(h["ai"], h["hl"], h["desc"], h["img"]) for h in hs]))
        check("…the chip 12 from the top and the byline 12 from the foot, on each", all(h["chipTop"] == 12 and h["metaBot"] == 12 for h in hs), str([(h["ai"], h["chipTop"], h["metaBot"]) for h in hs]))
        check("…and a full turn of the deck is back on the first card", box()["ai"] == "0", box()["ai"])
        check("the notes filter has its four", o["seg"] == ["all", "urgent", "animal", "enclosure"], str(o["seg"]))

        # KEY INSIGHTS · node 757:9930 (25 Sep 2026: "Add this section under
        # notes. Make sure Each Container has to Scroll inside"): the band
        # under the notes, four 297×430 cards, and each list scrolling INSIDE
        # its card — a real wheel over a list moves the list, not the page
        k = c.eval("""(()=>{const q=s=>document.querySelector(s),R=e=>e.getBoundingClientRect(),r=v=>Math.round(v*10)/10;const b=q('#keyInsights');if(!b)return {n:0};
          const cards=[...document.querySelectorAll('.kins__card')];return {n:1, after:b.previousElementSibling?.id, gap:r(R(b).top-R(q('#recentObs')).bottom), wide:r(R(b).width-R(q('#panel-modules')).width),
            cards:cards.map(x=>[r(R(x).width),r(R(x).height)]), kinds:cards.map(x=>x.dataset.k), rowH:r(R(q('.kins__row')).height),
            scrollable:cards.map(x=>x.classList.contains('is-scrollable')), over:cards.map(x=>{const l=x.querySelector('.kins__list');return l.scrollHeight>l.clientHeight}),
            broken:[...b.querySelectorAll('img')].filter(i=>i.complete&&!i.naturalWidth).length}})()""")
        check("Key Insights sits 16 under the notes, the column plus 8 a side", k.get("n") == 1 and k.get("after") == "recentObs" and k.get("gap") == 16 and k.get("wide") == 16, str(k))
        check("…four 297×430 cards — natality, mortality, transfers, food — with 43px rows and every image loaded",
              k.get("kinds") == ["natality", "mortality", "transfer", "food"] and all(x == [297, 430] for x in k.get("cards", [])) and k.get("rowH") == 43 and k.get("broken") == 0, str(k))
        check("…the thumb shows exactly on the cards whose list overflows", k.get("scrollable") == k.get("over"), str(k))
        c.eval("document.getElementById('keyInsights').scrollIntoView({block:'center'}); 1"); time.sleep(0.4)
        pt = json.loads(c.eval("(r=>JSON.stringify([r.left+r.width/2,r.top+r.height/2]))(document.querySelector('.kins__card .kins__list').getBoundingClientRect())"))
        y0 = c.eval("scrollY")
        c.cmd("Input.dispatchMouseEvent", type="mouseWheel", x=pt[0], y=pt[1], deltaX=0, deltaY=80); time.sleep(0.5)
        inner = c.eval("document.querySelector('.kins__card .kins__list').scrollTop"); moved = c.eval("scrollY") - y0
        check("…and a wheel over a card scrolls its list inside the card, not the page", inner > 0 and moved == 0, f"list {inner}, page {moved}")
        check("the species words sit on the fade, not on a frosted plate", "blur" not in o["plate"], o["plate"])
        check("the Quick Actions panel stays contextual", o["ctx"], "")
        check("no page-level sideways scroll", o["ovf"] == 0, str(o["ovf"]))

        # THE DECK, PRESSED — the arrow keys on the front card, then a real drag
        lit = lambda: c.eval("[...document.querySelectorAll('.adeck__dots i')].findIndex(i => i.classList.contains('on'))")
        key = lambda k: c.eval(f"document.querySelector('.adeck__stack').dispatchEvent(new KeyboardEvent('keydown', {{key: '{k}', bubbles: true}})); 1")
        key("ArrowRight"); time.sleep(0.9); after_next = lit()
        key("ArrowLeft"); time.sleep(0.9); after_prev = lit()
        check("→ brings the second card up, ← brings the first back", after_next == 1 and after_prev == 0, f"{after_next} -> {after_prev}")
        c.eval("document.getElementById('heroStage').scrollIntoView({block:'center'}); 1"); time.sleep(0.4)
        r = json.loads(c.eval("(r=>JSON.stringify([r.left,r.top,r.width,r.height]))(document.querySelector('.adeck__card[data-i=\"0\"]').getBoundingClientRect())"))
        x, y = r[0] + r[2] * .6, r[1] + r[3] / 2
        c.cmd("Input.dispatchMouseEvent", type="mousePressed", x=x, y=y, button="left", clickCount=1)
        for i in range(1, 9):
            c.cmd("Input.dispatchMouseEvent", type="mouseMoved", x=x - i * 40, y=y, button="left", buttons=1); time.sleep(0.016)
        c.cmd("Input.dispatchMouseEvent", type="mouseReleased", x=x - 320, y=y, button="left", clickCount=1); time.sleep(0.9)
        thrown = lit()
        check("a flick sends the front card to the back", thrown == 1, str(thrown))
        # LEFT TO RIGHT BRINGS THE LAST CARD BACK (25 Sep 2026: "left to right
        # that card has to come") — a real rightward drag, the same input path
        r = json.loads(c.eval("(r=>JSON.stringify([r.left,r.top,r.width,r.height]))(document.querySelector('.adeck__card[data-i=\"0\"]').getBoundingClientRect())"))
        x, y = r[0] + r[2] * .25, r[1] + r[3] / 2
        c.cmd("Input.dispatchMouseEvent", type="mousePressed", x=x, y=y, button="left", clickCount=1)
        for i in range(1, 9):
            c.cmd("Input.dispatchMouseEvent", type="mouseMoved", x=x + i * 45, y=y, button="left", buttons=1); time.sleep(0.016)
        c.cmd("Input.dispatchMouseEvent", type="mouseReleased", x=x + 360, y=y, button="left", clickCount=1); time.sleep(0.9)
        back = lit()
        clean = c.eval("[...document.querySelectorAll('.adeck__card')].filter(c=>c.style.transform||c.style.opacity||c.style.zIndex).length")
        check("a rightward drag brings the previous card back to the front", back == 0 and clean == 0, f"lit={back} inline={clean}")
        # THE DWELL UNDER REDUCED MOTION: no animation, so the deck never turns by itself
        check("under reduced motion the deck's dwell runs no animation", c.eval("document.querySelector('.adeck__dwell').getAnimations().length") == 0, "")

        # THE NOTES FILTER AND THE HOLD MENU
        c.eval("document.querySelector('.v2seg__opt[data-k=enclosure]').click(); 1"); time.sleep(0.8)
        shown = c.eval("[...document.querySelectorAll('.obs')].filter(o=>!o.hidden).length")
        check("Enclosures narrows the rail to the enclosure notes", shown == 2, str(shown))
        c.eval("document.querySelector('.v2seg__opt[data-k=all]').click(); 1"); time.sleep(0.8)
        c.eval("document.querySelector('.obs').dispatchEvent(new MouseEvent('contextmenu',{bubbles:true,cancelable:true,clientX:100,clientY:100})); 1"); time.sleep(0.5)
        check("press-and-hold / right-click lifts the note with a menu", c.eval("document.body.classList.contains('v2ctx-open') && !!document.querySelector('.v2ctx-lift')"), "")
        c.cmd("Input.dispatchKeyEvent", type="keyDown", key="Escape", code="Escape", windowsVirtualKeyCode=27); time.sleep(0.4)
        check("…and Escape puts it back", not c.eval("document.body.classList.contains('v2ctx-open')"), "")

    # THE DECK TURNS ON ITS OWN ("it has to auto scroll", 24 Sep 2026) — checked
    # in a Chrome that does not force reduced motion: the dwell is one 6000ms
    # animation, frozen and seeked to its end rather than waited for
    print("\nthe deck turns on its own")
    with Chrome(width=WIDTH, height=1200, reduced_motion=False) as c:
        c.goto(BASE + "index.html?v=2", settle=2.4)
        lit = lambda: c.eval("[...document.querySelectorAll('.adeck__dots i')].findIndex(i => i.classList.contains('on'))")
        a = c.eval("(a => a.length ? {n: a.length, state: a[0].playState, ms: a[0].effect.getTiming().duration} : {n: 0})(document.querySelector('.adeck__dwell').getAnimations())")
        check("one running dwell of 6000ms per front card", a.get("n") == 1 and a.get("state") == "running" and a.get("ms") == 6000, str(a))
        c.eval("document.querySelector('.adeck__dwell').getAnimations()[0].finish(); 1"); time.sleep(0.9)
        first = lit()
        c.eval("document.querySelector('.adeck__dwell').getAnimations()[0].finish(); 1"); time.sleep(0.9)
        check("its end turns the deck, and the next front card starts its own", first == 1 and lit() == 2, f"{first} -> {lit()}")
        # THE TURN IS ONE MOTION ("Animation need more smooth", 25 Sep 2026):
        # the moment the dwell ends the leaver is on its way AND the next card
        # is already rising — both animating in the same frame — the leaver
        # above the deck and still opaque at half time, when three quarters
        # of it has gone (no translucent card crossing the stack); and once
        # it has gone it rests
        # at the back at opacity 0 with nothing running on it — no snap back
        # to the front, no fade in the open. The flight is paused and seeked,
        # not waited for.
        c.eval("document.querySelector('.adeck__dwell').getAnimations()[0].finish(); 1"); time.sleep(0.08)
        m = c.eval("""(()=>{const l=document.querySelector('.adeck__card.is-flying'), f=document.querySelector('.adeck__card[data-i="0"]');
          if(!l||!f) return {leaver:!!l, front:!!f};
          const a=l.getAnimations()[0]; const T=a.effect.getTiming(); a.pause(); a.currentTime=T.duration*.5;
          const o=getComputedStyle(l).opacity, z=getComputedStyle(l).zIndex, x=Math.round(l.getBoundingClientRect().left-f.getBoundingClientRect().left);
          const out={leaver:true, front:true, rising:f.getAnimations().length>0, o, z, x, ms:T.duration, i:l.dataset.i}; a.play(); return out})()""")
        check("the leaver and the riser move in the same frame, the leaver above the deck", m.get("rising") and m.get("z") == "4" and m.get("i") == "3", str(m))
        check("…a 640ms flight, still opaque at half time with most of the card gone", m.get("ms") == 640 and m.get("o") == "1" and m.get("x", 0) < -300, str(m))
        time.sleep(1.0)
        after = c.eval("""(()=>{const cs=[...document.querySelectorAll('.adeck__card')];const back=cs.filter(x=>x.dataset.i==='3');
          return {flying:cs.filter(x=>x.classList.contains('is-flying')).length, running:back.reduce((n,x)=>n+x.getAnimations().length,0), o:back.map(x=>getComputedStyle(x).opacity), stack:document.querySelector('.adeck__stack').getBoundingClientRect().height}})()""")
        check("…and once gone it rests at the back at opacity 0 with nothing running, the stack still 210", after["flying"] == 0 and after["running"] == 0 and all(v == "0" for v in after["o"]) and after["stack"] == 210, str(after))
        r = c.eval("(r => [r.left + r.width / 2, r.top + r.height / 2])(document.querySelector('.adeck__card[data-i=\"0\"]').getBoundingClientRect())")
        c.cmd("Input.dispatchMouseEvent", type="mouseMoved", x=r[0], y=r[1]); time.sleep(0.3)
        check("a pointer over the band holds it", c.eval("document.querySelector('.adeck__dwell').getAnimations()[0].playState") == "paused", "")
        c.cmd("Input.dispatchMouseEvent", type="mouseMoved", x=5, y=5); time.sleep(0.3)
        check("…and leaving lets it run", c.eval("document.querySelector('.adeck__dwell').getAnimations()[0].playState") == "running", "")

        print("\nthe catalogue and both layouts agree")
        check("antz.checkDefaults() is clean", c.eval("antz.checkDefaults().length") == 0,
              c.eval("JSON.stringify(antz.checkDefaults())"))

        print("\nconsole")
        errs = c.errors()
        check("no errors or exceptions", not errs, "; ".join(str(e)[:110] for e in errs[:3]))


    # ── THE SWITCH · profile menu → Home page → Version 1 / Version 2 ─────
    # `?v=` was reachable only by typing it, which is the invisible-affordance
    # problem the profile menu exists to fix, so the menu carries the two
    # compositions as a radio group (8 Sep 2026).
    #
    # THE ONLY CHECK THAT MEANS ANYTHING IS PRESSING IT. Reading the rows and
    # their ticks would pass on a switch wired to nothing; setPageVersion
    # NAVIGATES — it has to, because `?v=` is read before the body is parsed
    # and again on boot to decide what to mount — so what is asserted is the
    # page that comes back.
    print("\nswitching version from the profile menu")
    with Chrome(width=WIDTH, height=1200) as c:
        c.goto(BASE + "index.html", settle=2.0)
        c.eval(OPEN_MENU)
        time.sleep(0.35)
        g = c.eval(VER_GROUP)
        # THREE SINCE 16 SEP, not two — V3 is the black page, node 506:10213.
        # The count is asserted rather than "at least two" because a row that
        # fails to render is exactly the failure this group has had before.
        check("the menu carries a Home page group of three radios",
              g["open"] and len(g["ver"]) == 3
              and all(r["role"] == "menuitemradio" for r in g["ver"])
              and "HOME PAGE" in [h.upper() for h in g["heads"]],
              f"{g['heads']} {[r['label'] for r in g['ver']]}")
        # AND EXACTLY ONE TICK. Version 1's `checked` was `!isV2()`, which is
        # true on V3 as well — the row would have ticked itself on a page it
        # was not showing. It reads its own predicate now, and what is asserted
        # is the invariant rather than three separate values.
        check("the tick is on the page you are actually on, and only there",
              [r["checked"] for r in g["ver"]] == ["true", "false", "false"],
              str([r["checked"] for r in g["ver"]]))
        check("neither row clips its note",
              not any(r["clipped"] for r in g["ver"]),
              str([r["note"] for r in g["ver"]]))
        check("the menu is wholly on screen with the group in it", g["onScreen"],
              f"{g['menuH']}px tall")

        c.eval(PRESS_VER % "2")
        time.sleep(1.8)
        w = c.eval(WHERE)
        # V2 is stamped "4" since 24 Sep 2026 — it wears V4's stylesheet, with
        # data-home="v2" for its own additions — so ?v=2 is what says "V2"
        check("pressing Version 2 lands on V2, at ?v=2",
              w["v"] == "4" and w["search"] == "?v=2", f"{w['v']} {w['search']}")
        check("…and it is really V2: no deck mounted", w["deck"] == 0, str(w["deck"]))

        # THE NO-OP. A row that reloads the whole page to arrive where you
        # already are looks broken, so setPageVersion returns false instead.
        c.eval(OPEN_MENU)
        time.sleep(0.35)
        g = c.eval(VER_GROUP)
        check("the tick has moved with the page",
              [r["checked"] for r in g["ver"]] == ["false", "true", "false"],
              str([r["checked"] for r in g["ver"]]))
        c.eval(PRESS_VER % "2")
        time.sleep(1.0)
        w = c.eval(WHERE)
        check("choosing the page you are on only closes the menu",
              w["v"] == "4" and w["search"] == "?v=2"
              and c.eval("(()=>{const m=document.querySelector('.pmenu');return !!m&&m.hidden})()"),
              f"{w['v']} {w['search']}")

        # AND BACK — to the PLAIN url, because V1 is the absence of the
        # parameter rather than `?v=1`.
        c.eval(OPEN_MENU)
        time.sleep(0.35)
        c.eval(PRESS_VER % "1")
        time.sleep(1.8)
        w = c.eval(WHERE)
        check("pressing Version 1 goes back to the plain URL",
              w["v"] == "1" and w["search"] == "", f"{w['v']} {w['search']!r}")
        check("…and V1's deck is mounted again", w["deck"] == 6, str(w["deck"]))

        # ── AND V3, THE BLACK PAGE · node 506:10213, 16 Sep 2026 ──────────
        # The boot gate was `PAGE_VERSION !== '2'`, which mounted V1's deck
        # and rail for anything that was not V2 — so V3 would have opened with
        # two bands it does not have and a dwell timer running behind them.
        # It reads `=== '1'` now, and this is what proves it.
        c.eval(OPEN_MENU)
        time.sleep(0.35)
        c.eval(PRESS_VER % "3")
        time.sleep(1.8)
        w = c.eval(WHERE)
        check("pressing Version 3 lands on V3, at ?v=3",
              w["v"] == "3" and w["search"] == "?v=3", f"{w['v']} {w['search']}")
        check("…and it is really V3: no deck mounted", w["deck"] == 0, str(w["deck"]))
        # THE GROUND IS BLACK AND THE PLANTING IS GONE — the two things that
        # make it this page rather than V2 with a different seed. `.foliage`
        # is asserted because it painted straight over the glow when V3 first
        # rendered: the artboard illustration measured 221 where the node
        # reads 74, and nothing else in the page would have failed.
        v3 = json.loads(c.eval("""(()=>{const cs=getComputedStyle;
          const f=document.querySelector('.foliage');
          return JSON.stringify({
            root: cs(document.documentElement).backgroundColor,
            hasGlow: cs(document.documentElement).backgroundImage.includes('radial-gradient'),
            foliage: f ? cs(f).display : 'absent',
            searchBg: cs(document.querySelector('.search')).backgroundColor,
            searchR: cs(document.querySelector('.search')).borderTopLeftRadius,
            searchBf: cs(document.querySelector('.search')).backdropFilter,
            scanBf: cs(document.querySelector('.search-btn')).backdropFilter,
            hint: (document.querySelector('.search__hint')
                   ? cs(document.querySelector('.search__hint')).color : 'absent'),
            qaBand: (document.querySelector('.qa-band')
                     ? cs(document.querySelector('.qa-band')).display : 'absent'),
            pillInk: cs(document.querySelector('.qa-pill')).color,
            pillFill: cs(document.querySelector('.qa-pill')).backgroundColor,
            footGap: (()=>{const s=[...document.querySelectorAll('#moduleGrid .slot')].pop();
                      return s ? Math.round(document.documentElement.scrollHeight
                             - (s.getBoundingClientRect().bottom + scrollY)) : -1})(),
            ink: cs(document.querySelector('.greeting__name')).color})})()"""))
        check("…on a black ground with the warm glow over it",
              v3["root"] == "rgb(0, 0, 0)" and v3["hasGlow"],
              f"{v3['root']} glow={v3['hasGlow']}")
        check("…and no planting, which would paint straight over it",
              v3["foliage"] == "none", str(v3["foliage"]))
        # THE HEADER IS GLASS, NOT A HOLE IN THE BLACK · ruled 17 Sep 2026.
        #
        # THIS CHECK USED TO ASSERT 10%, THE NODE'S OWN FILL, and it was
        # right until the ruling changed. 506:10233 states
        # `rgba(255,255,255,0.1)` flat, and over PURE BLACK that is 24 levels
        # of 255 — it rendered as a dark rectangle with a hairline, and was
        # reported as "glass effect not working". The fill is 14% behind the
        # house glass filter now, which is the same material the Quick
        # Actions pill at the foot of this page already uses.
        #
        # SO THE ASSERTION MOVED WITH IT rather than being deleted: what is
        # checked is that the field and the scan button carry a REFRACTING
        # material at all — a blur with a brightness lift — because that is
        # the thing that was missing and the thing that can silently go away
        # again. The radius and the ink are still the node's.
        glass = ("blur" in v3["searchBf"] and "brightness" in v3["searchBf"]
                 and v3["searchBf"] == v3["scanBf"])
        check("…the search and scan are glass, 12px radius, ink white",
              glass and v3["searchR"] == "12px" and v3["ink"] == "rgb(255, 255, 255)"
              and v3["searchBg"] == "rgba(255, 255, 255, 0.14)",
              f"{v3['searchBg']} r={v3['searchR']} {v3['searchBf']}")
        # AND THE PLACEHOLDER IS WHITE · 506:10237 sets the whole string in
        # `text-white`. The rotating hint that sits over the field is the
        # thing that actually draws it, and it kept its own light-page grey.
        check("…with the placeholder and its cycling word white",
              v3["hint"] in ("rgb(255, 255, 255)", "absent"), str(v3["hint"]))
        # AND THERE IS NO WHITE WASH AT THE FOOT. `.qa-band` is white at 20%
        # falling to grey — correct under the pill on a pale page, a grey
        # slab across the bottom 182px of a black one.
        check("…and no pale wash under the Quick Actions bar",
              v3["qaBand"] == "none", str(v3["qaBand"]))
        # THE BAR IS DARK GLASS WITH WHITE MARKS · ruled 17 Sep 2026, "make it
        # icon white". The pill is glass, so its own lightness follows whatever
        # scrolls behind it — a light green disc over a Pharmacy card, a mid
        # grey over the black foot — and white marks on the stock 40% white
        # fill would only have swapped which of the two was unreadable. The
        # fill is 506:10916's dark pane, the same material the scrolled search
        # row uses at the other end of this page.
        check("…the Quick Actions bar is dark glass with white marks",
              v3["pillInk"] == "rgb(255, 255, 255)"
              and v3["pillFill"] == "rgba(30, 30, 30, 0.4)",
              f"{v3['pillInk']} on {v3['pillFill']}")
        # AND THE PAGE ENDS WHERE THE CARDS DO. `#panel-modules` gives back the
        # pill's own 112px and that is the whole of what the foot needs;
        # `.main-frame` and `.page` were adding 72 more, which on black is
        # visible as nothing at all. Asserted as a RANGE because the pill's
        # clearance is derived from tokens: anything past ~130 is the empty
        # space this was reported as.
        check("…and the page hugs the last card, less the pill's clearance",
              0 < v3["footGap"] <= 130, f"{v3['footGap']}px below the last card")

        # ── THE VERTICAL RHYTHM · 506:10213 states it to the pixel ────────
        # The Greeting block runs 0-200 with 16 of padding either end, the
        # Home Header 16-128 on its own 24, the Search Row 128-184, and the
        # Main Frame's Modules begin at 208 — so the hero top IS 208 and the
        # gap from the field to the banner is 24.
        #
        # ASSERTED BECAUSE IT WAS WRONG IN THREE PLACES AT ONCE, and each was
        # inherited rather than written: the header began at 0, the row ran 52
        # in flow where the node draws 56, and the gap measured 46 against 24
        # — that last one `.modules-band`'s `margin-top`, which V3 picked up
        # when it was named beside V2 on the structural rules and which exists
        # to make room for a teal wash this page does not draw.
        rhythm = json.loads(c.eval("""(()=>{const b=e=>e.getBoundingClientRect();
          const R=e=>[Math.round(b(e).top),Math.round(b(e).bottom)];
          /* THE BANNER MOVED INTO THE GRID ON V3 · 506:10260 makes it the
             first band of the module block rather than chrome above it, so
             the page's own `.hero` is hidden there and the card carries it.
             Both resolve to the same BOX — 208 to 352 on the page's 24 — so
             the three checks below are unchanged in what they assert; they
             just have to look in the right place. `.hero` first would match
             the hidden markup copy and measure zero. */
          const HERO=()=>document.querySelector('.card[data-variant="hero.v3"] .hero')
                       || document.querySelector('.hero');
          return JSON.stringify({
            hdr:R(document.querySelector('.home-header')),
            field:R(document.querySelector('.search')),
            hero:R(HERO()),
            heroX:[Math.round(b(HERO()).left), Math.round(b(HERO()).right)],
            card1:R([...document.querySelectorAll('#moduleGrid .card')]
                    .find(e=>e.dataset.variant!=='hero.v3')),
            gap:Math.round(parseFloat(getComputedStyle(
              document.querySelector('#moduleGrid')).rowGap))})})()"""))
        # ONLY AT 744, WHICH IS THE ARTBOARD'S OWN WIDTH — and on this project
        # that is not a caveat but the rule: the frame is 744 and its numbers
        # ARE the app's, which is why the phone/tablet boundary was moved to
        # 743/744. Above it the page padding grows and below it the greeting's
        # name wraps, so the ladder is a different ladder and asserting these
        # y-values there would be asserting a coincidence. What survives every
        # width is the GAP and the hero's own box, checked underneath.
        if WIDTH == 744:
            check("the header is the node's 16 to 128",
                  rhythm["hdr"] == [16, 128], str(rhythm["hdr"]))
            check("…the field 130 to 182", rhythm["field"] == [130, 182],
                  str(rhythm["field"]))
            check("…the hero 208 to 352, on the page's own 24 either side",
                  rhythm["hero"] == [208, 352] and rhythm["heroX"] == [24, 720],
                  f"{rhythm['hero']} x{rhythm['heroX']}")
        # AT EVERY WIDTH: the field-to-hero gap is 26 (the node's 24 of frame
        # padding plus the 2 its search row carries under the field), and the
        # grid follows the hero by one gutter. These are the two relationships
        # the ladder exists to produce; the y-values above are where they land
        # at 744.
        check("the hero follows the field by the node's gap",
              rhythm["hero"][0] - rhythm["field"][1] == 26,
              f"{rhythm['hero'][0] - rhythm['field'][1]}px (node 26)")
        # AGAINST `--grid-gap`, NOT A LITERAL 16. On the artboard the space
        # between the banner and the cards IS the space between two card rows
        # — which is why the hero's own margin is written as that token — and
        # the token steps 16 → 14 → 12 with the breakpoints. Asserting 16 here
        # passed at 744 and failed at 390 on a page that was correct.
        check("…and the first card row one gutter under it",
              rhythm["card1"][0] - rhythm["hero"][1] == rhythm["gap"],
              f"{rhythm['card1'][0] - rhythm['hero'][1]}px on a {rhythm['gap']}px gutter")

        # ── AND THE BAR TURNS TO DARK GLASS WHEN IT STICKS · 506:10916 ────
        # THE SECOND ARTBOARD EXISTS FOR THIS. The bar is rgba(30,30,30,.4)
        # behind a 20px blur with its bottom corners at 28, 88 tall, on 16 of
        # side padding where the resting row has 24 — and the greeting is gone.
        # What shipped first was the pale mint wash V1 and V2 use, which on a
        # black page reads as a light slab dropped on top of it.
        stuck = json.loads(c.eval("""(()=>{
          scrollTo(0, 900);
          return new Promise(r=>setTimeout(()=>{
            const b=e=>e.getBoundingClientRect();
            const row=document.querySelector('.search-row');
            const pre=getComputedStyle(row,'::before');
            r(JSON.stringify({
              stuck: row.classList.contains('is-stuck'),
              top: Math.round(b(row).top), h: Math.round(b(row).height),
              hdrH: Math.round(b(document.querySelector('.home-header')).height),
              bg: pre.backgroundColor,
              blur: pre.backdropFilter||pre.webkitBackdropFilter,
              radius: pre.borderBottomLeftRadius, opacity: pre.opacity,
              pad: getComputedStyle(row).paddingLeft}))}, 700))})()""",
          await_promise=True))
        check("scrolled, the bar sticks at the top",
              stuck["stuck"] and stuck["top"] == 0,
              f"stuck={stuck['stuck']} top={stuck['top']}")
        if WIDTH == 744:
            check("…in the node's own 88", stuck["h"] == 88, f"{stuck['h']}px")
        check("…as dark glass, not the pale wash V1 and V2 use",
              stuck["bg"] == "rgba(30, 30, 30, 0.4)"
              and "blur(20px)" in stuck["blur"] and stuck["opacity"] == "1",
              f"{stuck['bg']} {stuck['blur']} opacity {stuck['opacity']}")
        check("…with its bottom corners at 28 and 16 of side padding",
              stuck["radius"] == "28px" and stuck["pad"] == "16px",
              f"r={stuck['radius']} pad={stuck['pad']}")
        # AND THE GREETING IS STILL THERE, SCROLLED OFF — not collapsed. It
        # WAS collapsed, with `body:has(.search-row.is-stuck)` taking the
        # header to `height: 0`, and that latched the page: the collapse
        # removes the 112px the observer uses to decide the row is stuck, so
        # once it closed `is-stuck` could never clear. Scrolled to 1200 and
        # back to 0, the header was still 0 tall and the greeting never came
        # back. Asserted as PRESENT so the collapse cannot be reintroduced.
        # NOT COLLAPSED — asserted as "still has height", not as 112. The
        # header is 112 at 744 and taller at 390, where the name wraps; what
        # the latch did was take it to ZERO, and that is the thing to pin.
        check("…with the greeting scrolled off rather than collapsed",
              stuck["hdrH"] > 0, f"{stuck['hdrH']}px")

        # ── AND IT ALL COMES BACK ON THE WAY UP ──────────────────────────
        # The round trip, not just the down leg. A state must not consume the
        # signal that ends it, and the only way to see that is to go back.
        back = json.loads(c.eval("""(()=>{
          scrollTo(0, 0);
          return new Promise(r=>setTimeout(()=>{
            const b=e=>e.getBoundingClientRect();
            const row=document.querySelector('.search-row');
            r(JSON.stringify({
              stuck: row.classList.contains('is-stuck'),
              rowTop: Math.round(b(row).top),
              hdrH: Math.round(b(document.querySelector('.home-header')).height),
              veil: getComputedStyle(row,'::before').opacity}))}, 800))})()""",
          await_promise=True))
        check("scrolled back to the top, the bar un-sticks and the header returns",
              not back["stuck"] and back["hdrH"] > 0 and back["rowTop"] > 0,
              f"stuck={back['stuck']} header={back['hdrH']}px rowTop={back['rowTop']}")
        check("…and the dark glass fades back out with it",
              back["veil"] == "0", f"opacity {back['veil']}")

        # ── V3'S OWN CARD SET · 506:10213, read off the frame's geometry ──
        # Every card in that artboard is a whole number of grid cells — 162
        # wide and 144 tall on a 16 gutter, the same grid V2 uses — so 340 is
        # two columns, 304 two rows and 464 three. That is what makes V3 a
        # LAYOUT rather than twenty new components, and it is what this
        # asserts: the footprints, in the frame's own order.
        #
        # IT SEEDED V2'S SET FOR TWO DAYS, which looked like the black page
        # with the wrong cards on it. The seed reads `isV3()` now.
        cards = json.loads(c.eval("""(()=>{const b=e=>e.getBoundingClientRect();
          try{localStorage.clear()}catch(e){}
          return JSON.stringify([...document.querySelectorAll('#moduleGrid .card')]
            .map(x=>[x.dataset.variant,
                     Math.round(b(x).width)+'x'+Math.round(b(x).height)]))})()"""))
        # 17 Sep 2026 · THE SET IS 506:10269's OWN WIDGETS NOW. The footprints
        # below are unchanged — the frame's geometry did not move — but
        # fifteen of the ids did: the seed used to fill the frame's ORDER with
        # the nearest cards the catalogue already had, and a queue standing in
        # for 506:10368 has the right footprint and the wrong card in it.
        # This list is the one place that difference is asserted, so it is the
        # one place that has to be rewritten when it changes; left alone it
        # would have gone on passing for the shape while the content moved
        # underneath it, which is the failure this file's own header warns
        # about.
        want = [
            # 17 Sep, later · THE BANNER IS A CARD NOW. 506:10260 "Modules" is
            # 696x2224 — the Hero Banner at y=0, the Modules Container at 160
            # — so the banner is the first band of the module block, not
            # chrome above it. In the markup it was the one thing on this page
            # with no handle on it in edit mode.
            ("hero.v3", "696x144"),
            ("insights.v3", "340x144"), ("species.v3stats", "340x144"),
            # the promo banner, four columns and ONE row (506:12894) — its
            # absence is why every row below it sat 160px above the frame
            ("promo.tags", "696x144"),
            ("notes.v3", "340x464"), ("pharmacy.v3requests", "340x304"),
            ("approvals.v3transfer", "340x144"),
            # V3's own one-cell tiles, not the doors — 506:10428 stacks the
            # glyph and name together where `door` pushes them apart, and two
            # of these four cells carry a figure rather than a name at all.
            ("eggs.v3", "162x144"), ("species.v3new", "162x144"),
            ("users.v3", "162x144"), ("mortality.v3", "162x144"),
            ("pharmacy.v3stock", "340x304"), ("pharmacy.default", "162x144"),
            ("lab.default", "162x144"), ("species.v3week", "340x144"),
            ("species.v3list", "340x304"), ("approvals.v3helpdesk", "340x144"),
            ("mortality.v3widgets", "340x144"), ("eggs.v3collected", "340x304"),
            ("medical.v3actions", "340x144"), ("communication.v3chat", "340x144"),
            # AND THE BAND THAT CLOSES IT · 517:13020, four columns and one
            # row. It was absent, which is why the grid used to end on a
            # half-empty row where the frame ends square.
            ("quick.v3actions", "696x144"),
        ]
        got = [tuple(r) for r in cards]
        if WIDTH == 744:
            check("V3 seeds its own twenty-two, in the frame's order",
                  got == want,
                  "as drawn" if got == want else
                  f"{len(got)} cards; first difference "
                  f"{next((f'{g} want {w}' for g, w in zip(got, want) if g != w), 'length only')}")
        else:
            # away from 744 the columns change, so the footprints do; what
            # still has to hold is WHICH cards and in what order
            check("V3 seeds its own twenty-two, in the frame's order",
                  [g[0] for g in got] == [w[0] for w in want],
                  f"{len(got)} cards")
        # AND NOTES IS THREE ROWS, which is the one span this grid did not
        # have. 464 is 144 x 3 + 16 x 2, and no existing size is 3 tall — a
        # stretched `tall` would have changed every card using that size on
        # four other pages, so `xtall` is its own step.
        if WIDTH == 744:
            check("…with Notes on the new three-row step, not a stretched tall",
                  dict(got).get("notes.v3") == "340x464",
                  str(dict(got).get("notes.v3")))
        # ── NO ROW FLAGS, AND NO HOLES IN THE MIDDLE OF THE GRID ──────────
        # `newRow` pins a card to a fresh row so a DESIGNED gap survives
        # first-fit. 506:10269 has no gaps — every row of it fills all four
        # columns — so the seven flags this seed carried did nothing on a
        # fresh page and did real damage once a card was dragged: a flag
        # travels with its card, so moving Species Management below the promo
        # left Key Insights alone on a row with two empty cells beside it.
        # Reported as "when I arrange the widgets, empty space was there".
        #
        # Asserted two ways: no card carries the flag, and the packed grid has
        # no gap ABOVE its last row. The last row may be short — twenty-two
        # cards spanning 56 cells cannot always end on a multiple of four, and
        # nothing is left to fill it. Measured across 40 random arrangements
        # while this was written: interior holes zero every time.
        grid = json.loads(c.eval("""(() => {\n  const g = document.getElementById("moduleGrid").getBoundingClientRect();\n  const set = new Set();\n  for (const e of document.querySelectorAll("#moduleGrid .card")) {\n    const b = e.getBoundingClientRect();\n    const x = Math.round((b.x-g.x)/178), y = Math.round((b.y-g.y)/160);\n    const w = Math.round((b.width+16)/178), h = Math.round((b.height+16)/160);\n    for (let dy=0; dy<h; dy++) for (let dx=0; dx<w; dx++) set.add((y+dy)+":"+(x+dx));\n  }\n  const maxY = Math.max(...[...set].map(s=>+s.split(":")[0]));\n  let holes = 0;\n  for (let y=0; y<maxY; y++) for (let x=0; x<4; x++) if (!set.has(y+":"+x)) holes++;\n  return JSON.stringify({holes, flagged: antz.state().cards.filter(c=>c.newRow).length});\n})()"""))
        check("…with no row flags left on it", grid["flagged"] == 0,
              str(grid["flagged"]) + " cards carry newRow")
        check("…and no holes above the last row", grid["holes"] == 0,
              str(grid["holes"]) + " interior cells empty")
        errs = c.errors()
        check("no console errors across three switches", not errs,
              "; ".join(str(e)[:110] for e in errs[:3]))

    # ── THE QUICK ACTIONS PILL — node 270:4176 ────────────────────────────
    # It replaced a corner FAB and a sixteen-cell dock on the ruling of 8 Sep
    # ("Remove Current Fab"), so the first check is that the FAB is GONE:
    # leaving both would put two ways to the same sixteen verbs on one page.
    #
    # THE COLLAPSE IS THE PART THAT CAN ROT SILENTLY. It is driven by the
    # sticky search row's observer — one signal, two consumers — so a change to
    # that observer breaks a behaviour on the other side of the page. Measured
    # as a WIDTH, not a class: the class is what the stylesheet reads, and the
    # question is whether the label actually went.
    print("\nthe Quick Actions row")
    with Chrome(width=WIDTH, height=768) as c:
        c.goto(BASE + "index.html?v=2", settle=2.2)
        r = c.eval(PILL)
        check("the pill is there and the FAB is not", r["pill"] and not r["fab"],
              f"pill={r['pill']} fab={r['fab']}")
        # AND THE BAR CARRIES NOTHING ELSE AT REST · ruled 10 Sep 2026,
        # "Edit Modules remove here becouse it already in the Profile". An
        # Edit control sat in this row for part of the day and floated over
        # the cards it was offering to rearrange; the profile menu already
        # holds that entry. The mode's OWN buttons still arrive here while
        # editing, which is checked further down — so this pins the resting
        # state only: two controls, the pill and the disc.
        #
        # THE ANCHOR IS ASSERTED PRESENT AND HIDDEN, not absent, and that is
        # the real point of the check. createEditMode swaps Done in by
        # `editBtn.replaceWith(doneBtn)`, so deleting that button from the
        # slot would leave replaceWith with no parent to act on — silently —
        # and there would be no way out of edit mode. Hidden is correct;
        # gone is a trap, and it is the kind that passes a visual check.
        bar = json.loads(c.eval("""(()=>{
          // the Modules chip (.mhint, 25 Sep 2026) hangs off the row by design
          // and is asserted on its own below; anything else is still a stray
          const shown=[...document.querySelectorAll('.qa-row button:not(.mhint)')]
            .filter(b=>getComputedStyle(b).display!=='none')
            .map(b=>b.textContent.trim()||b.getAttribute('aria-label')||'?');
          const v2=document.documentElement.dataset.home==='v2';
          const a=document.querySelector(v2 ? '#modulesHead .link-btn:not(.link-btn--done)' : '.qa-edit > .link-btn:not(.link-btn--done)');
          return JSON.stringify({shown, anchorPresent:!!a,
            anchorHidden:a?getComputedStyle(a).display==='none':null})})()"""))
        check("…and the resting bar is the pill and the disc, nothing more",
              bar["shown"] == ["Quick Actions", "Chat"], str(bar["shown"]))
        # THE MODULES CHIP (25 Sep 2026): IN the row, so chip + pill + disc
        # are centred as one group ("Bottom actions not center aligned"), and
        # it opts back in to pointers — `.qa` passes taps through, and a chip
        # that did not opt in let a tap open the note under it. Hit-tested
        # at its own centre, because element.click() skips that failure.
        mh = c.eval("""(()=>{const ch=document.querySelector('.mhint'); if(!ch) return {n:0, v2:document.documentElement.dataset.home==='v2'};
          const R=e=>e.getBoundingClientRect(); const els=[ch, document.querySelector('.qa-pill'), document.querySelector('.qa-chat')].filter(e=>e&&R(e).width>1);
          const L=Math.min(...els.map(e=>R(e).left)), Rr=Math.max(...els.map(e=>R(e).right)); const r=R(ch);
          const hit=document.elementFromPoint(r.left+r.width/2, r.top+r.height/2);
          return {n:document.querySelectorAll('.mhint').length, inRow:ch.parentElement.classList.contains('qa-row'), centreOff:Math.round((L+Rr)/2-innerWidth/2),
            hit:!!hit?.closest('.mhint'), label:ch.getAttribute('aria-label'), v2:document.documentElement.dataset.home==='v2'}})()""")
        if mh.get("v2"):
            check("V2's Modules chip sits in the row, the three centred as one group", mh["n"] == 1 and mh["inRow"] and abs(mh["centreOff"]) <= 1, str(mh))
            check("…a tap at its centre reaches the chip, not the note under it", mh["hit"], str(mh))
            check("…and says how many modules are below", str(mh.get("label", "")).endswith("modules below. Go to Modules"), str(mh.get("label")))
        v2 = c.eval("document.documentElement.dataset.home === 'v2'")
        check("…with the mode's swap anchor kept" + (" in the Modules head, shown (node 718:17649)" if v2 else ", and kept hidden"),
              bar["anchorPresent"] and (not bar["anchorHidden"] if v2 else bar["anchorHidden"]),
              f"present={bar['anchorPresent']} hidden={bar['anchorHidden']}")
        # 40 AND NOT THE NODE'S 109 — the ruling of 8 Sep; see --qa-b in the
        # stylesheet for why the artboard's number does not survive a page that
        # scrolls. Below the phone boundary it is 24.
        #
        # THE BOUNDARY IS 744, NOT 768, and this line was the last thing left
        # holding the old number. Node 321:3570 is drawn at 744 and specifies
        # the TABLET treatment there, so the phone band was moved to
        # `max-width: 743px` throughout the stylesheet — which makes 744 a
        # tablet, and a tablet stands the pill 40 from the foot. Read at 744
        # against the old 768 this asked for 24, got the correct 40, and
        # failed a page that is right.
        want_b = 40 if WIDTH >= 744 else 24
        check(f"centred on the page, {want_b} from the foot",
              r["centred"] and near(r["fromFoot"], want_b, 1.5),
              f"centred={r['centred']} foot={r['fromFoot']}")
        # GLASS SINCE NODE 295:5561, where 280:3521 drew flat #37BD69 with a
        # white label and a white 1px stroke. The fill is asserted as RGBA and
        # not RGB on purpose: an opaque pill would satisfy a colour check and
        # have no glass in it whatever. `backgroundImage` stays `none` because
        # a leftover gradient would sit ON TOP of the fill and hide it.
        check("the frame's stadium, white-at-40% and a black label",
              r["radius"] == "999px" and r["borderW"] == "0px"
              and r["bgColor"] == "rgba(255, 255, 255, 0.4)"
              and r["ink"] == "rgb(0, 0, 0)" and r["bg"] == "none",
              f"{r['radius']} / {r['bgColor']} / {r['ink']} / border {r['borderW']}")
        # THE REFRACTION IS THE 9 SEP INSTRUCTION and the frame cannot draw it:
        # over a flat artboard a 40% fill renders flat, so this is the one part
        # of the material that only the build can be checked for.
        check("…and both controls actually refract what is behind them",
              "blur(20px)" in (r["backdrop"] or "")
              and "saturate(1.8)" in (r["backdrop"] or "")
              and "blur(20px)" in (r["chatBackdrop"] or ""),
              f"pill {r['backdrop']} | disc {r['chatBackdrop']}")
        # …BUT NOT EQUALLY, AND THAT IS THE RULING OF 9 SEP. The disc drops the
        # pill's saturation because amplifying the backdrop is what let the
        # backdrop's HUE win — see the departure note under `.qa-chat`.
        check("…the disc refracting less hard than the pill, deliberately",
              "saturate(1)" in (r["chatBackdrop"] or "")
              and "saturate(1.8)" not in (r["chatBackdrop"] or ""),
              r["chatBackdrop"])
        # ONE DEPTH FOR THE PAIR, where the previous frame gave them two and
        # both were transcribed. Compared as strings so they cannot drift.
        check("…on one shared drop, the node's dy2/blur4 at 25%",
              r["shadow"].startswith("rgba(0, 0, 0, 0.25) 0px 2px 4px 0px")
              and r["shadow"] == r["chatShadow"],
              f"same={r['shadow'] == r['chatShadow']} {r['shadow'][:46]}")
        # THE MARK IS MASKED, NOT A SECOND ASSET. 295:5561 exports it identical
        # to the committed file but `fill="black"`; if someone ever commits that
        # export and reverts to an <img>, the mask goes and this fails.
        check("…and the grid mark is the one asset, inked off the pill",
              r["gridMask"] and "qa-actions.svg" in r["gridMask"]["mask"]
              and r["gridMask"]["ink"] == "rgb(0, 0, 0)",
              f"{(r['gridMask'] or {}).get('ink')} via {(r['gridMask'] or {}).get('mask','')[-24:]}")
        # …AT 18.33 IN A 20 BOX, WHICH IS THE ONE THING 295:5580 CAUGHT WRONG.
        # The frame's glyph container is 20x20 (`fi_10348852`) holding artwork
        # inset `5.21% 3.14% 3.15% 5.21%` — 18.33 square at 1.042 from the top
        # left, the same number as the export's own 18.3294 viewBox. Sizing the
        # mask `100% 100%` stretched it over the full 20 and drew the mark 9%
        # too large: measured against the node's render, the glyph's ink box was
        # (16,16,20,20) against the frame's (17,17,18,18), and every column of
        # the glyph box differed while the label's did not. Fixed, both read
        # (17,17,18,18) and the region's mean error halves, 14.19 → 7.33.
        # The 20px BOX is asserted alongside the mask so a future change cannot
        # satisfy this by shrinking the container instead.
        check("…sized 18.33 inside the frame's 20px box, not stretched to it",
              r["gridMask"]["box"] == [20, 20]
              and r["gridMask"]["size"].startswith("18.33px 18.33px")
              and r["gridMask"]["pos"].startswith("1.042px 1.042px"),
              f"box {r['gridMask']['box']} mask {r['gridMask']['size']} at {r['gridMask']['pos']}")

        # THE DISC · 56 SINCE 295:5561, where every frame before drew the pair
        # the same height. It was in 270:4176 too and was never built; this is
        # what stops it being dropped again.
        check("the chat disc is beside it, 56 across — 4 more than the pill",
              r["chat"] and near(r["chatW"], 56, 1) and near(r["chatH"], 56, 1)
              and r["chatH"] > r["h"],
              f"{r['chatW']}x{r['chatH']} vs pill {r['w']}x{r['h']}")
        # ITS TINT: FITTED STOPS, AND ALPHAS THAT ARE NOT THE NODE'S.
        #
        # The STOPS are a measurement, not a preference. Figma's handles are at
        # 0%/100% of a gradient that runs PAST the disc; projected onto the box
        # they land at 50.5% and 94.8% along 142.21deg. Transcribing the handles
        # instead compresses the ramp into the shape and darkens its whole upper
        # half. Fitted against three sampled pixels, worst error 3/255.
        #
        # The ALPHAS are 55/35 where the node says 20/40, and that is a ruling
        # of 9 Sep 2026 rather than a transcription error — DO NOT "restore" it
        # to the node. At the node's alphas the disc takes whatever hue is
        # behind it: measured 16°, orange, over V1's coral observation card
        # against the node's own 189°, and three of V1's four priority colours
        # are warm. At 55/35 it measures 191° over that card and 189° over the
        # module grid. Both halves are asserted literally so either drifting
        # back fails here with the reason attached.
        check("…wearing the cyan→mint tint at its fitted stops and ruled alphas",
              r["chatBgColor"] == "rgba(255, 255, 255, 0.35)"
              and "142.21deg" in r["chatBgImage"]
              and "rgba(0, 175, 214, 0.55) 50.5%" in r["chatBgImage"]
              and "rgba(96, 221, 186, 0.55) 94.8%" in r["chatBgImage"]
              and r["chatBorderW"] == "0px",
              r["chatBgImage"][:96])
        check("…12 from the pill, which is the frame's gap",
              near(r["chatGap"], 12, 1), str(r["chatGap"]))
        check("…carrying the frame's own 24px glyph, loaded",
              r["chatGlyph"] and near(r["chatGlyphW"], 24, 1),
              f"loaded={r['chatGlyph']} {r['chatGlyphW']}px")
        # a disc with a glyph and no text has no accessible name without this
        check("…and it is named for a screen reader", r["chatLabel"] == "Chat",
              str(r["chatLabel"]))
        check("it reads \"Quick Actions\" at rest", r["label"] == "Quick Actions" and r["labelW"] > 60,
              f"{r['label']!r} at {r['labelW']}px")
        check("the wash is behind it", r["band"], "")

        # scrolled: the words go, the pill closes to a disc around its glyph
        c.eval("scrollTo(0, 600); 1")
        time.sleep(0.8)
        sc = c.eval(PILL)
        check("scrolled: the label collapses to nothing",
              sc["scrolled"] and sc["labelW"] == 0, f"scrolled={sc['scrolled']} label={sc['labelW']}px")
        # A TRUE CIRCLE SINCE THE PADDING BECAME THE NODE'S 16 all round: the
        # old 14 closed the pill to 48x52, a 4px oval that read as a near-miss.
        check("…and the pill is a circle, not a near-miss",
              abs(sc["w"] - sc["h"]) <= 1 and near(sc["w"], 52, 1),
              f"{sc['w']}x{sc['h']}")
        # the disc has no label to lose and must not move or resize with it
        check("…while the chat disc holds its size",
              near(sc["chatW"], 56, 1) and near(sc["chatH"], 56, 1),
              f"{sc['chatW']}x{sc['chatH']}")
        # ── THE PAIR STAYS A PAIR · ruled 10 Sep 2026 ──────────────────────
        # THIS ROW HAS NOW BEEN RULED BOTH WAYS, and the second ruling is the
        # one in force: "here this gab i dont want. make centre when i scroll
        # it."
        #
        # The geometry allows exactly one of these at a time. The row is
        # centred and holds pill + 12 + disc, so when the pill narrows from
        # 168 to 52 either the row re-centres — constant gap, disc travels —
        # or the pill reserves its open width — both controls still, gap
        # opens to ~69. The reservation was built first, to stop the disc
        # moving under a finger mid-scroll; it was then rejected on the gap it
        # produced, which is what the user actually saw.
        #
        # So what is asserted now is the CONSTANT GAP and a centred row, and
        # the disc's travel is asserted as a consequence rather than left
        # unstated — half the pill's collapse, (168-52)/2 = 58.
        check("…the gap stays the frame's 12, open and collapsed alike",
              r["gapToDisc"] == 12 and sc["gapToDisc"] == 12,
              f"{r['gapToDisc']} → {sc['gapToDisc']}")
        check("…the pill's own centre never moves",
              abs(sc["pillCentre"] - r["pillCentre"]) <= 2,
              f"{r['pillCentre']}→{sc['pillCentre']}")
        # AND THE DISC TAKES THE WHOLE SHIFT, which is the accepted cost of
        # the ruling and is pinned so it cannot quietly grow: it is exactly
        # half the label's collapse, and anything else means the row stopped
        # being centred.
        check("…and the disc takes the shift, half the label's collapse",
              abs(abs(sc["discCentre"] - r["discCentre"]) - (r["w"] - 52) / 2) <= 3,
              f"disc {r['discCentre']}→{sc['discCentre']}, "
              f"expected {round((r['w'] - 52) / 2)}")
        check("…with the row still centred on the page while scrolled",
              sc["centred"], f"centred={sc['centred']}")

        # the menu, on a white material over a softened page
        c.eval("document.querySelector('.qa-pill').click(); 1")
        time.sleep(0.6)
        m = c.eval(MENU)
        # ═══ WHICH PANEL IS LIVE IS READ, NOT ASSUMED · 22 September 2026 ═══
        #
        # `QA_CONTENT` in index.html selects between two panels that are BOTH
        # fully built and fully styled, and it has now moved in both
        # directions: the verbs (8 Sep) → the launcher (9 Sep) → the verbs
        # again, on the owner re-posting the phone app's own Quick Actions
        # sheet — "These are Original Quick Actions. Update Current Quick
        # Actions", and, asked which surface, "All Modules Popup Selection i
        # was telling to change."
        #
        # THE LESSON OF THAT SECOND MOVE IS WHY THIS IS A BRANCH AND NOT AN
        # EDIT. When the constant went to 'modules' the verb panel's checks
        # were overwritten with the launcher's, so flipping it back left the
        # suite asserting a panel that no longer existed: three failures and
        # one hard crash, in a file whose whole subject is the control that
        # changed. Both readings are now asserted, the live one decides which
        # runs, and the constant costs nothing on either side of the flip.
        #
        # WHAT IS ASSERTED IN BOTH CASES: the panel holds ONE population and
        # not both. A panel carrying verbs AND tiles means the switch failed
        # open, which is the failure neither branch would otherwise catch.
        launcher_live = bool(m["isModules"])
        if launcher_live:
            # NINETEEN MODULES · the 9 Sep ruling, built from
            # mockups/module-launcher.html variant 4A.
            check("it opens all nineteen modules, and no verbs",
                  m["open"] and m["tiles"] == 19 and m["cells"] == 0,
                  f"tiles={m['tiles']} verbs={m['cells']} head={m['head']!r}")
            # WHITE AT 40% OVER A 15px BLUR · node 371:5157, and ruling five on
            # this surface in six days: .94 at radius 22, then the profile
            # menu's borrowed material, then 4A's .62/30/saturate(1.8), which
            # went to .92 to stay white over an 82% black backdrop and back
            # when that became a light 30% tint. The node states .4 and 15 with
            # NO saturation, and the saturate is asserted ABSENT rather than
            # merely not required — it was never in the file, and a lift nobody
            # can point at a source for is what makes the next comparison
            # against the artboard fail for reasons nobody can name.
            check("the node's white at 40% over a 15px blur, and no saturation",
                  m["material"] == "rgba(255, 255, 255, 0.4)" and m["radius"] == "28px"
                  and "blur(15px)" in (m["panelBlur"] or "")
                  and "saturate" not in (m["panelBlur"] or ""),
                  f"{m['material']} r={m['radius']} {m['panelBlur']}")
            # AND NO CLIP WINDOW, in any state. The verb panel unfolds out of
            # the pill's measured box by transitioning `clip-path`; the
            # launcher scales up out of the pill as one surface instead, and a
            # clip window would open over a panel that is already growing.
            # Asserted because `.qa.is-open .qa-menu` outranks the launcher's
            # own rule on specificity and put the clip back once.
            check("…and no clip window, which this panel does not unfold from",
                  m["clip"] == "none", str(m["clip"]))
        else:
            # ══ THE PANEL IS NODE 635:21410 · 23 September 2026 ══════════
            # A field, four named categories of chips, and a foot row. What
            # was asserted here until today was a flat 4x4 of `.qa-act` on the
            # phone sheet's wording — all of it correct, and all of it about a
            # panel the node replaced. Rewritten rather than patched: three of
            # these checks have no counterpart in the old set.
            panel = json.loads(c.eval(r"""JSON.stringify((() => {
              const cats = [...document.querySelectorAll('.qa-cat')];
              const chip = (c) => c.querySelector('.qa-chip');
              return {
                labels: [...document.querySelectorAll('.qa-chip__t')].map(t => t.textContent.trim()),
                cats: cats.map(c => [c.querySelector('.qa-cat__t').textContent.trim(),
                                     getComputedStyle(chip(c)).backgroundColor,
                                     getComputedStyle(chip(c)).color]),
                perCat: cats.map(c => c.querySelectorAll('.qa-chip').length),
                field: !!document.querySelector('.qa-search__in'),
                placeholder: (document.querySelector('.qa-search__in')||{}).placeholder,
                foot: [...document.querySelectorAll('.qa-foot__b')].map(b => b.textContent.trim()),
                footH: [...document.querySelectorAll('.qa-foot__b')].map(
                  b => Math.round(b.getBoundingClientRect().height)),
                /* every chip glyph is an EXPORT, so "does it exist" is a
                   loaded <img> and not a sprite lookup */
                hollow: [...document.querySelectorAll('.qa-chip')].filter(c => {
                  const i = c.querySelector('img');
                  return !(i && i.complete && i.naturalWidth > 0);
                }).map(c => c.textContent.trim()),
                /* a chip is as wide as its words; anything cropped is a
                   label the panel is not actually showing */
                cropped: [...document.querySelectorAll('.qa-chip__t')].filter(
                  t => t.scrollWidth - t.clientWidth > 1).map(t => t.textContent.trim()),
                chatOp: +getComputedStyle(document.querySelector('.qa-chat')).opacity,
              };
            })())"""))
            check("it opens the sixteen chips, and no modules",
                  m["open"] and len(panel["labels"]) == 16 and m["tiles"] == 0,
                  f"chips={len(panel['labels'])} tiles={m['tiles']}")
            check("…and they are the node's sixteen, in its order",
                  panel["labels"] == SHEET,
                  "" if panel["labels"] == SHEET else
                  f"{[x for x in panel['labels'] if x not in SHEET] or '—'} "
                  f"in place of {[x for x in SHEET if x not in panel['labels']] or '—'}")
            # FOUR GROUPS, FOUR APIECE, AND EACH ON ITS OWN TONE. The fills
            # are the node's literal values: this is the check that fails if
            # someone "tidies" four tints into one.
            got = [tuple(x) for x in panel["cats"]]
            check("…in the node's four categories, four chips each",
                  [g[0] for g in got] == [c[0] for c in CATS] and panel["perCat"] == [4, 4, 4, 4],
                  f"{[g[0] for g in got]} / {panel['perCat']}")
            check("…each group on its own fill and its own ink",
                  got == CATS,
                  "; ".join(f"{g[0]}: {g[1]} / {g[2]}" for g, w in zip(got, CATS) if g != w)
                  or "")
            check("every chip glyph is a file that actually loaded",
                  not panel["hollow"], ", ".join(panel["hollow"]))
            check("…and no label is cropped — a chip is as wide as its words",
                  not panel["cropped"], ", ".join(panel["cropped"]))
            # THE FIELD · 635:21411. Asserted as present and as EMPTY-LABELLED:
            # the node's placeholder is the only text in it.
            check("the panel carries the node's search field",
                  panel["field"] and panel["placeholder"] == "Search",
                  f"field={panel['field']} placeholder={panel['placeholder']!r}")
            # ── THE FOOT · the 23 Sep ruling, and the part no node draws ───
            # TWO, NOT THREE — Chat left the foot on 23 Sep ("Also Chat Remove
            # from Down hear"). It never belonged beside these: both of these
            # are ways of FINDING something, which is what the field above
            # them is for, and chat is a conversation — with a control of its
            # own already, the disc beside the pill.
            check("…and a foot row of the two places it can send you",
                  panel["foot"] == ["Search everything", "Scan a tag"],
                  str(panel["foot"]))
            check("…every one of them over the 44px touch floor",
                  panel["footH"] and min(panel["footH"]) >= 44, str(panel["footH"]))
            # AND THE DISC STANDS DOWN WHILE THE PANEL IS UP — screen
            # 632:19754 draws one control at the foot in this state. Checked
            # as opacity because taking it out of the layout would move the
            # pill; see the rule's own note.
            check("…while the chat disc outside stands down",
                  panel["chatOp"] == 0, f"disc opacity {panel['chatOp']}")
            # THE PANEL'S OWN MATERIAL · solid white at the node's 24 radius.
            # It was 94% over a blur(24) until today; the node fills it flat
            # and blurs the page instead, and the saturate went with it —
            # two blurs over one photograph took the chips' 4-8% tints
            # halfway to grey.
            check("solid white at the node's 24px radius, and no frosting",
                  m["material"] == "rgb(255, 255, 255)" and m["radius"] == "24px"
                  and not (m["panelBlur"] or "none").startswith("blur"),
                  f"{m['material']} r={m['radius']} {m['panelBlur']}")
            # AND IT STILL UNFOLDS — the entrance survived the redesign, and
            # this is the check that catches the clip being lost to a rule
            # written for the launcher.
            check("…and it unfolds through a clip window, which is its entrance",
                  "inset(" in str(m["clip"]), str(m["clip"]))
        # THE BACKDROP IS WHITE, AND THAT IS RULING FOUR on it in two days: the
        # profile menu's material, then a 6% dim, then black at 25% over 14px,
        # then "Instead of Background Should White Blured like Apple
        # background", with 4A chosen — white at 22% over a 16px blur — and
        # now, 10 Sep: "Background of main page should Black", and then — on
        # being shown 82% — "I told little black Blur". A LIGHT black tint:
        # 30% over the same 16px blur, saturation at 1.
        #
        # THE UPPER BOUND IS WHAT THIS CHECK IS FOR. 62% and then 82% were
        # both shipped past it by widening the range to match what had been
        # built, which is backwards: the bound is the ruling that has survived
        # all five revisions — the page stays legible behind the panel — and
        # 82% satisfied the word "black" while breaking it.
        #
        # THE UPPER BOUND IS STILL THE POINT, and it is the one thing every
        # version of this instruction has kept: a launcher is a thing you
        # reach for FROM a page, so the page has to stay discernible behind
        # it. The blur is asserted as PRESENT for that reason — going to flat
        # opaque black would pass an "is it black" check and lose the page.
        check("the backdrop is a black blur, and stops short of hiding the page",
              m["veilOpacity"] == "1"
              and m["veilColor"].startswith("rgba(0, 0, 0")
              and .2 <= m["veilAlpha"] <= .4
              and 10 <= m["veilPx"] <= 24,
              f"{m['veilColor']} blur={m['veilPx']}px")
        check("the panel is wholly on screen", m["onScreen"], f"{m['w']}x{m['h']}")
        # THE LABEL COMES BACK WHILE IT IS OPEN, scrolled or not: the control
        # that opened the panel must not change shape under the finger.
        # On V2 the word is "Close" while open (owner, 25 Sep 2026) — shorter,
        # so the pill does change width there; the label must still show.
        v2 = c.eval("document.documentElement.dataset.home === 'v2'")
        word = c.eval("document.querySelector('.qa-pill__t').textContent")
        check("…and the pill wears its label again while open",
              (m["labelW"] > 30 and word == "Close") if v2 else m["labelW"] > 60, f"{m['labelW']} {word!r}")
        check("Escape closes it", c.eval(
            "(()=>{document.dispatchEvent(new KeyboardEvent('keydown',{key:'Escape',bubbles:true}));"
            "return 1})()") == 1)
        time.sleep(0.5)
        check("…and the panel is hidden, not merely faded",
              c.eval("document.querySelector('.qa-menu').hidden") is True)

        # back at the top the label returns on its own
        c.eval("scrollTo(0, 0); 1")
        time.sleep(0.8)
        top = c.eval(PILL)
        check("back at the top the label returns",
              not top["scrolled"] and top["labelW"] > 60,
              f"scrolled={top['scrolled']} label={top['labelW']}px")
        errs = c.errors()
        check("no console errors through any of it", not errs,
              "; ".join(str(e)[:110] for e in errs[:3]))

    # ══ THE THREE LAUNCHER SECTIONS, AND WHEN THEY HAVE A SUBJECT ═════════
    # Everything from here to the verb branch below asserts `.qa-mod` — the
    # nineteen module tiles, their colours, and the one surface they arrive on.
    # None of it has a subject when the pill opens the verbs: the tiles are not
    # built, so the checks do not fail, they crash on the first
    # getBoundingClientRect of undefined. Which is what they did on 22 Sep.
    #
    # SKIPPED RATHER THAN DELETED, and skipped OUT LOUD. The launcher is one
    # word away in index.html and the day it comes back these are the checks
    # that were written against its frame; a silent skip is how a suite ends up
    # green over a component nobody is testing any more.
    if launcher_live:
        # ══ NINETEEN COLOURED TILES, WHICH IS THE OPPOSITE OF WHAT WAS HERE ═══
        # This section used to enforce the 8 September brief's colour rules — "DO
        # NOT give every action a different color", one neutral wash, monochrome
        # glyphs, no plates. The launcher is a different component answering a
        # different question, and the 9 September ruling is explicitly the other
        # way: every module wears its own fixed colour. So the checks are inverted
        # rather than deleted, and what they now guard is the part that is easy to
        # get wrong — flat instead of a ramp, no shadow, one rhythm, and an ink
        # that suits the colour it sits on.
        print("\nthe nineteen module tiles")
        with Chrome(width=WIDTH, height=900) as c:
            c.goto(BASE + "index.html?v=2", settle=2.0)
            c.eval("document.querySelector('.qa-pill').click(); 1")
            time.sleep(0.9)
            g = json.loads(c.eval(TILES))
            # WHAT THIS WIDTH IS OWED, derived the way the stylesheet derives it —
            # AND THE DERIVATION INVERTED ON 15 SEP. Node 370:4029 states a 696
            # panel on its 744 artboard (the screen less 24 either side) with
            # `flex: 1` tiles, where every version before it stated a 150 tile and
            # sized the panel from it. So above the breakpoint the panel is the
            # number and three columns divide what is left of it: 205 at 744 and
            # at every width above, because the panel stops growing at 696.
            #
            # BELOW IT THE OLD DERIVATION STILL HOLDS, because two columns have no
            # stated measure in the file — 150 is still the floor a label needs,
            # and the clamp takes over on a narrow phone: 150 at 430, 139 at 390,
            # 124 at 360. The 577/578 boundary is unchanged by all of this, which
            # looks like luck and is not: 3x150 + 2x16 + 2x24 = 530 plus 48 of
            # screen margin is the same 578 the old 546-plus-32 arrived at.
            #
            # AND ONE COLUMN UNDER 378, added 15 Sep with the node's tile. That
            # tile spends 70px before the label starts, so two of them stop
            # holding the longest unbreakable word — `Administer`, 73px — below
            # that width. The tile's own padding moves with the band and is
            # asserted alongside, because it is what buys the word its room: 10
            # either side where two columns are tight, the node's 16 where they
            # are not.
            want_cols = 3 if WIDTH >= 578 else (2 if WIDTH >= 378 else 1)
            want_panel = min({3: 696, 2: 2 * 150 + 16 + 48}.get(want_cols, 10 ** 6),
                             WIDTH - 48)
            want_tile = (want_panel - 48 - (want_cols - 1) * 16) // want_cols
            want_pad = "16px 10px" if want_cols == 2 else "16px"
            want_justify = "flex-start" if want_cols == 1 else "center"
            check("all nineteen are there, and every one is drawn",
                  g["n"] == 19 and g["visible"] == 19, f"{g['n']} tiles, {g['visible']} drawn")
            check("…carrying the modules' own names",
                  g["names"][0] == "Medical" and "Commu\u00adnication" in g["names"],
                  f"{g['names'][0]} … {g['names'][-1]!r}")
            # ONE GROUND ON ALL NINETEEN · node 371:5441, ruled 15 Sep 2026. This
            # replaces a count of SIXTEEN distinct colours, and the replacement is
            # the substance of the change rather than a loosened check: the fill
            # went tile → chip on 10 Sep to settle a contrast debt, and the node
            # empties the chip as well. The nineteen are now told apart by glyph
            # and name alone. Asserted as a count so that one tile getting its
            # `--qa-mod-c` back fails here instead of being absorbed.
            check("every tile wears one ground, the node's 20% black",
                  g["grounds"] == ["rgba(0, 0, 0, 0.2)"], str(g["grounds"]))
            check("…flat, with no ramp on any of them",
                  g["withGradient"] == 0, f"{g['withGradient']} with a gradient")
            check("…and not one chip is filled any more",
                  g["chipsFilled"] == 0, f"{g['chipsFilled']} still filled")
            # AND IT IS GLASS. The 20% veil is only the node's material with the
            # blur behind it — without it the tile is a flat grey rectangle that
            # measures identically and looks nothing like the file, which is the
            # failure a colour check cannot see.
            # AND NO BLUR OF ITS OWN, though 371:5441 declares blur(8px). Asserted
            # ABSENT, which is the opposite of what this checked yesterday: a
            # nested backdrop-filter does not sample its parent's background. The
            # panel's own filter makes a backdrop root, so the tile sampled the
            # page behind the whole panel and laid its 20% black over THAT —
            # coming out 11 levels LIGHTER than the panel where the artboard is 19
            # levels darker. Putting the declared value back is the obvious fix
            # and it is the bug.
            check("…and no blur of its own, which rendered the tile inverted",
                  g["tileBlur"] == ["none"], str(g["tileBlur"]))
            # THE GROUND IS DARKER THAN THE PANEL, MEASURED OFF THE RENDER. The
            # style-level checks above all passed while the tiles were invisible —
            # `rgba(0, 0, 0, 0.2)` was correctly set and composited onto the wrong
            # backdrop. Only the rendered pixels see it, so the separation the
            # artboard draws is asserted as a number: the tile sits at least 12
            # levels below the panel beside it (artboard 19, ours 27; the artboard
            # reads lighter because its blur bleeds the surround inward).
            # Skipped at one column, where there is no gutter between two tiles to
            # sample — the gap below a tile is a row's worth of panel and picks up
            # a different part of the page, which would compare two grounds rather
            # than a tile against its own surround. The separation is a property of
            # the material, so any multi-column width proves it.
            if want_cols > 1:
                sep = _sample_tile_separation(c)
                check("…and reads darker than the panel it sits on, as the artboard does",
                      sep is not None and sep >= 12,
                      f"tile is {sep} levels below the panel" if sep is not None
                      else "could not sample")
            # THE SHADOW GOES AND A HAIRLINE RETURNS, the exact reverse of 10 Sep
            # ("Apple Cards Radius, Shadow"). A drop shadow under a translucent
            # pane reads as dirt on the panel behind it; the node draws a 0.5px
            # border instead, transparent at rest.
            check("no tile casts a shadow, and every one carries the hairline",
                  g["withShadow"] == 0 and g["withBorder"] == 19,
                  f"{g['withShadow']}/19 shadowed, {g['withBorder']}/19 bordered")
            # THE CHIP SURVIVES AS A BOX. 371:5442 keeps the 32/r9 container and
            # drops only its fill, so the 20px glyph still sits at a fixed size
            # whatever the label does. Asserted because deleting the empty box is
            # the obvious tidy-up and it would let the glyph move.
            check("…the chip still a 32px box at a squircle's radius, just unfilled",
                  g["chipW"] == 32 and g["chipH"] == 32 and g["chipR"] == 9,
                  f"{g['chipW']}x{g['chipH']} r{g['chipR']}")
            # AND THE PAIR IS CENTRED, not run out from the left edge. This is the
            # one layout property that changed with the material and the only one
            # a screenshot diff would catch late.
            check(f"…with the chip and label {want_justify}, 6 apart, on {want_pad} of pad",
                  g["justify"] == [want_justify] and g["tileGap"] == ["6px"]
                  and g["tilePad"] == [want_pad],
                  f"{g['justify']} gap {g['tileGap']} pad {g['tilePad']}"
                  f" (wanted {want_justify} on {want_pad} at {WIDTH})")
            # ONE RHYTHM, every number a multiple of 4: 150x70 tiles, a 16px
            # gutter on both axes, 32px of panel padding, and the panel 24px clear
            # of the row rather than the verb panel's 8.
            check(f"{want_tile}x72 tiles at radius 16, on a 16px gutter both ways",
                  # `gapX` is tile[1].left - tile[0].right, which is only a
                  # horizontal gutter when there IS a second column — at one it
                  # measures the wrap back to the next row and reads -264.
                  g["tileW"] == want_tile and g["tileH"] == 72 and g["radius"] == 16
                  and (want_cols == 1 or g["gapX"] == 16) and g["gapY"] == 16,
                  f"{g['tileW']}x{g['tileH']} r{g['radius']} gap {g['gapX']}/{g['gapY']}"
                  f" (wanted {want_tile} wide at {WIDTH})")
            # THREE, NOT FOUR · ruled 10 Sep 2026, "Quick access module has come
            # in 3 coloums". The panel is sized FROM the column count — 3x150 +
            # 2x16 + 2x32 = 546 — so this asserts the pair together: a panel that
            # kept its 712 while the grid went to three would stretch the tiles.
            #
            # AND TWO BELOW 578, which is that same 546 plus the 16px screen
            # margins the panel is clamped to. This pair used to be asserted as
            # the constants 3 and 546 at EVERY width, which read as a verifier
            # that hardcoded the desktop — and the note it was carried under said
            # so, that the panel "correctly reflows to one column on a phone".
            # IT DID NOT REFLOW AT ALL: it held three columns and squeezed the
            # tiles to 87, and eighteen of the nineteen labels were truncated
            # behind `overflow: hidden`. The checks were right to fail and the
            # diagnosis was what was wrong, so what they assert now is the
            # derivation rather than either constant — sized from the column
            # count in force, at whichever width is being run.
            check(f"…in {'three' if want_cols == 3 else 'two'} columns on a "
                  f"{want_panel}px panel with 24px padding",
                  g["cols"] == want_cols and g["panelW"] == want_panel
                  and g["panelPad"] == "24px",
                  f"{g['cols']} cols, {g['panelW']}px, pad {g['panelPad']}"
                  f" (wanted {want_cols} at {want_panel} for {WIDTH})")
            check("…standing 24 clear of the pill row, not 8",
                  near(g["clearOfRow"], 24, 1), f"{g['clearOfRow']}px")
            # AND ALL NINETEEN ARE REACHABLE, which two columns made a question.
            # At three the field is seven rows and fits a phone outright; at two it
            # is ten and 944px of content sits in a 728px panel. That is fine —
            # the panel has been a scroll container the whole time — but "fine"
            # here means the LAST tile can actually be brought into it, and that
            # the page behind does not take the scroll instead, which is the way
            # this fails in practice. Checked as the rendered box of the last
            # tile, not as `scrollTop` agreeing with itself.
            reach = json.loads(c.eval("""(()=>{const b=e=>e.getBoundingClientRect();
              const m=document.querySelector('.qa-menu');
              const t=[...document.querySelectorAll('.qa-mod')], last=t[t.length-1];
              const y0=scrollY; m.scrollTop=m.scrollHeight;
              return JSON.stringify({inside: b(last).top>=b(m).top-1 && b(last).bottom<=b(m).bottom+1,
                pageMoved: Math.round(scrollY-y0), room: m.scrollHeight-m.clientHeight})})()"""))
            check("…and every one of the nineteen can be reached in the panel",
                  reach["inside"] and reach["pageMoved"] == 0,
                  f"last tile inside={reach['inside']}, page moved {reach['pageMoved']}px, "
                  f"{reach['room']}px of scroll")
            c.eval("document.querySelector('.qa-menu').scrollTop = 0; 1")
            # ONE INK ON ALL NINETEEN, STILL — but it is dark now, not white.
            # "text All has to be white" was ruled against COLOURED tiles on
            # 10 Sep; the cards went white later the same day, which reverses the
            # ink rather than the principle. What the principle actually says is
            # that there is no per-tile ink decision, and that is what is checked:
            # ONE value across all nineteen, whatever it is, and no returning
            # `--dark` class.
            check("one ink across all nineteen, and it is white on the glass",
                  len(g["inks"]) == 1 and g["inks"][0] == "rgb(255, 255, 255)"
                  and g["darkClass"] == 0,
                  f"{g['inks']} (+{g['darkClass']} --dark)")
            # AND THE NODE'S OWN WEIGHT · 371:5444 is Inter Medium 14 at +0.1,
            # the project's `Antz_Body_Medium`. "Module Name make it Bold" was
            # ruled on 10 Sep for near-black ink carrying a white card's
            # hierarchy; on the glass the label is the only ink on the tile.
            check("…at the node's Medium 14, not the white card's bold 13.5",
                  g["weights"] == ["500"] and g["sizes"] == ["14px"],
                  f"{g['weights']} at {g['sizes']}")
            # ── THE CONTRAST DEBT IS BACK, AND IT IS MEASURED OFF THE SCREEN ───
            # This check was a real AA floor for five days and is a recorded
            # exception again. It has to be said plainly: the 10 Sep white card
            # measured 10.68:1 worst case, and node 371:5441 trades that away for
            # its material. Worst case is 2.41 at 744, 2.56 at 1024, 2.63 at 390
            # and 2.67 at 360; best is around 6:1. Most tiles are under AA and a
            # few under the 3:1 non-text floor.
            #
            # THESE NUMBERS ROSE ONCE THE TILE COMPOSITED CORRECTLY. They read
            # 2.05 / 2.12 / 2.15 / 2.18 while the tile's own `backdrop-filter` was
            # sampling the page instead of the panel — the black was landing on a
            # bright ground, so the tile came out lighter than its surround AND
            # the label lost most of its contrast. Removing that blur was a
            # fidelity fix; the contrast was the second thing it bought.
            #
            # AND IT CANNOT BE READ OFF STYLE ANY MORE. The tile is 20% black over
            # a 40% white panel over a 30% black veil over whatever the page draws
            # behind it, so `backgroundColor` returns `rgba(0, 0, 0, 0.2)` and a
            # luminance read of it — which ignores alpha — reports 21:1 for a tile
            # that actually measures 2.06. That is a check passing while the
            # screen is wrong, so the measurement moved to the rendered pixels:
            # sample the tile's ground between the label's right edge and the
            # tile's, clear of the chip, the ink and the corners.
            #
            # ASSERTED AS A FLOOR, NOT A TARGET, so the exception is bounded. If a
            # later change pushes any tile below what the node itself produces,
            # this fails — and the way back is a darker tile or a lower panel
            # alpha, both of which leave the file. The spread is the PAGE, not the
            # tiles: they are one ground, and the light bottom-left corner of the
            # page is why Communication reads worst.
            ink = _sample_ink_contrast(c, g["inkBoxes"])
            if ink is None:
                check("…the label's measured contrast, sampled off the render",
                      False, "could not sample — PIL missing or screenshot failed")
            else:
                worst, best, under_aa, under_3, worst_name, sampled = ink
                # 2.2, AND THE HEADROOM IS DELIBERATE. The measure is
                # deterministic — repeated runs at one width agree to two decimals
                # — but it lands differently at each width because the spread is
                # the PAGE showing through: 2.41 at 744, 2.56 at 1024, 2.63 at 390,
                # 2.67 at 360. A floor pinned to the tightest of those would fail
                # on an anti-aliasing change rather than on a real one, which is
                # the failure mode that makes a suite get ignored. It was 1.9 while
                # the tile composited over the page; raised with the fix, so the
                # inverted state cannot come back and still pass.
                check("…the label's contrast measured off the render, and bounded",
                      worst >= 2.2,
                      f"worst {worst_name} {worst:.2f}:1, best {best:.2f}:1 — "
                      f"{under_aa}/{sampled} under AA, {under_3}/{sampled} under 3:1 "
                      f"(of {sampled} tiles in the panel; recorded exception: "
                      f"node 371:5441's material, 15 Sep)")
            # AND THE TEXT-SHADOW STAYS RETIRED. It was load-bearing at .35 on the
            # coloured tiles — the only thing separating white ink from
            # administer, lab and parivesh. Putting it back is the obvious reflex
            # now that the ink is white again on a mid ground, and it is the wrong
            # one: the node draws no shadow, and a smear under 14px Medium is what
            # made the old tiles look cheap. If the contrast is ever called, the
            # answer is the material, not a shadow over it.
            check("…with the text-shadow retired, not left smearing the ink",
                  g["withShadowInk"] == 0, f"{g['withShadowInk']}/19 still shadowed")
            check("every glyph is the module's own file, loaded",
                  g["glyphsLoaded"] == 19, f"{g['glyphsLoaded']}/19")
            check("no label runs out of its tile", g["labelOverflow"] == 0,
                  str(g["labelOverflow"]))
            # AND NONE IS CLIPPED INSIDE ITS OWN BOX — the half the line above
            # cannot see. Kept as a separate check rather than folded in, because
            # the two fail for opposite reasons: the box overflows when the label
            # CANNOT shrink, and the text overflows when it shrinks too far.
            check("…and no word is cut off inside it",
                  not g["labelClipped"],
                  "none" if not g["labelClipped"] else
                  ", ".join(f"{n} by {px}px" for n, px in g["labelClipped"]))
            # AND NO WORD IS SPLIT DOWN THE MIDDLE, which is the one that holds.
            # The two above can both be green while the panel reads "Medica/l" —
            # `break-word` guarantees it by making the text fit whatever the box.
            # This asserts the box is wide enough that the backstop never fires.
            check("…and no word has to break in the middle of itself",
                  not g["wordBreaks"],
                  "none" if not g["wordBreaks"] else
                  ", ".join(f"{n} needs {need} has {has}"
                            for n, need, has in g["wordBreaks"]))
            errs = c.errors()
            check("no console errors", not errs, "; ".join(str(e)[:110] for e in errs[:3]))

        # ══ THE OPENING · THE TILES FLY OUT OF THE PILL ════════════════════════
        # The verb panel unfolded: one surface whose clip-path started as the
        # pill's measured box and opened outward, staggered by ROW. The launcher
        # does the opposite — the surface just fades, and the nineteen tiles each
        # travel from the pill to their own slot. So this measures DISTANCE FROM
        # THE PILL per tile per frame, not a window.
        #
        # FROZEN AND SEEKED, never slept through — and the freeze awaits the
        # animations rather than guessing when they exist; see freeze_at().
        print("\nthe launcher opens as one surface")
        with Chrome(width=WIDTH, height=900, reduced_motion=False) as c:
            c.goto(BASE + "index.html?v=2", settle=2.0)
            # THE BUDGET IS THE RULING · 220ms, replacing a 560ms flight with
            # 342ms of stagger behind it. Asserted off the token because that is
            # what both the open and the close transitions read, and because the
            # point of the ruling was the total time.
            tok = c.eval("(()=>{const c=getComputedStyle(document.documentElement);"
                         "return [c.getPropertyValue('--qa-mod-open').trim(),"
                         "c.getPropertyValue('--qa-mod-close').trim()].join(' ')})()")
            check("it opens in 220ms and closes in 180, not the fan's 900",
                  tok == "220ms 180ms", tok)

            c.eval("document.querySelector('.qa-pill').click(); 1")
            time.sleep(0.8)
            c.eval("document.querySelector('.qa-pill').click(); 1")
            time.sleep(0.6)
            c.eval("document.querySelector('.qa-pill').click(); 1")
            freeze_at(c, "is-open")

            def at(t):
                c.eval("(()=>{for(const a of document.getAnimations()){a.pause();"
                       "try{a.currentTime=%d}catch(e){}} return 1})()" % t)
                return json.loads(c.eval(SURFACE))

            f0 = at(0)
            # FRAME ZERO · the panel is small and invisible, and it is small FROM
            # THE PILL. .96 rather than the fan's .3: enough to read as arriving,
            # not enough to look like a modal zoom.
            check("frame 0: the panel is at 96% and invisible",
                  f0["panelOpacity"] == 0 and 0.95 <= f0["panelScale"] <= 0.97,
                  f"opacity {f0['panelOpacity']}, scale {f0['panelScale']}")
            # …AND GROWING FROM THE PILL. The origin point resolved into viewport
            # coordinates has to sit on the pill's centre horizontally; vertically
            # it sits at the panel's bottom edge, which is 24px above the pill's
            # own centre plus half the row — so the Y is checked as "below the
            # panel and above the pill", not as zero.
            check("…and it grows out of the pill, not out of its own middle",
                  abs(f0["originDX"]) <= 2 and -60 <= f0["originDY"] <= 0,
                  f"origin is {f0['originDX']}px, {f0['originDY']}px from the pill centre")
            check("…with no clip window, which this panel does not unfold from",
                  f0["clip"] == "none", f0["clip"])
            # THE WHOLE POINT OF THE RULING · not one tile is animating, in the
            # first frame or any other. This is the check that fails if the fan
            # comes back in any form: a keyframe, a transition, or a stray
            # --qa-dx left on a tile by a returning measureFan().
            check("no tile animates at all — the surface is the only thing moving",
                  f0["tileAnims"] == 0 and f0["strayVectors"] == 0,
                  f"{f0['tileAnims']} tile animations, {f0['strayVectors']} stray vectors")
            check("…so all nineteen are full size and full opacity in frame 0",
                  min(f0["tileOps"]) == 1 and set(f0["tileScales"]) == {1},
                  f"opacity min {min(f0['tileOps'])}, scales {sorted(set(f0['tileScales']))}")
            check("…with the pill's glyph still the grid",
                  f0["grid"] == 1 and f0["x"] == 0, f"grid={f0['grid']} x={f0['x']}")

            # MID-WAY · one movement, part-way through, on both properties at once.
            f = at(110)
            check("mid-open: the panel is part-way up and part-way out",
                  0 < f["panelOpacity"] < 1 and 0.96 < f["panelScale"] < 1,
                  f"opacity {f['panelOpacity']}, scale {f['panelScale']}")
            check("…and the tiles are still not moving",
                  f["tileAnims"] == 0 and min(f["tileOps"]) == 1,
                  f"{f['tileAnims']} tile animations, opacity min {min(f['tileOps'])}")

            # AND IT LANDS · full size, fully there, and the pill has become the ×.
            f = at(400)
            check("it lands: the panel at full size and fully there",
                  f["panelOpacity"] == 1 and f["panelScale"] == 1,
                  f"opacity {f['panelOpacity']}, scale {f['panelScale']}")
            check("…and the pill's glyph is the ×", f["grid"] == 0 and f["x"] == 1,
                  f"grid={f['grid']} x={f['x']}")

        # ══ THE CLOSING · THE SURFACE GOES BACK INTO THE PILL ══════════════════
        print("\nthe launcher closes the same way")
        with Chrome(width=WIDTH, height=900, reduced_motion=False) as c:
            c.goto(BASE + "index.html?v=2", settle=2.0)
            c.eval("document.querySelector('.qa-pill').click(); 1")
            time.sleep(0.8)
            c.eval("document.querySelector('.qa-pill').click(); 1")
            # `is-closing` goes on synchronously, before `is-open` comes off
            freeze_at(c, "is-closing")

            def at2(t):
                c.eval("(()=>{for(const a of document.getAnimations()){a.pause();"
                       "try{a.currentTime=%d}catch(e){}} return 1})()" % t)
                return json.loads(c.eval(SURFACE))

            f = at2(0)
            check("frame 0 of the close: the panel is still full size and there",
                  f["panelOpacity"] == 1 and f["panelScale"] == 1,
                  f"opacity {f['panelOpacity']}, scale {f['panelScale']}")
            # IT REVERSES RATHER THAN CUTTING. The fan's close had a reverse
            # distance order to prove; this one has only to shrink back toward the
            # same origin, so what is asserted is that both properties are moving
            # DOWN together and the tiles are still inert.
            f = at2(90)
            check("…it contracts back toward the pill, fading as it goes",
                  0 < f["panelOpacity"] < 1 and 0.96 <= f["panelScale"] < 1,
                  f"opacity {f['panelOpacity']}, scale {f['panelScale']}")
            check("…and no tile is animating on the way out either",
                  f["tileAnims"] == 0 and min(f["tileOps"]) == 1,
                  f"{f['tileAnims']} tile animations, opacity min {min(f['tileOps'])}")
            f = at2(400)
            check("it ends on the pill: the surface gone, back at 96%",
                  f["panelOpacity"] == 0 and 0.95 <= f["panelScale"] <= 0.97,
                  f"opacity {f['panelOpacity']}, scale {f['panelScale']}")
    else:
        print("\nthe launcher's three sections — no subject on this setting")
        print("  the pill opens the sixteen verbs, so `.qa-mod` is not built.")
        print("  Flip QA_CONTENT back to 'modules' and they run again.")

        # ══ THE PANEL UNFOLDS OUT OF THE PILL · the 8 September brief ═════════
        # "The FAB transforms INTO the Quick Actions module." The panel is laid
        # out at full size and REVEALED by a clip window that starts as the
        # pill's own measured box, so nothing scales and nothing reflows — and
        # the window's width and centre are the only proof of that. A panel
        # that merely faded in would pass every geometry check in this file.
        #
        # FROZEN AND SEEKED, never slept through.
        print("\nthe sixteen verbs unfold out of the pill")
        with Chrome(width=WIDTH, height=900, reduced_motion=False) as c:
            c.goto(BASE + "index.html?v=2", settle=2.0)
            c.eval("document.querySelector('.qa-pill').click(); 1")
            freeze_at(c, "is-open")

            def at(t):
                c.eval("(()=>{for(const a of document.getAnimations()){a.pause();"
                       "try{a.currentTime=%d}catch(e){}} return 1})()" % t)
                return json.loads(c.eval(STATE))

            f0 = at(0)
            # FRAME ZERO IS THE PILL, to the pixel and in the right place. The
            # width alone would pass on a window centred on the panel, which is
            # the bug this replaced: the surface came out of the middle of the
            # page rather than out of the control that was pressed.
            check("frame 0: the clip window is the pill's own box",
                  f0["winW"] is not None and near(f0["winW"], f0["pillW"], 2),
                  f"window {f0['winW']}px against a {f0['pillW']}px pill")
            check("…and centred on the pill, not on the panel",
                  f0["winCx"] is not None and near(f0["winCx"], f0["pillCx"], 2),
                  f"window centre {f0['winCx']} against the pill's {f0['pillCx']}"
                  f" (the panel's is {f0['menuCx']})")
            # THE STAGGER RUNS AWAY FROM THE FINGER. Read off the resolved
            # delays rather than off opacity: while opening AND while closing
            # the row nearest the pill is the more opaque one, so opacity
            # cannot tell the two directions apart. The delays can.
            check("…and the rows are delayed from the bottom up",
                  f0["delayBottom"] is not None and f0["delayTop"] is not None
                  and f0["delayBottom"] < f0["delayTop"],
                  f"bottom {f0['delayBottom']}ms, top {f0['delayTop']}ms")
            # EVERY CELL IN A ROW MOVES AS ONE. The brief rules out staggering
            # individual cards, and the row index is MEASURED off each cell's
            # top edge — so a column count the media queries moved under it
            # shows up here as a row that is not one opacity.
            # HALF OF --qa-t-surface, WHICH IS 200ms. Seeked at 200 the window
            # has already landed and `progress` reads 1, which is a pass on the
            # end state wearing a mid-flight check's name — it is the surface's
            # whole duration, not a point inside it.
            mid = at(100)
            check("mid-flight: the window has opened and no row has split",
                  0 < (mid["progress"] or 0) < 1 and mid["rowSpread"] <= 0.001,
                  f"progress {mid['progress']}, widest spread within a row"
                  f" {mid['rowSpread']}")
            end = at(900)
            check("it ends fully unfolded, every row opaque",
                  end["progress"] == 1 and min(end["rows"].values()) == 1,
                  f"progress {end['progress']}, dimmest row"
                  f" {min(end['rows'].values())}")
            # AND THE MARK HAS MORPHED — one 20px box holding the grid and a
            # CSS ×, rotating through each other rather than being swapped.
            check("…with the pill's mark now the ×, not the grid",
                  end["grid"] == 0 and end["x"] == 1,
                  f"grid {end['grid']}, × {end['x']}")

        print("\nand it folds back the same way, in reverse")
        with Chrome(width=WIDTH, height=900, reduced_motion=False) as c:
            c.goto(BASE + "index.html?v=2", settle=2.0)
            c.eval("document.querySelector('.qa-pill').click(); 1")
            time.sleep(0.9)
            c.eval("document.querySelector('.qa-pill').click(); 1")
            freeze_at(c, "is-closing")
            s = json.loads(c.eval(STATE))
            # THE CLOSE IS THE OPEN REVERSED, which is a claim about WHICH ROW
            # WAITS: the head goes first and the row over the pill is the last
            # thing on screen. `--qa-row-r` is set at the same time as
            # `--qa-row` for exactly this, and nothing else reads it.
            check("closing: the delays have flipped — the top row leads",
                  s["delayTop"] is not None and s["delayBottom"] is not None
                  and s["delayTop"] < s["delayBottom"],
                  f"top {s['delayTop']}ms, bottom {s['delayBottom']}ms")
            errs = c.errors()
            check("no console errors through the unfold or the fold",
                  not errs, "; ".join(str(e)[:110] for e in errs[:3]))

        # ══ V2 ONLY · WHAT YOU HAVE NOT FINISHED, AND WHERE A NEW ONE GOES ══
        # Ruled 23 Sep 2026 in two moves. The first built a BINDING ROW — a
        # persistent "On Site › Section › Enclosure" that scoped actions used
        # silently — and it was rejected on sight: "this part won't work."
        # What replaced it is idea 4 of the same conversation: the panel opens
        # on the work already in flight, and a new one asks where it goes.
        #
        # "Leave the Changes in V1 & V3" is the second half, and it is the one
        # that rots silently — a version-scoped feature leaks the day someone
        # lifts a rule out of `.qa--ctx`, and nothing about V2 looks wrong when
        # it does. So the last block opens V1, V3 and V4 and asserts ABSENCE.
        print("\nV2 opens on what you have not finished")
        with Chrome(width=WIDTH, height=900) as c:
            c.goto(BASE + "index.html?v=2", settle=2.0)
            c.eval("localStorage.removeItem('antz.qa.scope'); 1")
            c.goto(BASE + "index.html?v=2", settle=2.0)
            c.eval("window.__a=[];const o=console.info;"
                   "console.info=(...x)=>{window.__a.push(x.join(' '));o(...x)}; 1")
            c.eval("document.querySelector('.qa-pill').click(); 1")
            time.sleep(0.6)
            q = lambda js: json.loads(c.eval("JSON.stringify(" + js + ")"))

            band = q("({on:!document.querySelector('.qa-cont').hidden,"
                     " n:document.querySelector('.qa-cont__n').textContent,"
                     " rows:[...document.querySelectorAll('.qa-item')].map(r=>r.dataset.kind),"
                     " h:Math.round(document.querySelector('.qa-cont__list').getBoundingClientRect().height),"
                     " scrollH:document.querySelector('.qa-cont__list').scrollHeight,"
                     " fade:getComputedStyle(document.querySelector('.qa-cont'),'::after').backgroundImage,"
                     " more:!!document.querySelector('.qa-cont__more'),"
                     " bind:!!document.querySelector('.qa-bind')})")
            # TWO REJECTED THINGS, ASSERTED BY NAME so that bringing either
            # back is a decision somebody has to make twice: the binding row
            # ("this part won't work") and the disclosure button that the
            # scrolling container replaced.
            check("neither the binding row nor the Show-more button is there",
                  not band["bind"] and not band["more"], str(band)[:120])
            # ALL FIVE ARE IN THE DOM, THREE ARE IN THE BOX. The container is
            # what limits it now, so the assertion is geometric: the list is
            # shorter than its own contents, which is the only thing that
            # proves it scrolls rather than merely fits.
            check("it opens on all the unfinished work, in a three-row box",
                  band["on"] and band["n"] == "5" and len(band["rows"]) == 5
                  and band["scrollH"] > band["h"] + 10, str(band)[:150])
            # 56 AND 6 SINCE THE SPACING PASS OF 23 SEP — the row height and
            # the gap are tokens on `.qa-cont`, and this is the arithmetic
            # they feed. It is written out rather than read back off the
            # element, so a token changing by accident fails here.
            check("…and the box is exactly three rows tall",
                  band["h"] == 3 * 56 + 2 * 6, f"{band['h']}px, want {3*56+2*6}")
            # …AND IT SAYS SO BEFORE ANYBODY SCROLLS. A cut list with no edge
            # is a list people believe has three things in it.
            # THE GRADIENT, NOT THE PSEUDO-ELEMENT'S `content`. An empty
            # string is what `content: ''` computes to, so asserting that only
            # proved the ::after existed — it would have passed over a fade
            # with no gradient left in it.
            check("…with a fade under the cut, so the overflow is visible",
                  "linear-gradient" in str(band["fade"]), str(band["fade"])[:60])
            check("…drafts first, then unsent, then what someone else holds",
                  band["rows"] == ["draft", "draft", "unsent", "awaiting", "awaiting"],
                  str(band["rows"]))
            check("the foot is the two places it can send you — Chat is gone",
                  q("[...document.querySelectorAll('.qa-foot__b')].map(b=>b.textContent.trim())")
                  == ["Search everything", "Scan a tag"], "")

            # ══ THE FIELD IS A SEARCH, NOT A FILTER ═════════════════════════
            # "if i search it has to act like global Search was working same
            # Way. First Show Quick Actions, then module name, other results."
            # The order is the ruling and the index is Global Search's own, so
            # what is checked here is the ORDER and the REACH — that a query
            # gets past the sixteen chips into animals and enclosures at all.
            def groups():
                return q("[...document.querySelectorAll('.qa-hits')].map(g=>"
                         "g.querySelector('.qa-hits__t').firstChild.textContent.trim())")
            c.eval("""(()=>{const i=document.querySelector('.qa-search__in');i.focus();
              i.value='medic';i.dispatchEvent(new Event('input',{bubbles:true}));return 1})()""")
            time.sleep(0.4)
            g = groups()
            check("a query puts Quick Actions first, then the module",
                  g[:2] == ["Quick Actions", "Modules"], str(g))
            check("…and the panel's own lists step aside while it searches",
                  q("({grid:document.querySelector('.qa-menu__grid').hidden,"
                    " band:document.querySelector('.qa-cont').hidden,"
                    " res:!document.querySelector('.qa-res').hidden})")
                  == {"grid": True, "band": True, "res": True}, "")
            c.eval("""(()=>{const i=document.querySelector('.qa-search__in');
              i.value='leo';i.dispatchEvent(new Event('input',{bubbles:true}));return 1})()""")
            time.sleep(0.4)
            g = groups()
            # THE REACH IS THE POINT. "leo" matches no chip and no module, and
            # the old filter would have shown an empty panel; the index finds
            # the animals, the species, the enclosures they live in and the
            # identifiers on them.
            check("…and a query no chip matches still finds animals and enclosures",
                  "Animals" in g and "Enclosures" in g and "Quick Actions" not in g,
                  str(g))
            # A CAPPED GROUP SAYS WHAT IT IS HIDING. Three rows with 44 beside
            # the heading is an honest cap; three rows alone is a lie.
            check("…each capped group carrying its real total",
                  q("!!document.querySelector('.qa-hits__t span')"), "")

            # ══ THE SPACING PASS OF 23 SEP · "Need propre Space, & some
            # Breathing Space Need" ═════════════════════════════════════════
            # EVERY ROW THE SAME HEIGHT, whether it carries a subtitle or not.
            # They were 44 and 46 — a two-pixel disagreement nobody can name
            # and everybody reads as a list that is not quite straight. The
            # 56 is arithmetic (20 + 2 + 16 content, 9 either side), so this
            # fails if a line-height is ever left to inherit.
            sp = q("({rows:[...new Set([...document.querySelectorAll('.qa-hit')]"
                   "  .map(x=>Math.round(x.getBoundingClientRect().height)))],"
                   " gap:getComputedStyle(document.querySelector('.qa-hits')).gap,"
                   " groupGap:getComputedStyle(document.querySelector('.qa-res')).gap,"
                   " headPad:getComputedStyle(document.querySelector('.qa-hits__t')).paddingLeft,"
                   " rowPad:getComputedStyle(document.querySelector('.qa-hit')).paddingLeft})")
            check("every result row is one height, subtitle or no subtitle",
                  sp["rows"] == [56], str(sp["rows"]))
            check("…on one 4px scale: 6 between rows, 22 between groups",
                  sp["gap"] == "6px" and sp["groupGap"] == "22px", str(sp)[:100])
            # AND THE HEADING SHARES THE ROW'S LEFT EDGE rather than sitting
            # against the panel wall while its own rows are indented away.
            check("…with the headings on the rows' own left edge",
                  sp["headPad"] == sp["rowPad"], f"heading {sp['headPad']} vs row {sp['rowPad']}")

            # ── THE PANEL KEEPS ITS SHAPE; THE LIST MOVES ──────────────────
            # Thirteen results used to grow the panel until its top edge was
            # 8px off the top of the screen and the whole surface scrolled —
            # field included, away from the answers it was producing.
            # THE SCROLLER IS `.qa-body` SINCE 23 SEP, not the results and not
            # the panel. A real iPad's keyboard is what found the difference:
            # with the panel scrolling, 524px of room put the foot 247px below
            # its own bottom edge and took the field with it on the first
            # scroll. The field and the foot are frame; only the middle moves.
            shape = q("(()=>{const m=document.querySelector('.qa-menu'),"
                      "  r=m.getBoundingClientRect(), b=document.querySelector('.qa-body');"
                      "  return {panelScrolls:m.scrollHeight>m.clientHeight+1,"
                      "    bodyScrolls:b.scrollHeight>b.clientHeight+1,"
                      "    clearsTop:Math.round(r.top)>40,"
                      "    field:document.querySelector('.qa-search').getBoundingClientRect().top>=r.top-1,"
                      "    foot:document.querySelector('.qa-foot').getBoundingClientRect().bottom<=r.bottom+1}})()")
            # ── THE FRAME DOES NOT GIVE · 23 Sep ──────────────────────────
            # The panel is a flex column with a max-height, and a flex child's
            # default is `flex-shrink: 1` — so when the contents wanted more
            # room than the panel had, the browser took it out of the FIELD.
            # Measured at 28px against the node's 52 while a search was
            # running, and at 51.16 even at rest: it had been shrinking from
            # the day the panel became a column, one sub-pixel at a time,
            # until the body grew enough to make it obvious.
            #
            # CHECKED AS AN EXACT 52, not a floor. A floor passes at 51.16,
            # which is precisely the value that hid this for a fortnight.
            frame = q("({field:+document.querySelector('.qa-search')"
                      "   .getBoundingClientRect().height.toFixed(2),"
                      " shrink:getComputedStyle(document.querySelector('.qa-search')).flexShrink,"
                      " footShrink:getComputedStyle(document.querySelector('.qa-foot')).flexShrink})")
            check("the field holds the node's 52 while the body fights for room",
                  frame["field"] == 52 and frame["shrink"] == "0" and frame["footShrink"] == "0",
                  str(frame))
            check("the body scrolls inside the panel, not the panel itself",
                  not shape["panelScrolls"] and shape["bodyScrolls"], str(shape))
            check("…so the field and the foot stay put, and the panel clears the screen edge",
                  shape["field"] and shape["foot"] and shape["clearsTop"], str(shape))

            # ══ THE KEYBOARD TRAVELS IT ═════════════════════════════════════
            # And the caret never leaves the field — the check is that the
            # highlight moved AND `document.activeElement` is still the input,
            # which is what stops the next letter typed going nowhere.
            def key(k, vk):
                for t in ("keyDown", "keyUp"):
                    c.cmd("Input.dispatchKeyEvent", type=t, key=k, code=k,
                          windowsVirtualKeyCode=vk, nativeVirtualKeyCode=vk)
                time.sleep(0.15)
            key("ArrowDown", 40); key("ArrowDown", 40)
            nav = q("({row:(document.querySelector('.qa-hit.is-active b')||{}).textContent,"
                    " caret:document.activeElement.className,"
                    " aria:document.querySelector('.qa-search__in').getAttribute('aria-activedescendant')})")
            # ══ THE SOFTWARE KEYBOARD · found on a real iPad, 23 Sep ════════
            # The panel is anchored above the pill at the foot of the page,
            # and iPadOS raises its keyboard OVER the bottom of the screen
            # without resizing the layout viewport — so every `bottom:` in the
            # stylesheet went on describing a screen whose lower half was
            # covered, and the panel sat under the keys with one and a half
            # rows showing. Nothing in CSS can see this; `visualViewport` is
            # the only thing that knows.
            #
            # SIMULATED BY OVERRIDING `visualViewport.height`, which is what
            # the handler reads. Emulating a real keyboard is not available
            # here, and the arithmetic is the part that was wrong.
            KB = 620
            c.eval("""(()=>{const vv=window.visualViewport;
              Object.defineProperty(vv,'height',{get:()=>innerHeight-%d,configurable:true});
              Object.defineProperty(vv,'offsetTop',{get:()=>0,configurable:true});
              vv.dispatchEvent(new Event('resize')); return 1})()""" % KB)
            time.sleep(0.45)
            kb = q("(()=>{const qa=document.querySelector('.qa'),"
                   "  m=document.querySelector('.qa-menu'), r=m.getBoundingClientRect();"
                   "  return {isKb:qa.classList.contains('is-kb'),"
                   "    kbVar:getComputedStyle(qa).getPropertyValue('--qa-kb').trim(),"
                   "    top:Math.round(r.top), bottom:Math.round(r.bottom),"
                   "    keysTop:innerHeight-%d,"
                   "    rowOp:+getComputedStyle(document.querySelector('.qa-row')).opacity,"
                   "    field:Math.round(document.querySelector('.qa-search').getBoundingClientRect().bottom),"
                   "    foot:Math.round(document.querySelector('.qa-foot').getBoundingClientRect().bottom)}})()" % KB)
            check("with the keyboard up the panel sits above the keys",
                  kb["isKb"] and kb["bottom"] <= kb["keysTop"], str(kb)[:150])
            check("…and its whole box is still on screen",
                  kb["top"] >= 0 and kb["kbVar"] == f"{KB}px", str(kb)[:130])
            # THE FIELD AND THE FOOT ARE INSIDE THE PANEL, which is the check
            # that would have caught the original bug: they were both below
            # its bottom edge, scrolled away with the rest of the surface.
            check("…with the field and the foot still inside it",
                  kb["field"] < kb["bottom"] and kb["foot"] <= kb["bottom"],
                  f"field {kb['field']}, foot {kb['foot']}, panel bottom {kb['bottom']}")
            # AND THE PILL STANDS DOWN — it is behind the keys and cannot be
            # pressed; leaving it rendered makes it flash back for a frame
            # every time the keyboard animates.
            # …AND THE FIELD STILL DOES NOT SHRINK, which is where the squeeze
            # was worst: the keyboard halves the panel, so the frame is under
            # the most pressure exactly when you are typing into it.
            check("…with the field still at its full 52 under the keyboard",
                  q("+document.querySelector('.qa-search').getBoundingClientRect()"
                    ".height.toFixed(2)") == 52, "")
            check("…and the pill row stands down behind the keys",
                  kb["rowOp"] == 0, str(kb["rowOp"]))
            c.eval("""(()=>{const vv=window.visualViewport;
              Object.defineProperty(vv,'height',{get:()=>innerHeight,configurable:true});
              vv.dispatchEvent(new Event('resize')); return 1})()""")
            time.sleep(0.45)
            back = q("({isKb:document.querySelector('.qa').classList.contains('is-kb'),"
                     " rowOp:+getComputedStyle(document.querySelector('.qa-row')).opacity})")
            check("…and it all comes back when the keyboard goes down",
                  not back["isKb"] and back["rowOp"] == 1, str(back))

            check("the down arrow moves a highlight, not the caret",
                  nav["row"] and nav["caret"] == "qa-search__in" and nav["aria"],
                  str(nav))
            check("no console errors through any of it",
                  not c.errors(), "; ".join(str(e)[:110] for e in c.errors()[:3]))

        print("\nV2 asks where a new one goes")
        with Chrome(width=WIDTH, height=900) as c:
            c.goto(BASE + "index.html?v=2", settle=2.0)
            c.eval("localStorage.removeItem('antz.qa.scope'); 1")
            c.goto(BASE + "index.html?v=2", settle=2.0)
            c.eval("window.__a=[];const o=console.info;"
                   "console.info=(...x)=>{window.__a.push(x.join(' '));o(...x)}; 1")
            q = lambda js: json.loads(c.eval("JSON.stringify(" + js + ")"))
            c.eval("document.querySelector('.qa-pill').click(); 1"); time.sleep(0.6)

            # A DRAFT RESUMES; ONE A PERSON IS HOLDING ONLY OPENS.
            c.eval("""document.querySelector('.qa-item[data-kind="draft"]').click(); 1""")
            time.sleep(0.5)
            c.eval("document.querySelector('.qa-pill').click(); 1"); time.sleep(0.5)
            c.eval("""document.querySelector('.qa-item[data-kind="awaiting"]').click(); 1""")
            time.sleep(0.5)
            said = q("window.__a")
            check("a draft resumes and one held by a person only opens",
                  len(said) == 2 and said[0].startswith("[antz] resume:")
                  and said[1].startswith("[antz] view:"), str(said)[:140])

            c.eval("document.querySelector('.qa-pill').click(); 1"); time.sleep(0.5)
            c.eval("""document.querySelector('.qa-chip[data-action="dispense"]').click(); 1""")
            time.sleep(0.4)
            st = q("({t:document.querySelector('.qa-stage__t').textContent,"
                   " path:document.querySelector('.qa-stage__path').textContent,"
                   " first:(document.querySelector('.qa-pick b')||{}).textContent,"
                   " head:[getComputedStyle(document.querySelector('.qa-search')).display,"
                   "       getComputedStyle(document.querySelector('.qa-cont')).display,"
                   "       getComputedStyle(document.querySelector('.qa-menu__grid')).display]})")
            check("a scoped action asks, in place, starting at the Site",
                  st["t"] == "Dispense Medicine" and "enclosure" in st["path"]
                  and st["first"] == "Bannerghatta Safari", str(st)[:150])
            # `[hidden]` LOSES TO ANY AUTHOR `display`, and this file has been
            # caught by that three times.
            check("…with the field and the band standing down, not merely marked",
                  st["head"] == ["none", "none", "none"], str(st["head"]))

            for _ in range(3):
                if c.eval("!document.querySelector('.qa-stage').hidden"):
                    c.eval("document.querySelectorAll('.qa-pick')[0].click(); 1")
                    time.sleep(0.3)
            filed = q("window.__a").pop()
            check("…and it files against the place it just showed you",
                  "· on Bannerghatta Safari › Carnivore Safari › CAR-01" in filed, filed[:120])

            # THE SECOND ONE IS ONE TAP, AND STILL SHOWS ITS WORKING. This is
            # what the rejected binding row was for, done without asserting a
            # place: the upper levels arrive as crumbs you are looking at.
            c.eval("document.querySelector('.qa-pill').click(); 1"); time.sleep(0.5)
            c.eval("""document.querySelector('.qa-chip[data-action="dispense"]').click(); 1""")
            time.sleep(0.4)
            again = q("({crumbs:[...document.querySelectorAll('.qa-crumb')].map(x=>x.textContent),"
                      " first:(document.querySelector('.qa-pick b')||{}).textContent,"
                      " marked:!!document.querySelector('.qa-pick--last'),"
                      " sub:(document.querySelector('.qa-pick--last span')||{}).textContent})")
            check("the second one opens on the leaf, the path already walked",
                  again["crumbs"] == ["Bannerghatta Safari", "Carnivore Safari"]
                  and again["first"] == "CAR-01", str(again)[:150])
            check("…with the one you used last on top, and saying so",
                  again["marked"] and again["sub"].startswith("Last used"), str(again["sub"]))
            still = q("!document.querySelector('.qa-stage').hidden")
            check("…but the leaf is never chosen for you",
                  still, "" if still else "the picker closed itself — something was picked")
            check("no console errors through any of it",
                  not c.errors(), "; ".join(str(e)[:110] for e in c.errors()[:3]))

        # V4 CARRIES THE CONTEXTUAL PANEL TOO since 24 Sep 2026 (owner: "implement
        # the Quick Access features we did for v2 here also"), so it moved out of
        # the absence loop below and into this presence check.
        print("\n…and V4 carries the same contextual panel")
        with Chrome(width=WIDTH, height=900) as c:
            c.goto(BASE + "index.html?v=4", settle=2.0)
            c.eval("document.querySelector('.qa-pill').click(); 1")
            time.sleep(0.6)
            c.eval("""(()=>{const i=document.querySelector('.qa-search__in');
              i.value='leo';i.dispatchEvent(new Event('input',{bubbles:true}));return 1})()""")
            time.sleep(0.3)
            v4 = json.loads(c.eval("""JSON.stringify({
              ctx: document.querySelector('.qa').classList.contains('qa--ctx'),
              band: !!document.querySelector('.qa-cont'),
              res: !!document.querySelector('.qa-res'),
              chips: document.querySelectorAll('.qa-chip').length})"""))
            check("V4: the Continue band, and a field that searches everything",
                  v4["ctx"] and v4["band"] and v4["res"] and v4["chips"] == 16, str(v4))
            check("…V4: no console errors", not c.errors(),
                  "; ".join(str(e)[:110] for e in c.errors()[:3]))

        print("\n…and V1 and V3 are left exactly as they were")
        for ver, url in (("V1", "index.html"), ("V3", "index.html?v=3")):
            with Chrome(width=WIDTH, height=900) as c:
                c.goto(BASE + url, settle=2.0)
                c.eval("document.querySelector('.qa-pill').click(); 1")
                time.sleep(0.6)
                d = json.loads(c.eval("""JSON.stringify({
                  ctx: document.querySelector('.qa').classList.contains('qa--ctx'),
                  band: !!document.querySelector('.qa-cont'),
                  bind: !!document.querySelector('.qa-bind'),
                  res: !!document.querySelector('.qa-res'),
                  stage: !!document.querySelector('.qa-stage'),
                  chips: document.querySelectorAll('.qa-chip').length})"""))
                # AND THE FIELD STILL FILTERS CHIPS HERE, which is the half of
                # "leave the changes in V1 & V3" that an absence check cannot
                # see: the results list is V2's, so on every other version the
                # field must go on doing exactly what it did yesterday.
                c.eval("""(()=>{const i=document.querySelector('.qa-search__in');
                  i.value='egg';i.dispatchEvent(new Event('input',{bubbles:true}));return 1})()""")
                time.sleep(0.3)
                filt = json.loads(c.eval("""JSON.stringify({
                  shown:[...document.querySelectorAll('.qa-chip')].filter(x=>!x.hidden)
                          .map(x=>x.textContent.trim()),
                  cats:[...document.querySelectorAll('.qa-cat')].filter(x=>!x.hidden).length})"""))
                check(f"…{ver}: the field still narrows the sixteen, as it did",
                      filt["shown"] == ["Add Eggs"] and filt["cats"] == 1, str(filt))
                c.eval("""(()=>{const i=document.querySelector('.qa-search__in');
                  i.value='';i.dispatchEvent(new Event('input',{bubbles:true}));return 1})()""")
                time.sleep(0.25)
                # …and a chip that WOULD ask a question on V2 must still fire
                # straight out here. This is what catches `contextual` being
                # defaulted to true rather than read from isV2().
                c.eval("""document.querySelector('.qa-chip[data-action="dispense"]').click(); 1""")
                time.sleep(0.4)
                shut = c.eval("!document.querySelector('.qa').classList.contains('is-open')")
                check(f"{ver}: the same sixteen, and none of V2's additions",
                      d["chips"] == 16 and not d["ctx"] and not d["band"]
                      and not d["bind"] and not d["res"] and not d["stage"], str(d))
                check(f"…{ver}: a chip still fires straight out, asking nothing",
                      shut, f"panel still open={not shut}")

    # ══ NO PLANTING ON V2 ══════════════════════════════════════════════════
    # The artboard planting belonged to the retired V2 home. V2 now carries
    # V4's plain header — no foliage, no wave — so that is what is asserted.
    print("\nno planting on V2 (V4's plain header)")
    with Chrome(width=WIDTH, height=900) as c:
        c.goto(BASE + "index.html?v=2", settle=2.0)
        pl = c.eval("(()=>{const f=document.querySelector('.foliage');return !f||getComputedStyle(f).display==='none'||f.getBoundingClientRect().height===0})()")
        check("the planting is not drawn", pl, "")


    # ══ THE NUMBERS, AND WHAT A FINGER CAN ACTUALLY HIT ═══════════════════
    print("\nthe figures and the touch targets")
    with Chrome(width=WIDTH, height=900) as c:
        c.goto(BASE + "index.html?v=2", settle=2.0)
        # TABULAR FIGURES ON THE VALUES · 10 Sep 2026. Inter's default figures
        # are proportional, so a value re-rendering 02 → 12 changes width and a
        # stacked day column does not align on its tens digit. Checked on the
        # RESOLVED property of real elements rather than on the rule, since a
        # later `font-variant-numeric` or a `font` shorthand further down would
        # silently reset it — a `font` shorthand resets it to `normal`.
        fig = json.loads(c.eval("""(()=>{
          const want=['.figure__value','.l-headline__value','.l-headline__tile-value',
                      '.l-stat__value','.site-stat__value','.site-fig__value',
                      '.l-focus__day','.l-focus__ref','time'];
          const bad=[], seen=[];
          for(const sel of want){
            for(const e of document.querySelectorAll(sel)){
              const v=getComputedStyle(e).fontVariantNumeric;
              seen.push(sel);
              if(!/tabular-nums/.test(v)) bad.push(sel+':'+v);
            }}
          // and the note copy must NOT have it - proportional belongs in prose
          const prose=document.querySelector('.l-note__body,.l-note__text,p');
          return JSON.stringify({checked:[...new Set(seen)].length, bad:[...new Set(bad)],
            n:seen.length,
            prose:prose?getComputedStyle(prose).fontVariantNumeric:'(none found)'})})()"""))
        check("every data figure is set in tabular numerals",
              not fig["bad"] and fig["n"] > 0,
              f"{fig['n']} figures across {fig['checked']} families"
              if not fig["bad"] else f"proportional: {fig['bad']}")
        # AND SCOPED · tabular figures are wider and colder, and a date inside
        # a sentence should keep the sentence's rhythm. If this ever reads
        # tabular, someone has put the property on `body`.
        check("…and the prose is left proportional", fig["prose"] != "tabular-nums",
              str(fig["prose"]))

        # THE TOUCH TARGETS, HIT-TESTED RATHER THAN MEASURED — and the probe
        # itself is the thing that has to be right here. Three ways it lied
        # before this form:
        #
        #   1. THE BOX IS NOT THE TARGET. `::after { inset: -3px }` gives the
        #      38px header controls a real 44; reading getBoundingClientRect()
        #      reports 38 and calls it a failure.
        #   2. `elementFromPoint` ONLY SEES THE VIEWPORT. The pager dots sit
        #      far below the fold, so every probe returned null, no growth was
        #      found, and 6x6 was reported for a control that is 12x32. The
        #      element has to be scrolled into view first.
        #   3. A HIDDEN CONTROL IS NOT A TARGET. "Edit Modules" is
        #      `visibility: hidden; pointer-events: none` in the resting state
        #      — it belongs to editing mode — so asserting a floor on it fails
        #      on a control no finger can reach anyway.
        #
        # So: skip what is not interactive, scroll what is, and refuse to
        # report a number at all if the centre itself is not hittable.
        hit = json.loads(c.eval("""(()=>{
          const out={};
          const probe=(sel,name)=>{
            const e=document.querySelector(sel); if(!e){out[name]='absent'; return}
            const cs=getComputedStyle(e);
            if(cs.visibility==='hidden'||cs.display==='none'||cs.pointerEvents==='none'){
              out[name]='inert'; return}
            e.scrollIntoView({block:'center'});
            const r=e.getBoundingClientRect();
            if(r.top<0||r.bottom>innerHeight){out[name]='offscreen'; return}
            const hits=(x,y)=>{let n=document.elementFromPoint(x,y);
              while(n){ if(n===e) return true; n=n.parentElement } return false};
            if(!hits(r.left+r.width/2, r.top+r.height/2)){out[name]='covered'; return}
            let L=0,R=0,T=0,B=0;
            while(L<24 && hits(r.left-L-1, r.top+r.height/2)) L++;
            while(R<24 && hits(r.right+R, r.top+r.height/2)) R++;
            while(T<24 && hits(r.left+r.width/2, r.top-T-1)) T++;
            while(B<24 && hits(r.left+r.width/2, r.bottom+B)) B++;
            out[name]=[Math.round(r.width)+L+R, Math.round(r.height)+T+B];
          };
          probe('.icon-btn--bell','bell'); probe('.avatar-btn','avatar');
          probe('.search-btn','scan');
          probe('.dots__dot:nth-child(2)','pagerDot');
          return JSON.stringify(out)})()"""))
        # 44 IS THE FLOOR THE BRIEF SET. The bell and the avatar are drawn at
        # 38 and reach it through the `::after`; the scan button is 64 outright.
        big = {k: hit[k] for k in ("bell", "avatar", "scan") if isinstance(hit.get(k), list)}
        short = {k: v for k, v in big.items() if min(v) < 44}
        check("bell, avatar and scan all clear the 44px floor",
              len(big) == 3 and not short,
              ", ".join(f"{k} {v[0]}x{v[1]}" for k, v in big.items())
              if not short else f"under 44: {short} (of {hit})")
        # THE PAGER DOTS CANNOT REACH IT, AND THE NUMBER IS THE POINT. They sit
        # on a 12px pitch — 6 drawn, 6 gap — so a target wider than 12 steals
        # its neighbour's press; vertically it takes all the card has. 6x6 to
        # 12x32 is ten times the area and still under the floor. Asserted as a
        # floor so the gain cannot be lost, and left short rather than papered
        # over: closing it needs the dots' gap or the card's padding to grow,
        # which is a visible change and wants ruling.
        d = hit.get("pagerDot")
        # the pager belonged to the Key Insights card of the retired V2 home;
        # when no pager is drawn there is nothing to measure (24 Sep 2026)
        check("…and the pager dots take all the room the layout allows",
              d == "absent" or (isinstance(d, list) and d[0] == 12 and d[1] >= 30),
              f"{d[0]}x{d[1]} on a 12px pitch, from 6x6"
              if isinstance(d, list) else f"probe said: {d}")
        check("no console errors", not c.errors(), str(c.errors()))

    print()
    if fails:
        print(f"{len(fails)} FAILED: " + ", ".join(fails))
        sys.exit(1)
    print("ALL PASS")


main()
