"""Compile the V5 app's database extract (antz-command-centre-v5/public/data,
itself built from Dump20260622.sql by tools/etl/build.py) into the small,
V2-only data module js/data/v5db.js. Names and numbers only; photos are the
project's own, chosen by kind."""
import json, struct, re, collections, sys
R = '/Users/naveen/Documents/antz-command-centre-v5/public/data/'
D = json.load(open(R + 'dims.json')); P = json.load(open(R + 'profiles.json'))
EV = open(R + 'events.bin', 'rb').read(); AN = open(R + 'animals.bin', 'rb').read()
col = lambda buf, off, n, fmt: struct.unpack_from(f'<{n}{fmt}', buf, off)
TODAY = D['meta']['historyDays'] - 1
SLOTS = ['bg-safari', 'bg-zoo', 'hg-field', 'ms-rescue']
sites = sorted(D['sites'], key=lambda s: -s['animals'])[:4]
slug = lambda n: re.sub(r'^-|-$', '', re.sub(r'[^a-z0-9]+', '-', n.lower()))
KLASS = {'Mammalia': 'mammal', 'Aves': 'aves', 'Reptilia': 'reptile'}

# ── the photos this project already has, by kind ──
PHOTO_WORDS = [
  (r'macaque|langur|monkey|tamarin|marmoset|capuchin|baboon|lemur|loris', ['bonnet-macaque', 'rhesus-macaque']),
  (r'orangutan|gibbon|chimp|gorilla|\bape\b', ['sumatran-orangutan']),
  (r'tiger', ['bengal-tiger']), (r'leopard|panther|jaguar|ocelot|lynx|\bcat\b|caracal|serval', ['indian-leopard']),
  (r'\blion\b', ['asiatic-lion']), (r'bear|badger|wolverine|honey', ['sloth-bear']),
  (r'gaur|bison|buffalo|cattle|\bbull\b|yak|takin', ['gaur']), (r'nilgai', ['nilgai']),
  (r'deer|sambar|muntjac|chital|barasingha|elk|moose', ['chital', 'sambar', 'barasingha']),
  (r'buck|antelope|gazelle|duiker|tahr|goat|sheep|ibex|oryx|impala|kudu|eland', ['blackbuck', 'nilgai']),
  (r'vulture|condor', ['cinereous-vulture']), (r'kite|hawk|eagle|kestrel|falcon|buzzard|harrier|owl|osprey', ['black-kite']),
  (r'parakeet|parrot|macaw|cockatoo|lory|lorikeet|conure|cockatiel|budgerigar', ['rose-ringed-parakeet']),
  (r'crane|stork|heron|ibis|egret|plover|flamingo|spoonbill|bustard', ['sarus-crane']),
  (r'peafowl|peacock|pheasant|fowl|partridge|quail|turkey|grouse', ['indian-peafowl']),
  (r'myna|oriole|warbler|tanager|finch|sparrow|robin|thrush|starling|hoopoe|roller|toucan|hornbill|kingfisher|bulbul|sunbird|dove|pigeon', ['hill-myna']),
  (r'snake|python|(?<!jer)boa|krait|cobra|viper|adder|mamba|racer', ['indian-rock-python']),
  (r'tortoise|turtle|terrapin', ['indian-star-tortoise']),
  (r'scorpion|spider|tarantula|beetle|mantis|centipede|millipede', ['giant-forest-scorpion']),
]
BY_CLASS = {'mammal': ['chital', 'sambar', 'gaur', 'nilgai', 'blackbuck', 'barasingha', 'sloth-bear', 'bonnet-macaque'],
            'aves': ['hill-myna', 'rose-ringed-parakeet', 'indian-peafowl', 'sarus-crane', 'black-kite'],
            'reptile': ['indian-rock-python', 'indian-star-tortoise'], 'other': ['giant-forest-scorpion']}
def photo(name, klass):
    h = sum(map(ord, name))
    for pat, files in PHOTO_WORDS:
        if re.search(pat, name, re.I): return files[h % len(files)]
    pool = BY_CLASS.get(klass, BY_CLASS['other']); return pool[h % len(pool)]

# ── events, per flow, per site: (day, species index, animal id) ──
SPIX = {}  # species index in events → species row; events use the dims species list index
def flow_rows(metric, site_key):
    f = D['flows'].get(metric)
    if not f or site_key not in f['slices']: return []
    a, n = f['slices'][site_key]
    day = col(EV, f['day'] + a * 2, n, 'H'); sp = col(EV, f['species'] + a * 2, n, 'H'); an = col(EV, f['animal'] + a * 4, n, 'i')
    return list(zip(day, sp, an))
# animals: id → sex
N = D['animals']['count']
AID = col(AN, D['animals']['id'], N, 'i'); ASEX = col(AN, D['animals']['sex'], N, 'B')
SEX = dict(zip(AID, ASEX))
# which code is male/female? count by species name hint later; ETL uses 1=male 2=female conventionally
sex_counts = collections.Counter(ASEX)

TYPES = r'\s+(Wetland Quarter Park|Wildlife Estate|Wildlife Haven|Wildlife Centre|Wildlife Reserve|Nature Reserve|Rescue Centre|Zoological Park|Habitat|Sanctuary|Refuge|Biopark)$'
def short(name):
    s = re.sub(TYPES, '', name)
    return s if s and s != name else name
out_sites, species, flows, staff = [], {}, {}, {}
def klass_of(row): return KLASS.get(row['cls'], 'other')
for slot, s in zip(SLOTS, sites):
    here = [r for r in D['species'] if r['siteKey'] == s['key']]
    users = [u for u in D['users'] if u['siteKey'] == s['key']]
    out_sites.append({'id': slot, 'key': s['key'], 'name': s['name'], 'short': short(s['name']),
                      'code': s['code'], 'counts': {'sections': s['sections'], 'enclosures': s['enclosures'], 'staff': len(users), 'species': len(here), 'animals': s['animals']}})
    staff[slot] = [{'name': u['name'], 'role': u['role']} for u in sorted(users, key=lambda u: -(u['observations'] + u['records'] + u['assessments'])) if u['role'] != 'Super Admin'][:12]
    # the catalogue: the five largest holdings of each class at this site
    byk = collections.defaultdict(list)
    for r in sorted(here, key=lambda r: -r['weight']): byk[klass_of(r)].append(r)
    picks = [r for k in ('mammal', 'aves', 'reptile', 'other') for r in byk[k][:5]]
    # first arrival of each species at this site, for "New"
    acc = flow_rows('accession', s['key'])
    idx = {i: r for i, r in enumerate(D['species'])}
    first = {}
    for d, spx, _ in acc:
        nm = idx[spx]['name'] if spx in idx else None
        if nm: first[nm] = min(first.get(nm, 99999), d)
    for r in picks:
        e = species.setdefault(r['name'], {'name': r['name'], 'latin': P.get(slug(r['name']), {}).get('scientific_name'), 'klass': klass_of(r),
             'iucn': (r.get('iucn') or '').split(' (')[0] or None, 'cites': (r.get('cites') or '').split(' (')[0] or None,
             'photo': photo(r['name'], klass_of(r)), 'bySite': {}, 'added': None})
        e['bySite'][slot] = r['weight']
        if r['name'] in first:
            ago = TODAY - first[r['name']]
            e['added'] = ago if e['added'] is None else min(e['added'], ago)
    # the flows the V2 cards and Key Insights read
    def window(metric, days):
        rows = [x for x in flow_rows(metric, s['key']) if TODAY - days < x[0] <= TODAY]
        per = collections.Counter(idx[x[1]]['name'] for x in rows if x[1] in idx)
        return {'total': len(rows), 'rows': [{'name': n, 'count': c} for n, c in per.most_common(8)]}, rows
    fl = {}
    for m, key in [('births', 'natality'), ('mortality', 'mortality')]:
        fl[key] = window(m, 10)[0]; fl[key]['days'] = 10
    # transfers are rare here (20 at the largest site in six years), so they
    # are counted over a year — ONE window at every site, so that sites added
    # together are added over the same days
    w, _ = window('transfers', 365)
    fl['transfers'] = {**w, 'days': 365}
    # arrivals: the last 7 days, else the last 30 — with the sex of each animal
    for days in (7, 30, 90):
        w, rows = window('accession', days)
        if w['total']: break
    arr = collections.defaultdict(lambda: [0, 0, 0])
    for d, spx, aid in rows:
        if spx not in idx: continue
        sx = SEX.get(aid, 0); arr[idx[spx]['name']][0 if sx == 1 else 1 if sx == 2 else 2] += 1
    fl['arrivals'] = {'days': days, 'total': w['total'], 'rows': [{'name': n, 'm': v[0], 'f': v[1], 'u': v[2]} for n, v in sorted(arr.items(), key=lambda kv: -sum(kv[1]))[:4]]}
    flows[slot] = fl
    # everything a flow row names must be in the catalogue, for its latin, class and photo
    for key in ('natality', 'mortality', 'transfers', 'arrivals'):
        for r in fl[key]['rows']:
            if r['name'] not in species:
                src = next((x for x in D['species'] if x['name'] == r['name']), None)
                k = klass_of(src) if src else 'other'
                species[r['name']] = {'name': r['name'], 'latin': P.get(slug(r['name']), {}).get('scientific_name'), 'klass': k,
                    'iucn': ((src or {}).get('iucn') or '').split(' (')[0] or None, 'cites': ((src or {}).get('cites') or '').split(' (')[0] or None,
                    'photo': photo(r['name'], k), 'bySite': {}, 'added': None, 'listed': False}

home = SLOTS[0]
hs = [e for e in species.values() if home in e['bySite']]
seed = []
for k in ('mammal', 'aves', 'reptile', 'mammal'):
    c = next((e for e in sorted(hs, key=lambda e: -e['bySite'][home]) if e['klass'] == k and e['name'] not in seed), None)
    if c: seed.append(c['name'])
# one real animal for the note cards' plate: the first registered animal of
# the home site's lead species
sp_rows = {i: r for i, r in enumerate(D['species'])}
ASP = col(AN, D['animals']['species'], N, 'H'); ASITE_KEY = sites[0]['key']
plate = None
for i in range(N):
    r = sp_rows.get(ASP[i])
    if r and r['siteKey'] == ASITE_KEY and r['name'] == seed[0]: plate = {'aid': AID[i], 'species': seed[0]}; break
db = {'plate': plate, 'source': 'Dump20260622.sql · species_mgmt_anon', 'today': D['meta']['today'], 'sites': out_sites,
      'species': sorted(species.values(), key=lambda e: e['name']), 'seed': seed, 'flows': flows, 'staff': staff,
      'sexCodes': {str(k): v for k, v in sex_counts.items()}}
json.dump(db, open(sys.argv[1], 'w'), separators=(',', ':'), ensure_ascii=False)
print('sites', [(s['id'], s['name'], s['short'], s['counts']) for s in out_sites])
print('species', len(species), 'seed', seed, 'sexCodes', dict(sex_counts))
for sl in SLOTS: print(sl, {k: (v['total'], v['rows'][:3]) for k, v in flows[sl].items() if k != 'arrivals'}, flows[sl]['arrivals'])
print('bytes', len(json.dumps(db, separators=(',', ':'))))
