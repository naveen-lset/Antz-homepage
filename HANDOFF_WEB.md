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
