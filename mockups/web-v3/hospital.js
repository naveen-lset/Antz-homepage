/* WEB V3 MOCKUP · HOSPITAL, MODULE 1 OF 20 IN DEPTH (13 Oct 2026)
   Each tab is its own screen, and every patient opens the Figma "Patient
   Profile" page (933:2949) — the frame this whole mockup is drawn from.
   41 in-patients, the Dashboard's 41: 5 critical, 12 guarded, 24 stable, in
   four wards of 50 beds. SAMPLE data; the photographs are assets/img/species. */
(() => {
const PH = (s) => `../../assets/img/species/${s}.jpg`
/* the named patients first; the rest are made below so the wards fill */
const NAMED = [
  ['239719', 'Dheera', 'Bengal Tiger', 'Panthera tigris', 'bengal-tiger', 'M', 'Laceration, left flank — sutured', 'Dr. Kiran Iyer', 'Guarded'],
  ['120443', 'Raja', 'Asiatic Lion', 'Panthera leo persica', 'asiatic-lion', 'M', 'Acute colic', 'Dr. Meera Nair', 'Critical'],
  ['172290', 'Mira', 'Sloth Bear', 'Melursus ursinus', 'sloth-bear', 'F', 'Off feed, dental abscess', 'Dr. Kiran Iyer', 'Critical'],
  ['88120', 'Tara', 'Gaur', 'Bos gaurus', 'gaur', 'F', 'Hoof injury, front right', 'Dr. Rohan Mehta', 'Guarded'],
  ['61207', 'Kian', 'Indian Leopard', 'Panthera pardus fusca', 'indian-leopard', 'M', 'Post-vaccination check', 'Dr. Meera Nair', 'Stable'],
  ['143944', 'Sita', 'Sarus Crane', 'Antigone antigone', 'sarus-crane', 'F', 'Wing droop, suspected sprain', 'Dr. Kiran Iyer', 'Guarded'],
  ['30871', 'Kaal', 'Cinereous Vulture', 'Aegypius monachus', 'cinereous-vulture', 'M', 'Lead toxicity, chelation', 'Dr. Rohan Mehta', 'Critical'],
  ['40019', 'Naag', 'Indian Rock Python', 'Python molurus', 'indian-rock-python', 'U', 'Retained shed, dysecdysis', 'Dr. Meera Nair', 'Stable'],
  ['10221', 'Chinkara', 'Blackbuck', 'Antilope cervicapra', 'blackbuck', 'M', 'Horn fracture', 'Dr. Rohan Mehta', 'Stable'],
  ['33910', 'Mor', 'Indian Peafowl', 'Pavo cristatus', 'indian-peafowl', 'M', 'Bumblefoot', 'Dr. Kiran Iyer', 'Stable'],
  ['51122', 'Bunty', 'Sumatran Orangutan', 'Pongo abelii', 'sumatran-orangutan', 'F', 'Respiratory infection', 'Dr. Meera Nair', 'Critical'],
  ['77015', 'Chhota', 'Rhesus Macaque', 'Macaca mulatta', 'rhesus-macaque', 'M', 'Bite wound, tail', 'Dr. Rohan Mehta', 'Guarded'],
  ['92004', 'Kachua', 'Indian Star Tortoise', 'Geochelone elegans', 'indian-star-tortoise', 'F', 'Shell rot', 'Dr. Kiran Iyer', 'Stable'],
  ['64418', 'Barsa', 'Barasingha', 'Rucervus duvaucelii', 'barasingha', 'F', 'Pregnancy monitoring', 'Dr. Meera Nair', 'Guarded'],
]
const MORE_SP = [['Sambar', 'Rusa unicolor', 'sambar'], ['Chital', 'Axis axis', 'chital'], ['Nilgai', 'Boselaphus tragocamelus', 'nilgai'], ['Bonnet Macaque', 'Macaca radiata', 'bonnet-macaque'],
  ['Hill Myna', 'Gracula religiosa', 'hill-myna'], ['Black Kite', 'Milvus migrans', 'black-kite'], ['Rose-ringed Parakeet', 'Psittacula krameri', 'rose-ringed-parakeet'], ['Gaur', 'Bos gaurus', 'gaur'], ['Blackbuck', 'Antilope cervicapra', 'blackbuck']]
const NAMES = ['Gauri', 'Bholu', 'Rani', 'Moti', 'Shera', 'Champa', 'Lali', 'Tipu', 'Heera', 'Pari', 'Sultan', 'Juhi', 'Babli', 'Kalu', 'Meena', 'Sona', 'Tuntun', 'Lakshmi', 'Raju', 'Chandni', 'Golu', 'Mithu', 'Bijli', 'Sheru', 'Noor', 'Dhanno', 'Appu']
const REASONS = ['Routine post-op review', 'Diarrhoea', 'Weight loss', 'Lameness', 'Eye infection', 'Skin lesion', 'Quarantine on arrival', 'Dental check', 'Parasite load', 'Minor laceration']
const VETS = ['Dr. Kiran Iyer', 'Dr. Meera Nair', 'Dr. Rohan Mehta']
const SITES = ['Crimson Frosted', 'Clearspring', 'Hollowpine', 'Foxglen']
/* 5 critical, 12 guarded, 24 stable */
const want = { Critical: 5, Guarded: 12, Stable: 24 }
const have = { Critical: 0, Guarded: 0, Stable: 0 }
NAMED.forEach((n) => have[n[8]]++)
const fill = []; for (const k of ['Guarded', 'Stable', 'Critical']) for (let i = have[k]; i < want[k]; i++) fill.push(k)
const PAT = NAMED.map((n) => ({ aid: n[0], name: n[1], sp: n[2], latin: n[3], ph: n[4], sex: n[5], reason: n[6], vet: n[7], status: n[8] }))
fill.forEach((st, i) => { const s = MORE_SP[i % MORE_SP.length]; PAT.push({ aid: String(410000 + i * 137), name: NAMES[i % NAMES.length], sp: s[0], latin: s[1], ph: s[2], sex: 'MFU'[i % 3], reason: REASONS[i % REASONS.length], vet: VETS[i % 3], status: st }) })
/* wards: ICU 8 beds (7 in), Ward A 16 (14), Ward B 16 (13), Isolation 10 (7) */
const WARDS = [['ICU', 8, 7, 'Critical and post-surgical'], ['Ward A', 16, 14, 'Large mammals'], ['Ward B', 16, 13, 'Birds, reptiles and small mammals'], ['Isolation', 10, 7, 'Infectious and quarantine']]
const order = [...PAT].sort((a, b) => ({ Critical: 0, Guarded: 1, Stable: 2 }[a.status] - { Critical: 0, Guarded: 1, Stable: 2 }[b.status]))
let k = 0
for (const [w, , n] of WARDS) for (let b = 1; b <= n; b++) { const p = order[k++]; if (p) { p.ward = w; p.bed = b } }
PAT.forEach((p, i) => {
  p.case = `MED - ${12345 - i * 7}/25`; p.mr = `MR-${String(1234 + i * 31).padStart(7, '0')}`
  p.day = 1 + ((i * 5 + 3) % 14); p.site = SITES[i % 4]; p.encl = `Encl ${1 + (i % 9)}${'ABC'[i % 3]}`; p.sect = `Section ${1 + (i % 5)}`
  const d = new Date(2026, 9, 13 - p.day + 1); p.since = `${d.getDate()} ${['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'][d.getMonth()]} 2026`
  p.dis = p.status === 'Stable' ? ['ready', 'review', 'planned', null][i % 4] : p.status === 'Guarded' && i % 5 === 0 ? 'planned' : null
})
const byAid = new Map(PAT.map((p) => [p.aid, p]))
const TONE = { Critical: 'c', Guarded: 'y', Stable: 'g' }
const dot = (st) => `<span class="hdot" data-c="${TONE[st]}"></span>`
const status = (st) => `<span class="hstat">${dot(st)}${st}</span>`
const thumb = (p, cls = 'hthumb') => `<img class="${cls}" src="${PH(p.ph)}" alt="" loading="lazy">`

/* ── tab screens ── */
const chips = (name, opts, on) => `<div class="hchips" role="group" aria-label="${name}">${opts.map(([k, l, n]) => `<button type="button" class="hchip" data-chip="${name}:${k}" aria-pressed="${k === on}">${l}${n != null ? ` <b>${n}</b>` : ''}</button>`).join('')}</div>`
const toolbar = (V, ph, right = '') => `<div class="tools"><label class="search">${V.I.search}<input type="search" placeholder="${ph}" aria-label="Search"></label><div class="tools__r">${right}</div></div>`
const titleRow = (t, n, a, b) => `<div class="thead"><h2>${t}  - ${n}</h2><div class="cta">${a ? `<button type="button" class="btn-o" data-toast="${a}">${window.V3.I.plus}${a}</button>` : ''}${b ? `<button type="button" class="btn-p" data-toast="${b}">${b}</button>` : ''}</div></div>`
let filt = { adm: 'all', act: 'all' }

function admissions(V) {
  const n = (f) => PAT.filter((p) => f === 'all' || (f === 'today' ? p.day === 1 : f === 'week' ? p.day <= 7 : p.status === 'Critical')).length
  const rows = PAT.slice().sort((a, b) => a.day - b.day).filter((p) => filt.adm === 'all' || (filt.adm === 'today' ? p.day === 1 : filt.adm === 'week' ? p.day <= 7 : p.status === 'Critical'))
  return toolbar(V, 'Search patient, AID or case', chips('adm', [['all', 'All', n('all')], ['today', 'Today', n('today')], ['week', 'This week', n('week')], ['critical', 'Critical', n('critical')]], filt.adm)) +
    titleRow('Admissions', rows.length, 'Record vitals', 'New admission') +
    `<div class="table htable"><div class="table__row is-head"><span>Case</span><span>Patient</span><span>Ward · Bed</span><span>Admitted</span><span>Reason</span><span>Status</span></div>` +
    rows.map((p, i) => `<div class="table__row" style="--i:${i}" data-patient="${p.aid}" tabindex="0"><b>${p.case}</b>` +
      `<span class="hwho">${thumb(p)}<span>${p.name}<small>${p.sp} · AID ${p.aid}</small></span></span>` +
      `<span>${p.ward} · Bed ${p.bed}</span><span>${p.since}<small>Day ${p.day}</small></span><span class="hreason">${p.reason}<small>${p.vet}</small></span>${status(p.status)}</div>`).join('') + `</div>`
}

function wardMap(V) {
  return toolbar(V, 'Find a patient or bed', `<div class="hlegend">${[['g', 'Stable'], ['y', 'Guarded'], ['c', 'Critical'], ['free', 'Free bed']].map(([c, l]) => `<span><i data-c="${c}"></i>${l}</span>`).join('')}</div>`) +
    titleRow('Ward Occupancy', '41 of 50', 'Move patient', 'New admission') +
    `<div class="wgrid">${WARDS.map(([w, beds, n, what], wi) => {
      const ps = PAT.filter((p) => p.ward === w).sort((a, b) => a.bed - b.bed)
      return `<article class="w hward" style="--i:${wi}"><div class="w__head"><div class="w__t"><span class="w__title">${w}${V.I.chev}</span><span class="w__meta">${what}</span></div></div>` +
        `<div class="w__stat"><div class="w__hero"><span class="w__v">${n}</span><span class="w__u">of ${beds} beds</span></div></div>` +
        `<div class="beds">${Array.from({ length: beds }, (_, b) => { const p = ps.find((x) => x.bed === b + 1)
          return p ? `<button type="button" class="bed" data-c="${TONE[p.status]}" data-patient="${p.aid}" aria-label="Bed ${b + 1}: ${p.name}, ${p.sp}, ${p.status}">${thumb(p, 'bed__ph')}<span class="bed__n">${b + 1}</span><span class="bed__tip">${p.name} · ${p.sp}<small>${p.status} · Day ${p.day}</small></span></button>`
            : `<span class="bed is-free" aria-label="Bed ${b + 1}: free"><span class="bed__n">${b + 1}</span></span>` }).join('')}</div></article>`
    }).join('')}</div>`
}

function patientCard(p, i) {
  return `<button type="button" class="pcard" style="--i:${i}" data-patient="${p.aid}"><span class="pcard__ph">${thumb(p, 'ph')}<span class="prof__badge">${p.sex}</span><span class="pcard__st">${status(p.status)}</span></span>` +
    `<span class="pcard__id"><span class="k">AID : ${p.aid}</span><span class="n">${p.name}</span><span class="c">${p.sp}</span><span class="d">${p.latin}</span><span class="k">${p.ward} · Bed ${p.bed} · Day ${p.day}</span></span></button>`
}
function activeCases(V) {
  const n = (f) => PAT.filter((p) => f === 'all' || p.ward === f).length
  const ps = PAT.filter((p) => filt.act === 'all' || p.ward === filt.act)
  return toolbar(V, 'Search patients', chips('act', [['all', 'All wards', n('all')], ...WARDS.map(([w]) => [w, w, n(w)])], filt.act)) +
    titleRow('Active Cases', ps.length, 'Record vitals', 'New admission') +
    `<div class="pgrid">${ps.map(patientCard).join('')}</div>`
}

/* a vitals series that ends at the patient's current value */
const series = (end, spread, seed) => { let r = seed; return Array.from({ length: 7 }, (_, i) => i === 6 ? end : +(end + (((r = (r * 9301 + 49297) % 233280) / 233280) - .5) * spread).toFixed(1)) }
function vitals(p) {
  const s = +p.aid % 97
  const crit = p.status === 'Critical'
  return { hr: crit ? 104 + (s % 15) : 78 + (s % 12), t: crit ? 39.2 + (s % 7) / 10 : 38.4 + (s % 4) / 10, spo2: crit ? 88 + (s % 5) : 96 + (s % 3), rr: crit ? 29 + (s % 8) : 22 + (s % 5), w: 40 + (s * 3) % 180, bp: crit ? `${92 + s % 9}/${54 + s % 7}` : '118/76', s }
}
function criticalCare(V) {
  const ps = PAT.filter((p) => p.status === 'Critical')
  return toolbar(V, 'Search critical patients', `<button type="button" class="dd">Every 2hrs${V.I.down}</button>`) +
    titleRow('Critical Care', ps.length, 'Record vitals', 'Call vet on duty') +
    `<div class="crit">${ps.map((p, i) => { const v = vitals(p)
      const mini = (t, val, u, c, end, spread) => `<div class="cv"><span class="cv__t">${t}</span><div class="w__hero"><span class="cv__v" data-count="${val}">${val}</span><span class="w__u">${u}</span></div><div class="chart cv__ch" data-s="${series(end, spread, v.s + t.length).join(',')}" data-c="${c}"></div></div>`
      return `<article class="w critw" style="--i:${i}"><button type="button" class="critw__who" data-patient="${p.aid}">${thumb(p, 'critw__ph')}<span><b>${p.name}</b><small>${p.sp} · ${p.ward} Bed ${p.bed}</small><small>${p.reason}</small></span>${status(p.status)}</button>` +
        `<div class="critw__v">${mini('Heart Rate', v.hr, 'bpm', 'c', v.hr, 18)}${mini('Temperature', v.t.toFixed(1), '°C', 'y', v.t, 1.2)}${mini('SpO2', v.spo2, '%', 't', v.spo2, 5)}${mini('Respiration', v.rr, 'rpm', 'g', v.rr, 8)}</div>` +
        `<div class="critw__f"><span>Next check · ${['12:00', '12:30', '13:00', '13:30', '14:00'][i]}</span><span>${p.vet}</span></div></article>` }).join('')}</div>`
}

function discharges(V) {
  const col = (k, t, meta, act) => { const ps = PAT.filter((p) => p.dis === k)
    return `<section class="dcol"><header><b>${t}</b><span>${ps.length}</span></header><p>${meta}</p>` +
      ps.map((p, i) => `<article class="dcard" style="--i:${i}"><button type="button" class="dcard__who" data-patient="${p.aid}">${thumb(p)}<span><b>${p.name}</b><small>${p.sp} · ${p.ward} Bed ${p.bed}</small></span></button>` +
        `<div class="dcard__f"><span>Day ${p.day} · ${p.vet.replace('Dr. ', 'Dr ')}</span>${act ? `<button type="button" class="btn-o sm" data-toast="${act} ${p.name}">${act}</button>` : ''}</div></article>`).join('') + `</section>` }
  return toolbar(V, 'Search discharges', `<button type="button" class="dd">This week${V.I.down}</button>`) +
    titleRow('Discharges', PAT.filter((p) => p.dis).length, null, 'Discharge patient') +
    `<div class="dcols">${col('ready', 'Ready', 'Signed off, waiting for transport', 'Discharge')}${col('review', 'In review', 'Needs the attending vet', 'Review')}${col('planned', 'Planned this week', 'Expected to go home', null)}</div>`
}

function reports(V) {
  const R = [
    { t: 'trend', title: 'Average Stay', meta: 'Days in hospital • Month by month', value: '6.4', unit: 'days', ago: 'October so far', c: 'g', s: [7.8, 7.1, 7.4, 6.9, 6.6, 6.8, 6.4], ticks: ['Apr', 'Jul', 'Oct'], add: 'Download report' },
    { t: 'trend', title: 'Bed-days', meta: 'Occupied beds × days', value: '1,148', unit: 'this month', ago: 'Today', c: 't', s: [980, 1040, 1010, 1100, 1060, 1120, 1148], ticks: ['Apr', 'Jul', 'Oct'], add: 'Download report' },
    { t: 'trend', title: 'Readmissions', meta: 'Within 30 days of discharge', value: '3', unit: 'this month', ago: 'Today', c: 'c', s: [5, 4, 6, 3, 4, 2, 3], ticks: ['Apr', 'Jul', 'Oct'], add: 'Download report' },
    { t: 'split', title: 'Outcomes', meta: 'Patients discharged, last 90 days', value: '126', unit: 'patients', parts: [['Died in care', 4, 'c'], ['Transferred', 9, 'y'], ['Recovered', 113, 'g']], add: 'Download report' },
  ]
  return toolbar(V, 'Search reports', `<button type="button" class="dd">Last 6 months${V.I.down}</button>`) + titleRow('Reports', R.length, 'Schedule report', 'Export') +
    `<div class="wgrid">${R.map(V.widget).join('')}</div>`
}

/* ── the patient page: Figma 933:2949 itself ── */
const PTABS = ['Overview', 'Symptoms', 'Clinical Assessment', 'Prescription', 'Lab Requests', 'Investigation', 'Clinical Notes', 'Other Treatments', 'Monitoring', 'Anesthesia', 'Surgery', 'Media', 'Discharge']
const svg = (d) => `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">${d}</svg>`
const PI = {
  sick: svg('<circle cx="12" cy="12" r="8.5"/><path d="M8.5 10h.01M15.5 10h.01M8.5 16c1-1.3 2.2-2 3.5-2s2.5.7 3.5 2"/>'),
  doc: svg('<path d="M7 3h7l4 4v14H7z"/><path d="M14 3v4h4M10 12h5M10 16h5"/>'),
  pill: svg('<rect x="3" y="9" width="18" height="7" rx="3.5" transform="rotate(-35 12 12.5)"/><path d="m9.5 8.5 5 7"/>'),
  vet: svg('<circle cx="12" cy="7" r="3.2"/><path d="M5.5 20a6.5 6.5 0 0 1 13 0"/><path d="M12 13.5v3M10.5 15h3"/>'),
  cal: svg('<rect x="4" y="5" width="16" height="15" rx="2"/><path d="M4 10h16M9 3v4M15 3v4"/>'),
  bed: svg('<path d="M3 18V7M3 14h18v4M21 14v-2a3 3 0 0 0-3-3h-7v5"/><circle cx="7" cy="11" r="1.8"/>'),
  log: svg('<path d="M4 12a8 8 0 1 0 2.4-5.7M4 4v4h4"/><path d="M12 8v4l3 2"/>'),
  visit: svg('<path d="M10 17l5-5-5-5M15 12H3M14 4h5a1 1 0 0 1 1 1v14a1 1 0 0 1-1 1h-5"/>'),
  plus: svg('<path d="M12 5v14M5 12h14"/>'), chev: svg('<path d="m9 6 6 6-6 6"/>'), down: svg('<path d="m6 9 6 6 6-6"/>'),
}
function pHeader(id) {
  const p = byAid.get(id), V = window.V3
  return `<div class="hcard__l"><div class="hcard__id"><button type="button" class="back" data-out="active-cases" aria-label="Back to Active Cases">${V.I.back}</button>` +
      `<h1>${p.case}</h1><span class="pill">Inpatient</span><span class="pill is-sample">Sample data</span></div>` +
      `<p class="hcard__sub">Medical Record: ${p.mr}</p></div>` +
    `<div class="hcard__r"><span>Health Status</span><span class="hstat lg">${dot(p.status)}${p.status}</span><button type="button" class="ibtn" aria-label="More">${V.I.kebab}</button></div>`
}
function pLeft(id) {
  const p = byAid.get(id)
  return `<div class="prof"><div class="prof__panel"><div class="prof__photo"><img class="ph" src="${PH(p.ph)}" alt=""><span class="prof__badge">${p.sex}</span></div>` +
      `<div class="prof__id"><span class="k">AID : ${p.aid}</span><span class="n">${p.name}</span><span class="c">${p.sp}</span><span class="d">${p.latin}</span><span class="k">Encl: ${p.encl}</span><span class="k">Sect: ${p.sect}</span></div></div></div>` +
    `<div class="stats">${[['Attending veterinarian', p.vet, 'vet'], ['Chief veterinarian', 'Dr. Kiran Iyer', 'vet'], ['Admitted', `Day ${p.day} · Since ${p.since}`, 'cal'], [p.ward, `Bed ${p.bed} · ${p.site}`, 'bed']]
      .map(([k, v, ic]) => `<div class="srow"><span class="sico">${PI[ic]}</span><div><b>${k}</b><span>${v}</span></div></div>`).join('')}</div>` +
    `<div class="qa"><h2>Quick Actions</h2><div class="qa__list">${[['Symptoms', 'sick'], ['Clinical Assessments', 'doc'], ['Prescription', 'pill']].map(([l, ic]) =>
      `<button type="button" class="qa__it" data-toast="${l}">${PI[ic]}<span>${l}</span><span class="plus">${PI.plus}</span></button>`).join('')}` +
      `<button type="button" class="qa__more" data-toast="More actions">View more${PI.down}</button></div></div>` +
    `<div class="links"><button type="button" data-toast="Activity log"><span class="sico">${PI.log}</span><span>View Activity Log</span>${PI.chev}</button>` +
      `<button type="button" data-toast="Visit history"><span class="sico">${PI.visit}</span><span>View Visit History</span>${PI.chev}</button></div>`
}
function pBody(id, tab, V) {
  const p = byAid.get(id), v = vitals(p)
  if (tab === 'monitoring') {
    const C = [
      { t: 'trend', title: 'Weight', meta: 'As Needed', value: String(v.w), unit: 'Kg', ago: '5h ago', c: 'g', s: series(v.w, 12, v.s), ticks: ['7 Oct', '10 Oct', 'Today'], add: 'Add reading' },
      { t: 'trend', title: 'Heart Rate', meta: 'Every 2hrs • Next - 4:00 PM', value: String(v.hr), unit: 'bpm', ago: '5h ago', c: 'c', s: series(v.hr, 16, v.s + 1), ticks: ['7 Oct', '10 Oct', 'Today'], add: 'Add reading' },
      { t: 'note', title: 'SpO2', meta: 'Every 12hrs • Next - 4:00 PM', text: '', empty: true, add: 'Add reading' },
      { t: 'note', title: 'Behaviour', meta: 'Every 12hrs • Next - 4:00 PM', text: p.status === 'Stable' ? 'Alert and active; took the full morning feed and moved around the enclosure without favouring the leg.' : 'Observed increased lethargy and weakness during meal time no enthusiasm towards foods', ago: 'Last monitored: 2h ago', add: 'Add reading' },
      { t: 'trend', title: 'Respiration Rate', meta: 'Every 12hrs • Next - 4:00 PM', value: String(v.rr), unit: 'rpm', ago: '5h ago', c: 't', s: series(v.rr, 8, v.s + 2), ticks: ['7 Oct', '10 Oct', 'Today'], add: 'Add reading' },
      { t: 'trend', title: 'Blood Pressure', meta: 'As needed', value: v.bp, unit: 'mmHg', ago: '5h ago', c: 'y', s: series(118, 14, v.s + 3), ticks: ['7 Oct', '10 Oct', 'Today'], add: 'Add reading' },
      { t: 'trend', title: 'Temperature', meta: 'Every 2hrs • Next - 4:00 PM', value: v.t.toFixed(1), unit: '°C', ago: '5h ago', c: 'g', s: series(v.t, 1.4, v.s + 4), ticks: ['7 Oct', '10 Oct', 'Today'], add: 'Add reading' },
      { t: 'trend', title: 'Heart Rate', meta: 'Night • Every 4hrs', value: String(v.hr - 6), unit: 'bpm', ago: '9h ago', c: 'c', s: series(v.hr - 6, 14, v.s + 5), ticks: ['7 Oct', '10 Oct', 'Today'], add: 'Add reading' },
    ]
    return `<div class="tools"><label class="search">${V.I.search}<input type="search" placeholder="Search by Parameter" aria-label="Search by Parameter"></label>` +
      `<div class="tools__r"><button type="button" class="dd">Show All Medical Records${V.I.down}</button><div class="toggle"><button type="button" aria-pressed="true" aria-label="Cards">${V.I.list}</button><button type="button" aria-pressed="false" aria-label="Timeline">${V.I.grid}</button></div></div></div>` +
      `<div class="thead"><h2>Treatment Monitoring  - ${C.length}</h2><div class="cta"><button type="button" class="btn-o" data-toast="Add parameter">${V.I.plus}Parameter</button><button type="button" class="btn-p" data-toast="Schedule monitoring">Schedule</button></div></div>` +
      `<div class="wgrid">${C.map((w, i) => w.empty
        ? `<article class="w" style="--i:${i}">${V.head(w)}<div class="wempty"><b>No readings recorded yet</b><span>Values will appear here once the first reading is added</span></div></article>`
        : V.widget(w, i)).join('')}</div>`
  }
  if (tab === 'overview') {
    const W = [
      { t: 'progress', title: 'Treatment Plan', meta: `Day ${p.day} of ${p.day + 6} planned`, value: String(p.day), of: String(p.day + 6), unit: 'days', pct: Math.round(p.day / (p.day + 6) * 100), caption: p.reason, c: 'g', to: 'clinical-notes' },
      { t: 'list', title: 'Current Medication', meta: 'Active prescriptions', value: '3', unit: 'drugs', rows: [['Meloxicam 0.1 mg/kg · PO', 'Every 24 hrs', ''], ['Amoxicillin 15 mg/kg · IM', 'Every 12 hrs', 'y'], ['Vitamin B complex · IM', 'Every 48 hrs', '']], to: 'prescription', add: 'Prescription' },
      { t: 'timeline', title: 'Clinical Notes', meta: 'Latest first', items: [[p.status === 'Critical' ? 'Vitals unstable, fluids increased' : 'Eating well, sutures clean', `${p.vet} · 40 min ago`], ['Rechecked by keeper, resting comfortably', 'Keeper on duty · 5 hrs ago'], [`Admitted: ${p.reason}`, `${p.vet} · ${p.since}`]], to: 'clinical-notes', add: 'Add note' },
      { t: 'queue', title: 'Lab Requests', meta: 'For this patient', cols: [['To collect', 1, 'y'], ['In lab', 2, ''], ['Ready', 1, 'g']], to: 'lab-requests', add: 'New lab request' },
    ]
    return `<div class="thead"><h2>Overview  - ${W.length}</h2><div class="cta"><button type="button" class="btn-o" data-toast="Add note">${V.I.plus}Note</button><button type="button" class="btn-p" data-toast="Schedule">Schedule</button></div></div>` +
      `<div class="wgrid">${W.map(V.widget).join('')}</div>`
  }
  const E = {
    'symptoms': [['Lethargy', 'Moderate · since Day 1'], ['Reduced appetite', 'Mild · improving'], ['Favouring left limb', 'Noted by keeper · Day 2']],
    'clinical-assessment': [['Body condition 3/5', `${p.vet} · Day ${p.day}`], ['Hydration: mild deficit', `${p.vet} · Day ${Math.max(1, p.day - 1)}`], ['Wound: granulating, no discharge', 'Dr. Kiran Iyer · Day 2']],
    'prescription': [['Meloxicam 0.1 mg/kg · PO · 24 hrs', '5 days · started Day 1'], ['Amoxicillin 15 mg/kg · IM · 12 hrs', '7 days · started Day 1'], ['Vitamin B complex · IM · 48 hrs', '3 doses']],
    'lab-requests': [['CBC + biochemistry', 'Ready · Day 2'], ['Wound swab culture', 'In lab · Day 3'], ['Faecal parasitology', 'To collect']],
    'investigation': [['Radiograph, left flank', 'No foreign body · Day 1'], ['Ultrasound, abdomen', 'Within normal limits · Day 2']],
    'clinical-notes': [['Eating well, sutures clean', `${p.vet} · 40 min ago`], ['Rechecked by keeper, resting comfortably', 'Keeper on duty · 5 hrs ago'], [`Admitted: ${p.reason}`, p.since]],
    'other-treatments': [['Cold compress, 10 min', 'Twice a day'], ['Enclosure rest, no public view', 'Until review']],
    'anesthesia': [['Ketamine + medetomidine', 'Day 1 · 45 min · recovered well']],
    'surgery': [['Wound debridement and closure', 'Day 1 · Dr. Kiran Iyer · 1 hr 20 min']],
    'media': [['6 photographs', 'Wound progress, Day 1 to today'], ['1 video', 'Gait, Day 3']],
    'discharge': [[p.dis === 'ready' ? 'Ready for discharge' : 'Not yet ready', p.dis === 'ready' ? 'Signed off by the attending vet' : 'Review on Day ' + (p.day + 3)]],
  }[tab] || []
  const name = PTABS.find((t) => V.slug(t) === tab)
  return `<div class="thead"><h2>${name}  - ${E.length}</h2><div class="cta"><button type="button" class="btn-o" data-toast="Add ${name}">${V.I.plus}${name}</button></div></div>` +
    `<div class="w"><div class="tl">${E.map(([a, b]) => `<div><b>${a}</b><span>${b}</span></div>`).join('')}</div></div>`
}

/* THE DASHBOARD COUNTS THE SAME PATIENTS the tabs list, so a number on a
   widget is the number you find when you open it */
const H = (typeof MODULES !== 'undefined') && MODULES.find((m) => m.id === 'hospital')
if (H) {
  const w = (title) => H.widgets.find((x) => x.title === title)
  const crit = PAT.filter((p) => p.status === 'Critical')
  Object.assign(w('Critical Patients'), { value: String(crit.length), rows: crit.slice(0, 4).map((p) => [`${p.name} · ${p.sp}`, `Day ${p.day}`, 'c']) })
  const dis = (k) => PAT.filter((p) => p.dis === k).length
  w('Discharges').cols = [['Ready', dis('ready'), 'g'], ['In review', dis('review'), 'y'], ['This week', dis('planned'), '']]
  const week = PAT.filter((p) => p.day <= 7).length, perDay = Array.from({ length: 7 }, (_, i) => PAT.filter((p) => p.day === 7 - i).length)
  Object.assign(w('Admissions'), { value: String(week), s: perDay })
}
window.SCREENS = window.SCREENS || {}
window.SCREENS.hospital = {
  tabs: { 'admissions': admissions, 'ward-occupancy': wardMap, 'active-cases': activeCases, 'critical-care': criticalCare, 'discharges': discharges, 'reports': reports },
  after(root) {
    /* chips filter in place, with the same soft motion as a tab */
    root.querySelectorAll('[data-chip]').forEach((b) => b.addEventListener('click', () => {
      const [g, v] = b.dataset.chip.split(':'); filt[g] = v
      const redraw = () => { const t = g === 'adm' ? admissions : activeCases; root.innerHTML = `<div class="enter own">${t(window.V3)}</div>`; window.SCREENS.hospital.after(root) }
      document.startViewTransition && !matchMedia('(prefers-reduced-motion: reduce)').matches ? document.startViewTransition(redraw) : redraw()
    }))
    /* the search narrows rows and cards as you type */
    root.querySelector('.search input')?.addEventListener('input', (e) => {
      const q = e.target.value.trim().toLowerCase()
      root.querySelectorAll('.table__row:not(.is-head), .pcard, .bed:not(.is-free), .dcard, .critw').forEach((el) => { el.classList.toggle('is-dim', !!q && !el.textContent.toLowerCase().includes(q)) })
    })
    root.querySelectorAll('.table__row[data-patient]').forEach((r) => r.addEventListener('keydown', (e) => { if (e.key === 'Enter') r.click() }))
  },
  patient: {
    find: (id) => byAid.get(id),
    tabs: PTABS, first: 'monitoring',
    crumbs: (id) => { const p = byAid.get(id); return `<button type="button" data-out="dashboard">Hospital</button><i>/</i><button type="button" data-out="active-cases">All Patients</button><i>/</i><b>${p.case}</b>` },
    header: pHeader, left: pLeft, body: pBody,
  },
}
})()
