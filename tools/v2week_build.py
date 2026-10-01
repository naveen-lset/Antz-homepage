"""This week's animals for V2's health-strip sheet → assets/data/v2-week.json.

The ticker's sheet drills from a species into the animals behind its count
(owner, 1 Oct 2026: "tap a species → its animals: animal id, enclosure, site,
identifier"). The rows already exist in v2-births.json / v2-deaths.json, but
those key species by an index into the 3.6MB v2-modules.json, and a tap on the
home ticker should not fetch ~5MB. This keeps only the last WEEK days, keyed by
species NAME (the v5db.js names the ticker counts), so the file is a few KB.

Reads the three compiled files (not the dump), so it agrees with the Natality
and Mortality pages and with the ticker: 76 births / 192 deaths on 20 May 2026.

  births[name] = [[days ago, site index, sex, AAID, id type, id value, enclosure], …]
  deaths[name] = [[days ago, site index, sex, AAID, id type, id value, enclosure, cause, record], …]
  species[name] = [class, IUCN, photo]   (photo: assets/img/species/<photo>.jpg)
    site index → `sites` (v5db.js's slot ids, same order); sex 0 male, 1 female,
    2 undetermined, 3 indeterminate; record 1 when v2-modules.json holds the
    death record (#m/mortality/animal/<AAID> opens it).

Usage: python3 tools/v2week_build.py
"""
import json, os, collections
HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
D = lambda n: os.path.join(HERE, 'assets', 'data', n)
WEEK = 7
M = json.load(open(D('v2-modules.json'), encoding='utf-8'))
B = json.load(open(D('v2-births.json'), encoding='utf-8'))
X = json.load(open(D('v2-deaths.json'), encoding='utf-8'))
assert M['today'] == B['today'] == X['today'], 'the three files are from different days'
SP = [s['n'] for s in M['species']]
recorded = {r[0] for r in M['deaths']}

births, deaths = collections.defaultdict(list), collections.defaultdict(list)
for a, si, st, x, aid, it, iv, en, _dated in B['rows']:
    if a < WEEK: births[SP[si]].append([a, st, x, aid, B['idTypes'][it], iv, B['enclosures'][en]])
for a, si, st, x, aid, c, _nec, _age, _since, en, it, iv in X['rows']:
    if a < WEEK: deaths[SP[si]].append([a, st, x, aid, X['idTypes'][it], iv, X['enclosures'][en], X['causes'][c], 1 if aid in recorded else 0])

# what the sheet draws for each species in it: class (a keeper's word), IUCN, the project photograph
ONE = {'Mammalia': 'Mammal', 'Aves': 'Bird', 'Reptilia': 'Reptile', 'Amphibia': 'Amphibian', 'Teleostei': 'Fish'}
meta = {s['n']: [ONE.get(s.get('c'), 'Other'), s.get('iucn') or '', s.get('p') or ''] for s in M['species'] if s['n'] in births or s['n'] in deaths}
out = {'today': M['today'], 'days': WEEK, 'sites': [s['id'] for s in M['sites']], 'species': meta, 'births': births, 'deaths': deaths}
json.dump(out, open(D('v2-week.json'), 'w', encoding='utf-8'), separators=(',', ':'), ensure_ascii=False)
print('births', sum(map(len, births.values())), 'in', len(births), 'species ·',
      'deaths', sum(map(len, deaths.values())), 'in', len(deaths), 'species ·',
      'with a record', sum(r[8] for v in deaths.values() for r in v), '·', os.path.getsize(D('v2-week.json')), 'bytes')
