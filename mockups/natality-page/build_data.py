"""Births at V2's four sites, from the V5 extract, for mockups/natality-page.html.
Every birth event of the last two years: [day, species, site, sex]."""
import json, struct, collections
R = '/Users/naveen/Documents/antz-command-centre-v5/public/data/'
D = json.load(open(R + 'dims.json')); EV = open(R + 'events.bin', 'rb').read()
M = json.load(open('assets/data/v2-modules.json'))
col = lambda off, n, fmt: struct.unpack_from(f'<{n}{fmt}', EV, off)
f = D['flows']['births']; TODAY = D['meta']['historyDays'] - 1
SEXV = f['facets']['sex']['values']            # Undetermined, Female, Male, Indeterminate
SEXK = {'Male': 0, 'Female': 1}                # else 2 = unsexed
cat = {s['n']: s for s in M['species']}
names, ix = [], {}
ev = []
for site in M['sites']:
    key = next(s['key'] for s in D['sites'] if s['name'] == site['name'])
    a, n = dict(f['slices'])[key]
    day = col(f['day'] + a * 2, n, 'H'); sp = col(f['species'] + a * 2, n, 'H')
    sx = col(f['facets']['sex']['offset'] + a * 2, n, 'H')
    for d, s, x in zip(day, sp, sx):
        if TODAY - d >= 730 or d > TODAY: continue
        nm = D['species'][s]['name']
        if nm not in ix: ix[nm] = len(names); names.append(nm)
        ev.append([TODAY - d, ix[nm], M['sites'].index(site), SEXK.get(SEXV[x], 2)])
sp = []
for nm in names:
    c = cat.get(nm) or {}
    src = next((x for x in D['species'] if x['name'] == nm), {})
    sp.append({'n': nm, 'l': c.get('l') or '', 'c': c.get('c') or src.get('cls') or 'Other',
               'iucn': c.get('iucn') or (src.get('iucn') or '').split(' (')[0], 'p': c.get('p') or ''})
out = {'today': D['meta']['today'], 'sites': [{'id': s['id'], 'name': s['name'], 'short': s['short']} for s in M['sites']],
       'species': sp, 'ev': ev}
open('mockups/natality-page/data.js', 'w').write('window.NAT = ' + json.dumps(out, separators=(',', ':')) + ';\n')
print(len(ev), 'births,', len(sp), 'species', collections.Counter(e[3] for e in ev), collections.Counter(e[2] for e in ev))
print(sum(1 for e in ev if e[0] < 7), 'this week', sum(1 for e in ev if e[0] < 30), 'this month')
