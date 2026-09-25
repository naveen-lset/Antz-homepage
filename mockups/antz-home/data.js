/* ANTZ Home — redesign prototype · MOCK DATA ONLY
   Nothing here talks to an API. Every figure is invented for design review,
   in the shape the live product uses (sites, sections, enclosures, AAIDs). */
(function () {
  const SP = '../../assets/img/species/'
  const IMG = '../../assets/img/'

  const USER = { name: 'Sourav Tambe', first: 'Sourav', role: 'Curator', site: 'Bannerghatta Safari', avatar: IMG + 'avatar.png' }

  const SPECIES = [
    { id: 'tara',  species: 'Asian Elephant',       name: 'Tara',   status: 'Healthy', tone: 'ok',    meta: '42 yrs', img: 'img/asian-elephant.jpg', sci: 'Elephas maximus', enclosure: 'ELE-02 · Elephant Camp', keeper: 'Ramesh Patil' },
    { id: 'raja',  species: 'Asiatic Lion',         name: 'Raja',   status: 'Under observation', tone: 'warn', meta: '9 yrs', img: SP + 'asiatic-lion.jpg', sci: 'Panthera leo persica', enclosure: 'CAR-01 · Lion House 2', keeper: 'Anita Deshmukh' },
    { id: 'zara',  species: 'Indian Leopard',       name: 'Zara',   status: 'Healthy', tone: 'ok',    meta: '3 yrs',  img: SP + 'indian-leopard.jpg', sci: 'Panthera pardus fusca', enclosure: 'CAR-03 · Leopard Den', keeper: 'Anita Deshmukh' },
    { id: 'shera', species: 'Bengal Tiger',         name: 'Shera',  status: 'Healthy', tone: 'ok',    meta: '11 yrs', img: SP + 'bengal-tiger.jpg', sci: 'Panthera tigris tigris', enclosure: 'CAR-02 · Tiger Moat', keeper: 'Vikram Rao' },
    { id: 'bhalu', species: 'Sloth Bear',           name: 'Bhalu',  status: 'In hospital', tone: 'bad', meta: '14 yrs', img: SP + 'sloth-bear.jpg', sci: 'Melursus ursinus', enclosure: 'Hospital · ICU 2', keeper: 'Dr. Meera Nair' },
    { id: 'mina',  species: 'Sumatran Orangutan',   name: 'Mina',   status: 'New arrival', tone: 'info', meta: '6 yrs', img: SP + 'sumatran-orangutan.jpg', sci: 'Pongo abelii', enclosure: 'PRI-04 · Primate Island', keeper: 'Kian Joseph' },
    { id: 'kalu',  species: 'Blackbuck',            name: 'Herd B', status: 'Healthy', tone: 'ok',    meta: '64 animals', img: SP + 'blackbuck.jpg', sci: 'Antilope cervicapra', enclosure: 'HRB-02 · Hoofstock Barn', keeper: 'Ramesh Patil' },
    { id: 'sara',  species: 'Sarus Crane',          name: 'Pair 3', status: 'Nesting', tone: 'info', meta: '2 eggs', img: SP + 'sarus-crane.jpg', sci: 'Antigone antigone', enclosure: 'WET-01 · Wetland Aviary', keeper: 'Priya Menon' },
    { id: 'star',  species: 'Indian Star Tortoise', name: 'Group 1', status: 'Healthy', tone: 'ok',   meta: '43 animals', img: SP + 'indian-star-tortoise.jpg', sci: 'Geochelone elegans', enclosure: 'REP-01 · Reptile House', keeper: 'Kian Joseph' },
  ]

  const ANNOUNCEMENTS = [
    { id: 'a1', cat: 'Veterinary', title: 'Annual Health Assessment', body: 'Schedule updated for all large mammal enclosures. Keepers should confirm crate-training status by Friday so the vet team can plan sedation-free checks.', date: '12 Sep 2026', img: IMG + 'hospital.jpg' },
    { id: 'a2', cat: 'Exhibits', title: 'Zara and Kian go on exhibit Monday', body: 'The leopard cubs move to the public viewing yard from 10:00. Expect larger crowds at the Carnivore Safari; visitor flow will be one-way.', date: '11 Sep 2026', img: IMG + 'hero-leopard.jpg' },
    { id: 'a3', cat: 'Nutrition', title: 'Fresh browse moves to mornings', body: 'Browse deliveries arrive at 07:30 from this week. Kitchen teams please prioritise herbivore sections before the heat of the day.', date: '10 Sep 2026', img: IMG + 'diet-kitchen.jpg' },
    { id: 'a4', cat: 'Safety', title: 'Monsoon drill on Thursday', body: 'A site-wide flood response drill runs 15:00–16:00. Low-lying enclosures in the Wetland section will practise the move-up protocol.', date: '09 Sep 2026', img: IMG + 'v3-hero.jpg' },
    { id: 'a5', cat: 'Conservation', title: 'Cheetah coalition health report', body: 'All four males passed quarterly checks. Body condition scores are stable and the enrichment programme is showing results.', date: '07 Sep 2026', img: IMG + 'v3-species.png' },
    { id: 'a6', cat: 'Aviary', title: 'Parakeet flock rehomed', body: 'The rescued rose-ringed parakeets have moved to Aviary 3 after quarantine. Night-time temperature logging continues for two weeks.', date: '05 Sep 2026', img: IMG + 'v3-note-photo.png' },
  ]

  /* NOTES · the live V4 card's own shape: a priority, the entity it is about
     (an animal by AAID or an enclosure by code), tags, and the reactions */
  const NOTES = [
    { id: 'n1', pri: 'critical', kind: 'animal', ent: 'AAID : 87546/24', entName: 'Big Bull', more: 2, title: 'Deep Flank Wound', date: '03 Sep', ago: '10 min ago', tags: ['Open Wound', 'Bleeding'], body: 'Found a 6cm laceration on the left flank during the morning check, still bleeding lightly. Separated him into the night house and called the duty vet.', who: 'Ramesh Patil', likes: 12, comments: 4, img: IMG + 'obs-animal.png', isNew: true, mine: false },
    { id: 'n2', pri: 'high', kind: 'enclosure', ent: 'ENC : HB-04', entName: 'Hoofstock Barn', more: 0, title: 'Metal Work', date: '02 Sep', ago: '42 min ago', tags: ['Rust and Corrosion', 'Structural Changes'], body: 'The lower rail on the north gate has rusted through where it meets the post, and the whole panel now flexes when the animals lean on it.', who: 'Anita Deshmukh', likes: 31, comments: 9, img: null, thumb: IMG + 'hospital.jpg', isNew: true, mine: true },
    { id: 'n3', pri: 'moderate', kind: 'animal', ent: 'AAID : 44120/25', entName: 'Zara', more: 1, title: 'Feed Refusal', date: '01 Sep', ago: '1 hr ago', tags: ['Appetite', 'Diet Change'], body: 'Third morning running that she has left the meat and taken only the browse. Weight is steady and she is bright and active.', who: 'Dr. Meera Nair', likes: 8, comments: 6, img: IMG + 'hero-leopard.jpg', isNew: true, mine: false },
    { id: 'n4', pri: 'low', kind: 'animal', ent: 'AAID : 21077/19', entName: 'Bhalu', more: 0, title: 'Coat Condition', date: '31 Aug', ago: '3 hr ago', tags: ['Skin', 'Recovery'], body: 'Patchy fur on the shoulders is growing back after the diet change. Keep the supplement for another fortnight and re-photograph.', who: 'Priya Menon', likes: 5, comments: 2, img: '../../assets/img/species/sloth-bear.jpg', isNew: false, mine: true },
    { id: 'n5', pri: 'high', kind: 'enclosure', ent: 'ENC : AVI-02', entName: 'Aviary 2', more: 0, title: 'Water Line Leak', date: '30 Aug', ago: 'Yesterday', tags: ['Plumbing'], body: 'Small leak at the drinker. Plumbing ticket raised and the birds have a temporary bowl until it is fixed.', who: 'Kian Joseph', likes: 3, comments: 1, img: null, thumb: IMG + 'v3-parakeet.png', isNew: false, mine: false },
    { id: 'n6', pri: 'moderate', kind: 'animal', ent: 'AAID : 90311/22', entName: 'Pair 3', more: 1, title: 'Nest Building', date: '29 Aug', ago: 'Yesterday', tags: ['Breeding', 'Behaviour'], body: 'Pair 3 have started building on the island. Keep the wetland path closed so disturbance stays low this week.', who: 'Priya Menon', likes: 14, comments: 3, img: '../../assets/img/species/sarus-crane.jpg', isNew: false, mine: false },
  ]

  const REPORTS = [
    { id: 'r1', status: 'attention', title: 'Medical report pending sign-off', src: 'Veterinary', time: '10 min ago', module: 'medical' },
    { id: 'r2', status: 'critical',  title: 'Bhalu moved to ICU — respiratory distress', src: 'Hospital', time: '26 min ago', module: 'hospital' },
    { id: 'r3', status: 'attention', title: '12 pharmacy items below reorder level', src: 'Pharmacy', time: '1 hr ago', module: 'pharmacy' },
    { id: 'r4', status: 'info',      title: 'Lab results ready for 6 samples', src: 'Laboratory', time: '2 hr ago', module: 'lab' },
    { id: 'r5', status: 'ok',        title: 'Daily enclosure checks complete — Carnivore Safari', src: 'Housing', time: '3 hr ago', module: 'housing' },
    { id: 'r6', status: 'attention', title: '3 permits expire within 30 days', src: 'Compliance', time: 'Today, 08:10', module: 'reports' },
  ]

  /* THE MODULES. `level` is the brief's hierarchy; `sizes` are the predefined
     spans a card may take (w×h in grid cells), first one is the default at 5
     columns; `viz` names the visual language — each module speaks its own. */
  const MODULES = {
    medical:   { name: 'Medical', level: 1, tone: 'red',   icon: 'medical',  viz: 'severity',   sizes: ['2x2', '3x2', '2x1'], stat: ['14', 'open cases'], stat2: ['3', 'critical'] },
    species:   { name: 'Species Management', level: 1, tone: 'green', icon: 'species', viz: 'collection', sizes: ['3x2', '2x2', '5x2'], stat: ['28', 'species'], stat2: ['147', 'animals'] },
    hospital:  { name: 'Hospital', level: 1, tone: 'teal',  icon: 'hospital', viz: 'space',      sizes: ['2x2', '2x1', '3x2'], stat: ['12', 'occupied'], stat2: ['4', 'available'] },
    pharmacy:  { name: 'Pharmacy', level: 2, tone: 'slate', icon: 'pharmacy', viz: 'inventory',  sizes: ['2x1', '2x2', '1x1'], stat: ['248', 'stock items'], stat2: ['12', 'low stock'] },
    lab:       { name: 'Lab', level: 2, tone: 'slate',      icon: 'lab',      viz: 'pipeline',   sizes: ['3x1', '2x1', '1x1'], stat: ['18', 'awaiting results'], stat2: ['6', 'processing'] },
    tasks:     { name: 'Tasks', level: 2, tone: 'green',    icon: 'tasks',    viz: 'agenda',     sizes: ['1x2', '2x1', '1x1'], stat: ['52', 'open'], stat2: ['8', 'due today'] },
    housing:   { name: 'Housing', level: 2, tone: 'teal',   icon: 'housing',  viz: 'stat',       sizes: ['1x1', '2x1'], stat: ['23', 'enclosures'], stat2: ['6', 'sections'] },
    diet:      { name: 'Diet & Kitchen', level: 2, tone: 'amber', icon: 'diet', viz: 'progress', sizes: ['1x1', '2x1'], stat: ['31', 'feeds today'], stat2: ['19', 'done'] },
    administer:{ name: 'Administer', level: 3, tone: 'neutral', icon: 'administer', viz: 'compact', sizes: ['1x1'], stat: ['9', 'doses due'] },
    approvals: { name: 'Approvals', level: 3, tone: 'neutral', icon: 'approvals', viz: 'compact', sizes: ['1x1'], stat: ['5', 'waiting'] },
    security:  { name: 'Security', level: 3, tone: 'neutral', icon: 'security', viz: 'compact', sizes: ['1x1'], stat: ['0', 'incidents'] },
    comms:     { name: 'Communication', level: 3, tone: 'neutral', icon: 'comms', viz: 'compact', sizes: ['1x1'], stat: ['3', 'unread'] },
    /* not on the default Home — reachable from Add Module, Search, All Modules */
    users:     { name: 'Users', level: 3, tone: 'neutral', icon: 'users', viz: 'compact', sizes: ['1x1'], stat: ['86', 'staff'] },
    reports:   { name: 'Reports', level: 3, tone: 'neutral', icon: 'reports', viz: 'compact', sizes: ['1x1', '2x1'], stat: ['11', 'reports'] },
    eggs:      { name: 'Eggs & Incubation', level: 2, tone: 'amber', icon: 'eggs', viz: 'stat', sizes: ['1x1', '2x1'], stat: ['45', 'incubating'], stat2: ['1', 'hatching soon'] },
    mortality: { name: 'Mortality', level: 2, tone: 'red', icon: 'mortality', viz: 'stat', sizes: ['1x1', '2x1'], stat: ['3', 'this week'], stat2: ['9', 'in 10 days'] },
    parivesh:  { name: 'Parivesh', level: 3, tone: 'neutral', icon: 'reports', viz: 'compact', sizes: ['1x1'], stat: ['3', 'permits expiring'] },
    followup:  { name: 'Follow Up', level: 2, tone: 'teal', icon: 'tasks', viz: 'stat', sizes: ['1x1', '2x1'], stat: ['18', 'due, 7 days'], stat2: ['15', 'already late'] },
  }

  /* variants the Add Module flow offers — one visual idea each */
  const VARIANTS = {
    default: { label: 'Summary', note: 'The module’s own visual — what it is best at showing' },
    compact: { label: 'Compact', note: 'Icon, name and the one number that matters' },
    list:    { label: 'Needs attention', note: 'The top three items waiting on you' },
  }

  const DEFAULT_HOME = [
    { id: 'medical', size: '2x2' }, { id: 'species', size: '3x2' },
    { id: 'hospital', size: '2x2' }, { id: 'pharmacy', size: '2x1' }, { id: 'tasks', size: '1x2' },
    { id: 'lab', size: '2x1' },
    { id: 'housing', size: '1x1' }, { id: 'diet', size: '1x1' }, { id: 'administer', size: '1x1' },
    { id: 'approvals', size: '1x1' }, { id: 'security', size: '1x1' },
  ]

  const MEDICAL = {
    split: [{ k: 'critical', n: 3 }, { k: 'serious', n: 4 }, { k: 'stable', n: 7 }],
    cases: [
      { who: 'Bhalu', what: 'Respiratory distress', sev: 'critical', where: 'ICU 2' },
      { who: 'Big Bull', what: 'Flank laceration', sev: 'critical', where: 'Night house' },
      { who: 'Raja', what: 'Lameness, left fore', sev: 'serious', where: 'Lion House 2' },
    ],
  }
  const HOSPITAL = { beds: [1,1,1,0,1,1,1,1,0,1,1,1,0,1,0,1], wards: [['ICU', 2, 2], ['Ward A', 6, 8], ['Ward B', 4, 6]] }
  const PHARMACY = { low: [['Meloxicam 1.5mg/ml', 18], ['Ivermectin 1%', 24], ['Enrofloxacin 50mg', 31]] }
  const LAB = [['Received', 9], ['Processing', 6], ['Awaiting', 18], ['Reported', 22]]
  const TASKS = [['08:30', 'Weigh Mina', 'done'], ['10:00', 'Crate training · Tara', 'now'], ['11:30', 'Enclosure check · CAR-03', ''], ['14:00', 'Vet round · ICU', ''], ['16:00', 'Diet review', '']]
  const CLASSES = [['Mammals', 92], ['Birds', 31], ['Reptiles', 19], ['Others', 5]]

  /* context-aware quick actions — the palette leads with the context in view */
  const ACTIONS = {
    Species:  [['Add Animal', 'plus'], ['Transfer', 'transfer'], ['Accession', 'accession'], ['Add Eggs', 'eggs']],
    Medical:  [['New Case', 'medical'], ['Hospitalise', 'hospital'], ['Prescription', 'pharmacy'], ['Follow Up', 'tasks']],
    Pharmacy: [['Dispense', 'pharmacy'], ['Request', 'request'], ['Reorder', 'reorder'], ['Audit', 'approvals']],
    Hospital: [['Admit', 'hospital'], ['Transfer', 'transfer'], ['Discharge', 'discharge'], ['Isolation', 'security']],
  }


  /* QUICK ACTIONS · the live panel's own content (index.html
     HOME_QUICK_ACTIONS / QA_GROUPS / QA_RESUME), so the mock shows the
     design that is live, not a new one */
  const QA_GROUPS = [
    { id: 'clinical', name: 'Medical & Clinical Care', column: 0 },
    { id: 'animal', name: 'Animal Management', column: 0 },
    { id: 'ops', name: 'Operations & Administration', column: 1 },
    { id: 'estate', name: 'Site & System Management', column: 1 },
  ]
  const ICO = '../../assets/icon/'
  const QA_ACTIONS = [
    ['clinical', 'New Medical Record', 'qa-medical.svg'], ['clinical', 'Dispense Medicine', 'qa-medical.svg'], ['clinical', 'Hospitalise', 'qa-medical.svg'], ['clinical', 'Add Fetal Death', 'qa-fetal.svg'],
    ['animal', 'Transfer Animal', 'qa-paw.svg'], ['animal', 'Add Accession', 'qa-paw.svg'], ['animal', 'Add Eggs', 'qa-egg.svg'], ['animal', 'Report Missing / Escaped Animal', 'qa-paw.svg'],
    ['ops', 'New Request', 'qa-request.svg'], ['ops', 'New Note', 'qa-request.svg'], ['ops', 'New Announcement', 'qa-announce.svg'], ['ops', 'Add User', 'qa-user.svg'],
    ['estate', 'New Site', 'qa-site.svg'], ['estate', 'New Section', 'qa-section.svg'], ['estate', 'New Enclosure', 'qa-section.svg'], ['estate', 'Master Settings', 'qa-master.svg'],
  ].map(([group, label, icon]) => ({ group, label, icon: ICO + icon }))
  const QA_RESUME = [
    { kind: 'draft', label: 'Draft', action: 'New Medical Record', icon: ICO + 'qa-medical.svg', where: 'CAR-03 · Indian Leopard', ago: '14 min ago' },
    { kind: 'draft', label: 'Draft', action: 'Dispense Medicine', icon: ICO + 'qa-medical.svg', where: 'BER-01 · Sloth Bear', ago: '18 hr ago' },
    { kind: 'unsent', label: 'Not sent', action: 'Report Missing / Escaped Animal', icon: ICO + 'qa-paw.svg', where: 'HRB-02 · Blackbuck', ago: '40 min ago' },
    { kind: 'awaiting', label: 'With Curator', action: 'Transfer Animal', icon: ICO + 'qa-paw.svg', where: 'CAR-01 → Rescue Holding', ago: '2 days ago' },
    { kind: 'awaiting', label: 'With Finance', action: 'New Request', icon: ICO + 'qa-request.svg', where: 'Bannerghatta Safari', ago: '4 days ago' },
  ]

  const RECENT_SEARCHES = ['Tara', 'Meloxicam', 'CAR-03', 'Lab results', 'Bhalu']

  window.ANTZ = { QA_GROUPS, QA_ACTIONS, QA_RESUME, USER, SPECIES, ANNOUNCEMENTS, NOTES, REPORTS, MODULES, VARIANTS, DEFAULT_HOME, MEDICAL, HOSPITAL, PHARMACY, LAB, TASKS, CLASSES, ACTIONS, RECENT_SEARCHES }
})()
