/* ══════════════════════════════════════════════════════════════════════════
   ANTZ COMMAND CENTRE · ROLE-AWARE DASHBOARD

   EIGHTEEN MODULES, EACH WITH ITS OWN PICTURE. The rule this file is built to
   is that a card's visual has to answer the module's own question before the
   reader gets to a number. So there is no shared "stat card" renderer here on
   purpose — a ward map, an incubation track and a compliance runway are three
   different shapes because they are three different questions, and the fastest
   way to make eighteen modules look like one product in the bad sense would
   have been to draw all three as bar charts.

   FOUR ROLES, ONE SHELL. Nothing about the chrome, type, spacing or card
   geometry changes between roles. What changes is ORDER, SPAN and DEPTH:
   which modules come first, how much room each gets, and how much supporting
   detail it carries. A module can also be absent from a role — Management does
   not need the treatment administration queue — which is a hierarchy decision,
   not a permissions one.
   ══════════════════════════════════════════════════════════════════════════ */

(function () {
'use strict';

/* ── data ────────────────────────────────────────────────────────────────
   Fixed figures, chosen to be internally consistent: the ward's occupied beds
   equal Hospital's count, the species blocks sum to the collection total, the
   feed flow balances. A dashboard whose own numbers disagree teaches the
   reader to stop trusting all of them. */

const D = {
  medical:   { cases: { Critical: 8, Serious: 23, Stable: 45, Recovering: 39 }, closed: 25 },
  hospital:  { beds: 56, occupied: 41, isolation: 6 },
  pharmacy:  { items: [
                 { n: 'Enrofloxacin',  pct: 12, note: 'low' },
                 { n: 'Meloxicam',     pct: 34, note: 'expiry 14d' },
                 { n: 'Ivermectin',    pct: 78, note: 'ok' },
                 { n: 'Ketamine',      pct: 22, note: 'controlled' },
                 { n: 'Vitamin B-Cx',  pct: 91, note: 'ok' },
               ] },
  lab:       { collected: 34, testing: 18, result: 62, blocking: 7 },
  species:   { groups: [
                 { n: 'Mammal',    v: 18240, c: '#336E8C' },
                 { n: 'Bird',      v: 21460, c: '#4E8A7A' },
                 { n: 'Reptile',   v: 9870,  c: '#A9761B' },
                 { n: 'Amphibian', v: 6450,  c: '#7E8C92' },
               ] },
  mortality: { total: 26, field: [0,0,1,0,2,0,0,1,0,0,3,0,1,0,0,2,0,0,1,0,0,0,2,0,1,0,0,3,0,0,1,0,0,0,2,0],
               causes: [['Age', 9], ['Disease', 7], ['Trauma', 6], ['Unknown', 4]] },
  fetal:     { journey: { Expected: 34, Live: 21, Lost: 8, Intervention: 5 } },
  eggs:      { clutches: [
                 { sp: 'Peafowl',   pct: 92, d: 2 },
                 { sp: 'Grey Hbill', pct: 74, d: 9 },
                 { sp: 'Sarus',     pct: 55, d: 16 },
                 { sp: 'Painted St', pct: 31, d: 24 },
               ] },
  housing:   { plots: [
                 { n: 'CAR', pct: 96 }, { n: 'HRB', pct: 71 }, { n: 'BER', pct: 58 },
                 { n: 'BTF', pct: 64 }, { n: 'RSC', pct: 103 }, { n: 'QRN', pct: 40 },
                 { n: 'REP', pct: 83 }, { n: 'AVI', pct: 92 }, { n: 'PRM', pct: 47 },
                 { n: 'SML', pct: 55 }, { n: 'NOC', pct: 33 }, { n: 'VET', pct: 22 },
               ] },
  diet:      { stock: 4200, kitchen: 3860, issued: 3640, animals: 3510, waste: 130 },
  followup:  { Overdue: 12, Due: 18, Upcoming: 34 },
  parivesh:  { items: [
                 { n: 'CZA Return',    d: 4,  t: 'crit' },
                 { n: 'Vet Register',  d: 17, t: 'warn' },
                 { n: 'Waste Audit',   d: 41, t: 'ok' },
               ], overdue: 1 },
  administer:{ Waiting: 22, Due: 9, Exception: 4 },
  users:     { roles: [
                 { r: 'Keeper',  have: 11, need: 12 },
                 { r: 'Vet',     have: 3,  need: 4 },
                 { r: 'Security',have: 8,  need: 8 },
                 { r: 'Admin',   have: 5,  need: 6 },
               ] },
  security:  { gates: [
                 { x: 12, y: 26, s: 'ok' },  { x: 34, y: 14, s: 'ok' },
                 { x: 58, y: 30, s: 'warn' },{ x: 79, y: 20, s: 'ok' },
                 { x: 88, y: 62, s: 'crit' },{ x: 62, y: 76, s: 'ok' },
                 { x: 38, y: 68, s: 'ok' },  { x: 16, y: 58, s: 'ok' },
               ] },
  reports:   { pending: 6, published: 18 },
  approvals: { New: 14, Waiting: 9, Aging: 6, Escalated: 3 },
  comms:     { threads: [
                 { w: 'Tiger CAR-02 pacing — review', a: 'Dr Menon', t: 'crit' },
                 { w: 'Feed substitution, Aviary',    a: 'Kitchen',  t: 'warn' },
                 { w: 'Night patrol handover',        a: 'Security', t: 'info' },
                 { w: 'Quarantine release, RSC-04',   a: 'Dr Rao',   t: 'ok' },
               ] },
};

const esc = (s) => String(s == null ? '' : s).replace(/[&<>"']/g,
  (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));

const sum = (o) => Object.values(o).reduce((a, b) => a + b, 0);

/* Head is shared because it IS the same object on every card — a name, a
   status dot and at most one flag. Everything below it differs. */
function head(name, tone, flag) {
  return '<span class="c__head">' +
    '<span class="c__dot' + (tone ? ' is-' + tone : '') + '" aria-hidden="true"></span>' +
    '<span class="c__name">' + esc(name) + '</span>' +
    (flag ? '<span class="c__flag is-' + tone + '">' + esc(flag) + '</span>' : '') +
  '</span>';
}

/* ── the eighteen visuals ────────────────────────────────────────────────
   Each takes the role's depth ('lite' | 'full') and returns the card body.
   `lite` drops supporting rows; it never shrinks the visual, because the
   visual is the thing the card exists to show. */

const V = {

/* MEDICAL · clinical case journey. Segment width is the share of cases, so
   where attention is concentrated is a shape rather than four numbers. */
medical(depth, role) {
  const c = D.medical.cases, total = sum(c);
  const tone = { Critical: 'crit', Serious: 'warn', Stable: 'info', Recovering: 'ok' };
  const col  = { Critical: 'var(--crit)', Serious: 'var(--warn)', Stable: 'var(--info)', Recovering: 'var(--ok)' };
  const tint = { Critical: 'var(--crit-t)', Serious: 'var(--warn-t)', Stable: 'var(--info-t)', Recovering: 'var(--ok-t)' };

  if (role === 'management') {
    /* Management gets the exception, not the queue: three bands, and the one
       that matters carries the reading. */
    return head('Medical', 'crit', 'Watch') +
      '<div class="c__read"><span class="c__num c__num--hero" style="color:var(--crit)">' + c.Critical + '</span>' +
      '<span class="c__of">critical of ' + total + ' open</span></div>' +
      '<div class="jr">' +
        '<div class="jr__seg" style="flex:' + c.Critical + ';background:var(--crit)"></div>' +
        '<div class="jr__seg" style="flex:' + c.Serious + ';background:var(--warn)"></div>' +
        '<div class="jr__seg" style="flex:' + (c.Stable + c.Recovering) + ';background:var(--ok-b)"></div>' +
      '</div>' +
      '<div class="jr-key"><span><i style="background:var(--crit)"></i>Critical</span>' +
      '<span><i style="background:var(--warn)"></i>Watch</span>' +
      '<span><i style="background:var(--ok-b)"></i>Stable</span></div>';
  }

  return head('Medical', 'crit', role === 'vet' ? c.Critical + ' critical' : null) +
    '<div class="jr">' + Object.keys(c).map((k) => (
      '<div class="jr__seg" style="flex:' + c[k] + ';background:' + tint[k] + '">' +
        '<b style="color:' + col[k] + '">' + c[k] + '</b></div>'
    )).join('') + '</div>' +
    '<div class="jr-key">' + Object.keys(c).map((k) => (
      '<span><i style="background:' + col[k] + '"></i>' + k + '</span>'
    )).join('') + '</div>' +
    (depth === 'full'
      ? '<div class="c__foot is-deep"><span>' + total + ' open</span><span>' + D.medical.closed + ' closed this cycle</span></div>'
      : '');
},

/* HOSPITAL · ward map. Fifty-six cells, coloured by state. "How full is the
   hospital" is answered by density before any number is read. */
hospital(depth, role) {
  const { beds, occupied, isolation } = D.hospital;
  let cells = '';
  for (let i = 0; i < beds; i++) {
    const cls = i < isolation ? ' is-iso' : i < occupied ? ' is-occ' : '';
    cells += '<span class="bed' + cls + '"></span>';
  }
  const pct = Math.round((occupied / beds) * 100);
  return head('Hospital', pct > 85 ? 'crit' : pct > 70 ? 'warn' : 'ok', pct + '% full') +
    '<div class="ward" aria-hidden="true">' + cells + '</div>' +
    '<div class="jr-key">' +
      '<span><i style="background:var(--info)"></i>Occupied ' + (occupied - isolation) + '</span>' +
      '<span><i style="background:var(--warn)"></i>Isolation ' + isolation + '</span>' +
      '<span><i style="background:var(--ok-t);box-shadow:inset 0 0 0 1px var(--ok-b)"></i>Free ' + (beds - occupied) + '</span>' +
    '</div>';
},

/* PHARMACY · the shelf. Fill is stock; the mark is the exception. */
pharmacy(depth) {
  const rows = depth === 'full' ? D.pharmacy.items : D.pharmacy.items.slice(0, 3);
  const low = D.pharmacy.items.filter((i) => i.pct < 25).length;
  return head('Pharmacy', low ? 'crit' : 'ok', low ? low + ' low' : null) +
    '<div class="shelf">' + rows.map((i) => (
      '<div class="shelf__row">' +
        '<span class="shelf__name">' + esc(i.n) + '</span>' +
        '<span class="shelf__bar"><span class="shelf__fill' +
          (i.pct < 25 ? ' is-low' : i.pct < 50 ? ' is-mid' : '') +
          '" style="width:' + i.pct + '%"></span></span>' +
        '<span class="shelf__meta">' + esc(i.note) + '</span></div>'
    )).join('') + '</div>';
},

/* LAB · pipeline. The stage that is blocking clinical decisions is the one
   that changes colour, because "where is the work stuck" is the question. */
lab(depth, role) {
  const l = D.lab;
  const st = [['Collected', l.collected, false], ['Testing', l.testing, true], ['Result', l.result, false]];
  return head('Lab', 'warn', role === 'vet' ? l.blocking + ' blocking' : null) +
    '<div class="pipe">' + st.map(([n, v, block]) => (
      '<div class="pipe__st' + (block ? ' is-block' : '') + '">' +
        '<div class="pipe__n">' + v + '</div><div class="pipe__l">' + n + '</div></div>'
    )).join('') + '</div>' +
    (depth === 'full'
      ? '<div class="c__foot is-deep"><span>' + l.blocking + ' holding a clinical decision</span></div>' : '');
},

/* SPECIES MANAGEMENT · collection landscape. Blocks sized by population, so
   composition and imbalance are read from area rather than from a legend. */
species(depth) {
  const g = D.species.groups, total = g.reduce((a, b) => a + b.v, 0);
  return head('Species Management', 'info', null) +
    '<div class="land" style="min-height:74px">' + g.map((x) => {
      const share = x.v / total;
      return '<div class="land__b" style="flex:' + Math.round(share * 100) +
        ' 1 0;height:' + (46 + share * 38) + 'px;background:' + x.c + '">' +
        '<span style="color:#fff">' + x.n + '<br>' + x.v.toLocaleString('en-IN') + '</span></div>';
    }).join('') + '</div>' +
    (depth === 'full'
      ? '<div class="c__foot is-deep"><span>' + total.toLocaleString('en-IN') + ' animals</span><span>' + g.length + ' groups</span></div>' : '');
},

/* MORTALITY · an event field. Each dot is an event; darker is a cluster. A
   concentration shows up as a patch, which a bar chart of causes hides. */
mortality(depth, role) {
  const m = D.mortality;
  return head('Mortality', 'warn', role === 'management' ? 'Within range' : null) +
    '<div class="field" aria-hidden="true">' +
      m.field.map((v) => '<span class="ev' + (v ? ' is-' + v : '') + '"></span>').join('') +
    '</div>' +
    (depth === 'full'
      ? '<div class="jr-key is-deep">' + m.causes.map(([n, v]) => (
          '<span><i style="background:var(--warn)"></i>' + n + ' ' + v + '</span>')).join('') + '</div>'
      : '<div class="c__foot"><span>' + m.total + ' this cycle</span></div>');
},

/* FETAL DEATH · outcome journey. Expected splits into what survived, what was
   lost and what was intervened on. */
fetal(depth) {
  const j = D.fetal.journey;
  const col = { Expected: 'var(--idle)', Live: 'var(--ok)', Lost: 'var(--crit)', Intervention: 'var(--warn)' };
  return head('Fetal Death', 'warn', null) +
    '<div class="jr">' + Object.keys(j).map((k) => (
      '<div class="jr__seg" style="flex:' + j[k] + ';background:' + col[k] + '">' +
        '<b style="color:#fff">' + j[k] + '</b></div>'
    )).join('') + '</div>' +
    '<div class="jr-key">' + Object.keys(j).map((k) => (
      '<span><i style="background:' + col[k] + '"></i>' + k + '</span>')).join('') + '</div>';
},

/* EGGS · incubation track. Each clutch is a rail moving toward its own hatch,
   and the ones approaching turn. Days remaining is intrinsic time (§26). */
eggs(depth) {
  const cl = depth === 'full' ? D.eggs.clutches : D.eggs.clutches.slice(0, 3);
  const soon = D.eggs.clutches.filter((c) => c.d <= 3).length;
  return head('Eggs', soon ? 'crit' : 'info', soon ? soon + ' hatching' : null) +
    '<div class="track">' + cl.map((c) => (
      '<div class="track__row"><span class="track__sp">' + esc(c.sp) + '</span>' +
        '<span class="track__rail"><span class="track__go' +
          (c.d <= 3 ? ' is-due' : c.d <= 10 ? ' is-soon' : '') +
          '" style="width:' + c.pct + '%"></span></span>' +
        '<span class="track__d">' + c.d + 'd</span></div>'
    )).join('') + '</div>';
},

/* HOUSING · the estate. One plot per section, tinted by capacity pressure, so
   "where is capacity under pressure" is a place and not a percentage. */
housing(depth) {
  const p = D.housing.plots;
  const over = p.filter((x) => x.pct > 100).length;
  return head('Housing', over ? 'crit' : 'warn', over ? over + ' over capacity' : null) +
    '<div class="estate">' + p.map((x) => (
      '<div class="plot' + (x.pct > 100 ? ' is-over' : x.pct > 85 ? ' is-tight' : '') + '">' +
        '<b>' + x.pct + '%</b><span>' + esc(x.n) + '</span></div>'
    )).join('') + '</div>';
},

/* DIET & KITCHEN · feed flow, ending in what was wasted. */
diet(depth) {
  const d = D.diet;
  const steps = [['Stock', d.stock], ['Kitchen', d.kitchen], ['Issued', d.issued], ['Animals', d.animals]];
  return head('Diet & Kitchen', 'ok', null) +
    '<div class="flow">' + steps.map(([n, v], i) => (
      (i ? '<span class="flow__a" aria-hidden="true">&rsaquo;</span>' : '') +
      '<div class="flow__n"><b>' + (v / 1000).toFixed(1) + 'k</b><span>' + n + '</span></div>'
    )).join('') +
    '<span class="flow__a" aria-hidden="true">&rsaquo;</span>' +
    '<div class="flow__n is-loss"><b>' + d.waste + '</b><span>Wastage</span></div></div>';
},

/* FOLLOW UP · a timeline by urgency, not a calendar. */
followup(depth) {
  const f = D.followup, max = Math.max.apply(null, Object.values(f));
  const tone = { Overdue: 'crit', Due: 'warn', Upcoming: 'info' };
  return head('Follow Up', 'crit', f.Overdue + ' overdue') +
    '<div class="lanes">' + Object.keys(f).map((k) => (
      '<div class="lane"><span class="lane__l">' + k + '</span>' +
        '<span class="lane__bar"><span class="lane__fill is-' + tone[k] +
          '" style="width:' + Math.round((f[k] / max) * 100) + '%"></span></span>' +
        '<span class="lane__n">' + f[k] + '</span></div>'
    )).join('') + '</div>';
},

/* PARIVESH · compliance runway. Time is the axis because here time IS the
   work — the one place §26 allows it to be the primary dimension. */
parivesh(depth) {
  const p = D.parivesh;
  const span = 60;
  return head('Parivesh', p.overdue ? 'crit' : 'warn', p.overdue ? p.overdue + ' overdue' : null) +
    '<div class="runway">' + p.items.map((i) => (
      '<span class="runway__t" style="left:' + Math.min(96, (i.d / span) * 100) + '%">' +
        '<span class="runway__pin is-' + i.t + '"></span>' +
        '<span class="runway__d">' + esc(i.n) + '</span></span>'
    )).join('') + '</div>' +
    '<div class="runway__scale"><span>now</span><span>30d</span><span>60d</span></div>';
},

/* ADMINISTER · the treatment queue, by state. */
administer(depth) {
  const a = D.administer, max = Math.max.apply(null, Object.values(a));
  const tone = { Waiting: 'idle', Due: 'warn', Exception: 'crit' };
  return head('Administer', 'warn', a.Exception + ' exceptions') +
    '<div class="lanes">' + Object.keys(a).map((k) => (
      '<div class="lane"><span class="lane__l">' + k + '</span>' +
        '<span class="lane__bar"><span class="lane__fill is-' + tone[k] +
          '" style="width:' + Math.round((a[k] / max) * 100) + '%"></span></span>' +
        '<span class="lane__n">' + a[k] + '</span></div>'
    )).join('') + '</div>';
},

/* USERS · staff coverage. Filled pips are posts covered, hollow are gaps —
   the question is coverage, not attendance. */
users(depth) {
  const r = D.users.roles;
  const gaps = r.reduce((a, b) => a + (b.need - b.have), 0);
  return head('Users', gaps ? 'warn' : 'ok', gaps ? gaps + ' unfilled' : null) +
    '<div class="cov">' + r.map((x) => {
      let pips = '';
      for (let i = 0; i < x.need; i++) pips += '<span class="cov__pip' + (i >= x.have ? ' is-gap' : '') + '"></span>';
      return '<div class="cov__row"><span class="cov__r">' + esc(x.r) + '</span>' +
        '<span class="cov__pips">' + pips + '</span>' +
        '<span class="cov__n">' + x.have + '/' + x.need + '</span></div>';
    }).join('') + '</div>';
},

/* SECURITY · the perimeter. A gate with a problem is a place on a plan. */
security(depth) {
  const g = D.security.gates;
  const bad = g.filter((x) => x.s !== 'ok').length;
  return head('Security', bad ? 'crit' : 'ok', bad ? bad + ' exceptions' : 'Clear') +
    '<div class="perim" aria-hidden="true">' + g.map((x) => (
      '<span class="gate is-' + x.s + '" style="left:' + x.x + '%;top:' + x.y + '%"><i></i></span>'
    )).join('') + '</div>';
},

/* REPORTS · a document snapshot. */
reports(depth) {
  const r = D.reports;
  let docs = '';
  for (let i = 0; i < 6; i++) docs += '<span class="doc' + (i < 2 ? ' is-new' : '') + '"></span>';
  return head('Reports', 'info', null) +
    '<div class="docs" aria-hidden="true">' + docs + '</div>' +
    '<div class="c__foot"><span>' + r.pending + ' pending</span><span>' + r.published + ' published</span></div>';
},

/* APPROVALS · the age queue. Aging and escalated are what the card is for. */
approvals(depth, role) {
  const a = role === 'management' ? { Escalated: D.approvals.Escalated, Aging: D.approvals.Aging } : D.approvals;
  const max = Math.max.apply(null, Object.values(a));
  const tone = { New: 'info', Waiting: 'idle', Aging: 'warn', Escalated: 'crit' };
  return head('Approvals', 'crit', D.approvals.Escalated + ' escalated') +
    '<div class="lanes">' + Object.keys(a).map((k) => (
      '<div class="lane"><span class="lane__l">' + k + '</span>' +
        '<span class="lane__bar"><span class="lane__fill is-' + tone[k] +
          '" style="width:' + Math.round((a[k] / max) * 100) + '%"></span></span>' +
        '<span class="lane__n">' + a[k] + '</span></div>'
    )).join('') + '</div>';
},

/* COMMUNICATION · threads waiting on a reply. Management sees only the
   critical one; everyone else sees the live list. */
comms(depth, role) {
  const t = role === 'management' ? D.comms.threads.filter((x) => x.t === 'crit') : D.comms.threads;
  const rows = depth === 'full' ? t : t.slice(0, 2);
  return head('Communication', 'info', null) +
    '<div class="thr">' + rows.map((x) => (
      '<div class="thr__t"><span class="c__dot is-' + x.t + '"></span>' +
        '<span class="thr__w">' + esc(x.w) + '</span>' +
        '<span class="thr__a">' + esc(x.a) + '</span></div>'
    )).join('') + '</div>';
},
};

/* ── the four roles ──────────────────────────────────────────────────────
   `span` is columns; `feat` gives the card the feature padding. Order is the
   hierarchy. A module missing from a role is missing on purpose. */

const ROLES = {
  vet: {
    name: 'Vet', ask: 'What needs my clinical attention?',
    sections: [
      { title: 'Needs attention now', cards: [
        { m: 'medical',    span: 2, feat: true, depth: 'full' },
        { m: 'hospital',   span: 2, feat: true, depth: 'full' },
        { m: 'lab',        span: 1, depth: 'full' },
        { m: 'administer', span: 1, depth: 'full' },
        { m: 'followup',   span: 1, depth: 'full' },
        { m: 'pharmacy',   span: 1, depth: 'full' },
      ] },
      { title: 'Clinical context', note: 'Outcomes and open threads', cards: [
        { m: 'mortality', span: 1, depth: 'lite' },
        { m: 'fetal',     span: 1, depth: 'lite' },
        { m: 'comms',     span: 2, depth: 'full' },
      ] },
    ],
  },

  biologist: {
    name: 'Biologist', ask: 'What is happening across the collection?',
    sections: [
      { title: 'The collection', cards: [
        { m: 'species', span: 2, feat: true, depth: 'full' },
        { m: 'housing', span: 2, feat: true, depth: 'full' },
        { m: 'eggs',    span: 2, depth: 'full' },
        { m: 'fetal',   span: 1, depth: 'lite' },
        { m: 'mortality', span: 1, depth: 'full' },
      ] },
      { title: 'Support and observation', cards: [
        { m: 'diet',    span: 2, depth: 'lite' },
        { m: 'medical', span: 1, depth: 'lite' },
        { m: 'lab',     span: 1, depth: 'lite' },
        { m: 'reports', span: 1, depth: 'lite' },
        { m: 'comms',   span: 1, depth: 'lite' },
      ] },
    ],
  },

  admin: {
    name: 'Admin', ask: 'What operational work needs to be handled?',
    sections: [
      { title: 'Work in hand', cards: [
        { m: 'approvals', span: 2, feat: true, depth: 'full' },
        { m: 'parivesh',  span: 2, feat: true, depth: 'full' },
        { m: 'users',     span: 2, depth: 'full' },
        { m: 'pharmacy',  span: 1, depth: 'full' },
        { m: 'security',  span: 1, depth: 'full' },
      ] },
      { title: 'Operational context', cards: [
        { m: 'lab',        span: 1, depth: 'lite' },
        { m: 'housing',    span: 1, depth: 'lite' },
        { m: 'administer', span: 1, depth: 'lite' },
        { m: 'reports',    span: 1, depth: 'lite' },
        { m: 'comms',      span: 2, depth: 'lite' },
      ] },
    ],
  },

  management: {
    name: 'Management', ask: 'What is the overall state, risk and decision priority?',
    sections: [
      { title: 'Risk and capacity', cards: [
        { m: 'medical',  span: 2, feat: true, depth: 'lite' },
        { m: 'hospital', span: 2, feat: true, depth: 'lite' },
        { m: 'housing',  span: 2, depth: 'lite' },
        { m: 'parivesh', span: 2, depth: 'lite' },
      ] },
      { title: 'Decisions and standing', cards: [
        { m: 'approvals', span: 1, depth: 'lite' },
        { m: 'security',  span: 1, depth: 'lite' },
        { m: 'mortality', span: 1, depth: 'lite' },
        { m: 'species',   span: 1, depth: 'lite' },
        { m: 'reports',   span: 1, depth: 'lite' },
        { m: 'comms',     span: 1, depth: 'lite' },
      ] },
    ],
  },
};

/* ── render ──────────────────────────────────────────────────────────────── */

const board = document.getElementById('board');
const rolesEl = document.querySelector('.roles');
const titleEl = document.getElementById('roleTitle');
const askEl = document.getElementById('roleAsk');
let current = 'vet';

rolesEl.innerHTML = Object.keys(ROLES).map((k) => (
  '<button class="role" type="button" data-role="' + k + '" aria-pressed="' +
    (k === current) + '">' + ROLES[k].name + '</button>'
)).join('');

function render() {
  const r = ROLES[current];
  titleEl.textContent = r.name;
  askEl.textContent = r.ask;

  board.innerHTML = r.sections.map((sec) => (
    '<section class="sec">' +
      '<div class="sec__head"><h2 class="sec__title">' + esc(sec.title) + '</h2>' +
        (sec.note ? '<span class="sec__note">' + esc(sec.note) + '</span>' : '') + '</div>' +
      '<div class="grid">' + sec.cards.map((c) => {
        const body = V[c.m](c.depth || 'lite', current);
        const span = c.span >= 3 ? 'sp3' : c.span === 2 ? 'sp2' : '';
        return '<button type="button" class="c' + (c.feat ? ' c--feat' : '') +
          (span ? ' ' + span : '') + '" data-module="' + c.m + '">' + body + '</button>';
      }).join('') + '</div>' +
    '</section>'
  )).join('');

  for (const b of rolesEl.querySelectorAll('.role')) {
    b.setAttribute('aria-pressed', String(b.dataset.role === current));
  }
}

rolesEl.addEventListener('click', (e) => {
  const b = e.target.closest('.role');
  if (!b || b.dataset.role === current) return;
  current = b.dataset.role;
  render();
});

render();

/* A test hook, so the responsive sweep can read composition rather than
   guessing it from screenshots. */
window.antzDash = {
  role: () => current,
  setRole: (r) => { if (ROLES[r]) { current = r; render(); } },
  roles: () => Object.keys(ROLES),
  modules: () => Object.keys(V),
  layout: () => [...document.querySelectorAll('.c')].map((el) => ({
    m: el.dataset.module,
    w: Math.round(el.getBoundingClientRect().width),
    h: Math.round(el.getBoundingClientRect().height),
    x: Math.round(el.getBoundingClientRect().left),
  })),
};

})();
