# V2 on the Web: session handoff (8 Oct 2026)

Everything here applies to the **Web** layout only. That is V2 in a desktop browser at 1200px or wider, with a mouse or trackpad, and the head script sets `data-v2desk` on `<html>` to mark it. Tablet and phone are unchanged.

Run it locally: `python3 -m http.server 5175` from this folder, then open <http://localhost:5175/?v=2>.

## Home page: Figma `918:24`

Figma: <https://www.figma.com/design/CNhiaOGCLdnlNxj7x2Ohrd/Desktop-Navigation?node-id=918-24>

- **Header:** white, with rounded bottom corners and the search box on the right. There is no sky and no ticker.
- **Site chips:** a row across the page, with the ☰ site menu first.
- **Left column, 744px:** the Modules panel. It holds a 4-column grid of 162 × 144 tiles (`V2_DESK_LAYOUT`, seed 5, saved under `antz.home.layout.v2d`), with Observation Notes underneath.
  - The frame's first row repeats Housing three times. Medical, Housing, Pharmacy and Lab are used there for now, until the owner confirms the real modules.
- **Right column, 632px:**
  - **Favourites Animals.**
  - **Pending:** the catalogue card, drawn outside the grid. The app's module script exposes `window.__antzCard` for this.
  - **Announcements:** a vertical list showing three cards, with the rest scrolling inside the card. It no longer auto-advances.
- **Code locations:**
  - Layout moves: the `V2 ON THE WEB` script near the end of `index.html`.
  - Styles: the end of `review.css`. The block marked "FIGMA 918:24" overrides earlier web rules.

## Modules

- **Quick Actions opens the Modules Explorer.**
  - It is built by `openExplorer` in `ModulePages.js`, and the mockup is `mockups/all-modules-web.html` (design B).
  - Its sidebar lists Recent, All modules and the four areas, and the module list is grouped by area.
  - The right-hand panel shows the hovered module's description, an **Open** button and **Go straight to** links to its screens. Search covers screens too.
- **Every module opens a page.**
  - Species, Medical, Mortality, Eggs and Natality keep their built pages.
  - The other 15 use a sidebar shell (`MOD_FLOWS`). Its screens are placeholders, and only Pharmacy's list comes from a real screenshot.
- **Every module page has a web bar** with three parts:
  - the antz logo, which goes Home;
  - a module switcher showing the current module (for example "● Pharmacy ▾"). It searches, lists Recent and opens with ⌘K;
  - a breadcrumb.
- Home unwinds browser history using a depth counter on `history.state.md`.
- Recent modules are stored under `antz.home.recentModules`.

## Figma pushes

Both frames are on the "Claude Screens" page of the same file:

- **Web Home · Desktop (8 Oct):** `928:30`
- **Modules Explorer · Web (8 Oct):** `928:788`

Both were built with `tools/figma-push` from the site-command-centre branch. That converter crashes on hidden 0px text. A scratch copy was patched to clamp font sizes to at least 1px, but the fix has not been copied back to the tool.

## Mockups added

- `obs-widget-web.html`: three ways to place Observation Notes.
- `web-home-clean.html`: three decluttered home layouts.
- `all-modules-web.html`: three ways to present All Modules.

## Open questions

- Which modules belong in the first row of the grid?
- Should the ticker come back? The Figma frame leaves it out.
- The real screen lists for modules other than Pharmacy are needed.
- Should the switcher on module pages open the Explorer?

## Status (8 Oct 2026, end of session)

- **Deployed.** <https://home-page-changes.vercel.app/?v=2> serves this work. Vercel project `home-page-changes` (team `naveen-lsets-projects`); deploy `home-page-changes-oqxa7ua20`, made from a clean `git archive` of `bc39786`.
- **Not on GitHub yet.** The push was refused with a 403: this Mac's git is signed in as `Naveenkumar310`, and the repo is `naveen-lset/Antz-homepage`. Fix it by adding `Naveenkumar310` as a collaborator with Write access, or by pushing with a token from `naveen-lset`. Until then, another device can't pull this work.
- **Deploying from this Mac:** Node.js and the Vercel tool are installed under `~/.local/node/bin` (add that to PATH). The token is stored in `~/.vercel-token`. It was pasted into a chat, so revoke it and make a new one.
- `mockups/event-home.html` has edits made outside this session. They are not committed and were not deployed.

---

# Session 11 Oct 2026: role-based home

Run it: `python3 -m http.server 8080` from `/Users/naveen/Home Page`, then open <http://localhost:8080/Antz-Selected-Modules/>.

## Changed in the live build

- **Modules Explorer, one module per row and a narrower panel.** A short block in `review.css`, after the explorer's Figma 950:6513 rules:
  - `.mx__panel` is `min(880px, 100%)` wide (it was 1060);
  - `.mx__rows` is a single column.
- `index.html` line 13909 loads `review.css?v=20261011a` (bumped to clear the cache).

## Role-based home: the mockup the owner accepted

`mockups/role-home-live.html` is the one to carry forward. The owner rejected four hand-made designs and asked to "match my live home exactly".

- **How it works:** it loads `../index.html` in an iframe, so the page *is* the live home. A role changes only four things:
  1. **Modules grid:** writes a role layout to `antz.home.layout.v2d` (version 13, seed 5) using real card variants. Action cards are the role's quick access, for example `medical.actions` (New Case / Administer / Request Medicine), `administer.actions`, `pharmacy.actions`, `reports.actions` and `communication.actions`.
  2. **Pending card:** the six rows of `#v2dPending` are relabelled.
  3. **Favourites:** retitled to "My Patients" (Vet and Doctor) or "Watch List" (Zoologist) and refilled.
  4. **Role label:** a pill under the name.
- **Data:** the five role layouts are in the `ROLES` object at the top of the script. The visitor's own saved grid is restored on `pagehide`.
- **Cards to avoid on the web home:** `medical.pending` (draws a V3 sticky note) and `natality.list` (renders empty at full width).
- **Live-home rule:** the home always keeps a Species card and a Medical card (`CORE_VARIANTS`), so even Admin has them.

## Other mockups from this session (rejected or superseded, kept for reference)

- `mockups/role-home-web.html`: a hand-designed premium version. The owner disliked the look.
- `mockups/role-home-thinking.html`: the role research:
  - the real V5 staff roles: Vet 15, Supervisor 9, Biologist 9, Curator 2 and others;
  - findings from the data, such as the 72-death reptile cluster at Crimson Frosted, the 14,296 necropsy backlog and 9% of animals sexed at Crimson Frosted;
  - the Indian zoo-rule deadlines.

## Open questions for the owner

- **Doctor:** the para-vet / compounder, or the vet? No source has a "Doctor" role.
- **Zoologist:** merge it with Biologist, or make it a Welfare & Behaviour role? No V5, spec or CZA source has "Zoologist".
- **Supervisor (9 users) and Curator:** add them as roles?
- **Admin:** one role covering office and IT, or two?
- The deadline dates come from the 2009 Recognition of Zoo Rules. The 2013 and 2022 amendments haven't been checked.

## Not done

- **Not built into the live home.** The role switch exists only in the mockup wrapper.
- **Sample numbers:** Pending rows the V5 data doesn't track (Observations, Welfare assessments, Samples, Weights, Discharge review and so on).
- **Not committed:** this folder's `.git` points to a worktree that no longer exists (`/Users/naveen/Antz-homepage-1/.git/worktrees/Antz-Selected-Modules`), so git can't commit here.
- **Not deployed.**

# Session 13 Oct 2026: web version

## Round 1 was rejected and undone

The owner said it was "not matching the overall design concept". Round 1 had a gradient module hero, a floating module dock, home tiles reused as module widgets, and Announcements as a full-width band.

- `index.html` and `review.css` are restored to the 11 Oct state.
- A copy of round 1 is in `mockups/round1-rejected/` (as .txt, not served as a page).

## Round 2: review mockups in `mockups/web-v3/`

Built from the Figma file `CNhiaOGCLdnlNxj7x2Ohrd`:
- Home: 918:24.
- Module pages: "Patient Profile", 933:2949.

Open <http://localhost:8080/Antz-Selected-Modules/mockups/web-v3/home.html>.

**`home.html`** frames the live home and changes three things:
1. Announcements stay in the right column under Pending. That column now ends level with the Modules panel, and the list scrolls inside it with a fade.
2. Cards and tiles rise slightly on hover.
3. A module tile opens `module.html` and grows into its header.

**`module.html?m=<id>#t=<tab>`** covers all 20 modules. It is built from:
- Figma parts: the top bar with the module selector (⌘K), breadcrumbs, the header card with the site picker, the summary column (photo card, info card, Quick Actions, links), and the tabbed card with outlined pill tabs (dark-teal active).
- The Dashboard tab: the module's widgets, in the Figma "Monitoring Card" anatomy.

Widget types: trend, split, list, queue, progress, bars, timeline, note.

The other tabs show sample records. Switching tab or module never reloads (View Transitions), and browser Back works.

**Files:**
- `data.js`: the modules, their tabs, info, actions and widgets. All figures are SAMPLE.
- `app.js`: drawing and motion.
- `tokens.css`: the module gradients, copied from index.html.

## Module by module, in depth

**Hospital is done (1 of 20):** `hospital.js` + `screens.css`. `app.js` lets a module draw its own tab screens (`window.SCREENS[id].tabs`) and a record page inside it (`.patient`, at `#t=<tab>&p=<id>`).

Hospital has 41 in-patients (5 critical, 12 guarded, 24 stable) in 4 wards with 50 beds:
- **Admissions:** table, with filter chips.
- **Ward Occupancy:** a bed map for each ward, with hover cards.
- **Active Cases:** the Figma profile card for every patient.
- **Critical Care:** four vitals charts for each patient.
- **Discharges:** Ready / In review / Planned columns.
- **Reports:** report cards.

Every patient opens the **Figma Patient Profile** (933:2949), with its 13 tabs. Monitoring matches the frame, Overview has 4 widgets, and the other tabs list entries.

The Dashboard widgets count the same patients the tabs show.

**Next:** Medical, then Pharmacy, Lab, Species, Mortality, Eggs, Diet & Kitchen, Housing, and the rest. Each gets its own screens file.

## Open questions for the owner

1. "Same level": I read it as the Announcements container ending level with the Notes/Modules panel. Is that right?
2. Module navigation: tabs plus the module selector, without the Figma side rail. Is that right?
3. Each module's widget list in `data.js`: review module by module.

## Add Module widgets, module by module (13 Oct 2026, owner: "Each Module … Different Colours, Forms")

The owner meant the **Add Module sheet**: every module should offer proper widgets, in different shapes and colours.

The work happens in **`mockups/web-v3/widgets-preview.html`**, a copy of the live index.html. It adds a `<base href="../../">`, plus `window.__antzReq` and `window.__antzPicker` for review tooling. Live is untouched.

Open it, press **+** on Modules, and pick a module.

**Audit:** of 27 modules in the sheet:
- 5 have only the plain tile: Sites, Preventive Care, Necropsy, Assessment, Audit.
- Natality, Housing and Fetal Death are thin.
- Natality and Mortality "Ten-day listing" were empty blocks; they are old V4 report tiles.
- obs.rail draws nothing.
- housing.enclosures is listed twice.

**Done: Natality.** It has 10 widgets:
- default and This Week, as before;
- a ten-day births list in place of the empty block;
- this month;
- births by month;
- by class;
- to verify;
- 30-day survival;
- births by sex;
- newest arrival.

They use existing layouts in different module gradients (gold, cyan, deep teal, slate, coral, green). Mortality's empty ten-day listing is replaced the same way.

**Next:** the five tile-only modules, then Housing, Fetal Death and the rest. When approved, port the catalogue changes into the live index.html.

## State at close (13 Oct 2026)

- **Run it:** `python3 -m http.server 8080` from `/Users/naveen/Home Page`, then open:
  - <http://localhost:8080/Antz-Selected-Modules/mockups/web-v3/home.html> (home mockup);
  - `module.html?m=hospital` (module pages);
  - `widgets-preview.html` (Add Module widgets).
- **Live build:** `index.html` and `review.css` are the 11 Oct versions, restored. Today's work is only in `mockups/web-v3/` and `mockups/round1-rejected/`.
- **Not committed:** this folder's `.git` still points to `/Users/naveen/Antz-homepage-1/.git/worktrees/Antz-Selected-Modules`, which no longer exists, so git can't commit. Fix with `git -C "/Users/naveen/Home Page/Antz-homepage-1" worktree repair "/Users/naveen/Home Page/Antz-Selected-Modules"`. The 11 Oct changes are uncommitted too.
- **Not deployed:** <https://home-page-changes.vercel.app/?v=2> still serves the 8 Oct build.
- **Waiting on the owner:**
  - review Natality's widgets in the Add Module sheet;
  - review the Hospital module pages;
  - answer the "same level" and side-menu questions above.

# Session 19 Oct 2026: Figma push and phone top bar

## Run it
`python3 -m http.server 8080` from `/Users/naveen/Home Page`, then open <http://localhost:8080/Antz-Selected-Modules/?v=2> at phone width (390 in the browser's device toolbar).

## Earlier the same day (commit ad3947a)
- Recently viewed became four tabs (Recent / Favourites / Bookmarks / Folders). This is `mountAnimals` in `index.html`.
- The Your Modules sheet now shows only the owner's 20 modules.
- Bottom row: Modules wears the grid mark, Quick Actions the bolt.
- These were deployed at the time, but committed only now.

## Pushed to Figma
- **File:** CNhiaOGCLdnlNxj7x2Ohrd.
- **Frame:** `977:581` "Mobile · Home (19 Oct)" at (2667, −552). It is the live phone home, 390 × 3221: the top-of-page state with the dock pinned to the bottom.
- **Build:** 433 editable layers, made from Chrome's rendering of the page. A pixel diff against Chrome shows only text smoothing and photo resampling.
- **Outlined numbers:** 76, 192, 2,411 and 110,020. The page pins DM Sans to `opsz 14`, which Figma can't set.
- **Live icon:** still frame 14 of `hs-live.gif`, because frame 0 is blank.
- A frame named "Working" (`985:581`) appeared during the build. We didn't make it, so it was left alone.

## Phone top bar, from Figma `993:1725` (top section `993:2563`)
- **Card:** the Recents tabs and the rail share one card, 70% white with r12, 12 under the search and 16 over the band's foot. The sky now ends at 382.
- **Tabs:**
  - The picked tab hugs its 18px mark and its name ("Recents"), with a 2px #1F515B bar.
  - The other three show a 20px mark and share the rest of the row, 29 apart.
- **Rail:** 4 inside the card, with 132 × 158 cards 6 apart at r10.
- **Animation:** `place()` sets every tab width in px, so the tabs, names, marks and bar move on one 460ms curve. Measured on a phone viewport: about 2ms per tap, no long tasks.
- **Other changes:**
  - The ticker is 14 under the sky.
  - The 👋🏻 is 2.4 after the name, in a flex row.
- **Files:**
  - `index.html`, in `mountAnimals`: the `.fav__box` wrapper, `place()`, and the re-measure on fonts and resize.
  - `review.css`, in the phone block (≤743px): the "Recents · 993:2502" and "the tabs · 993:2503" rules.
  - `review.css`: `.fav__box { display: contents }` keeps 744px and up unchanged.
  - The stylesheet is now `review.css?v=20261019c`.
- **Deployed:**
  - Production deployment `home-page-changes-j23fee1y5` serves <https://home-page-changes.vercel.app/?v=2>. Vercel project `home-page-changes`, scope `naveen-lsets-projects`.
  - It was uploaded from a clean copy (`git ls-files -co`) and matches this session's commit.

## Live bugs found (reported, not fixed)
1. On load, `scrollIntoView({block:'nearest'})` on the active site tab jumps the phone page down 208px.
2. `html.v2-tabs-stuck` stays set after an instant jump to the top, so the sky band covers the deck's dots and "View all".
3. The closed profile drawer's shadow bleeds about 20px into the left edge.

## Open questions for the owner
- Fix the three bugs above?
- Should tablet and web get the same Recents card? Only phones have it now.
- An enclosure card's species line wraps to two lines ("Marbled Phantom / Saki"). This predates this session.

## Not done
- **Not pushed:** `CleanUp` is ahead of `origin`. Push with the work SSH URL (`github-work`).
- **Not synced:** `mockups/web-v3/widgets-preview.html` still has the morning's tabs, not this top bar.

# Session 19–20 Oct 2026: Recents folder tabs, iPhone fixes, sky doodles

## Run it
`python3 -m http.server 8080` from `/Users/naveen/Home Page`, then <http://localhost:8080/Antz-Selected-Modules/?v=2> at phone width (390).
- Open the mockups through localhost, not from the file. The iframes, and the masks in header-concepts.html, fail on `file://`.

## Built and live

### Recents card: soft pills and a white folder (phone only, ≤743px)
- **Look:**
  - The four tabs (Recents, Favourites, Bookmarks, Folders) are soft white pills: 54 tall, 6 apart, r12.
  - The picked tab turns white and opens into the rail as one folder: white, with a soft shadow and no outline.
  - The rail sits 12 inside the folder.
- **Motion:** the folder glides to the next tab on the tabs' 460ms curve, `cubic-bezier(.32, .72, 0, 1)`.
- **Tablet and desktop:** unchanged; they keep the old underlined tabs.
- **Files:**
  - `review.css`, phone block: "Recents · SOFT PILLS AND A WHITE FOLDER", plus `.fav__fold { display: none }` outside the phone block and a step down to 11px below 360px.
  - `index.html`, `mountAnimals`: "THE WHITE FOLDER", made of `foldPath()`, `foldTo()` and `settle()`. `place()` calls `foldTo()`, and the ResizeObserver also watches the box.
- **How it got here** (owner's words):
  - "implement the Soft Pills" (variant A of `mockups/recents-folder-tabs.html`).
  - "pills between, reduce little" (gap 8 → 6).
  - "corner radius 8 or 6px", then "follow the corner radius of other containers" (r12).
  - "no breathing space" (inset 12).
  - "remove the outline".

### iPhone fixes (owner's screenshot: the app opened scrolled down, with a white strip above it)
- **Opens at the top:**
  - The site tabs' `draw()` used `scrollIntoView({block:'nearest'})`, which scrolled the page 208–222px down on load. This was live bug 1 from the earlier 19 Oct session.
  - It now scrolls only `.site-tabs__track` sideways.
  - The head script sets `history.scrollRestoration = 'manual'`.
- **Notch / status bar:**
  - `apple-mobile-web-app-status-bar-style` stays `default`. From iOS 26.1, home-screen apps on `black-translucent` get a forced dark scrim and blur over the top, and a short safe-area inset (WebKit bug 301108).
  - iOS paints the default bar in the page's colour. So `:root.has-wsky` is now `linear-gradient(#fff, #fff) no-repeat, #E6EEED` (the sky's top edge), and `theme-color` is `#E6EEED`. The page itself stays white.
  - **Not yet confirmed on a device.**

### Deploys (Vercel project `home-page-changes`, scope `naveen-lsets-projects`)
| Commit | What | Deployment |
|---|---|---|
| `8f9950c` | soft pills, r8 | `home-page-changes-ol155h5xy` |
| `a7dba3e` | r12, 12 inset, no outline | `home-page-changes-7iz7rsya4` |
| `6653229` | opens at the top; status bar colour | `home-page-changes-5oawoga01` (current production) |

Each deploy was made from a clean copy (`git ls-files -co`) with `vercel deploy --prod`. Delete the `.env.local` that `vercel link` writes before deploying.

## Mockups (review only)
- **`mockups/header-concepts.html`:** five header directions from the owner's Blinkit, Instamart and Zepto references (Sky, Module stores, Mint bento, Night rounds, Festival lights). The owner set these aside ("leave this concept now") and kept only Zepto's folder-tab idea.
- **`mockups/recents-folder-tabs.html`:** variants A Soft pills, B Open tabs and C Icons only, over the live home. A is now live; this page strips the live folder and draws its own.
- **`mockups/sky-doodles.html`** (new, waiting for the owner): subtle animal doodles and sparkles in the sky band behind the greeting.
  - **How:** one `.dd` layer is added inside `.wsky`.
  - **Variants:**
    - A Floating doodles: they sway in place.
    - B Drawn one by one: each draws itself in, sparkles pop, then it fades; at most 3 at once.
    - C Wanderers: a paw trail, a gull and a butterfly on an `offset-path`.
  - **Colours:** ink #1F515B at 16–24%; sparkles #00ABAB and #FFE86E.
- **Gotchas for these mockups:**
  - Scale the phones with `zoom`, not a transform. Under a transform the live fixed layers escape the rounded clip.
  - When zoomed, the live search-row observer (threshold 1) reads "stuck", so the mockups clear `.search-row.is-stuck` at the top.

## Open questions for the owner
- Which sky-doodle variant (A, B or C), and stronger or fainter?
- After closing and reopening the home-screen app: does it open at the top, and is the strip behind the notch now mint-grey?
- Live bugs 2 and 3 from the earlier 19 Oct session are still open.

## Not done
- **Not pushed:** GitHub `CleanUp` is still `a8b0179`. Every commit from 19 Oct (ad3947a → 6653229, plus this handoff) exists only on this Mac. Push with `git push git@github-work:naveen-lset/Antz-homepage.git CleanUp`.
- **Not built:** the sky doodles exist only in the mockup.
- **Not synced:** `mockups/web-v3/widgets-preview.html` still has the older tabs.
