/* ANTZ Home — redesign prototype · BEHAVIOUR · round 2
   ─────────────────────────────────────────────────────────────────────────
   Local state only. ?v=a STREAM, ?v=b SPLIT (from 1040px of page width the
   operational layer — Site Reports, what is due, the context's actions — gets
   its own column). Round 2: each section has its own idea (shelf, deck, V4
   note cards), the V4 palette, and motion that means something. */
(function () {
  const D = window.ANTZ
  const $ = (s, r = document) => r.querySelector(s)
  const $$ = (s, r = document) => [...r.querySelectorAll(s)]
  const esc = (s) => String(s).replace(/[&<>"']/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]))
  const icon = (n, cls = 'icon') => `<svg class="${cls}"><use href="#i-${n}"/></svg>`
  const calm = () => matchMedia('(prefers-reduced-motion: reduce)').matches
  const EASE = 'cubic-bezier(.32,.72,0,1)'
  const SPRING = 'cubic-bezier(.34,1.3,.64,1)'
  const VARIANT = new URLSearchParams(location.search).get('v') === 'b' ? 'b' : 'a'
  const body = document.body
  body.dataset.variant = VARIANT
  document.addEventListener('touchstart', () => {}, { passive: true })   /* iOS :active */

  /* focus moves only for the keyboard — a script's focus() after a tap draws
     the ring in Chrome and Safari, the blue outline the owner flagged */
  let lastInput = 'pointer'
  document.addEventListener('pointerdown', () => { lastInput = 'pointer' }, true)
  document.addEventListener('keydown', () => { lastInput = 'key' }, true)
  const kbd = () => lastInput === 'key'

  let toastT = 0
  function toast(msg) { const t = $('#toast'); t.textContent = msg; t.classList.add('is-on'); clearTimeout(toastT); toastT = setTimeout(() => t.classList.remove('is-on'), 2200) }
  document.addEventListener('click', (e) => { const b = e.target.closest('[data-toast]'); if (b) toast(b.dataset.toast) })

  /* the V4 gradient each module wears */
  const GRAD = { medical: 'medical', species: 'species', hospital: 'hospital', pharmacy: 'pharmacy', lab: 'lab', tasks: 'users', housing: 'followup', diet: 'diet', administer: 'administer', approvals: 'users', security: 'security', comms: 'parivesh', users: 'users', reports: 'parivesh', eggs: 'eggs', mortality: 'mortality', parivesh: 'parivesh', followup: 'followup' }
  const g = (id) => `var(--g-${GRAD[id] || 'users'})`

  /* ── segmented control: options + a thumb that slides to the chosen one ─ */
  function seg(el, opts, value, onPick) {
    el.innerHTML = `<span class="seg__thumb"></span>` + opts.map(([k, l, n]) => `<button class="seg__opt" type="button" data-k="${k}" aria-pressed="${k === value}">${esc(l)}${n != null ? ` <b>${n}</b>` : ''}</button>`).join('')
    const thumb = el.querySelector('.seg__thumb')
    const place = (instant) => {
      const on = el.querySelector('[aria-pressed="true"]'); if (!on) return
      if (instant) thumb.style.transition = 'none'
      thumb.style.width = on.offsetWidth + 'px'; thumb.style.transform = `translateX(${on.offsetLeft}px)`
      if (instant) { thumb.offsetWidth; thumb.style.transition = '' }
    }
    el.onclick = (e) => {
      const b = e.target.closest('.seg__opt'); if (!b) return
      el.querySelectorAll('.seg__opt').forEach((x) => x.setAttribute('aria-pressed', String(x === b)))
      place(false); onPick(b.dataset.k)
    }
    requestAnimationFrame(() => place(true))
    el._place = () => place(true)
  }

  /* no sidebar (owner, 24 Sep 2026) — the page is the whole width */
  const navMode = () => {}

  /* ══ HEADER ═════════════════════════════════════════════════════════════ */
  function tick() {
    const d = new Date(), h = d.getHours()
    $('#hello').textContent = h < 12 ? 'Good morning,' : h < 17 ? 'Good afternoon,' : 'Good evening,'
    $('#when').innerHTML = `<b>${d.toLocaleTimeString('en-IN', { hour: '2-digit', minute: '2-digit', hour12: false })}</b>${d.toLocaleDateString('en-IN', { weekday: 'short', day: 'numeric', month: 'short' })}`
  }
  tick(); setInterval(tick, 20000)
  const hdr = $('#hdr')
  function measureHeader() {
    hdr.style.setProperty('--search-l', ($('#compactTitle').scrollWidth + 16 + (body.classList.contains('has-menu') ? 56 : 0)) + 'px')
    hdr.style.setProperty('--search-r', (44 + 44 + 24) + 'px')
  }
  let lastY = scrollY, idleT = 0
  function onScroll() {
    const y = scrollY
    hdr.style.setProperty('--p', Math.min(1, Math.max(0, y / 96)).toFixed(3))
    const fab = $('#fab')
    if (y > 160 && y > lastY + 2) fab.classList.add('is-compact'); else if (y < lastY - 2 || y < 160) fab.classList.remove('is-compact')
    clearTimeout(idleT); idleT = setTimeout(() => fab.classList.remove('is-compact'), 900)
    lastY = y
    if (body.classList.contains('ss-open')) placeSearch()
    /* a fling or a jump can carry a section past the observer unseen; anything
       whose top is above the fold is shown, so nothing stays blank */
    $$('[data-reveal]:not(.is-shown)').forEach((s) => { if (s.getBoundingClientRect().top < innerHeight && s._watched) s.classList.add('is-shown') })
    const mh = $('#modHead')
    mh.classList.toggle('is-stuck', mh.getBoundingClientRect().top <= 65 && $('#secModules').getBoundingClientRect().bottom > 184)
  }
  addEventListener('scroll', onScroll, { passive: true })

  /* ══ MY SPECIES · the shelf ═════════════════════════════════════════════ */
  $('#railSpecies').innerHTML = D.SPECIES.map((s) =>
    `<button class="sp press" type="button" data-open="species" data-id="${s.id}" aria-label="${esc(s.name)}, ${esc(s.species)}, ${esc(s.status)}">` +
      `<img class="sp__img" src="${s.img}" alt="" loading="lazy" decoding="async" data-fly>` +
      (s.tone === 'bad' ? `<span class="sp__badge">Hospital</span>` : s.tone === 'info' && s.status === 'New arrival' ? `<span class="sp__badge" style="background:var(--c-secondary-dark)">New</span>` : '') +
      `<span class="sp__plate"><span class="sp__name">${esc(s.name)}</span><span class="sp__species">${esc(s.species)}</span>` +
      `<span class="sp__status tone-${s.tone}"><span class="dot"></span><span style="overflow:hidden;text-overflow:ellipsis">${esc(s.status)} · ${esc(s.meta)}</span></span></span></button>`).join('') +
    `<button class="sp__add press" type="button" data-toast="Add species opens the picker"><span class="plus">${icon('plus')}</span>Add species</button>`
  $('#spCount').textContent = `${D.SPECIES.length} followed`

  /* ══ ANNOUNCEMENTS · the stacked deck ═══════════════════════════════════ */
  const A = D.ANNOUNCEMENTS
  let order = A.map((_, i) => i)          /* order[0] is the front card */
  const deck = $('#deck')
  deck.innerHTML = A.map((a, i) =>
    `<div class="deck__card" data-ai="${i}" role="group" aria-roledescription="slide" aria-label="${i + 1} of ${A.length}: ${esc(a.title)}">` +
      `<div class="deck__img"><img src="${a.img}" alt="" decoding="async" data-fly></div>` +
      `<div class="deck__body"><span class="deck__chip">${esc(a.cat)}</span><div class="deck__title">${esc(a.title)}</div>` +
      `<div class="deck__desc">${esc(a.body)}</div><div class="deck__meta"><span><b>${esc(a.date)}</b> · ${esc(a.cat)}</span><span class="deck__read">Read ${icon('arrow')}</span></div></div></div>`).join('')
  $('#deckIndex').insertAdjacentHTML('beforeend', A.map((a, i) => `<button class="deck__row" type="button" role="tab" data-ai="${i}"><img src="${a.img}" alt=""><span style="min-width:0"><b>${esc(a.title)}</b><small>${esc(a.cat)} · ${esc(a.date.replace(' 2026', ''))}</small></span></button>`).join(''))
  $('#deckDots').innerHTML = A.map(() => '<i></i>').join('')
  $('#annCount').textContent = `${A.length} this week`
  function paintDeck() {
    order.forEach((ai, pos) => { const c = deck.querySelector(`[data-ai="${ai}"]`); c.dataset.i = Math.min(pos, 3); c.style.setProperty('--i', Math.min(pos, 3)); c.setAttribute('aria-hidden', String(pos !== 0)); c.tabIndex = pos === 0 ? 0 : -1 })
    const front = order[0]
    $$('#deckDots i').forEach((d, i) => d.classList.toggle('on', i === front))
    $('#deckCount').textContent = `${front + 1} / ${A.length}`
    $$('.deck__row').forEach((r) => r.setAttribute('aria-current', String(+r.dataset.ai === front)))
    const row = $(`.deck__row[data-ai="${front}"]`), th = $('#deckThumb')
    if (row && row.offsetParent) { th.style.height = row.offsetHeight + 'px'; th.style.transform = `translateY(${row.offsetTop}px)` }
  }
  function sizeDeck() {
    const w = deck.clientWidth
    deck.style.setProperty('--deck-h', (w <= 520 ? Math.round(w * 1.02) : Math.round(Math.min(300, Math.max(248, w * .4)))) + 'px')
  }
  /* send the front card away (dir -1 left / +1 right) and bring the next up */
  function advance(dir = -1, velocity = 0) {
    const c = deck.querySelector(`[data-ai="${order[0]}"]`)
    const w = deck.clientWidth
    if (calm()) { order = dir < 0 ? [...order.slice(1), order[0]] : [order[order.length - 1], ...order.slice(0, -1)]; paintDeck(); return }
    if (dir < 0) {
      const from = c.style.transform || 'translate(0,0)'
      c.classList.add('is-dragging')
      c.animate([{ transform: from }, { transform: `translateX(${-w * 1.1}px) rotate(-6deg)`, opacity: .2 }], { duration: Math.max(220, 380 - velocity * 120), easing: 'cubic-bezier(.3,.7,.4,1)' }).finished.then(() => {
        c.style.transform = ''; c.classList.remove('is-dragging')
        order = [...order.slice(1), order[0]]; paintDeck()
      })
    } else {
      /* back: the last card comes in from the left onto the top of the pile */
      order = [order[order.length - 1], ...order.slice(0, -1)]
      const n = deck.querySelector(`[data-ai="${order[0]}"]`)
      paintDeck()
      n.animate([{ transform: `translateX(${-w * 1.1}px) rotate(-6deg)`, opacity: .2 }, { transform: 'none', opacity: 1 }], { duration: 480, easing: EASE })
    }
  }
  function goTo(ai) {
    if (ai === order[0]) return
    const idx = order.indexOf(ai)
    const c = deck.querySelector(`[data-ai="${order[0]}"]`)
    const run = () => { order = [...order.slice(idx), ...order.slice(0, idx)]; paintDeck() }
    if (calm()) return run()
    c.animate([{ transform: 'none', opacity: 1 }, { transform: 'translateY(-10px) scale(.96)', opacity: 0 }], { duration: 200, easing: 'ease-in' }).finished.then(run)
  }
  $('#deckPrev').addEventListener('click', () => advance(1))
  $('#deckNext').addEventListener('click', () => advance(-1))
  $('#deckIndex').addEventListener('click', (e) => { const r = e.target.closest('.deck__row'); if (r) goTo(+r.dataset.ai) })
  deck.addEventListener('keydown', (e) => { if (e.key === 'ArrowLeft') advance(1); if (e.key === 'ArrowRight') advance(-1); if (e.key === 'Enter') openDetail(e.target.closest('.deck__card'), 'ann', A[order[0]].id) })
  /* drag: follow the finger with a little tilt; release decides */
  let dg = null
  deck.addEventListener('pointerdown', (e) => {
    const c = e.target.closest('.deck__card'); if (!c || c.dataset.i !== '0' || e.button > 0) return
    dg = { c, x0: e.clientX, y0: e.clientY, t0: performance.now(), dx: 0, on: false, pid: e.pointerId }
  })
  deck.addEventListener('pointermove', (e) => {
    if (!dg || e.pointerId !== dg.pid) return
    const dx = e.clientX - dg.x0, dy = e.clientY - dg.y0
    if (!dg.on) { if (Math.abs(dx) < 8) return; if (Math.abs(dy) > Math.abs(dx)) { dg = null; return } dg.on = true; dg.c.classList.add('is-dragging'); dg.c.setPointerCapture(e.pointerId) }
    dg.dx = dx
    /* rubber-band to the right: there is nothing to drag in from there */
    const x = dx > 0 ? dx * .35 : dx
    dg.c.style.transform = `translateX(${x}px) rotate(${x * .02}deg)`
    const k = Math.min(1, Math.abs(x) / (deck.clientWidth * .5))
    const next = deck.querySelector(`[data-ai="${order[1]}"]`); if (next && dx < 0) { next.style.transition = 'none'; next.style.transform = `translateY(${14 - 14 * k}px) scale(${.95 + .05 * k})`; next.style.filter = `brightness(${.86 + .14 * k})` }
  })
  const dropDeck = () => {
    if (!dg) return
    const d = dg; dg = null
    const next = deck.querySelector(`[data-ai="${order[1]}"]`); if (next) { next.style.transition = ''; next.style.transform = ''; next.style.filter = '' }
    if (!d.on) { openDetail(d.c, 'ann', A[+d.c.dataset.ai].id); return }
    const v = Math.abs(d.dx) / Math.max(1, performance.now() - d.t0)
    if (d.dx < -deck.clientWidth * .28 || (d.dx < -30 && v > .5)) advance(-1, v)
    else { d.c.classList.remove('is-dragging'); d.c.style.transform = '' }
  }
  deck.addEventListener('pointerup', dropDeck)
  deck.addEventListener('pointercancel', () => { if (dg) { dg.c.classList.remove('is-dragging'); dg.c.style.transform = ''; dg = null } })

  /* ══ RECENT NOTES · the V4 card ═════════════════════════════════════════ */
  const PRI = { critical: 'Critical', high: 'High', moderate: 'Moderate', low: 'Low' }
  const PRI_GLYPH = { critical: '<img src="../../assets/icon/obs-flame.svg" alt="">', high: '!!!', moderate: '!!', low: '!' }
  const initials = (n) => n.replace('Dr. ', '').split(' ').map((p) => p[0]).join('').slice(0, 2)
  const state = Object.fromEntries(D.NOTES.map((n) => [n.id, { liked: false, saved: false, ack: false, likes: n.likes }]))
  let ntFilter = 'all'
  function noteCard(n) {
    const s = state[n.id]
    return `<article class="nt press${s.ack ? ' is-ack' : ''}" data-open="note" data-id="${n.id}" tabindex="0" aria-label="${esc(PRI[n.pri])} priority note: ${esc(n.title)}">` +
      `<div class="nt__media${n.img ? '' : ' nt__media--enc'}">` +
        (n.img ? `<img class="nt__photo" src="${n.img}" alt="" loading="lazy" decoding="async" data-fly>` : `<span class="nt__kind">${n.kind === 'enclosure' ? 'Enclosure' : 'Animal'}</span>`) +
        (n.isNew ? `<span class="nt__new"><i></i>New</span>` : '') +
        `<span class="nt__pri pri-${n.pri}" title="${PRI[n.pri]} priority">${PRI_GLYPH[n.pri]}</span>` +
        `<div class="nt__plate"><img class="nt__thumb" src="${n.img || n.thumb}" alt=""><span class="nt__ent"><b>${esc(n.ent)}</b><span>${esc(n.entName)}</span></span>${n.more ? `<span class="nt__more">+${n.more}</span>` : ''}</div>` +
      `</div>` +
      `<div class="nt__body"><div class="nt__top"><span class="nt__title">${esc(n.title)}</span><span class="nt__date">${esc(n.date)}</span></div>` +
        `<div class="nt__tags">${n.tags.map((t) => `<span>${esc(t)}</span>`).join('')}</div><p class="nt__text">${esc(n.body)}</p></div>` +
      `<div class="nt__foot"><span class="nt__who"><span class="av">${initials(n.who)}</span>${esc(n.who)}</span>` +
        `<button class="nt__act" type="button" data-act="like" aria-pressed="${s.liked}" aria-label="Like">${icon('like')}<span class="count">${s.likes}</span></button>` +
        `<button class="nt__act" type="button" data-act="comment" aria-label="Comments">${icon('comment')}<span class="count">${n.comments}</span></button>` +
        `<button class="nt__act" type="button" data-act="save" aria-pressed="${s.saved}" aria-label="Save">${icon('save')}</button></div></article>`
  }
  function drawNotes(animate) {
    const match = (n) => ntFilter === 'all' || (ntFilter === 'critical' ? ['critical', 'high'].includes(n.pri) : ntFilter === 'mine' ? n.mine : n.kind === ntFilter)
    const list = D.NOTES.filter(match), track = $('#railNotes')
    const paint = () => {
      track.innerHTML = list.map(noteCard).join('')
      ;[...track.children].forEach((c, i) => c.style.setProperty('--i', i))
      track.scrollLeft = 0; edges(track.closest('.rail'))
      if (animate && !calm()) [...track.children].forEach((c, i) => c.animate([{ opacity: 0, transform: 'translateX(32px)' }, { opacity: 1, transform: 'none' }], { duration: 520, delay: i * 45, easing: EASE, fill: 'backwards' }))
    }
    if (animate && !calm() && track.children.length) {
      Promise.all([...track.children].map((c) => c.animate([{ opacity: 1 }, { opacity: 0, transform: 'translateX(-12px)' }], { duration: 150, easing: 'ease-in', fill: 'forwards' }).finished)).then(paint)
    } else paint()
  }
  const cnt = (f) => D.NOTES.filter((n) => f === 'all' || (f === 'critical' ? ['critical', 'high'].includes(n.pri) : f === 'mine' ? n.mine : n.kind === f)).length
  seg($('#ntSeg'), [['all', 'All', cnt('all')], ['critical', 'Urgent', cnt('critical')], ['animal', 'Animals', cnt('animal')], ['enclosure', 'Enclosures', cnt('enclosure')], ['mine', 'Mine', cnt('mine')]], 'all', (k) => { ntFilter = k; drawNotes(true) })
  $('#ntCount').innerHTML = `<b>${D.NOTES.filter((n) => n.isNew).length} new</b> since yesterday`
  drawNotes(false)
  /* reactions answer: the glyph dips and springs, a few sparks, the count rolls */
  $('#railNotes').addEventListener('click', (e) => {
    const b = e.target.closest('.nt__act'); if (!b) return
    e.stopPropagation()
    const id = b.closest('.nt').dataset.id, s = state[id]
    if (b.dataset.act === 'comment') return openDetail(b.closest('.nt'), 'note', id)
    if (b.dataset.act === 'like') { s.liked = !s.liked; s.likes += s.liked ? 1 : -1; const c = b.querySelector('.count'); c.textContent = s.likes; c.classList.remove('roll'); void c.offsetWidth; c.classList.add('roll') }
    if (b.dataset.act === 'save') { s.saved = !s.saved; toast(s.saved ? 'Saved to your notes' : 'Removed from saved') }
    const on = b.dataset.act === 'like' ? s.liked : s.saved
    b.setAttribute('aria-pressed', String(on))
    b.classList.remove('pop'); void b.offsetWidth; b.classList.add('pop')
    if (on && !calm()) for (let i = 0; i < 6; i++) { const sp = document.createElement('i'); sp.className = 'burst'; const a = i / 6 * Math.PI * 2; sp.style.setProperty('--bx', Math.cos(a) * 18 - 6 + 'px'); sp.style.setProperty('--by', Math.sin(a) * 18 + 'px'); b.append(sp); setTimeout(() => sp.remove(), 600) }
  })

  /* press-and-hold (or right-click): the card lifts, the page blurs, a menu */
  let holdT = 0, ctxCard = null, held = false
  function openCtx(card) {
    closeCtx(true)
    ctxCard = card; held = true
    const r = card.getBoundingClientRect(), n = D.NOTES.find((x) => x.id === card.dataset.id), s = state[n.id]
    const lift = card.cloneNode(true); lift.classList.add('ctx-lift'); lift.classList.remove('press')
    Object.assign(lift.style, { left: r.left + 'px', top: r.top + 'px', width: r.width + 'px', height: r.height + 'px', margin: 0 })
    document.body.append(lift)
    requestAnimationFrame(() => { lift.style.transform = 'scale(1.03)' })
    const menu = $('#ctxMenu')
    menu.innerHTML = [['reply', 'Reply'], ['medical', 'Raise medical case'], ['check', s.ack ? 'Mark unread' : 'Acknowledge'], ['share', 'Share'], ['save', s.saved ? 'Unsave' : 'Save']].map(([i, l]) => `<button type="button" role="menuitem" data-m="${l}">${esc(l)}${icon(i)}</button>`).join('')
    const mw = 250, right = r.right + 12 + mw < innerWidth
    const left = right ? r.right + 12 : Math.max(12, r.left - mw - 12)
    const top = Math.min(r.top, innerHeight - 250)
    Object.assign(menu.style, { left: left + 'px', top: top + 'px' })
    menu.style.setProperty('--ox', right ? '0' : '100%'); menu.style.setProperty('--oy', '0')
    body.classList.add('ctx-open')
    if (navigator.vibrate) navigator.vibrate(8)
    if (kbd()) menu.querySelector('button')?.focus()
  }
  function closeCtx(instant) {
    body.classList.remove('ctx-open')
    const lift = $('.ctx-lift'); if (lift) { if (instant) lift.remove(); else { lift.style.transform = 'scale(1)'; setTimeout(() => lift.remove(), 260) } }
    ctxCard = null
  }
  $('#railNotes').addEventListener('pointerdown', (e) => {
    const c = e.target.closest('.nt'); if (!c || e.target.closest('.nt__act') || e.button > 0) return
    held = false; clearTimeout(holdT)
    const x0 = e.clientX, y0 = e.clientY
    holdT = setTimeout(() => openCtx(c), 480)
    const cancel = (ev) => { if (!ev || Math.hypot(ev.clientX - x0, ev.clientY - y0) > 8) { clearTimeout(holdT); c.removeEventListener('pointermove', cancel) } }
    c.addEventListener('pointermove', cancel); c.addEventListener('pointerup', () => clearTimeout(holdT), { once: true }); c.addEventListener('pointercancel', () => clearTimeout(holdT), { once: true })
  })
  $('#railNotes').addEventListener('contextmenu', (e) => { const c = e.target.closest('.nt'); if (!c) return; e.preventDefault(); openCtx(c) })
  $('#railNotes').addEventListener('click', (e) => { if (held) { e.stopPropagation(); e.preventDefault(); held = false } }, true)
  $('#ctxVeil').addEventListener('click', () => closeCtx())
  $('#ctxMenu').addEventListener('click', (e) => {
    const b = e.target.closest('button'); if (!b || !ctxCard) return
    const id = ctxCard.dataset.id, s = state[id], m = b.dataset.m
    if (m === 'Acknowledge' || m === 'Mark unread') { s.ack = !s.ack; ctxCard.classList.toggle('is-ack', s.ack) }
    else if (m === 'Save' || m === 'Unsave') { s.saved = !s.saved; ctxCard.querySelector('[data-act=save]').setAttribute('aria-pressed', String(s.saved)) }
    toast(`${m}${m.startsWith('Raise') ? ' — mock' : ''}`)
    closeCtx()
  })

  /* ── rail edges ───────────────────────────────────────────────────────── */
  function edges(rail) { if (!rail) return; const t = rail.querySelector('.rail__track'); rail.classList.toggle('can-l', t.scrollLeft > 4); rail.classList.toggle('can-r', t.scrollLeft + t.clientWidth < t.scrollWidth - 4) }
  $$('.rail').forEach((r) => r.querySelector('.rail__track').addEventListener('scroll', () => edges(r), { passive: true }))

  /* ══ SITE REPORTS ═══════════════════════════════════════════════════════ */
  const ST = { critical: 'Critical', attention: 'Attention', info: 'Update', ok: 'Done' }
  const inF = (r, f) => f === 'all' || (f === 'attention' ? ['attention', 'critical'].includes(r.status) : r.status === f)
  let repFilter = 'all'
  function drawReports(animate) {
    const host = $('#repRows'), rows = D.REPORTS.filter((r) => inF(r, repFilter))
    const paint = () => {
      host.innerHTML = rows.map((r, i) => `<button class="row${animate ? ' enter' : ''}" type="button" data-open="report" data-id="${r.id}" style="--i:${i}"><span class="row__status st-${r.status}"><span class="dot"></span>${ST[r.status]}</span><span style="min-width:0"><span class="row__title">${esc(r.title)}</span><span class="row__meta">${esc(r.src)} · ${esc(r.time)}</span></span>${icon('chev')}</button>`).join('')
    }
    if (animate && !calm() && host.children.length) {
      const h0 = host.offsetHeight
      ;[...host.children].forEach((c) => c.classList.add('leave'))
      setTimeout(() => { paint(); const h1 = host.offsetHeight; host.animate([{ height: h0 + 'px' }, { height: h1 + 'px' }], { duration: 420, easing: EASE }) }, 170)
    } else paint()
  }
  seg($('#repSeg'), [['all', 'All', D.REPORTS.length], ['attention', 'Needs attention', D.REPORTS.filter((r) => inF(r, 'attention')).length], ['info', 'Updates', D.REPORTS.filter((r) => r.status === 'info').length], ['ok', 'Done', D.REPORTS.filter((r) => r.status === 'ok').length]], 'all', (k) => { repFilter = k; drawReports(true) })
  $('#repCount').innerHTML = `<b>${D.REPORTS.filter((r) => inF(r, 'attention')).length}</b> need attention`
  drawReports(false)

  /* ══ MODULES ════════════════════════════════════════════════════════════ */
  const KEY = 'antz-mock-home-v2'
  let home
  try { home = JSON.parse(localStorage.getItem(KEY)) } catch (_) {}
  if (!Array.isArray(home) || !home.length) home = D.DEFAULT_HOME.map((x) => ({ ...x }))
  const save = () => { try { localStorage.setItem(KEY, JSON.stringify(home)) } catch (_) {} }
  let uid = 0
  home.forEach((h) => { h.uid = h.uid || 'c' + (++uid); h.variant = h.variant || 'default' })
  const span = (size) => { const [w, h] = size.split('x').map(Number); return { w, h } }
  let COLS = 5
  const LIST_ITEMS = {
    medical: D.MEDICAL.cases.map((c) => [c.who, c.what, c.sev === 'critical']),
    pharmacy: D.PHARMACY.low.map((l) => [l[0], `${l[1]}% of reorder level`, true]),
    hospital: [['Bhalu', 'ICU 2 · respiratory', true], ['Big Bull', 'Night house · wound', false], ['Raja', 'Ward A · lameness', false]],
    lab: [['6 samples', 'results ready to read', false], ['CBC · Zara', 'awaiting 2 days', true], ['Faecal · Herd B', 'processing', false]],
    tasks: D.TASKS.filter((t) => t[2] !== 'done').slice(0, 3).map((t) => [t[1], t[0], t[2] === 'now']),
  }
  const fig = (n, l, cls = '') => `<span class="fig ${cls}"><b>${n}</b><small>${esc(l)}</small></span>`
  function viz(m, id, w, h, variant) {
    if (variant === 'compact' || m.viz === 'compact') return fig(m.stat[0], m.stat[1])
    if (variant === 'list') return `<div class="cases">${(LIST_ITEMS[id] || []).slice(0, h >= 2 ? 3 : 1).map((i) => `<div class="case"><span class="dot" style="opacity:${i[2] ? 1 : .45}"></span><span><b>${esc(i[0])}</b> · ${esc(i[1])}</span><em></em></div>`).join('')}</div>`
    switch (m.viz) {
      case 'severity': {
        const tot = D.MEDICAL.split.reduce((a, s) => a + s.n, 0)
        const bar = `<div class="sev">${D.MEDICAL.split.map((s) => `<i class="k-${s.k}" style="flex:${s.n}"></i>`).join('')}</div>`
        const key = `<div class="sev-key">${D.MEDICAL.split.map((s) => `<span><i style="opacity:${s.k === 'critical' ? 1 : s.k === 'serious' ? .6 : .32}"></i>${s.n} ${s.k}</span>`).join('')}</div>`
        const head = `<div class="figs" style="margin-top:0">${fig(tot, 'open cases')}${fig(D.MEDICAL.split[0].n, 'critical', 'fig--alert')}</div>`
        if (h < 2) return head + bar
        return head + bar + key + `<div class="cases">${D.MEDICAL.cases.slice(0, 3).map((c) => `<div class="case"><span class="dot" style="opacity:${c.sev === 'critical' ? 1 : .55}"></span><span><b>${esc(c.who)}</b> · ${esc(c.what)}</span><em>${esc(c.where)}</em></div>`).join('')}</div>`
      }
      case 'collection': {
        const imgs = D.SPECIES.slice(0, 3).map((s) => `<img src="${s.img}" alt="" loading="lazy">`).join('')
        const cls = `<div class="cls">${D.CLASSES.map(([k, n]) => `<div><span>${k}</span><i><u style="width:${Math.round(n / 92 * 100)}%"></u></i><em>${n}</em></div>`).join('')}</div>`
        const figs = `<div class="figs" style="margin-top:0">${fig(m.stat[0], m.stat[1])}${fig(m.stat2[0], m.stat2[1])}</div>`
        if (w >= 3 && h >= 2) return `<div class="coll"><div class="coll__mosaic">${imgs}</div><div class="coll__side">${figs}${cls}</div></div>`
        return h >= 2 ? figs + cls : figs
      }
      case 'space': {
        const occ = D.HOSPITAL.beds.filter(Boolean).length, free = D.HOSPITAL.beds.length - occ
        const figs = `<div class="figs" style="margin-top:0">${fig(occ, 'occupied')}${fig(free, 'available')}</div>`
        if (h < 2) return figs
        return figs + `<div class="beds" aria-label="${occ} beds occupied, ${free} free">${D.HOSPITAL.beds.map((b) => `<i class="${b ? '' : 'free'}"></i>`).join('')}</div>` + (w >= 2 ? `<div class="wards">${D.HOSPITAL.wards.map(([n, o, c]) => `<div><span>${n}</span><b>${o} / ${c}</b></div>`).join('')}</div>` : '')
      }
      case 'inventory': {
        const figs = `<div class="figs" style="margin-top:0">${fig(m.stat[0], m.stat[1])}${fig(m.stat2[0], m.stat2[1], 'fig--alert')}</div>`
        if (w < 2) return figs
        return figs + `<div class="inv">${D.PHARMACY.low.slice(0, h >= 2 ? 3 : 1).map(([k, p]) => `<div><span>${esc(k)}</span><i><u style="width:${p}%"></u></i><em>${p}%</em></div>`).join('')}</div>`
      }
      case 'pipeline':
        if (w < 2) return fig(m.stat[0], m.stat[1])
        return `<div class="pipe">${D.LAB.map(([k, n], i) => `<div class="${i <= 2 ? 'on' : ''}"><b>${n}</b><small>${k}</small></div>`).join('')}</div>`
      case 'agenda':
        if (h < 2) return `<div class="figs">${fig(m.stat2[0], m.stat2[1], 'fig--alert')}${w >= 2 ? fig(m.stat[0], m.stat[1]) : ''}</div>`
        return fig(m.stat2[0], m.stat2[1], 'fig--s') + `<div class="agenda">${D.TASKS.map(([t, l, s]) => `<div class="${s}"><em>${t}</em><span>${esc(l)}</span></div>`).join('')}</div>`
      case 'progress':
        return `<div class="prog">${fig(`${m.stat2[0]}<span style="font-size:15px;opacity:.8;font-weight:600"> / ${m.stat[0]}</span>`, 'feeds done today')}<i><u style="width:${Math.round(m.stat2[0] / m.stat[0] * 100)}%"></u></i></div>`
      default:
        return `<div class="figs">${fig(m.stat[0], m.stat[1])}${m.stat2 && w >= 2 ? fig(m.stat2[0], m.stat2[1]) : ''}</div>`
    }
  }
  function card(item, { cols = COLS, preview = false, k = 0 } = {}) {
    const m = D.MODULES[item.id], s = span(item.size), w = Math.min(s.w, cols), h = s.h
    const el = document.createElement('div')
    el.className = 'mod press' + (item.variant === 'compact' || m.viz === 'compact' ? ' mod--compact' : '')
    el.tabIndex = preview ? -1 : 0
    el.setAttribute('role', preview ? 'img' : 'button')
    Object.assign(el.dataset, { uid: item.uid || '', id: item.id, level: m.level, open: 'module', w, h })
    el.style.cssText = `grid-column: span ${w}; grid-row: span ${h}; --g: ${g(item.id)}; --k: ${k}`
    el.setAttribute('aria-label', `${m.name}: ${m.stat[0]} ${m.stat[1]}`)
    el.innerHTML = `<div class="mod__head"><span class="mod__glyph">${icon(m.icon)}</span><span class="mod__name">${esc(m.name)}</span><span class="mod__go">${icon('chev')}</span></div>` +
      `<div class="mod__body">${viz(m, item.id, w, h, item.variant)}</div>` +
      (preview ? '' : `<div class="mod__edit"><button class="mod__remove" type="button" aria-label="Remove ${esc(m.name)}">${icon('minus')}</button>` + (m.sizes.length > 1 ? `<button class="mod__size" type="button" aria-label="Change size of ${esc(m.name)}">${item.size.replace('x', '×')}</button>` : '') + `</div>`)
    return el
  }
  const grid = $('#mgrid')
  const drawGrid = () => grid.replaceChildren(...home.map((it, k) => card(it, { k })))
  function layoutGrid() {
    const gw = grid.clientWidth
    const cols = gw < 520 ? 2 : gw < 700 ? 3 : gw < 860 ? 4 : gw < 1420 ? 5 : 6
    grid.style.setProperty('--cols', cols)
    grid.style.setProperty('--row', Math.round(Math.min(176, Math.max(138, (gw - 16 * (cols - 1)) / cols * .86))) + 'px')
    if (cols !== COLS) { COLS = cols; drawGrid() }
  }

  /* ══ VARIANT B ══════════════════════════════════════════════════════════ */
  const today = $('#today')
  function applySplit() {
    const want = VARIANT === 'b' && $('.page').clientWidth >= 1040
    if (want === body.classList.contains('split')) return
    body.classList.toggle('split', want)
    const rep = $('#secReports')
    if (want) {
      today.innerHTML = `<div class="today__box"><h3>Due today <small>${D.TASKS.filter((t) => t[2] !== 'done').length} left</small></h3><div class="agenda" style="margin-top:0">${D.TASKS.map(([t, l, s]) => `<div class="${s}"><em>${t}</em><span>${esc(l)}</span></div>`).join('')}</div></div><div class="today__box" id="todayActs"></div>`
      today.prepend(rep); rep.classList.add('is-shown'); drawTodayActions()
    } else { $('#stream').insertBefore(rep, $('#secModules')); today.innerHTML = '' }
    requestAnimationFrame(() => $('#repSeg')._place?.())
  }
  const CTX_G = { Species: 'species', Medical: 'medical', Pharmacy: 'pharmacy', Hospital: 'hospital' }
  function drawTodayActions() {
    const box = $('#todayActs'); if (!box) return
    const ctx = currentContext(), gid = ctx === 'Species' ? 'animal' : 'clinical'
    if (box.dataset.g === gid) return
    box.dataset.g = gid
    const gp = D.QA_GROUPS.find((x) => x.id === gid)
    box.innerHTML = `<h3>Actions <small>for ${ctx}</small></h3><div class="qa-cat" data-tone="${gid}" style="padding:0"><div class="qa-chips">${D.QA_ACTIONS.filter((a) => a.group === gid).map((a, i) => chip(a, i)).join('')}</div></div>`
  }

  function relayout() {
    navMode(); measureHeader(); applySplit(); layoutGrid(); sizeDeck(); paintDeck()
    $$('.rail').forEach(edges); $$('.seg').forEach((s) => s._place?.())
    onScroll()
  }
  addEventListener('resize', () => requestAnimationFrame(relayout))

  /* ══ DETAIL · the photo flies; the page rises ═══════════════════════════ */
  const detail = $('#detail'), dc = $('#detailContent')
  let opener = null
  const bar = (t) => `<div class="detail__bar"><button class="icon-btn" type="button" data-close aria-label="Back">${icon('back')}</button><b>${esc(t)}</b></div>`
  const rise = (html) => `<div class="detail__rise">${html}</div>`
  function tpl(kind, id) {
    if (kind === 'species') {
      const s = D.SPECIES.find((x) => x.id === id)
      return { img: s.img, html: bar(s.name) + `<div class="detail__hero"><img src="${s.img}" alt="" data-hero></div><div class="detail__body">` + rise(
        `<div class="detail__kicker">${esc(s.species)} · <i style="font-weight:500;text-transform:none;letter-spacing:0">${esc(s.sci)}</i></div><h1 class="detail__title" style="--j:1">${esc(s.name)}</h1>` +
        `<p class="detail__lead" style="--j:2">${esc(s.status)} · ${esc(s.meta)}. Housed at ${esc(s.enclosure)}; primary keeper ${esc(s.keeper)}.</p>` +
        `<div class="facts" style="--j:3"><div><small>Enclosure</small><b>${esc(s.enclosure)}</b></div><div><small>Keeper</small><b>${esc(s.keeper)}</b></div><div><small>Status</small><b class="tone-${s.tone}">${esc(s.status)}</b></div><div><small>Age / count</small><b>${esc(s.meta)}</b></div></div>` +
        `<h3 style="--j:4">Recent activity</h3><div class="tl" style="--j:5"><div><em>Today</em>Weighed · steady</div><div><em>Yesterday</em>Enrichment · scatter feed, engaged 40 min</div><div><em>3 days ago</em>Vet check · no concerns</div></div>` +
        `<div class="detail__actions" style="--j:6"><button class="btn btn--primary" type="button" data-toast="Mock: Add note">${icon('plus')}Add note</button><button class="btn btn--tonal" type="button" data-toast="Mock: Medical record">${icon('medical')}Medical record</button><button class="btn btn--tonal" type="button" data-toast="Mock: Transfer">${icon('transfer')}Transfer</button></div>`) + `</div>` }
    }
    if (kind === 'ann') {
      const a = D.ANNOUNCEMENTS.find((x) => x.id === id)
      return { img: a.img, html: bar('Announcement') + `<div class="detail__hero"><img src="${a.img}" alt="" data-hero></div><div class="detail__body">` + rise(
        `<div class="detail__kicker">${esc(a.cat)}</div><h1 class="detail__title" style="--j:1">${esc(a.title)}</h1><p class="detail__lead" style="--j:2">${esc(a.body)}</p>` +
        `<p class="detail__lead" style="--j:3">Questions go to the ${esc(a.cat.toLowerCase())} desk. This notice stays pinned for seven days.</p>` +
        `<p style="--j:4;color:var(--ink-3);font-size:13px">${esc(a.date)} · ${esc(a.cat)}</p><div class="detail__actions" style="--j:5"><button class="btn btn--primary" type="button" data-toast="Mock: acknowledged">${icon('check')}Acknowledge</button></div>`) + `</div>` }
    }
    if (kind === 'note') {
      const n = D.NOTES.find((x) => x.id === id)
      return { img: n.img, html: bar('Note') + (n.img ? `<div class="detail__hero"><img src="${n.img}" alt="" data-hero style="object-position:50% 35%"></div>` : '') + `<div class="detail__body">` + rise(
        `<div class="detail__kicker pri-${n.pri}">${PRI[n.pri]} priority · ${esc(n.ago)}</div><h1 class="detail__title" style="--j:1">${esc(n.title)}</h1><p class="detail__lead" style="--j:2">${esc(n.body)}</p>` +
        `<div class="facts" style="--j:3"><div><small>${n.kind === 'enclosure' ? 'Enclosure' : 'Animal'}</small><b>${esc(n.entName)}</b></div><div><small>${esc(n.ent.split(' : ')[0])}</small><b>${esc(n.ent.split(' : ')[1])}</b></div><div><small>By</small><b>${esc(n.who)}</b></div></div>` +
        `<h3 style="--j:4">Comments · ${n.comments}</h3><div class="tl" style="--j:5"><div><em>12 min</em>Dr. Meera Nair · On my way, keep him in the night house.</div><div><em>8 min</em>Ramesh Patil · Done. Bleeding has slowed.</div></div>` +
        `<div class="detail__actions" style="--j:6"><button class="btn btn--primary" type="button" data-toast="Mock: reply">${icon('reply')}Reply</button><button class="btn btn--tonal" type="button" data-toast="Mock: case raised">${icon('medical')}Raise medical case</button></div>`) + `</div>` }
    }
    if (kind === 'report') {
      const r = D.REPORTS.find((x) => x.id === id), m = D.MODULES[r.module] || D.MODULES.reports
      return { html: bar('Site report') + `<div class="detail__body">` + rise(
        `<div class="detail__kicker st-${r.status}">${ST[r.status]} · ${esc(r.src)}</div><h1 class="detail__title" style="--j:1">${esc(r.title)}</h1>` +
        `<p class="detail__lead" style="--j:2">Raised ${esc(r.time)}. The summary sits here; the full record, history and actions stay inside ${esc(m.name)}.</p>` +
        `<div class="facts" style="--j:3"><div><small>Source</small><b>${esc(r.src)}</b></div><div><small>Status</small><b>${ST[r.status]}</b></div><div><small>Owner</small><b>Dr. Meera Nair</b></div></div>` +
        `<div class="detail__actions" style="--j:4"><button class="btn btn--primary" type="button" data-toast="Would open ${esc(m.name)} — detail lives inside the module">Open in ${esc(m.name)}</button></div>`) + `</div>` }
    }
    const m = D.MODULES[id]
    return { html: bar(m.name) + `<div class="detail__hero detail__hero--g" style="--g:${g(id)}"><div style="display:flex;flex-direction:column;gap:14px"><span class="mod__glyph" style="width:40px;height:40px">${icon(m.icon)}</span><div class="figs" style="margin-top:0">${fig(m.stat[0], m.stat[1])}${m.stat2 ? fig(m.stat2[0], m.stat2[1], 'fig--alert') : ''}</div></div></div>` +
      `<div class="detail__body">` + rise(`<div class="detail__kicker">Module preview</div><h1 class="detail__title" style="--j:1">${esc(m.name)}</h1><p class="detail__lead" style="--j:2">Home shows the glance. The records, filters and workflows open inside the ${esc(m.name)} module itself.</p>` +
      (LIST_ITEMS[id] ? `<h3 style="--j:3">Needs attention</h3><div class="tl" style="--j:4">${LIST_ITEMS[id].map((i) => `<div><em>${i[2] ? 'Now' : 'Today'}</em><span><b>${esc(i[0])}</b> · ${esc(i[1])}</span></div>`).join('')}</div>` : '') +
      `<div class="detail__actions" style="--j:5"><button class="btn btn--primary" type="button" data-toast="Would open the live ${esc(m.name)} module">Open ${esc(m.name)}</button></div>`) + `</div>` }
  }
  function flyImage(fromImg, toImg, dur, back) {
    const a = fromImg.getBoundingClientRect(), b = toImg.getBoundingClientRect()
    const f = document.createElement('img'); f.className = 'fly'; f.src = fromImg.currentSrc || fromImg.src
    f.style.objectPosition = getComputedStyle(fromImg).objectPosition
    Object.assign(f.style, { left: b.left + 'px', top: b.top + 'px', width: b.width + 'px', height: b.height + 'px', borderRadius: '12px' })
    document.body.append(f)
    const from = `translate(${a.left - b.left}px, ${a.top - b.top}px) scale(${a.width / b.width}, ${a.height / b.height})`
    const kf = [{ transform: from, borderRadius: '12px' }, { transform: 'none', borderRadius: '12px' }]
    return f.animate(back ? kf.reverse() : kf, { duration: dur, easing: EASE, fill: 'forwards' }).finished.then(() => f.remove())
  }
  function openDetail(src, kind, id) {
    closeSearch(); closeQA(); closeCtx(true)
    opener = src
    const t = tpl(kind, id)
    dc.innerHTML = t.html
    detail.scrollTop = 0; detail.classList.add('is-open'); detail.classList.remove('is-landed')
    document.documentElement.style.overflow = 'hidden'
    const land = () => { detail.classList.add('is-landed'); if (kbd()) detail.querySelector('[data-close]')?.focus({ preventScroll: true }) }
    if (calm()) { detail.animate([{ opacity: 0 }, { opacity: 1 }], { duration: 160 }).finished.then(land); return }
    const srcImg = src.querySelector('[data-fly]'), hero = detail.querySelector('[data-hero]')
    if (srcImg && hero) {
      /* the photo carries across: ground fades in, the image flies, text rises */
      hero.style.visibility = 'hidden'
      detail.animate([{ opacity: 0 }, { opacity: 1 }], { duration: 260, easing: 'ease-out' })
      flyImage(srcImg, hero, 520).then(() => { hero.style.visibility = '' })
      setTimeout(land, 240)
    } else {
      const to = detail.getBoundingClientRect(), from = src.getBoundingClientRect()
      detail.animate([{ transform: `translate(${from.left - to.left}px, ${from.top - to.top}px) scale(${from.width / to.width}, ${from.height / to.height})`, borderRadius: '12px', opacity: .5 }, { transform: 'none', borderRadius: '0px', opacity: 1 }], { duration: 480, easing: EASE }).finished.then(land)
    }
  }
  function closeDetail() {
    if (!detail.classList.contains('is-open')) return
    document.documentElement.style.overflow = ''
    const src = opener && opener.isConnected && opener.getBoundingClientRect().width ? opener : null
    const fin = () => { detail.classList.remove('is-open', 'is-landed'); detail.style.opacity = ''; if (src && kbd()) src.focus({ preventScroll: true }) }
    if (!src || calm()) { detail.animate([{ opacity: 1 }, { opacity: 0 }], { duration: 180 }).finished.then(fin); return }
    const srcImg = src.querySelector('[data-fly]'), hero = detail.querySelector('[data-hero]')
    if (srcImg && hero && hero.getBoundingClientRect().bottom > 0) {
      detail.classList.remove('is-landed')
      flyImage(srcImg, hero, 440, true)
      hero.style.visibility = 'hidden'
      detail.animate([{ opacity: 1 }, { opacity: 0 }], { duration: 300, delay: 60, easing: 'ease-in', fill: 'forwards' }).finished.then(fin)
    } else {
      detail.classList.remove('is-landed')
      const to = detail.getBoundingClientRect(), from = src.getBoundingClientRect()
      detail.animate([{ transform: 'none', borderRadius: '0px', opacity: 1 }, { transform: `translate(${from.left - to.left}px, ${from.top - to.top}px) scale(${from.width / to.width}, ${from.height / to.height})`, borderRadius: '12px', opacity: .3 }], { duration: 400, easing: EASE, delay: 60 }).finished.then(fin)
    }
  }
  detail.addEventListener('click', (e) => { if (e.target.closest('[data-close]')) closeDetail() })
  document.addEventListener('click', (e) => {
    if (body.classList.contains('is-edit') || e.defaultPrevented) return
    const o = e.target.closest('[data-open]')
    if (!o || o.closest('.detail') || o.closest('.deck') || e.target.closest('[data-toast]') || e.target.closest('.nt__act')) return
    openDetail(o, o.dataset.open, o.dataset.id)
  })
  document.addEventListener('keydown', (e) => {
    if ((e.key === 'Enter' || e.key === ' ') && e.target.matches('.mod[role=button], .nt') && !body.classList.contains('is-edit')) { e.preventDefault(); openDetail(e.target, e.target.dataset.open, e.target.dataset.id) }
  })

  /* ══ SEARCH ═════════════════════════════════════════════════════════════ */
  const q = $('#q'), ss = $('#ss')
  const INDEX = [
    ...D.SPECIES.map((s) => ({ g: 'Animals', t: `${s.name} — ${s.species}`, s: s.enclosure, img: s.img, open: ['species', s.id] })),
    ...[...new Set(D.SPECIES.map((s) => s.species))].map((sp) => ({ g: 'Species', t: sp, s: `${D.SPECIES.filter((s) => s.species === sp).length} on your list`, ico: 'species', grad: 'species', open: ['species', D.SPECIES.find((s) => s.species === sp).id] })),
    ...Object.entries(D.MODULES).map(([id, m]) => ({ g: 'Modules', t: m.name, s: `${m.stat[0]} ${m.stat[1]}`, ico: m.icon, grad: id, open: ['module', id] })),
    ...D.REPORTS.map((r) => ({ g: 'Reports', t: r.title, s: `${r.src} · ${r.time}`, ico: 'reports', grad: 'reports', open: ['report', r.id] })),
    ...Object.entries(D.ACTIONS).flatMap(([ctx, list]) => list.map(([l, i]) => ({ g: 'Actions', t: l, s: ctx, ico: i, grad: CTX_G[ctx], act: true }))),
  ]
  const ORDER = ['Animals', 'Species', 'Modules', 'Reports', 'Actions']
  let hits = [], active = -1
  const mark = (t, qq) => { const i = t.toLowerCase().indexOf(qq); return i < 0 ? esc(t) : esc(t.slice(0, i)) + '<mark>' + esc(t.slice(i, i + qq.length)) + '</mark>' + esc(t.slice(i + qq.length)) }
  const item = (h, i, qq) => `<button class="ss__item" type="button" role="option" data-hit="${i}"><span class="ss__thumb" style="${h.grad ? `--g:${g(h.grad)}` : ''}">${h.img ? `<img src="${h.img}" alt="">` : icon(h.ico || 'search')}</span><span class="ss__t"><b>${qq ? mark(h.t, qq) : esc(h.t)}</b><small>${esc(h.s)}</small></span></button>`
  function placeSearch() { const r = $('#searchBox').getBoundingClientRect(); ss.style.setProperty('--ss-top', (r.bottom + 8) + 'px'); ss.style.left = r.left + 'px'; ss.style.width = Math.min(760, Math.max(r.width, 360), innerWidth - r.left - 16) + 'px' }
  function drawSearch() {
    const qq = q.value.trim().toLowerCase()
    if (!qq) {
      hits = INDEX.filter((x) => x.g === 'Modules').slice(0, 4)
      ss.innerHTML = `<div class="ss__group in" style="--i:0"><div class="ss__label">Recent searches</div><div class="ss__recent">${D.RECENT_SEARCHES.map((r) => `<button class="chip" type="button" data-recent="${esc(r)}">${icon('clock')}${esc(r)}</button>`).join('')}</div></div><div class="ss__group in" style="--i:1"><div class="ss__label">Jump to</div>${hits.map((h, i) => item(h, i, '')).join('')}</div>`
    } else {
      const found = INDEX.filter((x) => (x.t + ' ' + x.s).toLowerCase().includes(qq))
      const animal = found.find((x) => x.g === 'Animals')
      if (animal) { const nm = animal.t.split(' — ')[0]; found.push({ g: 'Modules', t: 'Medical', s: `${nm}’s medical records`, ico: 'medical', grad: 'medical', open: ['module', 'medical'] }, { g: 'Reports', t: 'Recent Medical Reports', s: `${nm} · 2 this month`, ico: 'reports', grad: 'reports', open: ['report', 'r1'] }, { g: 'Actions', t: 'Create Medical Case', s: `for ${nm}`, ico: 'medical', grad: 'medical', act: true }) }
      hits = ORDER.flatMap((gg) => found.filter((x) => x.g === gg).slice(0, gg === 'Actions' ? 3 : 4))
      let gi = 0
      ss.innerHTML = hits.length ? ORDER.map((gg) => { const hs = hits.filter((h) => h.g === gg); return hs.length ? `<div class="ss__group in" style="--i:${gi++}"><div class="ss__label">${gg}</div>${hs.map((h) => item(h, hits.indexOf(h), qq)).join('')}</div>` : '' }).join('') : `<div class="ss__empty">Nothing matches “${esc(q.value)}”. Try an animal, a module or an action.</div>`
    }
    active = -1
  }
  function openSearch() { if (body.classList.contains('ss-open')) return; placeSearch(); drawSearch(); body.classList.add('ss-open'); q.setAttribute('aria-expanded', 'true') }
  function closeSearch() { body.classList.remove('ss-open'); q.setAttribute('aria-expanded', 'false') }
  function choose(h, el) { closeSearch(); q.blur(); if (h.act) return toast(`Mock: ${h.t} would open`); openDetail(el || $('#searchBox'), h.open[0], h.open[1]) }
  q.addEventListener('focus', openSearch)
  q.addEventListener('input', () => { openSearch(); drawSearch() })
  q.addEventListener('keydown', (e) => {
    const items = $$('.ss__item', ss)
    if (e.key === 'ArrowDown' || e.key === 'ArrowUp') { e.preventDefault(); active = (active + (e.key === 'ArrowDown' ? 1 : -1) + items.length) % items.length; items.forEach((x, i) => x.classList.toggle('is-active', i === active)); items[active]?.scrollIntoView({ block: 'nearest' }) }
    else if (e.key === 'Enter' && items.length) { const el = items[Math.max(0, active)]; choose(hits[+el.dataset.hit], el) }
    else if (e.key === 'Escape') { closeSearch(); q.blur() }
  })
  ss.addEventListener('click', (e) => { const r = e.target.closest('[data-recent]'); if (r) { q.value = r.dataset.recent; drawSearch(); q.focus(); return } const it = e.target.closest('.ss__item'); if (it) choose(hits[+it.dataset.hit], it) })
  $('#ssVeil').addEventListener('click', () => { closeSearch(); q.blur() })
  document.addEventListener('keydown', (e) => {
    if ((e.metaKey || e.ctrlKey) && e.key.toLowerCase() === 'k') { e.preventDefault(); scrollTo({ top: 0, behavior: calm() ? 'auto' : 'smooth' }); q.focus() }
    if (e.key === 'Escape') { if (body.classList.contains('ctx-open')) closeCtx(); else if (body.classList.contains('sheet-open')) closeSheet(); else if (detail.classList.contains('is-open')) closeDetail(); else if (body.classList.contains('qa-open')) closeQA() }
  })

  /* ══ QUICK ACTIONS · the live panel ════════════════════════════════════
     Built once: the field, "Continue where you left off", the sixteen chips
     in their four tinted groups, and the foot. Typing narrows the chips;
     Enter carries the query to the Home search. */
  const CTX_OF = { species: 'Species', medical: 'Medical', pharmacy: 'Pharmacy', hospital: 'Hospital' }
  function currentContext() {
    const mid = innerHeight / 2
    const inView = (el) => { const r = el.getBoundingClientRect(); return r.top < mid && r.bottom > mid * .4 }
    if (inView($('#secSpecies'))) return 'Species'
    let best = null, bd = 1e9
    $$('.mod').forEach((m) => { const c = CTX_OF[m.dataset.id]; if (!c) return; const r = m.getBoundingClientRect(); if (r.bottom < 0 || r.top > innerHeight) return; const d = Math.abs(r.top + r.height / 2 - mid); if (d < bd) { bd = d; best = c } })
    return best || 'Medical'
  }
  const chip = (a, i) => `<button class="qa-chip" type="button" style="--i:${i}" data-label="${esc(a.label)}" data-toast="Mock: ${esc(a.label)} would open"><img src="${a.icon}" alt="">${esc(a.label)}</button>`
  const cat = (gp) => `<div class="qa-cat" data-tone="${gp.id}" data-g="${gp.id}"><h3 class="qa-cat__t">${esc(gp.name)}</h3><div class="qa-chips">${D.QA_ACTIONS.filter((a) => a.group === gp.id).map((a) => chip(a, D.QA_ACTIONS.indexOf(a))).join('')}</div></div>`
  $('#qaPalette').innerHTML =
    `<label class="qa-search">${icon('search')}<input id="qaQ" type="search" placeholder="Search" autocomplete="off" aria-label="Search actions"></label>` +
    `<div class="qa-mid"><h3 class="qa-cont__t">Continue where you left off <span class="qa-cont__n">${D.QA_RESUME.length}</span></h3>` +
    `<div class="qa-cont">${D.QA_RESUME.map((r, i) => `<button class="qa-item" type="button" style="--i:${i}" data-toast="Mock: resume ${esc(r.action)} · ${esc(r.where)}"><img src="${r.icon}" alt=""><span class="qa-item__b"><b>${esc(r.action)}</b><span>${esc(r.where)}</span></span><span class="qa-item__s"><span class="qa-item__k k-${r.kind}">${esc(r.label)}</span><span class="qa-item__a">${esc(r.ago)}</span></span></button>`).join('')}</div>` +
    `<div class="qa-cats"><div class="qa-col">${D.QA_GROUPS.filter((x) => x.column === 0).map(cat).join('')}</div><div class="qa-col">${D.QA_GROUPS.filter((x) => x.column === 1).map(cat).join('')}</div></div>` +
    `<p class="qa-none" hidden>No action matches “<b></b>”. Press Enter to search everything.</p></div>` +
    `<div class="qa-foot"><button type="button" data-foot="search">${icon('search')}Search everything</button><button type="button" data-foot="scan" data-toast="Scanner would open">${icon('scan')}Scan a tag</button></div>`
  const qaQ = $('#qaQ')
  qaQ.addEventListener('input', () => {
    const v = qaQ.value.trim().toLowerCase()
    let any = false
    $$('.qa-chip', $('#qaPalette')).forEach((c) => { const on = !v || c.dataset.label.toLowerCase().includes(v); c.hidden = !on; any = any || on })
    $$('.qa-cat', $('#qaPalette')).forEach((c) => { c.hidden = !!v && !c.querySelector('.qa-chip:not([hidden])') })
    $('.qa-cont__t').hidden = $('.qa-cont').hidden = !!v
    const none = $('.qa-none'); none.hidden = any; none.querySelector('b').textContent = qaQ.value
  })
  qaQ.addEventListener('keydown', (e) => { if (e.key === 'Enter') { const v = qaQ.value; closeQA(); scrollTo({ top: 0 }); q.value = v; q.focus(); drawSearch() } })
  function openQA() {
    body.classList.add('qa-open'); $('#qaBtn').setAttribute('aria-expanded', 'true'); $('#fab').classList.remove('is-compact')
    qaQ.value = ''; qaQ.dispatchEvent(new Event('input'))
    if (kbd()) setTimeout(() => qaQ.focus(), 200)
  }
  function closeQA() { if (!body.classList.contains('qa-open')) return; body.classList.remove('qa-open'); $('#qaBtn').setAttribute('aria-expanded', 'false') }
  $('#qaBtn').addEventListener('click', () => body.classList.contains('qa-open') ? closeQA() : openQA())
  $('#qaVeil').addEventListener('click', closeQA)
  $('#qaPalette').addEventListener('click', (e) => {
    if (e.target.closest('[data-foot="search"]')) { closeQA(); scrollTo({ top: 0 }); q.focus(); return }
    if (e.target.closest('.qa-chip, .qa-item, [data-foot="scan"]')) closeQA()
  })
  let ctxT = 0
  addEventListener('scroll', () => { clearTimeout(ctxT); ctxT = setTimeout(drawTodayActions, 200) }, { passive: true })

  /* ══ EDIT HOME ══════════════════════════════════════════════════════════ */
  function flip(mutate) {
    const before = new Map($$('.mod', grid).map((el) => [el.dataset.uid, el.getBoundingClientRect()]))
    mutate()
    if (calm()) return
    $$('.mod', grid).forEach((el) => {
      const a = before.get(el.dataset.uid); if (!a || el.classList.contains('is-placeholder')) return
      const b = el.getBoundingClientRect(), dx = a.left - b.left, dy = a.top - b.top
      if (Math.abs(dx) + Math.abs(dy) < 1) return
      el.animate([{ transform: `translate(${dx}px, ${dy}px)` }, { transform: 'none' }], { duration: 420, easing: EASE, composite: 'add' })
    })
  }
  function setEdit(on) { body.classList.toggle('is-edit', on); if (!on) save() }
  $('#editBtn').addEventListener('click', () => setEdit(true))
  $('#doneBtn').addEventListener('click', () => { setEdit(false); toast('Home saved') })
  $('#restoreBtn').addEventListener('click', () => { flip(() => { home = D.DEFAULT_HOME.map((x) => ({ ...x, uid: 'c' + (++uid), variant: 'default' })); drawGrid() }); save(); toast('Default Home restored') })
  grid.addEventListener('click', (e) => {
    if (!body.classList.contains('is-edit')) return
    const el = e.target.closest('.mod'); if (!el) return
    const it = home.find((h) => h.uid === el.dataset.uid)
    if (e.target.closest('.mod__remove')) {
      const go = () => flip(() => { home = home.filter((h) => h !== it); el.remove() })
      if (calm()) go(); else el.animate([{ opacity: 1, transform: 'scale(1)' }, { opacity: 0, transform: 'scale(.8)' }], { duration: 220, easing: 'ease-in', fill: 'forwards' }).finished.then(go)
      toast(`${D.MODULES[it.id].name} removed`)
    } else if (e.target.closest('.mod__size')) {
      const sizes = D.MODULES[it.id].sizes
      it.size = sizes[(sizes.indexOf(it.size) + 1) % sizes.length]
      flip(() => el.replaceWith(card(it)))
    }
  })
  let drag = null
  grid.addEventListener('pointerdown', (e) => {
    if (!body.classList.contains('is-edit') || e.button > 0 || e.target.closest('button')) return
    const el = e.target.closest('.mod'); if (!el) return
    drag = { el, x0: e.clientX, y0: e.clientY, on: false, pid: e.pointerId }
    el.setPointerCapture(e.pointerId)
  })
  grid.addEventListener('pointermove', (e) => {
    if (!drag || e.pointerId !== drag.pid) return
    if (!drag.on) {
      if (Math.hypot(e.clientX - drag.x0, e.clientY - drag.y0) < 6) return
      const r = drag.el.getBoundingClientRect()
      drag.on = true; drag.dx = e.clientX - r.left; drag.dy = e.clientY - r.top
      const gh = drag.el.cloneNode(true); gh.classList.add('is-ghost')
      Object.assign(gh.style, { left: r.left + 'px', top: r.top + 'px', width: r.width + 'px', height: r.height + 'px', gridColumn: '', gridRow: '' })
      document.body.append(gh); drag.ghost = gh
      drag.el.classList.add('is-placeholder')
      autoScroll()
    }
    drag.py = e.clientY
    drag.ghost.style.left = (e.clientX - drag.dx) + 'px'; drag.ghost.style.top = (e.clientY - drag.dy) + 'px'
    const over = document.elementFromPoint(e.clientX, e.clientY)?.closest('.mod')
    if (over && over !== drag.el && over.parentElement === grid && over !== drag.last) {
      drag.last = over
      const r = over.getBoundingClientRect()
      flip(() => grid.insertBefore(drag.el, e.clientX > r.left + r.width / 2 ? over.nextSibling : over))
    } else if (!over) drag.last = null
  })
  function autoScroll() { if (!drag || !drag.on) return; const y = drag.py ?? 0; if (y < 110) scrollBy(0, -10); else if (y > innerHeight - 110) scrollBy(0, 10); requestAnimationFrame(autoScroll) }
  const endDrag = () => {
    if (!drag) return
    const d = drag; drag = null
    if (!d.on) return
    const r = d.el.getBoundingClientRect()
    const fin = () => { d.ghost.remove(); d.el.classList.remove('is-placeholder'); home = $$('.mod', grid).map((el) => home.find((h) => h.uid === el.dataset.uid)); save() }
    if (calm()) return fin()
    d.ghost.animate([{ left: d.ghost.style.left, top: d.ghost.style.top, transform: 'scale(1.04) rotate(-.6deg)' }, { left: r.left + 'px', top: r.top + 'px', transform: 'none' }], { duration: 320, easing: SPRING, fill: 'forwards' }).finished.then(fin)
  }
  grid.addEventListener('pointerup', endDrag)
  grid.addEventListener('pointercancel', endDrag)

  /* ══ ADD MODULE ═════════════════════════════════════════════════════════ */
  const sheet = $('#sheet')
  let pick = null
  const LEVEL = { 1: 'Core', 2: 'Operations', 3: 'Administration' }
  const shell = (step, title) => `<div class="sheet__grab"></div><div class="sheet__head">${step === 2 ? `<button class="icon-btn" type="button" data-back aria-label="Back">${icon('back')}</button>` : ''}<b>${esc(title)}</b><button class="icon-btn" type="button" data-shut aria-label="Close">${icon('close')}</button></div><div class="sheet__steps"><span class="${step === 1 ? 'on' : ''}"><i>1</i>Choose module</span><span>›</span><span class="${step === 2 ? 'on' : ''}"><i>2</i>Variant &amp; size</span><span>›</span><span><i>3</i>Add to Home</span></div>`
  function drawBrowse(filter = '', back = false) {
    const f = filter.toLowerCase(), on = new Set(home.map((h) => h.id))
    const ids = Object.keys(D.MODULES).filter((id) => D.MODULES[id].name.toLowerCase().includes(f))
    sheet.innerHTML = shell(1, 'Add Module') + `<div class="sheet__body"><div class="sheet__pane${back ? ' back' : ''}"><label class="search">${icon('search')}<input id="pickQ" type="search" placeholder="Search modules" value="${esc(filter)}" autocomplete="off"></label>` +
      [1, 2, 3].map((lv) => { const list = ids.filter((id) => D.MODULES[id].level === lv); return list.length ? `<div class="pick-level">${LEVEL[lv]}</div><div class="pick-list">${list.map((id) => { const m = D.MODULES[id]; return `<button class="pick press" type="button" data-pick="${id}"><span class="g" style="--g:${g(id)}">${icon(m.icon)}</span><span><b>${esc(m.name)}</b><small>${m.stat[0]} ${esc(m.stat[1])}</small></span>${on.has(id) ? '<span class="tag">On Home</span>' : ''}</button>` }).join('')}</div>` : '' }).join('') +
      (ids.length ? '' : `<div class="ss__empty">No module called “${esc(filter)}”.</div>`) + `</div></div>`
    const inp = $('#pickQ'); inp.addEventListener('input', () => { const v = inp.value, pos = inp.selectionStart; drawBrowse(v); const n = $('#pickQ'); n.focus(); n.setSelectionRange(pos, pos); n.closest('.sheet__pane').style.animation = 'none' })
  }
  function drawConfig(animatePane = true) {
    const m = D.MODULES[pick.id]
    const variants = m.viz === 'compact' ? ['compact'] : ['default', 'compact', ...(LIST_ITEMS[pick.id] ? ['list'] : [])]
    const sizes = pick.variant === 'compact' ? ['1x1'] : m.sizes
    if (!sizes.includes(pick.size)) pick.size = sizes[0]
    sheet.innerHTML = shell(2, m.name) + `<div class="sheet__body"><div class="sheet__pane" style="${animatePane ? '' : 'animation:none'}"><div class="cfg"><div><h4>Variant</h4><div class="opt-list" role="radiogroup" aria-label="Variant">${variants.map((v) => `<button class="opt" type="button" role="radio" data-var="${v}" aria-checked="${pick.variant === v}"><span class="opt__radio"></span><span><b>${D.VARIANTS[v].label}</b><small>${D.VARIANTS[v].note}</small></span></button>`).join('')}</div>` +
      `<h4 style="margin-top:20px">Size</h4><div class="seg" id="sizeSeg"></div></div><div><h4>Preview</h4><div class="preview" id="pv"></div></div></div></div></div>` +
      `<div class="sheet__foot"><button class="btn btn--tonal" type="button" data-back>Back</button><button class="btn btn--primary" type="button" data-add>${icon('plus')}Add to Home</button></div>`
    seg($('#sizeSeg'), sizes.map((s) => [s, s.replace('x', ' × ')]), pick.size, (k) => { pick.size = k; $('#pv').replaceChildren(card({ ...pick }, { cols: 3, preview: true })) })
    $('#pv').append(card({ ...pick }, { cols: 3, preview: true }))
  }
  function openSheet() { drawBrowse(); body.classList.add('sheet-open'); if (kbd()) setTimeout(() => $('#pickQ')?.focus({ preventScroll: true }), 400) }
  function closeSheet() { body.classList.remove('sheet-open'); if (kbd()) $('#addBtn').focus({ preventScroll: true }) }
  $('#addBtn').addEventListener('click', openSheet)
  $('#sheetVeil').addEventListener('click', closeSheet)
  sheet.addEventListener('click', (e) => {
    if (e.target.closest('[data-shut]')) return closeSheet()
    if (e.target.closest('[data-back]')) return drawBrowse('', true)
    const p = e.target.closest('[data-pick]'); if (p) { const m = D.MODULES[p.dataset.pick]; pick = { id: p.dataset.pick, variant: m.viz === 'compact' ? 'compact' : 'default', size: m.sizes[0] }; drawConfig(); return }
    const v = e.target.closest('[data-var]'); if (v) { pick.variant = v.dataset.var; drawConfig(false); return }
    if (e.target.closest('[data-add]')) {
      const it = { ...pick, uid: 'c' + (++uid) }
      home.push(it); save(); closeSheet()
      const el = card(it, { k: 0 }); grid.append(el)
      setTimeout(() => { el.scrollIntoView({ behavior: calm() ? 'auto' : 'smooth', block: 'center' }); setTimeout(() => el.classList.add('is-new'), 300) }, 250)
      toast(`${D.MODULES[it.id].name} added — drag it where you want it`)
    }
  })

  /* ══ ARRIVAL ════════════════════════════════════════════════════════════
     Sections in the first screen reveal on the ladder at load; the rest wait
     until they are scrolled to. Each reveals once. */
  $$('[data-stagger]').forEach((gp) => [...gp.children].forEach((c, i) => c.style.setProperty('--i', i)))
  drawGrid()
  relayout()
  const io = new IntersectionObserver((ents) => ents.forEach((en) => {
    if (!en.isIntersecting) return
    const el = en.target; el.classList.add('is-shown'); io.unobserve(el)
    setTimeout(() => { el.querySelectorAll('[data-stagger], .mgrid').forEach((x) => x.classList.add('settled')); if (el.id === 'secAnn') paintDeck(); el.querySelectorAll('.seg').forEach((s) => s._place?.()) }, 1300)
  }), { threshold: .12, rootMargin: '0px 0px -40px 0px' })
  requestAnimationFrame(() => requestAnimationFrame(() => $$('[data-reveal]').forEach((s) => { s._watched = true; io.observe(s) })))
  /* and the settle pass runs for those too */
  new MutationObserver((ms) => ms.forEach((m) => { const el = m.target; if (el.classList.contains('is-shown') && !el._settling) { el._settling = true; setTimeout(() => el.querySelectorAll('[data-stagger], .mgrid').forEach((x) => x.classList.add('settled')), 1300) } }))
    .observe(document.getElementById('stream'), { subtree: true, attributes: true, attributeFilter: ['class'] })
})()
