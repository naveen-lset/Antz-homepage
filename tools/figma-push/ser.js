/* DOM → auto-layout tree. Runs in the page. window.__ser(rootEl, opts) returns
   { tree, images:[{id,src}], canvases:[{id,rect}] }.
   Node: { t:'F'|'T'|'V'|'SP', n, w, h, x, y, abs, L:{m,gap,cgap,pad,pa,ca,wrap,grid}, sz:{h,v}, fills, strokes, sw, radius, fx, op, clip, kids, ... } */
(() => {
const NAME = window.__NAMES || {}
const px = (v) => parseFloat(v) || 0
const r1 = (v) => Math.round(v * 10) / 10
let IMG = [], CANV = [], uid = 0
const imgIndex = new Map()

function parseColor(c) {
  if (!c) return null
  const cm = c.match(/color\(srgb\s+([^)]+)\)/)
  if (cm) { const p = cm[1].split(/[\s/]+/).filter(Boolean).map(Number); const a = p.length > 3 ? p[3] : 1; if (a === 0) return null; return { r: p[0], g: p[1], b: p[2], a } }
  const m = c.match(/rgba?\(([^)]+)\)/)
  if (!m) return null
  const p = m[1].split(/[ ,/]+/).filter(Boolean).map(Number)
  const a = p.length > 3 ? p[3] : 1
  if (a === 0) return null
  return { r: p[0] / 255, g: p[1] / 255, b: p[2] / 255, a }
}
function splitTop(s) { const out = []; let d = 0, cur = ''; for (const ch of s) { if (ch === '(') d++; if (ch === ')') d--; if (ch === ',' && d === 0) { out.push(cur.trim()); cur = '' } else cur += ch } if (cur.trim()) out.push(cur.trim()); return out }
function gradient(g, w, h) {
  const lin = g.match(/^(repeating-)?linear-gradient\((.*)\)$/s), rad = g.match(/^(repeating-)?radial-gradient\((.*)\)$/s)
  if (!lin && !rad) return null
  const parts = splitTop((lin || rad)[2])
  let angle = 180, first = parts[0]
  if (lin) {
    if (/deg|turn|rad/.test(first) && !/rgb/.test(first)) { angle = /turn/.test(first) ? parseFloat(first) * 360 : /rad/.test(first) ? parseFloat(first) * 180 / Math.PI : parseFloat(first); parts.shift() }
    else if (/^to /.test(first)) { const t = first; angle = { 'to top': 0, 'to right': 90, 'to bottom': 180, 'to left': 270, 'to top right': 45, 'to right top': 45, 'to bottom right': 135, 'to right bottom': 135, 'to bottom left': 225, 'to left bottom': 225, 'to top left': 315, 'to left top': 315 }[t] ?? 180; parts.shift() }
  } else if (!/rgb/.test(first)) parts.shift()
  const stops = []
  parts.forEach((s, i) => {
    const cm = s.match(/rgba?\([^)]+\)|color\(srgb[^)]+\)/); if (!cm) return
    const c = parseColor(cm[0]) || { ...(parseColor(cm[0].replace(/,\s*0\)$/, ',1)')) || { r: 0, g: 0, b: 0 }), a: 0 }
    const pos = s.replace(cm[0], '').trim().split(/\s+/).filter(Boolean)
    stops.push({ c: { r: c.r, g: c.g, b: c.b, a: c.a ?? 1 }, p: pos.length ? (pos[0].endsWith('%') ? parseFloat(pos[0]) / 100 : parseFloat(pos[0]) / (lin ? Math.abs(w * Math.sin(angle * Math.PI / 180)) + Math.abs(h * Math.cos(angle * Math.PI / 180)) : Math.max(w, h))) : null })
  })
  if (stops.length < 2) return null
  stops.forEach((s, i) => { if (s.p == null) s.p = i === 0 ? 0 : i === stops.length - 1 ? 1 : null })
  for (let i = 1; i < stops.length - 1; i++) if (stops[i].p == null) { let j = i; while (stops[j].p == null) j++; const a = stops[i - 1].p, b = stops[j].p; for (let k = i; k < j; k++) stops[k].p = a + (b - a) * (k - i + 1) / (j - i + 1) }
  // stops outside the box (CSS allows -105% or 197%) are resampled at its edges, not clamped
  const at = (t) => { if (t <= stops[0].p) return stops[0].c; for (let i = 1; i < stops.length; i++) if (t <= stops[i].p) { const a = stops[i - 1], b = stops[i], k = b.p === a.p ? 1 : (t - a.p) / (b.p - a.p); return { r: a.c.r + (b.c.r - a.c.r) * k, g: a.c.g + (b.c.g - a.c.g) * k, b: a.c.b + (b.c.b - a.c.b) * k, a: a.c.a + (b.c.a - a.c.a) * k } } return stops[stops.length - 1].c }
  if (stops.some((s) => s.p < 0 || s.p > 1)) {
    const inner = stops.filter((s) => s.p > 0 && s.p < 1)
    const res = [{ c: at(0), p: 0 }, ...inner, { c: at(1), p: 1 }]
    stops.length = 0; res.forEach((s) => stops.push(s))
  }
  return lin ? { type: 'LIN', angle, stops } : { type: 'RAD', stops }
}
const clipText = (cs) => cs.webkitBackgroundClip === 'text' || cs.backgroundClip === 'text'
function bgPaints(cs, w, h, el) {
  const paints = []
  if (clipText(cs)) return paints
  const imgs = cs.backgroundImage && cs.backgroundImage !== 'none' ? splitTop(cs.backgroundImage) : []
  // CSS lists top first; Figma's array is bottom first
  const bc = parseColor(cs.backgroundColor)
  if (bc) paints.push({ type: 'SOLID', c: bc })
  imgs.slice().reverse().forEach((g) => {
    const gr = gradient(g, w, h); if (gr) { paints.push(gr); return }
    const u = g.match(/url\(["']?([^"')]+)["']?\)/)
    if (u) paints.push({ type: 'IMG', img: imgRef(u[1]), fit: cs.backgroundSize === 'contain' ? 'FIT' : 'FILL' })
  })
  return paints
}
function imgRef(src) {
  src = new URL(src, location.href).href
  if (!imgIndex.has(src)) { imgIndex.set(src, 'img' + imgIndex.size); IMG.push({ id: 'img' + (imgIndex.size - 1), src }) }
  return imgIndex.get(src)
}
function shadows(cs) {
  const s = cs.boxShadow; if (!s || s === 'none') return []
  return splitTop(s).map((one) => {
    const cm = one.match(/rgba?\([^)]+\)/); const c = cm ? parseColor(cm[0]) : null; if (!c) return null
    const rest = one.replace(cm[0], '').trim(); const inset = /inset/.test(rest)
    const n = rest.replace('inset', '').trim().split(/\s+/).map(px)
    return { type: inset ? 'INNER_SHADOW' : 'DROP_SHADOW', c, x: n[0] || 0, y: n[1] || 0, blur: n[2] || 0, spread: n[3] || 0 }
  }).filter(Boolean)
}
function radius(cs, w, h) {
  const f = (v) => { const p = v.split(' ')[0]; return p.endsWith('%') ? Math.min(w, h) * parseFloat(p) / 100 : px(p) }
  const rr = [f(cs.borderTopLeftRadius), f(cs.borderTopRightRadius), f(cs.borderBottomRightRadius), f(cs.borderBottomLeftRadius)].map((v) => Math.min(v, Math.min(w, h) / 2))
  return rr.some((v) => v > 0) ? rr.map(r1) : null
}
function strokes(cs) {
  const sides = ['Top', 'Right', 'Bottom', 'Left'].map((s) => ({ w: cs['border' + s + 'Style'] === 'none' ? 0 : px(cs['border' + s + 'Width']), c: parseColor(cs['border' + s + 'Color']) }))
  const vis = sides.filter((s) => s.w > 0 && s.c)
  if (!vis.length) return null
  const c = vis[0].c
  return { c, w: sides.map((s) => (s.w > 0 && s.c ? s.w : 0)) }
}
function effects(cs) {
  const fx = shadows(cs)
  const bf = (cs.backdropFilter || cs.webkitBackdropFilter || '').match(/blur\(([\d.]+)px\)/)
  if (bf) fx.push({ type: 'BACKGROUND_BLUR', blur: +bf[1] })
  const lf = (cs.filter || '').match(/blur\(([\d.]+)px\)/)
  if (lf) fx.push({ type: 'LAYER_BLUR', blur: +lf[1] })
  return fx
}

/* ── names ── */
const TAGN = { BUTTON: 'Button', A: 'Link', IMG: 'Image', svg: 'Icon', SVG: 'Icon', H1: 'Title', H2: 'Title', H3: 'Heading', H4: 'Heading', P: 'Text', UL: 'List', OL: 'List', LI: 'Item', SECTION: 'Section', HEADER: 'Header', NAV: 'Nav', MAIN: 'Main', ASIDE: 'Aside', INPUT: 'Field', LABEL: 'Label', ARTICLE: 'Card', FORM: 'Form', FOOTER: 'Footer', TEXTAREA: 'Field' }
const title = (s) => s.replace(/[-_]+/g, ' ').replace(/\s+/g, ' ').trim().replace(/\b\w/g, (m) => m.toUpperCase())
function roleOf(el) {
  const kids = [...el.children].filter((k) => getComputedStyle(k).display !== 'none')
  const txt = el.textContent.replace(/\s+/g, ' ').trim()
  const hasIcon = el.querySelector('svg, img')
  const parent = el.parentElement ? nameOf(el.parentElement).split(' · ')[0] : ''
  const blk = parent.split(' / ')[0]
  let role = 'Group'
  if (!kids.length && txt) role = 'Label'
  else if (hasIcon && txt && txt.length < 12) role = 'Stat'
  else if (hasIcon && !txt) role = 'Media'
  else if (txt) role = getComputedStyle(el).display.includes('flex') && getComputedStyle(el).flexDirection.startsWith('column') ? 'Stack' : 'Row'
  return blk ? `${blk} / ${role}` : role
}
const fileName = (src) => { const f = decodeURIComponent(src.split('/').pop().split('?')[0]).replace(/\.(svg|png|jpe?g|webp|gif)$/i, '').replace(/^(v2|v3|ki|pa|qa|sr|m|adeck|egg)-/, ''); return title(f) }
function nameOf(el) {
  const cls = [...(el.classList || [])].filter((c) => !/^(is|has)-/.test(c) && !/^js-/.test(c))
  for (const c of cls) if (NAME[c]) return NAME[c]
  let base = ''
  if (cls.length) {
    const c = cls.find((x) => x.includes('__')) || cls[0]
    const [blk, elem] = c.split('__')
    const b = NAME[blk] || title(blk.replace(/--.*/, ''))
    const eName = elem && elem.replace(/--.*/, '')
    base = elem ? `${b} / ${(window.__ELEM || {})[eName] || title(eName)}` : b
    const mod = c.split('--')[1]; if (mod && !elem) base += ` / ${title(mod)}`
  } else if (el.id && NAME['#' + el.id]) base = NAME['#' + el.id]
  else base = TAGN[el.tagName] || (el.id ? title(el.id) : roleOf(el))
  const lab = el.getAttribute && (el.getAttribute('aria-label') || '')
  if (lab && /^(BUTTON|A)$/.test(el.tagName) && lab.length < 40) base += ` · ${lab}`
  return base
}

/* ── svg ── */
function svgString(svg, color) {
  const cl = svg.cloneNode(true)
  const r = svg.getBoundingClientRect()
  cl.setAttribute('width', r1(r.width)); cl.setAttribute('height', r1(r.height)); cl.setAttribute('xmlns', 'http://www.w3.org/2000/svg')
  cl.querySelectorAll('use').forEach((u) => {
    const id = (u.getAttribute('href') || u.getAttribute('xlink:href') || '').replace('#', '')
    const sym = id && document.getElementById(id); if (!sym) { u.remove(); return }
    const g = document.createElementNS('http://www.w3.org/2000/svg', 'g')
    ;[...sym.childNodes].forEach((ch) => g.appendChild(ch.cloneNode(true)))
    ;['fill', 'stroke', 'stroke-width', 'stroke-linecap', 'stroke-linejoin'].forEach((a) => { if (sym.getAttribute(a)) g.setAttribute(a, sym.getAttribute(a)) })
    if (sym.getAttribute('viewBox') && !cl.getAttribute('viewBox')) cl.setAttribute('viewBox', sym.getAttribute('viewBox'))
    u.replaceWith(g)
  })
  const cs = getComputedStyle(svg)
  // the host's CSS fill/stroke become attributes on the root, where the
  // children inherit them unless they carry their own
  if (!svg.getAttribute('fill') && cs.fill && cs.fill !== 'rgb(0, 0, 0)') cl.setAttribute('fill', cs.fill)
  if (!svg.getAttribute('stroke') && cs.stroke && cs.stroke !== 'none') cl.setAttribute('stroke', cs.stroke)
  // the same for descendants styled from CSS (class rules), not attributes
  const src = svg.querySelectorAll('*'), dst = cl.querySelectorAll('*')
  if (src.length === dst.length) src.forEach((s, i) => {
    const c2 = getComputedStyle(s)
    if (!s.getAttribute('fill') && s.closest('svg') === svg && c2.fill && /url|rgb/.test(c2.fill) && c2.fill !== cs.fill) dst[i].setAttribute('fill', c2.fill)
    if (!s.getAttribute('stroke') && c2.stroke && c2.stroke !== 'none' && c2.stroke !== cs.stroke) dst[i].setAttribute('stroke', c2.stroke)
  })
  let out = new XMLSerializer().serializeToString(cl).replace(/currentColor/g, color || cs.color)
  out = out.replace(/\sclass="[^"]*"/g, '').replace(/\saria-[a-z]+="[^"]*"/g, '').replace(/\sstyle="[^"]*"/g, '')
  return out
}
const svgCache = {}
function fetchText(url) { if (svgCache[url] != null) return svgCache[url]; const x = new XMLHttpRequest(); x.open('GET', url, false); try { x.send() } catch (e) { return (svgCache[url] = '') } return (svgCache[url] = x.status === 200 ? x.responseText : '') }
function svgFromUrl(url, w, h, recolor) {
  let s = fetchText(url); if (!s) return null
  s = s.replace(/<\?xml[^>]*>/, '').replace(/<!--[\s\S]*?-->/g, '')
  s = s.replace(/<svg([^>]*)>/, (m, a) => `<svg${a.replace(/\s(width|height)="[^"]*"/g, '')} width="${r1(w)}" height="${r1(h)}">`)
  if (recolor) s = s.replace(/(fill|stroke)="(?!none)[^"]*"/g, `$1="${recolor}"`).replace(/currentColor/g, recolor)
  return s
}

/* ── text ── */
function fontOf(cs) {
  const fam = cs.fontFamily.split(',').map((f) => f.replace(/["']/g, '').trim())
  const known = ['Inter', 'DM Sans', 'Sour Gummy', 'Fraunces']
  const f = fam.find((x) => known.includes(x)) || 'Inter'
  return { f, wt: Math.min(900, Math.max(100, Math.round(px(cs.fontWeight) / 100) * 100)), it: cs.fontStyle === 'italic' }
}
function textStyle(cs) {
  const c = parseColor(cs.color) || { r: 0, g: 0, b: 0, a: 1 }
  const lh = cs.lineHeight === 'normal' ? null : px(cs.lineHeight)
  let g = null
  if (clipText(cs) && cs.backgroundImage !== 'none') g = gradient(splitTop(cs.backgroundImage)[0], 300, 60)
  return { ...fontOf(cs), g, sz: px(cs.fontSize), lh, ls: cs.letterSpacing === 'normal' ? 0 : px(cs.letterSpacing), c, tt: cs.textTransform, dec: /underline/.test(cs.textDecorationLine) ? 'U' : /line-through/.test(cs.textDecorationLine) ? 'S' : null }
}
const sameStyle = (a, b) => ['f', 'wt', 'it', 'sz', 'dec'].every((k) => a[k] === b[k]) && Math.abs(a.c.r - b.c.r) + Math.abs(a.c.g - b.c.g) + Math.abs(a.c.b - b.c.b) + Math.abs(a.c.a - b.c.a) < .01
function isPlainInline(el) {
  const cs = getComputedStyle(el)
  if (!/^inline$/.test(cs.display)) return false
  if (parseColor(cs.backgroundColor) || strokes(cs) || shadows(cs).length || (cs.backgroundImage && cs.backgroundImage !== 'none')) return false
  return [...el.childNodes].every((n) => n.nodeType === 3 || (n.nodeType === 1 && (n.tagName === 'BR' || isPlainInline(n))))
}
function collectRuns(el, runs, pre) {
  for (const n of el.childNodes) {
    if (n.nodeType === 3) { let s = n.textContent; if (!pre) s = s.replace(/\s+/g, ' '); if (s) runs.push({ s, st: textStyle(getComputedStyle(n.parentElement)) }) }
    else if (n.nodeType === 1) {
      if (n.tagName === 'BR') { runs.push({ s: '\n', st: textStyle(getComputedStyle(el)) }); continue }
      if (!visible(n)) continue
      const ncs = getComputedStyle(n), sp = (m) => (m > 0.5 ? ' '.repeat(Math.max(1, Math.round(m / (px(ncs.fontSize) * 0.3)))) : '')
      const ml = sp(px(ncs.marginLeft)), mr = sp(px(ncs.marginRight))
      if (ml) runs.push({ s: ml, st: textStyle(ncs) })
      collectRuns(n, runs, pre)
      if (mr) runs.push({ s: mr, st: textStyle(ncs) })
    }
  }
}
function pseudoText(el, which) {
  const p = getComputedStyle(el, which); const c = p.content
  if (!c || c === 'none' || c === 'normal' || !/^["']/.test(c)) return ''
  if (p.position === 'absolute' || p.position === 'fixed' || p.display === 'none') return ''
  return c.slice(1, -1).replace(/\\([0-9a-f]{1,6})\s?/gi, (m, h) => String.fromCodePoint(parseInt(h, 16)))
}
function textNode(el, rect, name) {
  const cs = getComputedStyle(el)
  const pre = /pre/.test(cs.whiteSpace)
  const runs = []
  const b = pseudoText(el, '::before'); if (b) runs.push({ s: b, st: textStyle(getComputedStyle(el, '::before')) })
  collectRuns(el, runs, pre)
  const a = pseudoText(el, '::after'); if (a) runs.push({ s: a, st: textStyle(getComputedStyle(el, '::after')) })
  // trim collapsed edges
  if (!pre && runs.length) { runs[0].s = runs[0].s.replace(/^\s+/, ''); runs[runs.length - 1].s = runs[runs.length - 1].s.replace(/\s+$/, '') }
  const chars = runs.map((r) => r.s).join('')
  if (!chars.trim()) return null
  const base = textStyle(cs)
  const segs = []; let pos = 0
  runs.forEach((r) => { if (!r.s) return; if (!sameStyle(r.st, base)) segs.push({ a: pos, b: pos + r.s.length, st: r.st }); pos += r.s.length })
  // single line?
  const range = document.createRange(); range.selectNodeContents(el)
  const rects = [...range.getClientRects()].filter((q) => q.width > 0)
  const lineH = base.lh || base.sz * 1.21
  const lines = new Set(rects.map((q) => Math.round(q.top / (lineH * .6)))).size
  const clamp = parseInt(cs.webkitLineClamp) || 0
  const ell = cs.textOverflow === 'ellipsis' && cs.whiteSpace.includes('nowrap') && el.scrollWidth > el.clientWidth + 1
  return { t: 'T', n: name || chars.slice(0, 40).replace(/\n/g, ' '), chars, st: base, segs, w: r1(rect.width), h: r1(rect.height), align: cs.textAlign === 'center' ? 'CENTER' : cs.textAlign === 'right' || cs.textAlign === 'end' ? 'RIGHT' : cs.textAlign === 'justify' ? 'JUSTIFIED' : 'LEFT', one: lines <= 1 && !clamp, trunc: ell ? 1 : clamp || 0, wrapOK: !cs.whiteSpace.includes('nowrap') }
}
function contentRect(el) {
  const r = el.getBoundingClientRect(), cs = getComputedStyle(el)
  const l = px(cs.paddingLeft) + px(cs.borderLeftWidth), t = px(cs.paddingTop) + px(cs.borderTopWidth)
  const w = r.width - l - px(cs.paddingRight) - px(cs.borderRightWidth), h = r.height - t - px(cs.paddingBottom) - px(cs.borderBottomWidth)
  return { left: r.left + l, top: r.top + t, width: w, height: h, right: r.left + l + w, bottom: r.top + t + h }
}

/* ── visibility ── */
function visible(el) {
  const cs = getComputedStyle(el)
  if (cs.display === 'none' || cs.visibility === 'hidden' || +cs.opacity === 0) return false
  if (el.hidden) return false
  const r = el.getBoundingClientRect()
  if (r.width < .5 && r.height < .5 && cs.overflow === 'visible') return [...el.children].some(visible)
  if (/sr-only|visually-hidden/.test(el.className) || (cs.position === 'absolute' && cs.clip === 'rect(0px, 0px, 0px, 0px)') || (r.width <= 1 && r.height <= 1 && cs.overflow === 'hidden')) return false
  return true
}
function hasBox(cs) {
  return !!(parseColor(cs.backgroundColor) || (cs.backgroundImage && cs.backgroundImage !== 'none') || strokes(cs) || shadows(cs).length || /blur/.test(cs.backdropFilter || '') || (cs.overflow !== 'visible' && cs.overflow !== 'clip'))
}

/* ── the walk ── */
function node(el, pr, ctx) {
  if (el.matches && el.matches(window.__SKIP || '#__none')) return null
  const cs = getComputedStyle(el)
  const r = el.getBoundingClientRect()
  const tag = el.tagName
  const base = { n: nameOf(el), w: r1(r.width), h: r1(r.height), x: r1(r.left - pr.left), y: r1(r.top - pr.top) }
  if (+cs.opacity < 1) base.op = +cs.opacity
  if (/^(absolute|fixed)$/.test(cs.position)) base.abs = true
  // CSS paint order: non-positioned in-flow boxes under positioned ones; z-index orders the rest
  base.zk = cs.position === 'static' ? -0.5 : (cs.zIndex === 'auto' ? 0 : parseInt(cs.zIndex) || 0)
  const flexGrow = px(cs.flexGrow)
  if (flexGrow > 0) base.grow = 1
  if (cs.alignSelf === 'stretch') base.stretch = 1

  if (tag === 'CANVAS' || (el.matches && el.matches(window.__RASTER || '#__none'))) { const id = 'cv' + CANV.length; CANV.push({ id, rect: { x: r.left + scrollX, y: r.top + scrollY, w: r.width, h: r.height } }); return { ...base, t: 'F', n: tag === 'CANVAS' ? 'Canvas' : base.n, fills: [{ type: 'IMG', img: id, fit: 'FILL' }] } }
  if (tag === 'svg' || tag === 'SVG') {
    if (el.closest('svg') !== el && el.ownerSVGElement) return null
    return { ...base, t: 'V', svg: svgString(el), n: el.getAttribute('aria-label') ? `Icon / ${el.getAttribute('aria-label')}` : (base.n === 'Icon' || base.n === 'Group' ? 'Icon' : base.n) }
  }
  if (tag === 'IMG') {
    let src = el.currentSrc || el.src
    const cont = cs.content && cs.content.match(/url\(["']?([^"')]+)["']?\)/); if (cont) src = cont[1]
    src = new URL(src, location.href).href
    const isSvg = /\.svg(\?|$)/i.test(src)
    const nm = el.alt ? `Image / ${el.alt.slice(0, 40)}` : (/^(Image|Group)$|\/ (Label|Media|Row|Stat|Group)$/.test(base.n) ? `${isSvg ? 'Icon' : 'Image'} / ${fileName(src)}` : base.n)
    if (isSvg) { const s = svgFromUrl(src, r.width, r.height); if (s) return { ...base, t: 'V', svg: s, n: nm, radius: radius(cs, r.width, r.height) } }
    return { ...base, t: 'F', n: nm, fills: [{ type: 'IMG', img: imgRef(src), fit: cs.objectFit === 'contain' ? 'FIT' : 'FILL' }], radius: radius(cs, r.width, r.height), strokes: strokes(cs), fx: effects(cs) }
  }
  // a CSS mask icon: the mask SVG, recoloured with the box's colour
  const mask = (cs.maskImage || cs.webkitMaskImage || '').match(/url\(["']?([^"')]+)["']?\)/)
  if (mask && !el.children.length) {
    const col = parseColor(cs.backgroundColor)
    const s = svgFromUrl(new URL(mask[1], location.href).href, r.width, r.height, col ? `rgb(${Math.round(col.r * 255)},${Math.round(col.g * 255)},${Math.round(col.b * 255)})` : '#000')
    if (s) return { ...base, t: 'V', svg: s, n: base.n.includes('/') ? base.n : 'Icon' }
  }

  if (![...el.children].some(visible) && !el.textContent.trim()) {
    const pb = getComputedStyle(el, '::before'), pu = pb.content !== 'none' && (pb.backgroundImage || '').match(/url\(["']?([^"')]+\.svg[^"')]*)["']?\)/)
    if (pu && !/absolute|fixed/.test(pb.position)) { const pw = px(pb.width) || r.width, ph = px(pb.height) || r.height; const sv = svgFromUrl(new URL(pu[1], location.href).href, pw, ph); if (sv) return { ...base, t: 'V', svg: sv, w: r1(pw), h: r1(ph), n: base.n.includes('·') ? base.n : 'Icon' } }
  }
  const f = { ...base, t: 'F' }
  const fills = bgPaints(cs, r.width, r.height, el); if (fills.length) f.fills = fills
  const st = strokes(cs); if (st) f.strokes = st
  const rad = radius(cs, r.width, r.height); if (rad) f.radius = rad
  const fx = effects(cs); if (fx.length) f.fx = fx
  if (cs.overflow !== 'visible' || cs.overflowX !== 'visible' || cs.overflowY !== 'visible') f.clip = 1

  // form fields: show value/placeholder as text
  if (tag === 'INPUT' || tag === 'TEXTAREA') {
    const val = el.value || el.placeholder || ''
    const ph = !el.value
    const cr = contentRect(el)
    const pcs = ph ? getComputedStyle(el, '::placeholder') : cs
    f.L = layoutFromPadding(cs, 'H', r)
    f.L.ca = 'CENTER'
    if (val) f.kids = [{ t: 'T', n: ph ? 'Placeholder' : 'Value', chars: val, st: textStyle(pcs), segs: [], w: r1(cr.width), h: r1(Math.min(cr.height, px(cs.lineHeight) || px(cs.fontSize) * 1.3)), align: 'LEFT', one: true, trunc: 1, wrapOK: false, grow: 1 }]
    return f
  }

  // collect children: elements, anonymous text, absolute pseudo boxes
  const kidsIn = [], kidsAbs = [], all = []
  const pureText = [...el.childNodes].every((n) => n.nodeType === 3 || (n.nodeType === 1 && (n.tagName === 'BR' || isPlainInline(n))))
  const hasText = el.textContent.trim().length > 0 || pseudoText(el, '::before') || pseudoText(el, '::after')
  if (pureText && hasText && !/flex|grid/.test(cs.display)) {
    const tn = textNode(el, contentRect(el))
    if (tn && !hasBox(cs) && !px(cs.paddingLeft) && !px(cs.paddingTop) && !px(cs.paddingRight) && !px(cs.paddingBottom)) {
      Object.assign(tn, { x: base.x, y: base.y, abs: base.abs, grow: base.grow, op: base.op, zk: base.zk })
      if (tn.n === tn.chars.slice(0, 40).replace(/\n/g, ' ') && !/^(Text|Title|Heading|Label|Group|Item)$/.test(base.n) && base.n !== 'Link') tn.n = tn.chars.slice(0, 40).replace(/\n/g, ' ')
      return tn
    }
    if (tn) { tn.x = r1(contentRect(el).left - r.left); tn.y = r1(contentRect(el).top - r.top); const it = { node: tn, rect: contentRect(el) }; kidsIn.push(it); all.push(it) }
  } else {
    for (const n of el.childNodes) {
      if (n.nodeType === 3) {
        if (!n.textContent.trim()) continue
        const range = document.createRange(); range.selectNodeContents(n); const rr = range.getBoundingClientRect()
        if (rr.width < .5) continue
        const tst = textStyle(cs)
        const s = n.textContent.replace(/\s+/g, ' ').trim()
        all.push(kidsIn[kidsIn.push({ node: { t: 'T', n: s.slice(0, 40), chars: s, st: tst, segs: [], w: r1(rr.width), h: r1(rr.height), x: r1(rr.left - r.left), y: r1(rr.top - r.top), align: 'LEFT', one: true, trunc: 0, wrapOK: true }, rect: rr }) - 1])
        continue
      }
      if (n.nodeType !== 1 || !visible(n)) continue
      const ccs = getComputedStyle(n)
      const add = (k, el2) => { let rc = el2.getBoundingClientRect(); if (k._dy) { rc = { left: rc.left, right: rc.right, width: rc.width, top: rc.top + k._dy, bottom: rc.bottom, height: rc.height - k._dy }; delete k._dy } const it = { node: k, rect: rc }; (k.abs ? kidsAbs : kidsIn).push(it); all.push(it) }
      if (ccs.display === 'contents') { for (const m of n.children) if (visible(m)) { const k = node(m, r, ctx); if (k) add(k, m) } continue }
      const k = node(n, r, ctx); if (!k) continue
      add(k, n)
    }
  }
  // positioned pseudo-elements (rules, dots, underlines) as absolute boxes
  for (const which of ['::before', '::after']) {
    const p = getComputedStyle(el, which)
    if (!p.content || p.content === 'none' || p.display === 'none' || !/absolute|fixed/.test(p.position)) continue
    const pw = px(p.width), ph = px(p.height); if (pw < .5 || ph < .5) continue
    const pf = bgPaints(p, pw, ph); const pst = strokes(p); if (!pf.length && !pst) continue
    let x = px(p.left), y = px(p.top)
    if (p.left === 'auto' && p.right !== 'auto') x = r.width - px(cs.borderLeftWidth) - px(cs.borderRightWidth) - px(p.right) - pw
    if (p.top === 'auto' && p.bottom !== 'auto') y = r.height - px(cs.borderTopWidth) - px(cs.borderBottomWidth) - px(p.bottom) - ph
    x += px(cs.borderLeftWidth); y += px(cs.borderTopWidth)
    const pit = { node: { t: 'F', n: which === '::before' ? `${base.n} / Before` : `${base.n} / After`, w: r1(pw), h: r1(ph), x: r1(x), y: r1(y), abs: true, fills: pf, strokes: pst, radius: radius(p, pw, ph), op: +p.opacity < 1 ? +p.opacity : undefined, pseudo: 1, zk: p.zIndex === 'auto' ? 0 : parseInt(p.zIndex) || 0 } }
    kidsAbs.push(pit); if (which === '::before') all.unshift(pit); else all.push(pit)
  }
  kidsAbs.forEach((k) => { if (k.node.pseudo) return; k.node.x = r1(k.rect.left - r.left); k.node.y = r1(k.rect.top - r.top) })

  f.L = inferLayout(el, cs, r, kidsIn)
  if (kidsIn.length === 1 && kidsIn[0].rect.width > r.width + 1 && (f.L.m === 'V' || f.L.m === 'H')) f.L = { m: 'H', gap: 0, pad: f.L.pad, pa: 'MIN', ca: 'MIN' }
  // a <button> centres its own label, with no flex rule to say so
  if (tag === 'BUTTON' && f.L.m === 'V' && kidsIn.length === 1 && kidsIn[0].node.t === 'T') { f.L.m = 'H'; f.L.pa = 'CENTER'; f.L.ca = 'CENTER'; const p = f.L.pad; f.L.pad = [Math.min(p[0], p[2]), p[1], Math.min(p[0], p[2]), p[3]] }
  if (f.L.negA && !f.fills && !f.strokes && !f.fx && !f.clip) { f.y = r1(f.y + f.L.negA); f.h = r1(f.h - f.L.negA); f._dy = f.L.negA; f.kids_shift = -f.L.negA }
  f.kids = []
  const sp = f.L.spacers || []; delete f.L.spacers
  all.forEach((k) => { f.kids.push(k.node); const i = kidsIn.indexOf(k); if (i >= 0 && sp[i]) f.kids.push({ t: 'SP', n: 'Spacer', size: r1(sp[i]), w: 0, h: 0 }) })
  if (f.kids_shift) { f.kids.forEach((k) => { if (k.abs) k.y = r1(k.y + f.kids_shift) }); delete f.kids_shift }
  if (f.L.m === 'N') f.kids.forEach((k) => { k.abs = true })
  // collapse a bare wrapper around one child of the same box
  if (f.kids.length === 1 && !f.fills && !f.strokes && !f.fx && !f.radius && !f.clip && !f.op && !f.kids[0].abs) {
    const k = f.kids[0]
    if (Math.abs(k.w - f.w) < 1 && Math.abs(k.h - f.h) < 1) {
      const generic = /^(Group|Text|Item|Label|Icon|Image|Link)$/.test(k.n) || (k.t === 'T')
      const keep = { ...k, x: f.x, y: f.y, abs: f.abs, grow: f.grow || k.grow, stretch: f.stretch }
      if (k.t !== 'T' && generic && !/^(Group)$/.test(f.n)) keep.n = f.n
      return keep
    }
  }
  return f
}
function layoutFromPadding(cs, m, r) {
  return { m, gap: 0, pad: [cs.paddingTop, cs.paddingRight, cs.paddingBottom, cs.paddingLeft].map(px).map((v, i) => r1(v + px(cs['border' + ['Top', 'Right', 'Bottom', 'Left'][i] + 'Width']))), pa: 'MIN', ca: 'MIN' }
}
function inferLayout(el, cs, r, kids) {
  const cssPad = layoutFromPadding(cs, 'V', r).pad
  if (!kids.length) return { m: 'V', gap: 0, pad: cssPad, pa: 'MIN', ca: 'MIN', empty: 1 }
  const R = kids.map((k) => k.rect)
  const disp = cs.display
  // GRID
  if (/grid/.test(disp) && kids.length > 1) {
    const cols = cs.gridTemplateColumns.split(' ').map(px).filter((v) => v > 0)
    const rows = cs.gridTemplateRows.split(' ').map(px).filter((v) => v > 0)
    const cg = px(cs.columnGap), rg = px(cs.rowGap)
    if (cols.length >= 1 && rows.length >= 1) {
      const pad = cssPad
      const colStart = [], rowStart = []; let a = r.left + pad[3]; cols.forEach((c) => { colStart.push(a); a += c + cg })
      let b = r.top + pad[0]; rows.forEach((c) => { rowStart.push(b); b += c + rg })
      const near = (arr, v) => { let bi = 0; arr.forEach((x, i) => { if (Math.abs(x - v) < Math.abs(arr[bi] - v)) bi = i }); return bi }
      const place = R.map((q) => { const ci = near(colStart, q.left), ri = near(rowStart, q.top); let ce = ci; while (ce + 1 < cols.length && colStart[ce + 1] < q.right - 2) ce++; let re = ri; while (re + 1 < rows.length && rowStart[re + 1] < q.bottom - 2) re++; return { r: ri, c: ci, rs: re - ri + 1, cs: ce - ci + 1 } })
      const occ = new Set(); let ok = true
      place.forEach((p) => { for (let i = p.r; i < p.r + p.rs; i++) for (let j = p.c; j < p.c + p.cs; j++) { const k = i + ':' + j; if (occ.has(k)) ok = false; occ.add(k) } })
      if (ok && (cols.length > 1 || rows.length > 1)) return { m: 'G', cols: cols.map(r1), rows: rows.map(r1), cg: r1(cg), rg: r1(rg), pad, place }
    }
  }
  let m = null
  if (/flex/.test(disp)) m = /column/.test(cs.flexDirection) ? 'V' : 'H'
  const stackV = R.every((q, i) => i === 0 || q.top >= R[i - 1].bottom - 1.5)
  const stackH = R.every((q, i) => i === 0 || q.left >= R[i - 1].right - 1.5)
  if (!m) m = stackV ? 'V' : stackH ? 'H' : null
  if (m === 'H' && /flex/.test(disp) && cs.flexWrap === 'wrap' && !stackH) {
    // wrapped rows
    return { m: 'H', wrap: 1, gap: r1(px(cs.columnGap)), cgap: r1(px(cs.rowGap)), pad: cssPad, pa: 'MIN', ca: 'MIN' }
  }
  if (m === 'V' && !stackV) m = null
  if (m === 'H' && !stackH) m = null
  if (!m && kids.length === 1) m = 'V'
  if (!m) return { m: 'N', pad: cssPad }
  const s = m === 'V' ? 'top' : 'left', e = m === 'V' ? 'bottom' : 'right'
  const S = m === 'V' ? r.top : r.left, E = m === 'V' ? r.bottom : r.right
  const gaps = R.slice(1).map((q, i) => q[s] - R[i][e])
  const jc = cs.justifyContent
  let pa = 'MIN', gap = 0, spacers = null
  const padA = R[0][s] - S, padB = E - R[R.length - 1][e]
  const negA = padA < -0.5 ? padA : 0
  const cssA = m === 'V' ? cssPad[0] : cssPad[3], cssB = m === 'V' ? cssPad[2] : cssPad[1]
  let pad = m === 'V' ? [padA, cssPad[1], padB, cssPad[3]] : [cssPad[0], padB, cssPad[2], padA]
  if (gaps.length) {
    const mn = Math.min(...gaps), mx = Math.max(...gaps)
    if (/space-between/.test(jc) && kids.length > 1) { pa = 'SPACE_BETWEEN'; gap = 0; pad = m === 'V' ? [cssA, cssPad[1], cssB, cssPad[3]] : [cssPad[0], cssB, cssPad[2], cssA] }
    else if (mx - mn <= 1.5) gap = (mn + mx) / 2
    else {
      // the usual gap wins; within 2px of it snaps; only real outliers keep extra room
      const cnt = {}; gaps.forEach((g) => { const k = Math.round(g); cnt[k] = (cnt[k] || 0) + 1 })
      const mode = +Object.entries(cnt).sort((x, y) => y[1] - x[1] || x[0] - y[0])[0][0]
      gap = mn < mode - 2 ? mn : mode
      spacers = gaps.map((g) => (g - gap > 2 ? g - gap : 0)); spacers.push(0)
      if (!spacers.some(Boolean)) spacers = null
    }
  }
  if (pa === 'MIN' && /center/.test(jc) && Math.abs(padA - padB) < 2 && padA > cssA + 1) { pa = 'CENTER'; pad = m === 'V' ? [cssA, cssPad[1], cssB, cssPad[3]] : [cssPad[0], cssB, cssPad[2], cssA] }
  else if (pa === 'MIN' && /flex-end|end/.test(jc) && padA > cssA + 1 && /flex/.test(disp)) { pa = 'MAX'; pad = m === 'V' ? [cssA, cssPad[1], cssB, cssPad[3]] : [cssPad[0], cssB, cssPad[2], cssA] }
  // cross axis
  const cs0 = m === 'V' ? 'left' : 'top', ce0 = m === 'V' ? 'right' : 'bottom'
  const CS = m === 'V' ? r.left : r.top, CE = m === 'V' ? r.right : r.bottom
  let cA = m === 'V' ? pad[3] : pad[0], cB = m === 'V' ? pad[1] : pad[2]
  const offA = R.map((q) => q[cs0] - CS), offB = R.map((q) => CE - q[ce0])
  if (Math.min(...offA) < cA - .5) cA = Math.max(0, Math.min(...offA))
  if (Math.min(...offB) < cB - .5) cB = Math.max(0, Math.min(...offB))
  const inner = (CE - CS) - cA - cB
  let votes = { MIN: 0, CENTER: 0, MAX: 0 }
  R.forEach((q, i) => {
    const sz = q[ce0] - q[cs0]
    if (Math.abs(sz - inner) < 1.5) { kids[i].node.fillX = 1; return }
    const a = offA[i] - cA, b = offB[i] - cB
    if (Math.abs(a - b) < 1.5) votes.CENTER++; else if (a < b) votes.MIN++; else votes.MAX++
  })
  const ai = cs.alignItems
  let ca = votes.CENTER > votes.MIN && votes.CENTER >= votes.MAX ? 'CENTER' : votes.MAX > votes.MIN ? 'MAX' : 'MIN'
  if (/flex/.test(disp) && m === 'H' && ai === 'baseline') ca = 'BASELINE'
  if (m === 'V') { pad[3] = cA; pad[1] = cB } else { pad[0] = cA; pad[2] = cB }
  return { m, gap: r1(gap), pad: pad.map((v) => r1(Math.max(0, v))), pa, ca, spacers, neg: gap < 0, negA: negA ? r1(negA) : 0 }
}

window.__ser = (root, opts = {}) => {
  IMG = []; CANV = []; imgIndex.clear()
  const r = root.getBoundingClientRect()
  const tree = node(root, r, {})
  tree.x = 0; tree.y = 0; tree.abs = false
  if (opts.name) tree.n = opts.name
  // the page colour often lives on <html>, above the root: carry it down
  if (!tree.fills) { let e = root; while (e && !tree.fills) { const c = parseColor(getComputedStyle(e).backgroundColor); if (c) tree.fills = [{ type: 'SOLID', c }]; e = e.parentElement } }
  return { tree, images: IMG, canvases: CANV }
}
})()
