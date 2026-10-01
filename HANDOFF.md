# ANTZ Home Page Redesign: Handoff

**Live review link:** <https://home-page-redesign-gold.vercel.app/?v=2>
**Status:** this is the finalized review build, frozen on 1 October 2026.
**This branch (`Handoff`)** holds exactly the files the link serves, and nothing else.
**Source:** branch `site-command-centre`, commit `2a73a0e`. That branch is where the app is developed, and this build is generated from it.

This document is for the team taking the redesign forward. It covers what each screen does, how the build is put together, where the data comes from, and which parts are still placeholders.

---

## 1. Run it, deploy it

The page loads JSON with `fetch`, so it has to be served over HTTP. Opening the file directly doesn't work.

```bash
# from the root of this branch
python3 -m http.server 8080
# then open http://localhost:8080/
```

The page always opens on V2. A small script at the top of `index.html` rewrites any `?v=` value to `?v=2` before the app reads it.

**Deploy:** the link is the Vercel project `home-page-redesign` (team `naveen-lsets-projects`). To redeploy this branch as it is:

```bash
vercel link --project home-page-redesign --yes
vercel deploy --prod --yes
```

`vercel.json` only turns on `cleanUrls`. A side effect is that `/index.html` answers with a 308 redirect to `/`.

> The bare domain `home-page-redesign.vercel.app` belongs to someone else. Vercel gave this project the `-gold` suffix, so always share the `-gold` link.

---

## 2. What is in this branch

| Path | What it is |
|---|---|
| `index.html` | The whole app in one file, about 3.4 MB. All the CSS, then every JavaScript module bundled as `__def('js/…', fn)` blocks, loaded through a small `__req()` resolver. |
| `review.css` | Review-only design changes layered on top of the app. Every rule sits under `:root[data-review]`, which only this build sets. |
| `assets/icon/` | 161 icons, mostly SVG exports from the Figma file. |
| `assets/img/` | Photographs, the ANTZ logo, the chat wallpaper and the eggs banner. |
| `assets/data/` | The data the module pages and sheets fetch (see §5). |
| `js/dashboard.js` | An older role dashboard. Copied by the build, but `index.html` does not load it. |
| `vercel.json` | `{"cleanUrls": true}` |

### How this build differs from the main app

The build script lives in `tools/review-build/build.py` on `site-command-centre`. It:

1. pins the page to V2 and sets `data-review` and `data-profile-drawer` on `<html>`;
2. replaces the profile menu's "Home page" version picker with **Background: Climate | Plain** (Plain is the default, and the choice is stored per device in `localStorage['rv-hdr']`);
3. retitles the tab "Home Page Redesign · ANTZ" and names the favourites band "My species";
4. adds `review.css`, and swaps the "View all" chevrons for the double chevron from the Figma file.

The main app (Vercel project `antz-module-selection-home`) is a separate deployment and has not had these changes deployed.

---

## 3. The Home page, top to bottom

Every overlay (popup, bottom sheet, drawer) **holds the page behind it still**: touch and wheel scrolling outside the overlay are blocked. Every motion is switched off when the device asks for reduced motion.

| Section | What it does |
|---|---|
| **Header** | Avatar, then "Good morning / afternoon / evening" and the name, then the weather readout and the bell. The avatar opens a **left side drawer**: ANTZ logo, current site, user, the app's six rows (My Profile … Help & Support, which open in the ANTZ app and are not part of this preview), the page controls (Edit, Add, Background, Reset) and Logout. The drawer fits a phone without scrolling. |
| **Search bar** | Sticky. When it sticks, it and the site chips become one glass sheet, and the **avatar docks to the left** of the search field. Search, then a scan button. |
| **My species** | The followed species as photo cards. The pencil edits the set. |
| **Health strip (ticker)** | Figma section 863:173. One continuous lane: TODAY'S NATALITY, then MORTALITY, then AUDIT. The red LIVE mark stays pinned at the left, and each run's label sticks after it. The lane drifts on its own and pauses under a finger or the pointer. Tapping a label or a species opens the **This week** sheet. |
| **This week sheet** | A Births / Deaths switch over every species of the last 7 days, each with its count. A row opens that species' profile (Life or Mortality tab). "View all" opens the Natality or Mortality report. |
| **Announcements** | A stacked deck. Swipe left for the next card, drag right to bring the previous one back; it also turns by itself. **Tapping the front card opens that announcement** on the feed page. "View all" opens the feed page. |
| **Site chips** | Sticky. Picking a site rescopes the notes, the counts and the insights. |
| **Observation Notes** | Filter tabs All / Urgent / Animals / Enclosures, each with its count. The rail loads more notes as it scrolls, and the filter applies to those as well. Tapping a note opens the **note popup**: a carousel that shows the neighbouring notes at the edges on a phone, grows to full screen on the first scroll, and shows comments in full screen. "View all" opens the feed page. |
| **Key Insights** | Today / W / M / 6M, and a **Custom range** calendar (one month on a phone, two from 744px; From/To, day count, Apply). The cards are Natality, Mortality, Vaccination pending, Deworming pending and Administration. Each card's list scrolls inside the card. A card's head opens its insight page; a species row opens that species' page. |
| **Modules** | **+** opens **Your Modules**: every module by category with a one-line description. Tap a row to open the module; swipe it left to **Add to Home** or **Remove** (with Undo). Medical is core and offers no Remove. The **pencil** enters edit mode: drag to reorder, − to remove (Medical and the Species Management stats card are locked), resize through the size picker (Medium / Large / Full Width), and at the foot two buttons, **+ Add Module** and a filled green **✓** to finish. |
| **Pending Actions** | A corkboard of five jobs (Sexing, Microchipping, Necropsy reports, Deworming, Vaccinations) with the open total. Each note opens its module page. |
| **Quick Actions** | The floating pill. It opens four folder cards (Medical & Clinical Care, Animal Management, Operations & Administration, Site & System Management), four actions each, plus a "5 Drafts" strip, search, and a foot row of *Search everything* and *Edit Modules*. |
| **Chat disc** | Opens the **Communication** page, styled after WhatsApp: a chat list on the left, the conversation on the right (two steps on a phone), with replies, photos, PDFs, voice notes and reactions. Hold a message to react or reply. |

### Module pages

The module pages open in the app and live in the URL hash, so they can be linked and the back button works:

| Route | Page |
|---|---|
| `#m/species`, `#m/species/<name>/<tab>` | Species Management, and a species' details page (tabs such as `life`, `mortality`, `health`) |
| `#m/medical/…` | Medical: Vaccination |
| `#m/mortality/…` | Mortality and carcass transfers, including `#m/mortality/animal/<AAID>` |
| `#m/necropsy/…` | Necropsy (Incoming / Pending / Draft / Completed) |
| `#m/eggs/…` | Egg collection |
| `#m/natality?days=N` | Natality insights (births, 1Y / 2Y / 3Y / Custom) |
| `#m/deaths?days=N` | Mortality insights |

The feed pages (Announcements, Notes) are a split view: a list you can hide, search and filter on one side, the post on the other, and a comment field pinned at the bottom.

---

## 4. Design rules this build follows

- **Type:** Antz text styles only. Inter 14 in three weights: Body_Title 600, Body_Regular 400, Body_Medium 500 (+0.1 letter spacing). Line height is normal. Section heads are 16 Medium.
- **Colours (MD3_Antz):**

  | Name | Value | Used for |
  |---|---|---|
  | OnSurface | `#006D35` | ticks, Add, the green Done button |
  | OnSurfaceVariant | `#44544A` | body text, tabs, icons |
  | neutralSecondary | `#7A8684` | secondary text |
  | SecondaryDark | `#00ABAB` | births |
  | Tertiary | `#FA6140` | deaths, Remove |
  | addPrimary | `#00AFD6` | focus rings, links |
  | OnSecondaryContainer | `#1F415B` | the dark navy |

- **Section heads are black** (`#000`). "My species" turns white only when the live sky behind it is dark.
- **Bottom sheets:** 16px from each side of the screen, up to 760px wide and then centred. The head is the same everywhere: a handle, the title on the left, a round close button on the right. No explanatory sentences; label and data only.
- **Spacing (Figma Home 816:2):** 20px between sections from 744px up, 12px on a phone. Tinted bands sit 8px outside the content column.
- **Phone type** stays at the tablet sizes (smaller sizes were rejected as too small).

**Figma file:** `CNhiaOGCLdnlNxj7x2Ohrd` ("Desktop-Navigation").

| Node | What it is |
|---|---|
| `816:2` | Home |
| `851:10787` | Health strip |
| `863:173` | Tickers |
| `829:595` | Site chips |
| `816:986` | Pending Actions |
| `816:936` | Module grid |

---

## 5. Data

There is **no backend**. Everything is in the page or in `assets/data/`.

- **V5 database (anonymised):** species, animals, sites, staff and counts come from an anonymised dump of the V5 app, bundled in `index.html` as `js/data/v5db.js`. Its "today" is **20 May 2026**, so date ranges and calendars count back from that day.
- **`assets/data/`:**

  | File | Size | Holds |
  |---|---|---|
  | `v2-modules.json` | 3.5 MB | module pages |
  | `v2-births.json` | 1.1 MB | births |
  | `v2-deaths.json` | 0.7 MB | deaths |
  | `v2-week.json` | 26 KB | the last 7 days, by species, for the This week sheet |

  The scripts that build them (`tools/v2modules_build.py`, `tools/v2week_build.py`, `tools/v5db_build.py`) are on `site-command-centre`.
- **Sample data, not real:** the egg-collection and transfer records; the **68% Audit Score** and the audit run in the ticker, which have no audit table behind them; the chat conversations; and the announcement photos.
- **Local only:** likes, saves, comments, custom ranges and the Home layout are kept in the browser. Nothing is sent anywhere.

---

## 6. Known gaps (read before building on it)

1. **Audit score** is a Figma placeholder. Tapping it shows "opens in the ANTZ app".
2. **Custom range → card head:** a Key Insights card opens its insight page on the last *N* days, not on the exact custom From–To range.
3. **Some rows hand off to the ANTZ app** and show a notice instead of a page: the drawer's six app rows, and modules without a page in this preview.
4. **Sample voice notes** in chat have no sound; they animate their waveform and say so. Recording a real voice note works where the browser allows it.
5. **The main app is behind.** It has not been redeployed with this work, and `review.css` exists only in this build.
6. **One automated check fails,** and only on V3 (empty cells in V3's grid). V2 passes 192 of 193 checks in `tools/verify_v2.py` on `site-command-centre`.

---

## 7. QA checklist

Check at **390** (phone), **744** (tablet portrait, the Figma artboard), **1024** and **1440** wide. Do a hard refresh first; browsers cache this page aggressively.

- [ ] Nothing scrolls sideways at any width; every image loads; no console errors.
- [ ] Scroll down: the search bar sticks, the avatar docks on its **left**, and the chips join it as one glass sheet.
- [ ] Ticker: LIVE stays pinned; tapping a species opens This week on the right tab, with that species highlighted.
- [ ] Announcements: swipe turns the deck; a tap opens the post.
- [ ] Notes: each filter tab shows exactly its count, even after scrolling the rail to the end; the popup fits the note.
- [ ] Key Insights: Custom picks a range, Apply recounts the cards, and the tab shows the range (744px and up).
- [ ] Your Modules: swipe a module to add it, Undo; swipe one that's on Home to remove it, Undo; Medical can't be removed.
- [ ] Edit mode: size picker, + Add Module, green ✓ to finish.
- [ ] Quick Actions: all four folders visible without a fade at 744 × 1024.
- [ ] Every sheet and popup: the page behind does not scroll.
- [ ] With reduced motion on, nothing animates and everything still works.
