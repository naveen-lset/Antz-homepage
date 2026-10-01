"""THE V2 MODULE PAGES' DATA (29 Sep 2026) — row-level records for the four
sites V2 draws, read straight from the V5 app's anonymised dump, written to
assets/data/v2-modules.json and fetched only when a module page first opens.

    python3 tools/v2modules_build.py

What it holds, and what it caps (every cap keeps the TRUE total beside it):
  species   every species held at the four sites: names, taxonomy, IUCN, CITES,
            and per site M / F / U, enclosures and chipped animals
  animals   the register, per species, up to ANIMAL_CAP animals
  deaths    every death in the last DEATH_DAYS days, plus the most recent
            NECROPSY_CAP deaths per site in each necropsy status
  doses     every vaccination and deworming still pending (due and not given),
            and those given in the last DOSE_DAYS days
  life      births and deaths per species per site per month, all time
And, for the Natality page only, assets/data/v2-births.json: every birth at
the four sites since BIRTHS_FROM, one row each —
  [days ago, species index, site index, sex (0 M, 1 F, 2 undetermined,
   3 indeterminate), AID, identifier type index, identifier, enclosure index,
   1 if dated by a real birth date (else by the day it was added to Antz)]
and assets/data/v2-deaths.json, the same for every death since BIRTHS_FROM
(the Mortality page; its row shape is written beside the dump below).

The clock is the extract's (20 May 2026). Nothing is invented here: eggs and
carcass transfers have no table, and the pages say so."""
import json, os, re, sys, collections
from datetime import date

sys.path.insert(0, '/Users/naveen/Documents/antz-command-centre-v5/tools/etl')
import dump

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DUMP = '/Users/naveen/Documents/antz-command-centre-v5/Dump20260622.sql'
OUT = os.path.join(HERE, 'assets', 'data', 'v2-modules.json')
TODAY = date(2026, 5, 20)
DEATH_DAYS, DOSE_DAYS, ANIMAL_CAP, NECROPSY_CAP = 120, 120, 50, 250
BIRTHS_FROM = date(2023, 1, 1)

# the four sites, in V2's slot order — the same four js/data/v5db.js lays over V2
V5 = open(os.path.join(HERE, 'index.html'), encoding='utf-8').read()
a = V5.index('const V5DB = ') + len('const V5DB = ')
V5DB = json.loads(V5[a:V5.index('\nconst on = () =>', a)])
SITES = [{'id': s['id'], 'name': s['name'], 'short': s['short']} for s in V5DB['sites']]
IX = {s['name']: i for i, s in enumerate(SITES)}

def day(v):
    try: return date.fromisoformat((v or '')[:10])
    except ValueError: return None
def iso(d): return d.isoformat() if d else None
def hm(v):
    m = re.search(r'[ T](\d{2}):(\d{2})', v or '')
    return f'{m.group(1)}:{m.group(2)}' if m else None
def sex(g):
    g = (g or '').lower()
    return 0 if g == 'male' else 1 if g == 'female' else 2
DISPOSAL = {'incinerated': 'Incinerated', 'incineration': 'Incinerated', 'combustion': 'Incinerated', 'burial': 'Burial', 'buried': 'Burial',
            'discarded': 'Discarded', 'fed out': 'Fed out', 'preserved': 'Preserved'}
def disposal(v):
    v = (v or '').strip()
    if not v or '<' in v or len(v) > 30: return None
    return DISPOSAL.get(v.lower(), v.title() if v.isupper() or v.islower() else v)
# a few rows of the dump carry rich-text notes that spilled into the next
# columns ('74);">Extensive soft tissue…'): a short plain value, or nothing
def text(v, n=40):
    v = (v or '').strip()
    return None if not v or '<' in v or '">' in v or len(v) > n else v
def num(v):
    try: return round(float(v), 4)
    except (TypeError, ValueError): return None

C = dump.columns(DUMP)
def getter(t):
    cols = C[t]
    return lambda r, c: r[cols.index(c)] if cols.index(c) < len(r) else None

TABLES = {'housing', 'report_deaths', 'report_births', 'vaccination', 'deworming', 'species'}
rows = collections.defaultdict(list)
for t, r in dump.rows(DUMP, TABLES):
    rows[t].append(r)
print('read', {t: len(v) for t, v in rows.items()}, file=sys.stderr)

# ── the reference biology, by common name ──
g = getter('species')
REF = {}
for r in rows['species']:
    n = g(r, 'common_name')
    if n and n not in REF:
        REF[n] = {'l': g(r, 'scientific_name'), 'c': g(r, 'taxonomic_class'), 'o': g(r, 'taxonomic_order'), 'f': g(r, 'taxonomic_family'),
                  'iucn': (g(r, 'iucn_status') or '').split(' (')[0] or None, 'cites': (g(r, 'cites_appendix') or '').split(' (')[0] or None}

# ── the register ──
g = getter('housing')
species = {}
animals = collections.defaultdict(list)
for r in rows['housing']:
    site = g(r, 'site_facilty')
    if site not in IX: continue
    n = g(r, 'common_name') or 'Unknown'
    s = species.setdefault(n, {'n': n, **REF.get(n, {}), 's': {}})
    if not s.get('l'): s['l'] = g(r, 'scientific_name')
    if not s.get('c'): s['c'] = g(r, 'class')
    if not s.get('o'): s['o'] = g(r, 'order')
    if not s.get('f'): s['f'] = g(r, 'family')
    per = s['s'].setdefault(SITES[IX[site]]['id'], {'m': 0, 'f': 0, 'u': 0, 'chip': 0, 'encl': set()})
    x = sex(g(r, 'gender'))
    per['mfu'[x]] += 1
    # the Housing tab's enclosure-wise table: M / F / U per enclosure per site
    e = s.setdefault('e', {}).setdefault(SITES[IX[site]]['id'], {}).setdefault(g(r, 'enclosure_name') or '—', [0, 0, 0])
    e[x] += 1
    if g(r, 'micro_chip'): per['chip'] += 1
    if g(r, 'enclosure_name'): per['encl'].add(g(r, 'enclosure_name'))
    animals[n].append([int(g(r, 'antz_animal_id') or 0), x, IX[site], g(r, 'enclosure_name') or None,
                       iso(day(g(r, 'birth_date'))), iso(day(g(r, 'accession_date'))), 1 if g(r, 'micro_chip') else 0, num(g(r, 'weight'))])
for s in species.values():
    for k, per in s['s'].items():
        s['s'][k] = [per['m'], per['f'], per['u'], len(per['encl']), per['chip']]
ANIMALS = {n: sorted(v, key=lambda a: -a[0])[:ANIMAL_CAP] for n, v in animals.items()}

# ── deaths: the window, plus each site's latest in every necropsy status ──
g = getter('report_deaths')
deaths_all = []
for r in rows['report_deaths']:
    site = g(r, 'site_facility')
    if site not in IX: continue
    d = day(g(r, 'mortality_recorded_on'))
    if not d or d > TODAY: continue
    deaths_all.append((d, r, site))
deaths_all.sort(key=lambda t: t[0], reverse=True)
keep, per_status, nec_total = [], collections.Counter(), collections.defaultdict(collections.Counter)
for d, r, site in deaths_all:
    st = g(r, 'necropsy_status') if g(r, 'necropsy_status') in ('Pending', 'Completed') else 'Unknown'
    nec_total[SITES[IX[site]]['id']][st] += 1
    recent = (TODAY - d).days < DEATH_DAYS
    if recent or per_status[(site, st)] < NECROPSY_CAP:
        per_status[(site, st)] += 1
        keep.append([int(g(r, 'antz_animal_id') or 0), g(r, 'common_name') or 'Unknown', IX[site], iso(d), hm(g(r, 'mortality_recorded_on')),
                     text(g(r, 'manner_of_death')), st, text(g(r, 'carcass_condition')),
                     disposal(g(r, 'carcass_disposal_method')), sex(g(r, 'gender')), g(r, 'enclosure_name') or None,
                     text(g(r, 'mortality_recorded_by')), iso(day(g(r, 'discovered_date'))),
                     text(g(r, 'mortality_notes'), 160), g(r, 'class') or None, iso(day(g(r, 'birth_date'))), g(r, 'section_name') or None])
        n = g(r, 'common_name') or 'Unknown'
        if n not in species: species[n] = {'n': n, **REF.get(n, {}), 's': {}}

# ── doses: pending (due, not given) at any date, and given in the window ──
doses = []
for t, kind in (('vaccination', 'v'), ('deworming', 'd')):
    g = getter(t)
    for r in rows[t]:
        site = g(r, 'site')
        if site not in IX: continue
        st = (g(r, 'status') or '').lower()
        due, given = day(g(r, 'vaccination_date')), day(g(r, 'administered_on'))
        if st == 'pending' and due and due <= TODAY: s = 'P'
        elif st == 'completed' and given and 0 <= (TODAY - given).days < DOSE_DAYS: s = 'C'
        else: continue
        n = g(r, 'common_name') or 'Unknown'
        doses.append([kind, int(g(r, 'animal_id') or 0), n, IX[site], (g(r, 'medicine_name') or '').strip() or 'Unnamed', iso(due), s, iso(given),
                      num(g(r, 'scheduled_quantity')), (g(r, 'unit') or '').strip() or None, num(g(r, 'qty_administered')), g(r, 'enclosure') or None,
                      int(g(r, 'id') or 0)])
        if n not in species: species[n] = {'n': n, **REF.get(n, {}), 's': {}}

# ── circle of life: births and deaths per species, per site, per month ──
life = collections.defaultdict(lambda: collections.defaultdict(lambda: collections.defaultdict(lambda: [0, 0])))
g = getter('report_births')
births = []
for r in rows['report_births']:
    site = g(r, 'site_facility')
    d = day(g(r, 'birth_date')) or day(g(r, 'added_on_antz'))
    if site in IX and d and date(2015, 1, 1) <= d <= TODAY:
        life[g(r, 'common_name') or 'Unknown'][SITES[IX[site]]['id']][d.strftime('%Y-%m')][0] += 1
        # THE NATALITY PAGE (29 Sep 2026): every birth since BIRTHS_FROM, one
        # row each, for assets/data/v2-births.json
        if d >= BIRTHS_FROM:
            n = g(r, 'common_name') or 'Unknown'
            if n not in species: species[n] = {'n': n, **REF.get(n, {}), 's': {}}
            gx = (g(r, 'gender') or '').lower()
            births.append([(TODAY - d).days, n, IX[site], 0 if gx == 'male' else 1 if gx == 'female' else 3 if gx == 'indeterminate' else 2,
                           int(g(r, 'antz_animal_id') or 0), g(r, 'identifier_type') or '', (g(r, 'identifier_value') or '').strip("' "),
                           g(r, 'enclosure_name') or '', 1 if day(g(r, 'birth_date')) else 0])
for d, r, site in deaths_all:
    g = getter('report_deaths')
    life[g(r, 'common_name') or 'Unknown'][SITES[IX[site]]['id']][d.strftime('%Y-%m')][1] += 1

# THE MORTALITY PAGE (29 Sep 2026): every death since BIRTHS_FROM, one row
# each, for assets/data/v2-deaths.json — with the age at death and the time
# from arrival to death where the record carries the dates for them
gd = getter('report_deaths')
deaths_page = []
def cause_of(v):
    # one row carries a fragment of pasted HTML before its words: keep the words
    v = (v or '').split('>')[-1].strip()
    return v[:1].upper() + v[1:] if v else 'Undetermined'
for d, r, site in deaths_all:
    if d < BIRTHS_FROM: continue
    n = gd(r, 'common_name') or 'Unknown'
    if n not in species: species[n] = {'n': n, **REF.get(n, {}), 's': {}}
    gx = (gd(r, 'gender') or '').lower()
    born, came = day(gd(r, 'birth_date')), day(gd(r, 'accession_date'))
    st = gd(r, 'necropsy_status')
    deaths_page.append([(TODAY - d).days, n, IX[site], 0 if gx == 'male' else 1 if gx == 'female' else 3 if gx == 'indeterminate' else 2,
                        int(gd(r, 'antz_animal_id') or 0), cause_of(gd(r, 'manner_of_death')),
                        0 if st == 'Pending' else 1 if st == 'Completed' else 2,
                        (d - born).days if born and born <= d else -1, (d - came).days if came and came <= d else -1,
                        gd(r, 'enclosure_name') or '', gd(r, 'identifier_type') or '', (gd(r, 'identifier_value') or '').strip("' ")])

# every species wears one of the project's own photographs, chosen by the
# kind of animal its name says — the same rule, lifted from v5db_build.py
src = open(os.path.join(HERE, 'tools', 'v5db_build.py'), encoding='utf-8').read()
ns = {'re': re}
exec(src[src.index('PHOTO_WORDS = ['):src.index('# ── events')], ns)
KLASS = {'Mammalia': 'mammal', 'Aves': 'aves', 'Reptilia': 'reptile'}
for s in species.values():
    s['p'] = ns['photo'](s['n'], KLASS.get(s.get('c'), 'other'))
photo = {}
SP = sorted(species.values(), key=lambda s: s['n'])
SPI = {s['n']: i for i, s in enumerate(SP)}
out = {
    'source': 'Dump20260622.sql · species_mgmt_anon', 'today': TODAY.isoformat(), 'sites': SITES,
    'caps': {'animals': ANIMAL_CAP, 'deathDays': DEATH_DAYS, 'necropsy': NECROPSY_CAP, 'doseDays': DOSE_DAYS},
    'species': SP,
    'animals': ANIMALS,
    'deaths': keep,
    'necropsyTotals': {k: dict(v) for k, v in nec_total.items()},
    'doses': doses,
    'life': {n: {k: dict(m) for k, m in per.items()} for n, per in life.items() if n in species},
}
os.makedirs(os.path.dirname(OUT), exist_ok=True)
json.dump(out, open(OUT, 'w'), separators=(',', ':'), ensure_ascii=False)
# the Natality page's births, in their own file, fetched only by that page
IDT, ENC = [], []
def ixof(lst, v):
    if v not in lst: lst.append(v)
    return lst.index(v)
brows = [[a, SPI[n], si, x, aid, ixof(IDT, it), iv, ixof(ENC, en), dk] for a, n, si, x, aid, it, iv, en, dk in sorted(births, key=lambda b: (b[0], -b[4]))]
BOUT = os.path.join(HERE, 'assets', 'data', 'v2-births.json')
json.dump({'today': TODAY.isoformat(), 'from': BIRTHS_FROM.isoformat(), 'idTypes': IDT, 'enclosures': ENC, 'rows': brows}, open(BOUT, 'w'), separators=(',', ':'), ensure_ascii=False)
print('births', len(brows), 'bytes', os.path.getsize(BOUT))
# …and the Mortality page's deaths:
#   [days ago, species index, site index, sex (as births), AID, cause index,
#    necropsy (0 pending, 1 completed, 2 not referred), age at death in days
#    (-1 unknown), days from arrival to death (-1 unknown), enclosure index,
#    identifier type index, identifier]
CAU, DENC, DIDT = [], [], []
drows = [[a, SPI[n], si, x, aid, ixof(CAU, c), nc, ag, sv, ixof(DENC, en), ixof(DIDT, it), iv] for a, n, si, x, aid, c, nc, ag, sv, en, it, iv in sorted(deaths_page, key=lambda b: (b[0], -b[4]))]
DOUT = os.path.join(HERE, 'assets', 'data', 'v2-deaths.json')
json.dump({'today': TODAY.isoformat(), 'from': BIRTHS_FROM.isoformat(), 'causes': CAU, 'idTypes': DIDT, 'enclosures': DENC, 'rows': drows}, open(DOUT, 'w'), separators=(',', ':'), ensure_ascii=False)
print('deaths', len(drows), 'bytes', os.path.getsize(DOUT))
print('species', len(out['species']), 'animals', sum(map(len, ANIMALS.values())), 'deaths', len(keep), 'doses', len(doses),
      'necropsy', out['necropsyTotals'], 'bytes', os.path.getsize(OUT))
