/* WEB V3 MOCKUP · the module page (13 Oct 2026). One page for every module:
   ?m=<module>#t=<tab>. Switching tab or module never reloads — the header and
   the summary column stay put and only the tab's content changes, through a
   View Transition where the browser has one. Arriving from Home, the tile you
   clicked grows into the header card (home.html leaves its rectangle in
   sessionStorage). Everything is SAMPLE data from data.js. */
(() => {
const $ = (s, el = document) => el.querySelector(s)
const esc = (s) => String(s ?? '').replace(/[&<>"']/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]))
const slug = (t) => t.toLowerCase().replace(/&/g, 'and').replace(/[^a-z0-9]+/g, '-').replace(/^-|-$/g, '')
const calm = () => matchMedia('(prefers-reduced-motion: reduce)').matches
const ICON = '../../assets/icon/'
const SITES = ['All sites', 'Crimson Frosted', 'Clearspring', 'Hollowpine', 'Foxglen']
const sv = (d, w = 1.8) => `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="${w}" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">${d}</svg>`
const I = {
  vet: sv('<circle cx="12" cy="7" r="3.2"/><path d="M5.5 20a6.5 6.5 0 0 1 13 0"/><path d="M12 13.5v3M10.5 15h3"/>'),
  team: sv('<circle cx="9" cy="8" r="3"/><circle cx="17" cy="9" r="2.4"/><path d="M3.5 19a5.5 5.5 0 0 1 11 0M14.5 19a4 4 0 0 1 6.5-3"/>'),
  bed: sv('<path d="M3 18V7M3 14h18v4M21 14v-2a3 3 0 0 0-3-3h-7v5"/><circle cx="7" cy="11" r="1.8"/>'),
  cal: sv('<rect x="4" y="5" width="16" height="15" rx="2"/><path d="M4 10h16M9 3v4M15 3v4"/>'),
  plus: sv('<path d="M12 5v14M5 12h14"/>', 2),
  pulse: sv('<path d="M3 12h4l2-5 4 10 2-5h6"/>'),
  exit: sv('<path d="M14 4h5v16h-5M10 8l-4 4 4 4M6 12h10"/>'),
  log: sv('<path d="M4 12a8 8 0 1 0 2.4-5.7M4 4v4h4"/><path d="M12 8v4l3 2"/>'),
  map: sv('<path d="M9 4 3 6v14l6-2 6 2 6-2V4l-6 2z"/><path d="M9 4v14M15 6v14"/>'),
  case: sv('<rect x="3" y="7" width="18" height="13" rx="2"/><path d="M9 7V5h6v2M12 11v5M9.5 13.5h5"/>'),
  pill: sv('<rect x="3" y="9" width="18" height="7" rx="3.5" transform="rotate(-35 12 12.5)"/><path d="m9.5 8.5 5 7"/>'),
  sick: sv('<circle cx="12" cy="12" r="8.5"/><path d="M8.5 10h.01M15.5 10h.01M8.5 16c1-1.3 2.2-2 3.5-2s2.5.7 3.5 2"/>'),
  doc: sv('<path d="M7 3h7l4 4v14H7z"/><path d="M14 3v4h4M10 12h5M10 16h5"/>'),
  report: sv('<path d="M4 20V10M10 20V4M16 20v-7M22 20H2"/>'),
  box: sv('<path d="m3 7 9-4 9 4-9 4z"/><path d="M3 7v10l9 4 9-4V7M12 11v10"/>'),
  rupee: sv('<path d="M7 4h10M7 8h10M7 4c5 0 6 8 0 8l7 8"/>'),
  truck: sv('<path d="M3 7h11v9H3zM14 10h4l3 3v3h-7"/><circle cx="7" cy="17.5" r="1.8"/><circle cx="17" cy="17.5" r="1.8"/>'),
  flask: sv('<path d="M9 3h6M10 3v6L4.5 18.5A1.7 1.7 0 0 0 6 21h12a1.7 1.7 0 0 0 1.5-2.5L14 9V3"/><path d="M7 15h10"/>'),
  paw: sv('<circle cx="7" cy="9" r="2"/><circle cx="12" cy="6" r="2"/><circle cx="17" cy="9" r="2"/><path d="M8 17c0-3 2-5 4-5s4 2 4 5-2 3-4 3-4 0-4-3z"/>'),
  tree: sv('<rect x="3" y="3" width="6" height="5" rx="1"/><rect x="15" y="10" width="6" height="5" rx="1"/><rect x="15" y="17" width="6" height="4" rx="1"/><path d="M6 8v11h9M6 12.5h9"/>'),
  egg: sv('<path d="M12 3c3.5 0 6.5 5.5 6.5 10.2A6.5 6.5 0 0 1 5.5 13.2C5.5 8.5 8.5 3 12 3z"/>'),
  tool: sv('<path d="M14.5 6.5a4 4 0 0 0 5 5L12 19a2.1 2.1 0 0 1-3-3z"/><path d="M14.5 6.5 17 4l3 3-2.5 2.5"/>'),
  food: sv('<path d="M7 3v8M5 3v5a2 2 0 0 0 4 0V3M7 11v10M17 3c-2 0-3 3-3 6s1 4 3 4v8"/>'),
  shield: sv('<path d="M12 3 5 6v6c0 4.5 3 7.5 7 9 4-1.5 7-4.5 7-9V6z"/><path d="m9 12 2 2 4-4"/>'),
  chat: sv('<path d="M4 5h16v11H9l-5 4z"/>'),
  cam: sv('<rect x="3" y="7" width="13" height="10" rx="2"/><path d="m16 11 5-3v8l-5-3"/>'),
  chev: sv('<path d="m9 6 6 6-6 6"/>', 2),
  down: sv('<path d="m6 9 6 6 6-6"/>', 2),
  back: sv('<path d="M20 12H4M10 6l-6 6 6 6"/>', 2),
  search: sv('<circle cx="11" cy="11" r="6.5"/><path d="m20 20-4-4"/>', 2),
  grid: sv('<rect x="4" y="4" width="7" height="7" rx="1.5"/><rect x="13" y="4" width="7" height="7" rx="1.5"/><rect x="4" y="13" width="7" height="7" rx="1.5"/><rect x="13" y="13" width="7" height="7" rx="1.5"/>', 2),
  list: sv('<path d="M8 6h12M8 12h12M8 18h12M4 6h.01M4 12h.01M4 18h.01"/>', 2.4),
  kebab: '<svg viewBox="0 0 20 20" fill="currentColor" aria-hidden="true"><circle cx="10" cy="4.5" r="1.6"/><circle cx="10" cy="10" r="1.6"/><circle cx="10" cy="15.5" r="1.6"/></svg>',
}
const COLOR = { g: '#1E8A4C', c: '#FA6140', t: '#00BDB2', y: '#E4B819', '': '#A9B6B1' }

/* ── state ── */
const byId = (id) => MODULES.find((m) => m.id === id)
/* A MODULE MAY DRAW ITS OWN SCREENS (window.SCREENS[id], e.g. hospital.js):
   `tabs[slug]` returns a tab's content, `after` wires it, and `patient` is a
   record page inside the module (the Figma Patient Profile) at #…&p=<id>. */
const SCREENS = window.SCREENS || {}
const S = () => SCREENS[mod.id] || {}
let mod = byId(new URLSearchParams(location.search).get('m')) || MODULES[0]
let pat, tab
let site = 0, listView = false, query = ''
function patFromHash() { const p = (location.hash.match(/p=([\w-]+)/) || [])[1]; return p && S().patient?.find(p) ? p : null }
const curTabs = () => (pat ? S().patient.tabs : mod.tabs)
function tabFromHash() { const t = (location.hash.match(/t=([\w-]+)/) || [])[1]; return curTabs().some((x) => slug(x) === t) ? t : (pat ? S().patient.first : 'dashboard') }
const tabName = () => curTabs().find((x) => slug(x) === tab) || 'Dashboard'
const urlOf = (m, t, p) => `?m=${m}#t=${t}${p ? `&p=${p}` : ''}`
pat = patFromHash(); tab = tabFromHash()
const RECENT = 'antz.v3.recent'
function noteRecent() { try { const r = JSON.parse(localStorage.getItem(RECENT) || '[]').filter((x) => x !== mod.id); r.unshift(mod.id); localStorage.setItem(RECENT, JSON.stringify(r.slice(0, 6))) } catch {} }
const recent = () => { try { return JSON.parse(localStorage.getItem(RECENT) || '[]') } catch { return [] } }

/* a transition where the browser has one; the change itself either way */
function vt(change) {
  if (document.startViewTransition && !calm()) return document.startViewTransition(change)
  change()
}

/* ── the top bar, the crumbs, the header card ── */
function drawTop() {
  document.documentElement.style.setProperty('--g', `var(${mod.g})`)
  $('#mselTile').innerHTML = `<img src="${ICON}${mod.icon}" alt="">`
  $('#mselName').textContent = mod.name
  document.title = `ANTZ · ${mod.name} (web v3 mockup)`
}
function drawCrumbs() {
  if (pat) { $('#crumbs').innerHTML = `<a href="home.html" data-home>Home</a><i>/</i>` + S().patient.crumbs(pat); return }
  const isDash = tab === 'dashboard'
  $('#crumbs').innerHTML = `<a href="home.html" data-home>Home</a><i>/</i>` +
    (isDash ? `<b>${esc(mod.name)}</b>` : `<button type="button" data-tab="dashboard">${esc(mod.name)}</button><i>/</i><b>${esc(tabName())}</b>`)
}
function drawHeader() {
  if (pat) { $('#hcard').innerHTML = S().patient.header(pat); return }
  $('#hcard').innerHTML =
    `<div class="hcard__l"><div class="hcard__id"><button type="button" class="back" data-home aria-label="Back to Home">${I.back}</button>` +
      `<h1>${esc(mod.name)}</h1><span class="pill">${esc(CAT[mod.cat])}</span><span class="pill is-sample">Sample data</span></div>` +
      `<p class="hcard__sub">${esc(mod.blurb)}</p></div>` +
    `<div class="hcard__r"><span>Site</span><div class="site"><button type="button" class="site__btn" aria-haspopup="menu" aria-expanded="false"><i></i>${esc(SITES[site])}${I.down}</button>` +
      `<div class="site__menu" role="menu" hidden>${SITES.map((s, i) => `<button type="button" role="menuitemradio" data-site="${i}" aria-pressed="${i === site}">${esc(s)}</button>`).join('')}</div></div>` +
      `<button type="button" class="ibtn" aria-label="More">${I.kebab}</button></div>`
}

/* ── the summary column (Figma 933:2997) ── */
function drawLeft() {
  if (pat) { $('#left').innerHTML = S().patient.left(pat); return }
  const photo = mod.photo ? `<img class="ph" src="${esc(mod.photo)}" alt="">` : `<img class="gl" src="${ICON}${mod.icon}" alt="">`
  $('#left').innerHTML =
    `<div class="prof"><div class="prof__panel"><div class="prof__photo">${photo}<span class="prof__badge">${esc(CAT[mod.cat].split(' ')[0].toUpperCase())}</span></div>` +
      `<div class="prof__id"><span class="k">Module · ${esc(SITES[site])}</span><span class="n">${esc(mod.name)}</span><span class="c">${esc(CAT[mod.cat])}</span><span class="d">${esc(mod.blurb)}</span></div></div></div>` +
    `<div class="stats">${mod.info.map(([k, v, ic]) => `<div class="srow"><span class="sico">${I[ic] || I.doc}</span><div><b>${esc(k)}</b><span>${esc(v)}</span></div></div>`).join('')}</div>` +
    `<div class="qa"><h2>Quick Actions</h2><div class="qa__list">${mod.actions.map(([l, ic]) =>
      `<button type="button" class="qa__it" data-toast="${esc(l)}">${I[ic] || I.plus}<span>${esc(l)}</span><span class="plus">${I.plus}</span></button>`).join('')}</div></div>` +
    `<div class="links">${mod.links.map(([l, ic]) => `<button type="button" data-toast="${esc(l)}"><span class="sico">${I[ic] || I.log}</span><span>${esc(l)}</span>${I.chev}</button>`).join('')}</div>`
}

/* ── the tabs ── */
function drawTabs() {
  $('#tabs').innerHTML = curTabs().map((t) => `<button type="button" role="tab" class="tab" data-tab="${slug(t)}" aria-selected="${slug(t) === tab}">${esc(t)}</button>`).join('')
  requestAnimationFrame(() => $('#tabs .tab[aria-selected="true"]')?.scrollIntoView({ block: 'nearest', inline: 'center', behavior: calm() ? 'auto' : 'smooth' }))
}

/* ── the widgets (Figma "Monitoring Card") ── */
const head = (w) =>
  `<div class="w__head"><div class="w__t"><button type="button" class="w__title" data-tab="${esc(w.to || 'dashboard')}">${esc(w.title)}${I.chev}</button>` +
  `<span class="w__meta">${esc(w.meta || '')}</span></div>` +
  (w.add ? `<button type="button" class="w__add" data-toast="${esc(w.add)}" aria-label="${esc(w.add)}"></button>` : '') + `</div>`
const hero = (v, u, ago) => `<div class="w__stat"><div class="w__hero"><span class="w__v" data-count="${esc(v)}">${esc(v)}</span>${u ? `<span class="w__u">${esc(u)}</span>` : ''}</div>${ago ? `<span class="w__ago">${esc(ago)}</span>` : ''}</div>`
const fmt = (n) => Number(n).toLocaleString('en-IN')
const BODY = {
  trend: (w) => hero(w.value, w.unit, w.ago) +
    `<div><div class="chart" data-s="${w.s.join(',')}" data-c="${w.c || 'g'}"></div><div class="ticks">${w.ticks.map((t) => `<span>${esc(t)}</span>`).join('')}</div></div>`,
  split: (w) => {
    const tot = w.parts.reduce((a, p) => a + p[1], 0)
    return hero(w.value, w.unit) +
      `<div><div class="split__bar">${w.parts.map((p, i) => `<i class="grow" style="--i:${i};flex:${Math.max(p[1] / tot, .02)};background:${COLOR[p[2]]}"></i>`).join('')}</div>` +
      `<div class="legend">${w.parts.slice().reverse().map((p) => `<div><i style="background:${COLOR[p[2]]}"></i><span>${esc(p[0])}</span><b>${fmt(p[1])}</b></div>`).join('')}</div></div>`
  },
  list: (w) => hero(w.value, w.unit) + `<div class="rows">${w.rows.map(([a, b, t]) => `<div><span>${esc(a)}</span><b class="${t ? 'tone-' + t : ''}">${esc(b)}</b></div>`).join('')}</div>`,
  queue: (w) => `<div class="queue">${w.cols.map(([l, n, c]) => `<div data-c="${c}"><b data-count="${n}">${fmt(n)}</b><span>${esc(l)}</span></div>`).join('')}</div>`,
  progress: (w) => hero(w.value, `of ${w.of} ${w.unit}`) +
    `<div><div class="prog"><i class="grow" style="width:${w.pct}%;background:${COLOR[w.c || 'g']}"></i></div><div class="prog__cap">${esc(w.caption)}</div></div>`,
  bars: (w) => {
    const max = Math.max(...w.bars.map((b) => b[1]))
    return hero(w.value, w.unit) +
      `<div><div class="bars">${w.bars.map(([l, n], i) => `<div class="growy" style="--i:${i};--h:${Math.max(8, n / max * 84)}px;background:${COLOR[w.c || 'g']}${i % 2 ? 'B3' : ''}"><b>${fmt(n)}</b></div>`).join('')}</div>` +
      `<div class="ticks">${w.bars.map(([l]) => `<span style="flex:1;text-align:center">${esc(l)}</span>`).join('')}</div></div>`
  },
  timeline: (w) => `<div class="tl">${w.items.map(([a, b]) => `<div><b>${esc(a)}</b><span>${esc(b)}</span></div>`).join('')}</div>`,
  note: (w) => `<div class="note"><p>${esc(w.text)}</p><div class="note__f"><span>${esc(w.ago)}</span><span class="note__dots"><b>•</b>•••••</span></div></div>`,
}
const widget = (w, i) => `<article class="w" style="--i:${i}" data-title="${esc(w.title.toLowerCase())}">${head(w)}${BODY[w.t](w)}</article>`

/* an area chart in the frame's shape: dashed guides, the line, open dots, the
   high and the low labelled. Drawn at the card's real width. */
function drawChart(el) {
  const s = el.dataset.s.split(',').map(Number), col = COLOR[el.dataset.c] || COLOR.g
  const W = el.clientWidth || 400, H = 100, top = 16, bot = 88
  const lo = Math.min(...s), hi = Math.max(...s), span = hi - lo || 1
  const x = (i) => 4 + i * (W - 8) / (s.length - 1)
  const y = (v) => bot - (v - lo) / span * (bot - top)
  const pts = s.map((v, i) => [x(i), y(v)])
  const d = pts.map((p, i) => (i ? 'L' : 'M') + p[0].toFixed(1) + ' ' + p[1].toFixed(1)).join(' ')
  const id = 'g' + Math.random().toString(36).slice(2, 8)
  const hiI = s.lastIndexOf(hi), loI = s.indexOf(lo)
  const nice = (v) => (Math.abs(v) >= 100 ? fmt(Math.round(v)) : String(+v.toFixed(2)))
  el.innerHTML =
    `<svg viewBox="0 0 ${W} ${H}" aria-hidden="true"><defs><linearGradient id="${id}" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="${col}" stop-opacity=".22"/><stop offset="1" stop-color="${col}" stop-opacity="0"/></linearGradient></defs>` +
      `<g class="grid"><line x1="0" x2="${W}" y1="18" y2="18"/><line x1="0" x2="${W}" y1="50" y2="50"/><line x1="0" x2="${W}" y1="82" y2="82"/></g>` +
      `<path class="fadein" d="${d} L${x(s.length - 1)} ${H} L${x(0)} ${H} Z" fill="url(#${id})"/>` +
      `<path class="ln draw" d="${d}" stroke="${col}"/>` +
      pts.map((p) => `<circle class="dot fadein" cx="${p[0]}" cy="${p[1]}" r="3.4" stroke="${col}"/>`).join('') + `</svg>` +
    `<span class="lab fadein" style="left:${pts[hiI][0]}px;top:${pts[hiI][1] - 6}px">${nice(hi)}</span>` +
    (loI !== hiI ? `<span class="lab fadein" style="left:${Math.max(14, pts[loI][0])}px;top:${pts[loI][1] - 6}px">${nice(lo)}</span>` : '')
  const ln = el.querySelector('.ln'); ln.style.setProperty('--len', Math.ceil(ln.getTotalLength()))
}
/* figures count up the first time they are drawn */
function countUp(root) {
  if (calm()) return
  root.querySelectorAll('[data-count]').forEach((el) => {
    const raw = el.dataset.count, m = /^(\D*)([\d,]*\.?\d+)(.*)$/.exec(raw); if (!m) return
    const target = parseFloat(m[2].replace(/,/g, '')), dec = (m[2].split('.')[1] || '').length, t0 = performance.now(), dur = 700
    const step = (t) => {
      const k = Math.min(1, (t - t0) / dur), e = 1 - Math.pow(1 - k, 3), v = target * e
      el.textContent = m[1] + (dec ? v.toFixed(dec) : Math.round(v).toLocaleString('en-IN')) + m[3]
      if (k < 1) requestAnimationFrame(step)
    }
    requestAnimationFrame(step)
  })
}

/* ── a screen that is not the Dashboard: its records ── */
const ANIMALS = ['Dheera · Bengal Tiger', 'Raja · Asiatic Lion', 'Mira · Sloth Bear', 'Tara · Indian Rhino', 'Kian · Persian Leopard', 'Bonnet Macaque troop', 'Sarus Crane pair', 'Gharial hatchlings', 'Blackbuck herd', 'Indian Peafowl']
/* what a module's records are about: an animal unless the module says otherwise */
const SUBJECT = {
  pharmacy: ['Item', ['Amoxicillin 500 mg', 'Meloxicam 1.5 mg/ml', 'Ivermectin 1%', 'Syringes 5 ml', 'Rabies Vaccine', 'Vitamin B Complex', 'Ketamine 50 mg/ml', 'Gauze rolls']],
  diet: ['Item', ['Chicken, whole · 120 kg', 'Bananas · 80 kg', 'Mealworms · 6 kg', 'Browse bundle · 40', 'Fish, rohu · 60 kg', 'Carrots · 45 kg']],
  housing: ['Enclosure', ['Paddock 3 · Hoofstock', 'Aviary 6 · Birds', 'Night house 2 · Carnivores', 'Encl 14 · Big cats', 'Vivarium 4 · Reptiles', 'Pond 1 · Aquatic']],
  users: ['Person', ['Dr. Kiran Iyer · Vet', 'Anita Deshmukh · Pharmacist', 'Kunal Singh · Keeper', 'Neha Joshi · Compliance', 'Rahul Verma · Auditor', 'Vikram Shah · Estate']],
  security: ['Subject', ['Gate 2 · Service vehicle', 'North perimeter fence', 'Visitor group · 42', 'Night patrol · Zone B', 'Gate 1 · Supplier truck']],
  reports: ['Report', ['Animal inventory by site', 'Dose compliance', 'Stock valuation', 'Mortality summary', 'Births by class']],
  approvals: ['Request', ['Transfer · 2 Blackbuck', 'Purchase · Incubator spares', 'Medicine · Ivermectin 1%', 'Access · New keeper', 'Transfer · Sarus Crane pair']],
  communication: ['Thread', ['Carnivore Section', 'Vets on call', 'Diet Kitchen', 'Monsoon hours notice', 'Night patrol roster']],
  parivesh: ['Application', ['Exhibit licence · Foxglen', 'Transport permit · CZA', 'Breeding permit · Gharial', 'Annual inventory return']],
  audit: ['Audit', ['Animal count · Crimson Frosted', 'Pharmacy stock · All sites', 'Kitchen hygiene · Clearspring', 'Enclosure safety · Foxglen']],
}
const STATES = [['open', 'In progress'], ['new', 'New'], ['done', 'Completed']]
const subj = () => (SUBJECT[mod.id] || ['Animal', ANIMALS])[1]
function records() {
  const pre = mod.id.slice(0, 3).toUpperCase(), name = tabName()
  let r = [...mod.id + tab].reduce((a, c) => a + c.charCodeAt(0), 7)
  const rnd = () => ((r = (r * 1103515245 + 12345) % 2147483648) / 2147483648)
  return Array.from({ length: 9 }, (_, i) => {
    const st = STATES[Math.floor(rnd() * 3)]
    return { id: `${pre}-${String(24000 + Math.floor(rnd() * 900)).padStart(5, '0')}/26`, what: subj()[Math.floor(rnd() * subj().length)], kind: name,
      site: SITES[1 + Math.floor(rnd() * 4)], date: `${String(13 - Math.min(12, i)).padStart(2, '0')} Oct`, st }
  })
}

/* ── the tab's content ── */
function drawBody({ enter = true } = {}) {
  const own = pat ? (() => S().patient.body(pat, tab, V3)) : S().tabs?.[tab] ? (() => S().tabs[tab](V3)) : null
  if (own) {
    $('#rbody').innerHTML = `<div class="${enter ? 'enter' : ''} own">${own()}</div>`
    $('#rbody').querySelectorAll('.chart').forEach(drawChart)
    S().after?.($('#rbody'), V3)
    if (enter) countUp($('#rbody'))
    return
  }
  const isDash = tab === 'dashboard'
  const items = isDash ? mod.widgets : records()
  const title = isDash ? `Overview  - ${mod.widgets.length}` : `${tabName()}  - ${items.length}`
  const [a0, a1] = mod.actions
  $('#rbody').innerHTML =
    `<div class="tools"><label class="search">${I.search}<input type="search" placeholder="Search in ${esc(isDash ? mod.name : tabName())}" value="${esc(query)}" aria-label="Search"></label>` +
      `<div class="tools__r"><button type="button" class="dd">${isDash ? 'This week' : 'All records'}${I.down}</button>` +
      `<div class="toggle" role="group" aria-label="View"><button type="button" data-view="grid" aria-pressed="${!listView}" aria-label="Cards">${I.grid}</button><button type="button" data-view="list" aria-pressed="${listView}" aria-label="List">${I.list}</button></div></div></div>` +
    `<div class="thead"><h2>${esc(title)}</h2><div class="cta">` +
      (a1 ? `<button type="button" class="btn-o" data-toast="${esc(a1[0])}">${I.plus}${esc(a1[0])}</button>` : '') +
      `<button type="button" class="btn-p" data-toast="${esc(a0[0])}">${esc(a0[0])}</button></div></div>` +
    (isDash
      ? `<div class="wgrid${listView ? ' is-list' : ''}${enter ? ' enter' : ''}">${mod.widgets.map(widget).join('')}</div>`
      : `<div class="table${enter ? ' enter' : ''}"><div class="table__row is-head"><span>ID</span><span>${esc((SUBJECT[mod.id] || ['Animal'])[0])}</span><span>Site</span><span>Date</span><span>Status</span></div>` +
        items.map((x, i) => `<div class="table__row" style="--i:${i}" data-toast="${esc(x.id)}"><b>${esc(x.id)}</b><span>${esc(x.what)}<small>${esc(x.kind)}</small></span><span>${esc(x.site)}</span><span>${esc(x.date)}</span><span class="st" data-s="${x.st[0]}">${esc(x.st[1])}</span></div>`).join('') + `</div>`)
  $('#rbody').querySelectorAll('.chart').forEach(drawChart)
  applyQuery()
  if (enter) countUp($('#rbody'))
}
function applyQuery() {
  const q = query.trim().toLowerCase()
  $('#rbody').querySelectorAll('.w').forEach((w) => { w.hidden = !!q && !w.dataset.title.includes(q) })
  $('#rbody').querySelectorAll('.table__row:not(.is-head)').forEach((r) => { r.hidden = !!q && !r.textContent.toLowerCase().includes(q) })
}

function drawAll() { drawTop(); drawCrumbs(); drawHeader(); drawLeft(); drawTabs(); drawBody(); noteRecent() }

/* ── moving: a tab, a module, home ── */
function setTab(t, { push = true } = {}) {
  if (t === tab) { $('#rbody').scrollIntoView({ block: 'nearest', behavior: 'smooth' }); return }
  query = ''
  vt(() => { tab = t; drawCrumbs(); drawTabs(); drawBody() })
  if (push) history.pushState({ m: mod.id, t }, '', urlOf(mod.id, t, pat))
  const card = $('.rcard'); if (card.getBoundingClientRect().top < 0) card.scrollIntoView({ block: 'start', behavior: calm() ? 'auto' : 'smooth' })
}
/* into a record page of this module, or (id null) back out of it */
function setPatient(id, { push = true, t } = {}) {
  query = ''
  const nt = t || (id ? S().patient.first : 'dashboard')
  vt(() => { pat = id; tab = nt; drawCrumbs(); drawHeader(); drawLeft(); drawTabs(); drawBody() })
  if (push) history.pushState({}, '', urlOf(mod.id, nt, id))
  scrollTo({ top: 0, behavior: calm() ? 'auto' : 'smooth' })
}
function setModule(id, { push = true, t = 'dashboard' } = {}) {
  const m = byId(id); if (!m) return
  query = ''
  vt(() => { mod = m; pat = null; tab = t; drawAll() })
  if (push) history.pushState({ m: id, t }, '', `?m=${id}#t=${t}`)
  scrollTo({ top: 0, behavior: calm() ? 'auto' : 'smooth' })
}
addEventListener('popstate', () => {
  const id = new URLSearchParams(location.search).get('m') || mod.id
  const t = (location.hash.match(/t=([\w-]+)/) || [])[1] || 'dashboard'
  const p = (location.hash.match(/p=([\w-]+)/) || [])[1] || null
  if (id !== mod.id) setModule(id, { push: false, t })
  else if (p !== pat) setPatient(p, { push: false, t })
  else setTab(t, { push: false })
})
function goHome() {
  try { sessionStorage.setItem('antz.v3.back', mod.id) } catch {}
  if (calm()) { location.href = 'home.html'; return }
  document.body.animate([{ opacity: 1, transform: 'none' }, { opacity: 0, transform: 'scale(.985)' }], { duration: 220, easing: 'ease-in', fill: 'forwards' })
    .finished.then(() => { location.href = 'home.html' })
}

/* ── the module selector (⌘K) ── */
const pop = $('#pop'), find = $('#popFind'), btn = $('#mselBtn')
function drawPop() {
  const q = find.value.trim().toLowerCase()
  const hit = (m) => !q || m.name.toLowerCase().includes(q) || m.tabs.some((t) => t.toLowerCase().includes(q))
  const it = (m) => `<button type="button" class="pop__it" data-mod="${m.id}" aria-current="${m.id === mod.id}" style="--g:var(${m.g})"><span class="mtile"><img src="${ICON}${m.icon}" alt=""></span>${esc(m.name)}</button>`
  let html = ''
  const rec = q ? [] : recent().map(byId).filter(Boolean).slice(0, 4)
  if (rec.length) html += `<div class="pop__cat">Recent</div><div class="pop__row">${rec.map(it).join('')}</div>`
  for (const [k, n] of Object.entries(CAT)) {
    const ms = MODULES.filter((m) => m.cat === k && hit(m)); if (!ms.length) continue
    html += `<div class="pop__cat">${esc(n)}</div><div class="pop__row">${ms.map(it).join('')}</div>`
  }
  $('#popList').innerHTML = html || `<p class="pop__none">No module called “${esc(find.value.trim())}”.</p>`
}
const openPop = () => { pop.hidden = false; btn.setAttribute('aria-expanded', 'true'); find.value = ''; drawPop(); find.focus() }
const shutPop = (focus) => { if (pop.hidden) return; pop.hidden = true; btn.setAttribute('aria-expanded', 'false'); if (focus) btn.focus() }
btn.addEventListener('click', () => (pop.hidden ? openPop() : shutPop(true)))
find.addEventListener('input', drawPop)
pop.addEventListener('keydown', (e) => {
  const its = [...pop.querySelectorAll('.pop__it')], i = its.indexOf(document.activeElement)
  if (e.key === 'Escape') { e.preventDefault(); shutPop(true) }
  else if (e.key === 'ArrowDown') { e.preventDefault(); its[Math.min(its.length - 1, i + 1)]?.focus() }
  else if (e.key === 'ArrowUp') { e.preventDefault(); (i <= 0 ? find : its[i - 1]).focus() }
  else if (e.key === 'Enter' && document.activeElement === find) { e.preventDefault(); its[0]?.click() }
})
pop.addEventListener('click', (e) => { const b = e.target.closest('[data-mod]'); if (!b) return; shutPop(false); if (b.dataset.mod !== mod.id) setModule(b.dataset.mod) })
addEventListener('keydown', (e) => {
  if ((e.metaKey || e.ctrlKey) && e.key.toLowerCase() === 'k') { e.preventDefault(); pop.hidden ? openPop() : shutPop(true); return }
  /* ← → walk the tabs when a tab has focus */
  const t = e.target.closest?.('.tab'); if (!t) return
  const step = { ArrowRight: 1, ArrowLeft: -1 }[e.key]; if (!step) return
  e.preventDefault()
  const ts = curTabs().map(slug), i = ts.indexOf(tab), n = ts[(i + step + ts.length) % ts.length]
  setTab(n); requestAnimationFrame(() => $(`.tab[data-tab="${n}"]`)?.focus())
})
document.addEventListener('pointerdown', (e) => {
  if (!pop.hidden && !e.target.closest('.msel')) shutPop(false)
  if (!e.target.closest('.site')) { const m = $('.site__menu'); if (m && !m.hidden) { m.hidden = true; $('.site__btn').setAttribute('aria-expanded', 'false') } }
})

/* ── everything else on the page is one listener ── */
let toastT = 0
function toast(msg) { const t = $('#toast'); t.textContent = msg; t.classList.add('on'); clearTimeout(toastT); toastT = setTimeout(() => t.classList.remove('on'), 2200) }
document.addEventListener('click', (e) => {
  const h = e.target.closest('[data-home]'); if (h) { e.preventDefault(); goHome(); return }
  const pt = e.target.closest('[data-patient]'); if (pt) { setPatient(pt.dataset.patient); return }
  const out = e.target.closest('[data-out]'); if (out) { setPatient(null, { t: out.dataset.out }); return }
  const tb = e.target.closest('[data-tab]'); if (tb) { setTab(tb.dataset.tab); return }
  const sb = e.target.closest('.site__btn'); if (sb) { const m = $('.site__menu'); m.hidden = !m.hidden; sb.setAttribute('aria-expanded', String(!m.hidden)); return }
  const si = e.target.closest('[data-site]'); if (si) { site = +si.dataset.site; vt(() => { drawHeader(); drawLeft(); drawBody() }); toast(`Showing ${SITES[site]}`); return }
  const v = e.target.closest('[data-view]'); if (v) { listView = v.dataset.view === 'list'; vt(() => drawBody({ enter: false })); return }
  const to = e.target.closest('[data-toast]'); if (to) { toast(`${to.dataset.toast} — opens in the ANTZ app (mockup)`); return }
})
document.addEventListener('input', (e) => { if (e.target.matches('.search input')) { query = e.target.value; applyQuery() } })
$('#fsBtn').addEventListener('click', () => (document.fullscreenElement ? document.exitFullscreen() : document.documentElement.requestFullscreen?.()))
/* a mouse wheel turns the tab row sideways */
$('#tabs').addEventListener('wheel', (e) => {
  const r = e.currentTarget; if (Math.abs(e.deltaX) > Math.abs(e.deltaY) || r.scrollWidth <= r.clientWidth) return
  e.preventDefault(); r.scrollBy({ left: e.deltaY, behavior: 'auto' })
}, { passive: false })
let rz = 0
addEventListener('resize', () => { clearTimeout(rz); rz = setTimeout(() => document.querySelectorAll('.chart').forEach(drawChart), 120) })

/* helpers a module's own screens draw with */
var V3 = window.V3 = { I, esc, slug, fmt, COLOR, ICON, SITES, widget, head, hero, BODY, mod: () => mod, site: () => site }
/* ── first draw, and the tile from Home growing into the header ── */
drawAll()
let from = null
try { from = JSON.parse(sessionStorage.getItem('antz.v3.from') || 'null'); sessionStorage.removeItem('antz.v3.from') } catch {}
if (from && from.id === mod.id && !calm()) {
  const to = $('#hcard').getBoundingClientRect()
  const fly = document.createElement('div')
  fly.className = 'fly'; fly.innerHTML = `<img src="${ICON}${mod.icon}" alt="">`
  Object.assign(fly.style, { left: from.x + 'px', top: from.y + 'px', width: from.w + 'px', height: from.h + 'px' })
  document.body.append(fly)
  const main = $('.wrap'); main.style.opacity = '0'
  fly.animate([
    { left: from.x + 'px', top: from.y + 'px', width: from.w + 'px', height: from.h + 'px', borderRadius: '12px' },
    { left: to.left + 'px', top: to.top + 'px', width: to.width + 'px', height: to.height + 'px', borderRadius: '12px' },
  ], { duration: 520, easing: 'cubic-bezier(.2,.7,.2,1)', fill: 'forwards' }).finished.then(() => {
    main.style.opacity = ''
    main.animate([{ opacity: 0 }, { opacity: 1 }], { duration: 240, easing: 'ease-out' })
    fly.animate([{ opacity: 1 }, { opacity: 0 }], { duration: 260, easing: 'ease-out', fill: 'forwards' }).finished.then(() => fly.remove())
    drawBody()
  })
}
})()
