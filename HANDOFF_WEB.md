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
