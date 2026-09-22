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
    cells:m.querySelectorAll('.qa-act').length,
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
  for(const cell of document.querySelectorAll('.qa-act')){
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
    delayBottom:dly('0'), delayTop:dly(String(Object.keys(rows).length-1)),
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
    print(f"V2 — node 280:3521, {WIDTH}px")

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

    # ── and V2 is the other page ──────────────────────────────────────────
    print("\nV2 is the other page")
    with Chrome(width=WIDTH, height=1200) as c:
        c.goto(BASE + "index.html?v=2", settle=2.2)
        o = c.eval(PROBE)
        check("`?v=2` is stamped on <html> ", o["stamp"] == "2", str(o["stamp"]))
        # HIDDEN IS NOT ABSENT, and both halves matter: the CSS drops them before
        # they paint and the bootstrap never builds them
        check("the deck is gone, and was never mounted",
              o["deckShown"] is False and o["deckMounted"] == 0,
              f"shown={o['deckShown']} slides={o['deckMounted']}")
        check("the observation rail is gone, and was never mounted",
              o["railShown"] is False and o["railMounted"] == 0,
              f"shown={o['railShown']} cards={o['railMounted']}")
        check("the gradient band moved onto the module grid",
              "gradient" in o["band"]["img"] and "255, 255, 255" in o["band"]["img"],
              o["band"]["img"][:56])
        check("…keeping its 32px bottom corners",
              o["band"]["radius"] == "0px 0px 32px 32px", o["band"]["radius"])

        # THE SECTION HEAD IS GONE AT REST — the ruling of 8 Sep 2026. The row's
        # only resting content was an Edit Modules button, which is the profile
        # menu's own first item.
        check("no section head at rest",
              o["head"]["h"] == 0 and o["head"]["vis"] == "hidden",
              f"{o['head']['h']}px, visibility {o['head']['vis']}")
        check("…and its control is out of the tab order, not merely clipped",
              not o["head"]["focusable"],
              "the Edit Modules button still takes focus" if o["head"]["focusable"] else "")

        print("\nthe seventeen cards it seeds")
        check("seventeen cards", o["n"] == 17, str(o["n"]))
        check("and they are the node's, in V2_LAYOUT's order", o["ids"] == WANT,
              "as drawn" if o["ids"] == WANT
              else f"unexpected {[i for i in o['ids'] if i not in WANT]}, "
                   f"missing {[i for i in WANT if i not in o['ids']]}")
        check("both new cards are drawn", o["three"] == 2, str(o["three"]))
        # THE RULING, ASSERTED FROM THE OTHER END. `ids` above would catch the
        # card coming back, but only as one line of a fifteen-way diff; this
        # says what it is.
        check("the ink Focus Hub is not seeded", o["fills"]["hub"] is None,
              "the dark blue card is back on the page" if o["fills"]["hub"] else "")
        # THE ALIGNMENT RULING, 8 Sep 2026: V2 is four columns, not five, so the
        # frame's rows can be reproduced instead of approximated. This is the
        # check that would catch the page silently going back to five — the
        # order above would still pass, drawn into ragged rows.
        # …AND ONLY ABOVE 700, WHICH IS WHERE THE STYLESHEET GIVES V2 FOUR.
        # Below that the page is two columns on purpose — four at 660 is a
        # 140px card carrying a 32px glyph and a wrapping name, and a phone is
        # not the frame this ruling is about. These two ran unconditionally
        # and so reported a failure at any phone width for a page that was
        # drawing exactly what it is supposed to draw.
        if WIDTH >= 700:
            check("the grid is the frame's four columns", o["gridCols"] == 4, str(o["gridCols"]))
            check("…and the rows are the frame's, card for card",
                  o["rows"] == WANT_ROWS,
                  "as drawn" if o["rows"] == WANT_ROWS else str(o["rows"]))
        else:
            check("below 700 the grid is two columns, as the stylesheet says",
                  o["gridCols"] == 2, str(o["gridCols"]))
        check("seeded at `tall`, which is 2x2 at four and five columns",
              {o["sizes"]["lite"], o["sizes"]["note"]} == {"tall"}, str(o["sizes"]))

        print("\nMy Focus Hub")
        check("the plate card is white", o["fills"]["lite"] == "plate", str(o["fills"]))
        check("the plate photograph is 92", near(o["litePhoto"]["w"], 92) or WIDTH < 768,
              str(o["litePhoto"]))
        check("three updates on it", o["liteUpdates"] == 3, str(o["liteUpdates"]))
        check("its badges sit in the flow, not on the photograph",
              o["liteBadgesInFlow"], f"inFlow={o['liteBadgesInFlow']}")
        check("it draws no enclosure line", o["liteRefs"] == 1, str(o["liteRefs"]))
        # It pages since 8 Sep 2026 — the node draws the indicator on the ink
        # card only, and a card that advances on its own has to say where you
        # are in it, so the plate card gained one it does not draw.
        check("it pages, and says so", o["liteDots"] == 3, str(o["liteDots"]))

        # ── and the ink variation, IF anything has put it on the page ───────
        # Not seeded since the ruling of 8 Sep; still in the catalogue, so a
        # saved layout or an Add Module can bring it back, and when it does
        # these are the numbers it has to hold. Skipped rather than failed —
        # a check that fails for the absence of what it measures teaches
        # nobody anything.
        if o["fills"]["hub"] == "ink":
            check("the ink card is #1F415B", o["fills"]["hub"] == "ink", str(o["fills"]))
            check("the ink photograph is 72", near(o["hubPhoto"]["w"], 72) or WIDTH < 768,
                  str(o["hubPhoto"]))
            check("three updates on it", o["hubUpdates"] == 3, str(o["hubUpdates"]))
            check("its badges sit ON the photograph", o["hubBadgesOnPhoto"],
                  f"onPhoto={o['hubBadgesOnPhoto']}")
            check("it carries the enclosure line", o["hubRefs"] == 2, str(o["hubRefs"]))
            check("it pages, and says so", o["hubDots"] == 3, str(o["hubDots"]))
            check("the hub carries animals AND enclosures",
                  o["kinds"]["latin"] == 2 and o["kinds"]["sub"] == 1,
                  f"{o['kinds']['latin']} binomials, {o['kinds']['sub']} plain subtitles")
        else:
            print("  ----  the ink card is off the page; its own geometry not checked")

        print("\nNotes")
        check("the thumbnail is 44", near(o["noteThumb"]["w"], 44) or WIDTH < 768, str(o["noteThumb"]))
        check("the priority pill is solid #FA6140", o["pri"] == "rgb(250, 97, 64)", str(o["pri"]))
        check("…and the plate is the same colour at 10%",
              o["tint"] == "rgba(250, 97, 64, 0.1)", str(o["tint"]))
        # four lines on a card at its designed width, two on a phone's single
        # column — the narrow case is a declared truncation, see the container
        # query in the stylesheet
        want_clamp = 4 if o["noteThumb"]["w"] >= 44 else 2
        check(f"the note clamps to {want_clamp} lines", o["noteClamp"] == want_clamp,
              str(o["noteClamp"]))
        check("…and its box is exactly the clamp, not a squeezed one",
              near(o["noteTextH"], o["noteClamp"] * 20, 1.5),
              f"{o['noteTextH']}px for {o['noteClamp']} lines of 20 "
              f"(content is {o['noteTextSH']}px)")
        check("five notes, and its indicator draws the running pill",
              o["noteRun"] and o["noteDots"] == 5, f"run={o['noteRun']} dots={o['noteDots']}")

        # ══ KEY INSIGHTS ═══════════════════════════════════════════════════
        # The card node 280:3521 put on this page, and the first card in the
        # product whose fill belongs to no module.
        print("\nKey Insights")
        k = o["ki"]
        check("the card is on the page", k is not None,
              "" if k else "insights.key did not render")
        if k:
            check("at `medium`, which is the frame's 2x1", k["size"] == "medium",
                  str(k["size"]))
            check("…and 2 cells wide, not 1 or 3",
                  near(k["w"], 2 * (k["h"] * 1.125) + 16, 3) or WIDTH < 700,
                  f"{k['w']}x{k['h']}")
            check("it wears its own ramp, not a module's",
                  k["fill"] == "solid" and "gradient" in k["ramp"], str(k["ramp"]))
            check("the frame's bulb is exported, not drawn", k["glyph"], "")
            check("the head reads Key Insights", k["title"] == "Key Insights", k["title"])
            # THE FIGURE AND ITS COLOUR TOGETHER. A figure in the wrong colour
            # is the failure this card is most likely to have, because three
            # near-identical pale tones sit next to each other in the palette.
            check("32 Birth Animals, in MD3_Antz/notes",
                  k["value"] == "32" and k["label"] == "Birth Animals"
                  and k["valueColor"] == "rgb(252, 244, 174)",
                  f"{k['value']} / {k['label']} / {k['valueColor']}")
            check("two tiles, and they carry the frame's two counts",
                  k["n"] == 2
                  and [t["label"] for t in k["tiles"]] == ["Death", "Transfers"]
                  and [t["value"] for t in k["tiles"]] == ["02", "12"],
                  str(k["tiles"]))
            # …AND IN TWO DIFFERENT LIBRARY COLOURS. Collapsing these onto one
            # semantic tone is the tempting simplification and it is the wrong
            # one: see the palette block.
            check("…in ErrorContainer and SecondaryContainer, not one tone",
                  [t["color"] for t in k["tiles"]]
                  == ["rgb(255, 211, 211)", "rgb(175, 239, 235)"],
                  str([t["color"] for t in k["tiles"]]))
            check("the tiles are 5% black under a blur, not plates",
                  k["tileBg"] == "rgba(0, 0, 0, 0.05)" and "blur(2px)" in (k["tileBlur"] or ""),
                  f"{k['tileBg']} / {k['tileBlur']}")
            # THE FRAME'S ASYMMETRY, WHICH IS EASY TO TIDY AWAY BY ACCIDENT:
            # the tiles reach 8 from the card edge where the head starts at 16.
            check("…and they reach half the padding from the edge, where the head reaches a whole one",
                  near(k["tileRight"] * 2, k["headLeft"], 1.5),
                  f"tiles {k['tileRight']} / head {k['headLeft']}")

        print("\npaging")
        for k, want_pages in (("lite", 3), ("note", 5)):
            g = o["pager"][k]
            check(f"{k}: {want_pages} pages, {want_pages} dots, all of them buttons",
                  g["pages"] == want_pages and g["dots"] == want_pages
                  and g["buttons"] == want_pages,
                  f"{g['pages']} pages / {g['dots']} dots / {g['buttons']} buttons")
            # A PASSIVE CARD IS NOT A CONTROL. If this ever regresses to a
            # <button>, the dots inside it become a control in a control —
            # which is the thing ModuleCard.js's standing rule forbids.
            check(f"{k}: the card is a group, not a button",
                  g["role"] == "group" and not g["clickable"],
                  f"{g['tag']} role={g['role']}")
            check(f"{k}: it has a dwell to advance on", g["dwell"])
            check(f"{k}: it rests on the first item", g["at"] == 0, str(g["at"]))
            check(f"{k}: one tab stop, not {want_pages}", g["tabbable"] == 1, str(g["tabbable"]))
            check(f"{k}: nothing off-screen is reachable", g["inertOff"])

        print("\nnothing is lost at this width")
        # THE ONE THAT MATTERS. Ellipsis is these cards' own behaviour on a long
        # binomial; a card whose content is taller than its box loses the bottom
        # of the updates list with nothing on screen to say so.
        check("no card clips its own content", not o["clipped"], str(o["clipped"]))
        check("nothing is drawn at zero size", not o["zero"], str(o["zero"]))
        check("every photograph and thumbnail loaded", o["imgs"])
        check("no horizontal overflow", o["hOverflow"] == 0, str(o["hOverflow"]))

        # AND EDIT MODE STILL HAS ITS CHROME. The collapse is scoped to the
        # resting state for one reason: the head carries Add Module and Done in
        # edit mode, and that Done is the only way out of it on the page itself.
        print("\nedit mode still has its head")
        c.eval("document.body.dispatchEvent(new KeyboardEvent('keydown',{key:'e',bubbles:true}))")
        time.sleep(0.7)
        ed = c.eval(EDIT_HEAD)
        # 44 IS THE TABLET AND DESKTOP HEIGHT, NOT THE PHONE'S. Below 768 the
        # row wraps — the title on one line, Add Module and Done full-width on
        # the next, 101px — which is the phone breakpoint's own design and is
        # what V1 does there too. So what is asserted is what the collapse must
        # not break: the head comes back, it is visible, and both controls can
        # be reached. The exact height is pinned only where one rule owns it.
        want_h = 44 if WIDTH >= 768 else None
        check("the head comes back, and the bar carries Add Module and Done",
              ed["vis"] == "visible" and ed["h"] > 0 and ed["done"] and ed["add"]
              and (want_h is None or near(ed["h"], want_h)), str(ed))
        # …AND THE OTHER TWO ARE OFF THE BAR · "Edit time Quick & Chat wont
        # there". `display: none` and not merely hidden, because the row is
        # centred on itself: a pill that keeps its box would push Add Module
        # and Done off centre by half of what is no longer there.
        # THE CAPSULE · ruled 10 Sep 2026 from the App Store's floating app
        # bar: "Same Way i want Add module With Tick icon". ONE container
        # holding the label and a filled round action, not two pills side by
        # side — which is what it was, and which read as two unrelated
        # buttons. So the shape is what is asserted: the slot is a real box
        # with the row's radius, Add Module has given up its own shadow to
        # it, and Done is a filled 40px circle carrying the tick.
        cap = json.loads(c.eval("""(()=>{
          const cap=document.querySelector('.qa-edit');
          const add=cap.querySelector('.add-module-btn');
          const done=cap.querySelector('.link-btn--done');
          const cs=getComputedStyle(cap), ds=getComputedStyle(done);
          const dr=done.getBoundingClientRect();
          const tick=done.querySelector('svg');
          return JSON.stringify({display:cs.display, radius:cs.borderRadius,
            merged:getComputedStyle(add).boxShadow==='none',
            doneW:Math.round(dr.width), doneH:Math.round(dr.height),
            fill:ds.backgroundColor, round:ds.borderRadius,
            tick:!!tick, wordHidden:getComputedStyle(done.querySelector('span')).display==='none',
            name:done.getAttribute('aria-label')})})()"""))
        # `flex`, NOT THE `inline-flex` THE RULE ASKS FOR, and that is correct:
        # the capsule is itself a flex item of `.qa-row`, and a flex item's
        # display is blockified — inline-flex computes to flex. What matters
        # is that it is a BOX at all, where the resting state is `contents`.
        check("the editing bar is one capsule, not two pills",
              cap["display"] in ("flex", "inline-flex") and cap["radius"] == "999px"
              and cap["merged"],
              f"{cap['display']} r={cap['radius']} addMerged={cap['merged']}")
        # 40 INSIDE THE 52, which is the reference's proportion and the
        # reason the capsule's right padding is 6.
        check("…with Done a filled round tick, and still named",
              cap["doneW"] == 40 and cap["doneH"] == 40 and cap["tick"]
              and cap["wordHidden"] and cap["name"] == "Done"
              and cap["round"] == "999px" and cap["fill"] != "rgba(0, 0, 0, 0)",
              f"{cap['doneW']}x{cap['doneH']} {cap['fill']} tick={cap['tick']} "
              f"name={cap['name']!r}")
        check("…while Quick Actions and Chat have left it",
              ed["pill"] == "none" and ed["chat"] == "none",
              f"pill {ed['pill']}, chat {ed['chat']}")
        c.eval("document.querySelector('.qa-row .link-btn--done').click()")
        time.sleep(0.7)
        out = c.eval(HEAD_AWAY)
        check("…and Done puts it away again", not out["editing"] and out["h"] == 0, str(out))

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
        check("pressing Version 2 lands on V2, at ?v=2",
              w["v"] == "2" and w["search"] == "?v=2", f"{w['v']} {w['search']}")
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
              w["v"] == "2" and w["search"] == "?v=2"
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
          const shown=[...document.querySelectorAll('.qa-row button')]
            .filter(b=>getComputedStyle(b).display!=='none')
            .map(b=>b.textContent.trim()||b.getAttribute('aria-label')||'?');
          const a=document.querySelector('.qa-edit > .link-btn:not(.link-btn--done)');
          return JSON.stringify({shown, anchorPresent:!!a,
            anchorHidden:a?getComputedStyle(a).display==='none':null})})()"""))
        check("…and the resting bar is the pill and the disc, nothing more",
              bar["shown"] == ["Quick Actions", "Chat"], str(bar["shown"]))
        check("…with the mode's swap anchor kept, and kept hidden",
              bar["anchorPresent"] and bar["anchorHidden"],
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

        # the menu: nineteen modules on a white material, page softened
        c.eval("document.querySelector('.qa-pill').click(); 1")
        time.sleep(0.6)
        m = c.eval(MENU)
        # NINETEEN MODULES, NOT SIXTEEN VERBS · the 9 Sep ruling, built from
        # mockups/module-launcher.html variant 4A. `QA_CONTENT` in index.html
        # selects which, and 'modules' is the shipped setting — the verb panel
        # and all of `.qa-act` are still present behind that one constant,
        # which is why `cells` is asserted EMPTY rather than ignored: a panel
        # holding both would mean the switch had failed open.
        check("it opens all nineteen modules, and no verbs",
              m["open"] and m["isModules"] and m["tiles"] == 19 and m["cells"] == 0,
              f"tiles={m['tiles']} verbs={m['cells']} head={m['head']!r}")
        # WHITE AT 40% OVER A 15px BLUR · node 371:5157, and ruling five on
        # this surface in six days: .94 at radius 22, then the profile menu's
        # borrowed material, then 4A's .62/30/saturate(1.8), which went to .92
        # to stay white over an 82% black backdrop and back when that became a
        # light 30% tint. The node states .4 and 15 with NO saturation, and the
        # saturate is asserted ABSENT rather than merely not required — it was
        # never in the file, and a lift nobody can point at a source for is
        # what makes the next comparison against the artboard fail for reasons
        # nobody can name.
        check("the node's white at 40% over a 15px blur, and no saturation",
              m["material"] == "rgba(255, 255, 255, 0.4)" and m["radius"] == "28px"
              and "blur(15px)" in (m["panelBlur"] or "")
              and "saturate" not in (m["panelBlur"] or ""),
              f"{m['material']} r={m['radius']} {m['panelBlur']}")
        # AND NO CLIP WINDOW, in any state. The verb panel unfolded out of the
        # pill's measured box by transitioning `clip-path`; the launcher scales
        # up out of the pill as one surface instead, and a clip window would
        # open over a panel that is already growing. Asserted because
        # `.qa.is-open .qa-menu` outranks the launcher's own rule on
        # specificity and put the clip back once.
        check("…and no clip window, which this panel does not unfold from",
              m["clip"] == "none", str(m["clip"]))
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
        check("…and the pill wears its label again while open", m["labelW"] > 60, str(m["labelW"]))
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

    # ══ THE PLANTING IS THE ARTBOARD'S, AT EVERY WIDTH ════════════════════
    # Three bands draw one image and the base rule's `foliage.png` is now
    # reached by none of them, which is exactly the arrangement that decays
    # quietly: widen a media query, or touch the base rule, and one band goes
    # back to the tiled sprigs with nothing failing. Nothing asserted this at
    # all until today — the phone's own ruling of 10 Sep shipped unchecked.
    #
    # WHAT IS ASSERTED IS THE DERIVATION, not three sets of constants. The
    # crop is one proportion at every width because it is stated as `cover` at
    # 67.89%, so it is checked as the same string everywhere. The hold is the
    # one thing that legitimately differs: it ends where the Main Frame's top
    # edge is, which is what "solid for as long as it is behind the greeting
    # and the field" means — so the edge is MEASURED and the mask is required
    # to hold to it, rather than both being written down twice and drifting.
    print("\nthe planting, and where it stops being solid")
    with Chrome(width=WIDTH, height=900) as c:
        c.goto(BASE + "index.html?v=2", settle=2.0)
        pl = json.loads(c.eval("""(()=>{const b=e=>e.getBoundingClientRect();
          const f=document.querySelector('.foliage'), cs=getComputedStyle(f);
          const m=(cs.webkitMaskImage||cs.maskImage||'');
          const hold=/#000(?:000)?\\s+0(?:px)?\\s*,\\s*(?:rgb\\(0,\\s*0,\\s*0\\)|#000(?:000)?)\\s+(\\d+)px/.exec(m)
                  || /,\\s*rgb\\(0,\\s*0,\\s*0\\)\\s+(\\d+)px/.exec(m);
          return JSON.stringify({
            img: /([^/"')]+\\.png)/.exec(cs.backgroundImage||'')?.[1] || null,
            size: cs.backgroundSize, pos: cs.backgroundPosition,
            boxH: Math.round(b(f).height),
            hold: hold ? +hold[1] : null,
            frameTop: Math.round(b(document.querySelector('.main-frame')).top),
            masks: m.split(/\\)\\s*,\\s*(?=linear|radial)/).length,
          })})()"""))
        check("it is the artboard's illustration, not the tiled sprigs",
              pl["img"] == "foliage-artboard.png", str(pl["img"]))
        # ONE CROP, STATED AS A PROPORTION. `cover` at 67.89% is the node's
        # 190.44% / -61.4% solved once; a vw offset was correct at 744 and
        # only there, which is the bug this replaced.
        check("…on the one crop that is correct in any box",
              pl["size"] == "cover" and pl["pos"] == "50% 67.89%",
              f"{pl['size']} at {pl['pos']}")
        # AND THE FEATHER IS ONE MASK, not the base rule's feather-intersect-
        # clearing pair: the clearing lifts the top-left for dark text over
        # busy sprigs, and this artwork carries the node's own flat 5% black
        # instead. Composited, the corner would be darkened twice.
        check("…through one mask, the clearing left off it",
              pl["masks"] == 1, f"{pl['masks']} mask layers")
        # THE HOLD ENDS AT THE MAIN FRAME'S EDGE — 182 on the tablet, 204 at
        # 900 and up, and on the phone it cannot: the name wraps at 390 and
        # not at 430, so 210 is a declared compromise between 227 and 191 and
        # is checked as that rather than against a moving edge.
        if WIDTH < 744:
            check("…holding solid to the phone's declared 210", pl["hold"] == 210,
                  f"hold {pl['hold']}, frame at {pl['frameTop']}")
        else:
            check("…holding solid to exactly where the Main Frame begins",
                  pl["hold"] is not None and abs(pl["hold"] - pl["frameTop"]) <= 1,
                  f"hold {pl['hold']}, frame at {pl['frameTop']}")
        # AND THE BOX IS THE HOLD PLUS THE FADE, which is the part that was
        # got wrong first: taking the tablet's 293 to the desktop would have
        # squeezed the 111px dissolve to 89 so that a constant could stay put.
        want_box = 293 if WIDTH < 900 else 315
        check(f"…in a {want_box}px box, the hold plus its 111 of fade",
              pl["boxH"] == want_box, f"{pl['boxH']}px")

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
        check("…and the pager dots take all the room the layout allows",
              isinstance(d, list) and d[0] == 12 and d[1] >= 30,
              f"{d[0]}x{d[1]} on a 12px pitch, from 6x6"
              if isinstance(d, list) else f"probe said: {d}")
        check("no console errors", not c.errors(), str(c.errors()))

    print()
    if fails:
        print(f"{len(fails)} FAILED: " + ", ".join(fails))
        sys.exit(1)
    print("ALL PASS")


main()
