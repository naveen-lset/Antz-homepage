// Builds one screen from a carrier payload. Placeholders: __KEY__, __X__, __Y__
const KEY = '__KEY__', POS = { x: __X__, y: __Y__ }
const page = await figma.getNodeByIdAsync('0:1')
await figma.setCurrentPageAsync(page)
// the carrier
const carriers = page.children.filter(n => n.name.startsWith('__carrier'))
const mine = carriers.filter(c => c.findAllWithCriteria({ types: ['TEXT'] }).some(t => t.characters.startsWith('@@' + KEY + '@@')))
let parts = []
// the newest upload wins; older ones for this screen are removed at the end
for (const t of (mine[mine.length - 1] ? mine[mine.length - 1].findAllWithCriteria({ types: ['TEXT'] }) : [])) {
  const m = t.characters.match(new RegExp('^@@' + KEY + '@@(\\d+)@@(\\d+)@@'))
  if (m) parts.push({ i: +m[1], s: t.characters.slice(m[0].length) })
}
if (!parts.length) throw new Error('no carrier for ' + KEY)
parts.sort((a, b) => a.i - b.i)
const P = JSON.parse(parts.map(p => p.s).join('').replace(/\u00A0/g, ' '))
const S = P.S, T = P.tree

// retry-safe: drop an earlier build of this screen
for (const n of page.children) if (n.name === T.n && n.type === 'FRAME') n.remove()

// fonts
const avail = (await figma.listAvailableFontsAsync()).map(f => f.fontName)
const styles = {}
avail.forEach(f => { (styles[f.family] = styles[f.family] || []).push(f.style) })
const W_INTER = { 100: 'Thin', 200: 'Extra Light', 300: 'Light', 400: 'Regular', 500: 'Medium', 600: 'Semi Bold', 700: 'Bold', 800: 'Extra Bold', 900: 'Black' }
const W_CAMEL = { 100: 'Thin', 200: 'ExtraLight', 300: 'Light', 400: 'Regular', 500: 'Medium', 600: 'SemiBold', 700: 'Bold', 800: 'ExtraBold', 900: 'Black' }
const fontCache = {}
function font(st) {
  const k = st.f + st.wt + (st.it ? 'i' : '')
  if (fontCache[k]) return fontCache[k]
  const fam = styles[st.f] ? st.f : 'Inter'
  const map = fam === 'Inter' ? W_INTER : W_CAMEL
  const list = styles[fam]
  const want = (w) => { const b = map[w]; return st.it ? (b === 'Regular' ? 'Italic' : b + ' Italic') : b }
  let style = null
  for (const d of [0, 100, -100, 200, -200, 300, -300, 400, -400]) { const w = st.wt + d; if (map[w] && list.includes(want(w))) { style = want(w); break } }
  if (!style) style = list.includes('Regular') ? 'Regular' : list[0]
  return (fontCache[k] = { family: fam, style })
}
const need = new Map()
;(function walk(n) { if (n.t === 'T') { const f = font(n.st); need.set(f.family + '|' + f.style, f); (n.segs || []).forEach(s => { const g = font(s.st); need.set(g.family + '|' + g.style, g) }) } (n.kids || []).forEach(walk) })(T)
for (const f of need.values()) await figma.loadFontAsync(f)

// paints
const col = (c) => ({ r: c.r, g: c.g, b: c.b })
function inv(m) { const [[a, c, e], [b, d, f]] = m; const det = a * d - b * c || 1e-9; return [[d / det, -c / det, (c * f - d * e) / det], [-b / det, a / det, (b * e - a * f) / det]] }
const images = []
function paints(list, w, h, node) {
  const out = []
  for (const p of list || []) {
    if (p.type === 'SOLID') out.push({ type: 'SOLID', color: col(p.c), opacity: p.c.a })
    else if (p.type === 'LIN') {
      const th = p.angle * Math.PI / 180, L = Math.abs(w * Math.sin(th)) + Math.abs(h * Math.cos(th))
      const dx = L * Math.sin(th) / Math.max(w, 1e-3), dy = -L * Math.cos(th) / Math.max(h, 1e-3)
      const S0 = [0.5 - dx / 2, 0.5 - dy / 2], E0 = [0.5 + dx / 2, 0.5 + dy / 2], N = [-(E0[1] - S0[1]), E0[0] - S0[0]]
      const M = [[E0[0] - S0[0], N[0], S0[0] - 0.5 * N[0]], [E0[1] - S0[1], N[1], S0[1] - 0.5 * N[1]]]
      out.push({ type: 'GRADIENT_LINEAR', gradientTransform: inv(M), gradientStops: p.stops.map(s => ({ position: s.p, color: { ...col(s.c), a: s.c.a } })) })
    } else if (p.type === 'RAD') {
      const k = 1.414
      out.push({ type: 'GRADIENT_RADIAL', gradientTransform: inv([[k, 0, 0.5 - 0.5 * k], [0, k, 0.5 - 0.5 * k]]), gradientStops: p.stops.map(s => ({ position: s.p, color: { ...col(s.c), a: s.c.a } })) })
    } else if (p.type === 'IMG') {
      out.push({ type: 'SOLID', color: { r: 0.85, g: 0.87, b: 0.86 } })
      images.push({ id: node.id, img: p.img, fit: p.fit })
    }
  }
  return out
}
function effects(fx) {
  return (fx || []).map(e => {
    if (e.type === 'DROP_SHADOW' || e.type === 'INNER_SHADOW') {
      const o = { type: e.type, color: { ...col(e.c), a: e.c.a }, offset: { x: e.x, y: e.y }, radius: e.blur, spread: e.spread, visible: true, blendMode: 'NORMAL' }
      if (e.type === 'DROP_SHADOW') o.showShadowBehindNode = false
      return o
    }
    return { type: e.type, radius: e.blur, visible: true }
  })
}
function decorate(f, n) {
  f.fills = paints(n.fills, n.w, n.h, f)
  if (n.strokes) {
    f.strokes = [{ type: 'SOLID', color: col(n.strokes.c), opacity: n.strokes.c.a }]
    f.strokeAlign = 'INSIDE'
    const [t, r, b, l] = n.strokes.w
    if (t === r && r === b && b === l) f.strokeWeight = t
    else { f.strokeTopWeight = t; f.strokeRightWeight = r; f.strokeBottomWeight = b; f.strokeLeftWeight = l }
  }
  if (n.radius) { const [a, b, c, d] = n.radius; if (a === b && b === c && c === d) f.cornerRadius = a; else { f.topLeftRadius = a; f.topRightRadius = b; f.bottomRightRadius = c; f.bottomLeftRadius = d } }
  if (n.fx && n.fx.length) {
    let fx = n.fx
    // Figma paints no inner shadow on a frame with no fill: make it a stroke
    if (!f.fills.length) { const ins = fx.filter(e => e.type === 'INNER_SHADOW' && !e.x && !e.y && !e.blur && e.spread > 0); if (ins.length && !n.strokes) { f.strokes = [{ type: 'SOLID', color: col(ins[0].c), opacity: ins[0].c.a }]; f.strokeWeight = ins[0].spread; f.strokeAlign = 'INSIDE' } fx = fx.filter(e => !ins.includes(e)) }
    f.effects = effects(fx)
  }
  if (n.op != null) f.opacity = n.op
}

// spacers become padding on a bare neighbour where they can
function bare(k) { return k && k.t === 'F' && !k.fills && !k.strokes && !k.fx && k.L && (k.L.m === 'V' || k.L.m === 'H') && !k.abs }
function mergeSpacers(n) {
  if (!n.kids) return
  n.kids.forEach(mergeSpacers)
  if (!n.L || (n.L.m !== 'V' && n.L.m !== 'H')) return
  const V = n.L.m === 'V', out = []
  for (let i = 0; i < n.kids.length; i++) {
    const k = n.kids[i]
    if (k.t !== 'SP') { out.push(k); continue }
    const next = n.kids.slice(i + 1).find(x => x.t !== 'SP' && !x.abs), prev = [...out].reverse().find(x => !x.abs)
    const grow = (x, start) => {
      const idx = V ? (start ? 0 : 2) : (start ? 3 : 1)
      x.L.pad[idx] += k.size
      if (V) x.h += k.size; else x.w += k.size
      if (start) (x.kids || []).forEach(c => { if (c.abs) { if (V) c.y += k.size; else c.x += k.size } })
    }
    if (bare(next)) grow(next, true)
    else if (bare(prev)) grow(prev, false)
    else out.push(k)
  }
  n.kids = out
  // what is left: every gap is gap + spacer. Use the most common total as the
  // frame's gap and settle each difference in a neighbour's padding
  if (!n.kids.some(k => k.t === 'SP') || n.L.pa === 'SPACE_BETWEEN') return
  const flow = [], G = []
  for (const k of n.kids) { if (k.abs) continue; if (k.t === 'SP') { if (G.length) G[G.length - 1] += k.size; continue } if (flow.length) G.push(n.L.gap); flow.push(k) }
  if (G.length < 1) return
  const cnt = {}; G.forEach(g => { const r = Math.round(g * 10) / 10; cnt[r] = (cnt[r] || 0) + 1 })
  const mode = +Object.entries(cnt).sort((a, b) => b[1] - a[1] || b[0] - a[0])[0][0]
  const padOf = (x) => x.t === 'F' && x.L && (x.L.m === 'V' || x.L.m === 'H')
  // plan every difference first; apply only if all of them have a home
  const plan = []
  for (let i = 0; i < G.length; i++) {
    const d = Math.round((G[i] - mode) * 10) / 10; if (!d) continue
    const prev = flow[i], next = flow[i + 1], ix = V ? 2 : 1, iy = V ? 0 : 3
    if (d < 0 && padOf(prev) && prev.L.pad[ix] >= -d) plan.push([prev, ix, d, false])
    else if (d < 0 && padOf(next) && next.L.pad[iy] >= -d) plan.push([next, iy, d, true])
    else if (d > 0 && padOf(next)) plan.push([next, iy, d, true])
    else if (d > 0 && padOf(prev)) plan.push([prev, ix, d, false])
    else return
  }
  for (const [x, i, d, start] of plan) {
    x.L.pad[i] += d; if (V) x.h += d; else x.w += d
    if (start) (x.kids || []).forEach(c => { if (c.abs) { if (V) c.y += d; else c.x += d } })
  }
  n.L.gap = mode; n.kids = n.kids.filter(k => k.t !== 'SP')
}
mergeSpacers(T)

let count = 0
function hug(f, n, fillsW, fillsH) {
  if (!n.L || !(n.kids || []).some(k => !k.abs && k.t !== 'SP') || n.L.m === 'N' || n.L.m === 'G') return
  try {
    if (!fillsW) f.layoutSizingHorizontal = 'HUG'
    if (!fillsH) f.layoutSizingVertical = 'HUG'
  } catch (e) { return }
  const okW = !fillsW && Math.abs(f.width - n.w) <= 1.01, okH = !fillsH && Math.abs(f.height - n.h) <= 1.01
  f.resize(okW ? f.width : Math.max(n.w, 0.01), okH ? f.height : Math.max(n.h, 0.01))
  if (okW) f.layoutSizingHorizontal = 'HUG'
  if (okH) f.layoutSizingVertical = 'HUG'
}
function build(n) {
  count++
  if (n.t === 'T') {
    const t = figma.createText()
    t.fontName = font(n.st)
    t.characters = n.chars
    t.fontSize = n.st.sz
    t.lineHeight = n.st.lh ? { unit: 'PIXELS', value: n.st.lh } : { unit: 'AUTO' }
    if (n.st.ls) t.letterSpacing = { unit: 'PIXELS', value: n.st.ls }
    t.fills = [{ type: 'SOLID', color: col(n.st.c), opacity: n.st.c.a }]
    t.textAlignHorizontal = n.align
    if (n.st.tt === 'uppercase') t.textCase = 'UPPER'; else if (n.st.tt === 'lowercase') t.textCase = 'LOWER'; else if (n.st.tt === 'capitalize') t.textCase = 'TITLE'
    if (n.st.dec === 'U') t.textDecoration = 'UNDERLINE'; else if (n.st.dec === 'S') t.textDecoration = 'STRIKETHROUGH'
    for (const s of n.segs || []) {
      if (s.b <= s.a) continue
      t.setRangeFontName(s.a, s.b, font(s.st)); t.setRangeFontSize(s.a, s.b, s.st.sz)
      t.setRangeFills(s.a, s.b, [{ type: 'SOLID', color: col(s.st.c), opacity: s.st.c.a }])
      if (s.st.dec === 'U') t.setRangeTextDecoration(s.a, s.b, 'UNDERLINE')
    }
    t.name = n.n
    if (n.op != null) t.opacity = n.op
    if (n.st.g) t.fills = paints([n.st.g], n.w, n.h, t)
    if (n.one && !n.trunc) t.textAutoResize = 'WIDTH_AND_HEIGHT'
    else {
      t.resize(Math.max(n.w, 1), Math.max(n.h, 1))
      t.textAutoResize = 'HEIGHT'
      if (n.trunc) { t.textTruncation = 'ENDING'; t.maxLines = n.trunc }
    }
    return t
  }
  if (n.t === 'V') {
    let v
    try { v = figma.createNodeFromSvg(S[n.svg]) } catch (e) { v = figma.createFrame(); v.fills = [] }
    v.name = n.n
    if (Math.abs(v.width - n.w) > .5 || Math.abs(v.height - n.h) > .5) v.resize(Math.max(n.w, .01), Math.max(n.h, .01))
    v.clipsContent = false
    if (n.op != null) v.opacity = n.op
    return v
  }
  if (n.t === 'SP') { const s = figma.createFrame(); s.name = 'Spacer'; s.fills = []; s.resize(Math.max(n.size, .01), Math.max(n.size, .01)); return s }
  const f = figma.createFrame()
  f.name = n.n
  f.clipsContent = !!n.clip
  f.resize(Math.max(n.w, .01), Math.max(n.h, .01))
  decorate(f, n)
  const kids = n.kids || []
  const L = n.L || { m: 'N' }
  const auto = kids.length && (L.m === 'V' || L.m === 'H' || L.m === 'G')
  if (auto && L.m !== 'G') {
    f.layoutMode = L.m === 'V' ? 'VERTICAL' : 'HORIZONTAL'
    ;[f.paddingTop, f.paddingRight, f.paddingBottom, f.paddingLeft] = L.pad.map(v => +v || 0)
    f.itemSpacing = L.pa === 'SPACE_BETWEEN' ? 0 : (+L.gap || 0)
    f.primaryAxisAlignItems = L.pa
    f.counterAxisAlignItems = L.ca === 'BASELINE' && L.m === 'H' ? 'BASELINE' : L.ca
    if (L.wrap) { f.layoutWrap = 'WRAP'; f.counterAxisSpacing = L.cgap || 0 }
    f.resize(Math.max(n.w, .01), Math.max(n.h, .01))
  } else if (auto && L.m === 'G') {
    f.layoutMode = 'GRID'
    f.gridRowCount = L.rows.length; f.gridColumnCount = L.cols.length
    f.gridRowGap = L.rg; f.gridColumnGap = L.cg
    ;[f.paddingTop, f.paddingRight, f.paddingBottom, f.paddingLeft] = L.pad
    L.cols.forEach((v, i) => { f.gridColumnSizes[i].type = 'FIXED'; f.gridColumnSizes[i].value = v })
    L.rows.forEach((v, i) => { f.gridRowSizes[i].type = 'FIXED'; f.gridRowSizes[i].value = v })
    f.resize(Math.max(n.w, .01), Math.max(n.h, .01))
  }
  let fillsW = false, fillsH = false, gi = 0
  const inflow = kids.filter(k => !k.abs)
  const order = L.m === 'G' ? inflow.map((k, i) => ({ k, p: L.place[i] })).sort((a, b) => a.p.r - b.p.r || a.p.c - b.p.c) : null
  const place = new Map(); if (order) order.forEach(o => place.set(o.k, o.p))
  const seq = L.m === 'G' ? [...order.map(o => o.k), ...kids.filter(k => k.abs)] : kids
  const built = []
  for (const k of seq) {
    const c = build(k)
    built.push({ c, k })
    if (auto && L.m === 'G' && !k.abs) {
      const p = place.get(k)
      f.appendChildAt(c, p.r, p.c)
      if (p.rs > 1) c.gridRowSpan = p.rs
      if (p.cs > 1) c.gridColumnSpan = p.cs
      try { c.layoutSizingHorizontal = 'FILL'; c.layoutSizingVertical = 'FILL' } catch (e) {}
      continue
    }
    f.appendChild(c)
    if (!auto || k.abs) {
      if (auto) c.layoutPositioning = 'ABSOLUTE'
      c.x = k.x; c.y = k.y
      continue
    }
    const V = L.m === 'V'
    // a single-line label hugs its text; one that must stretch along a row truncates
    // an icon keeps its own size: FILL stretches an SVG drawn with preserveAspectRatio="none"
    if (k.t === 'V') continue
    if (k.t === 'T' && k.one && !k.trunc) {
      try { if (k.grow && !V) { c.layoutSizingHorizontal = 'FILL'; c.textAutoResize = 'HEIGHT'; c.textTruncation = 'ENDING'; c.maxLines = 1; fillsW = true } } catch (e) {}
      continue
    }
    try {
      if (k.fillX) { if (V) { c.layoutSizingHorizontal = 'FILL'; fillsW = true } else { c.layoutSizingVertical = 'FILL'; fillsH = true } }
      if (k.grow) { if (V) { c.layoutSizingVertical = 'FILL'; fillsH = true } else { c.layoutSizingHorizontal = 'FILL'; fillsW = true } }
    } catch (e) {}
  }
  // paint order: browsers paint by z key; Figma by child order. Reorder when the
  // in-flow children already ascend (so their layout order is untouched)
  if (built.length > 1 && L.m !== 'G') {
    const key = (k) => (k.zk == null ? -0.5 : k.zk)
    const inflowKeys = built.filter(b => !b.k.abs).map(b => key(b.k))
    const mono = inflowKeys.every((v, i) => i === 0 || v >= inflowKeys[i - 1])
    if (mono) {
      const sorted = built.map((b, i) => ({ ...b, i })).sort((a, b2) => key(a.k) - key(b2.k) || a.i - b2.i)
      if (sorted.some((b, i) => b.i !== i)) for (const b of sorted) f.appendChild(b.c)
    }
  }
  if (auto && L.m !== 'G') hug(f, n, fillsW, fillsH)
  return f
}
const root = build(T)
root.x = POS.x; root.y = POS.y
root.clipsContent = true
if (P.fixedH) { root.layoutSizingVertical = 'FIXED'; root.resize(T.w, P.fixedH) }
// remove this screen's carrier
mine.forEach(c => c.remove())
const byImg = {}
images.forEach(i => { (byImg[i.img] = byImg[i.img] || []).push(i.id) })
return { root: root.id, name: root.name, w: root.width, h: root.height, nodes: count, images: byImg, fits: Object.fromEntries(images.map(i => [i.id, i.fit])) }
