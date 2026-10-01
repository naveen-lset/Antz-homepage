
# Mortality & Carcass Transfer: audit against the iPad screenshots, with a change spec

I made no repo edits. Scratch files (crops, our renders, `smp.py` pixel sampler) are in `/private/tmp/claude-504/-Users-naveen-Desktop-Module-Selection/c205e1c7-9d8d-4a38-bd3e-603dd1ce354d/scratchpad/mort/`. The server on 8763 and Chrome on 9463 are stopped.

**How values were measured**
- CSS px = original PNG px ÷ 2. The app starts at y=32; y=0–32 is the iOS status bar.
- Colours were sampled from the original PNGs and are exact.
- Font sizes are estimated from glyph cap heights on 2× crops, accurate to about ±1px.
- The app's font is the iOS system font (SF Pro).

## 0. Bugs found while rendering (fix whatever the restyle)

**B1. The Species tab on the mortality list is broken.**
- `tabs()` routes it to `mortality/species`.
- `ROUTES.mortality` then takes `view==='species'` as the species drill-down with `arg` undefined. It renders an empty species bar and "Reasons 0 / Animals 0".
- Fix: change the test to `if ((view === 'species' || view === 'reason') && arg)`, or route the tabs as `mortality/tab/species`.

**B2. The checklist sheet's closed accordion headers render clipped to about 18px.**
- Cause: `.msheet__body` is a flex column with `overflow-y:auto`, and its `details` children shrink.
- It goes away if the checklist becomes a full page (below). Otherwise add `.msheet__body > * { flex: none }`.

## 1. Palette (the module's own; none of these are in `--mp-*` today)

| Token | Hex | Where it appears |
|---|---|---|
| page-salmon | #FCCBBB | page background of the mortality list and transfers list |
| head-pink | #F7DFD7 | header band (bar, filter row, tabs) on both lists |
| head-line | #EAD4CC | 1px rules inside the mortality header band |
| head-line-2 | #FFBDA8 | 1px rule under the transfers bar; drill-down card borders and stat block |
| drill-bg | #FFE5DD | drill-down pages (species or reason): the whole page |
| line | #C3CEC7 | search, filter-button and row borders; form dividers |
| line-dark | #839D8D | form input borders, filter search border |
| ink | #44544A | title on the lists, body text, values |
| ink-dark | #250E01 | tab numbers and labels, "Carcass Transfers" link, check-in strip text |
| teal | #1F515B | AAID, CT id, search icon and placeholder, "Transfer Initiated", primary button |
| navy | #1F415B | drill-down and filter titles, checklist accordion headers, checklist title |
| mute | #7A8684 | Latin names, "Reported by", labels |
| red | #FA6140 | active tab number and underline, mortality date, "Unsuitable…" |
| green | #006D35 | counts, "Necropsy Completed" text, active profile tab |
| green-btn | #37BD69 | "View report", "Apply filters", "Submit", check icon |
| fab-green | #52F990 | mortality FAB |
| maroon | #4A0415 | transfer and necropsy-report header; dead badge in the main list |
| maroon-2 | #420413 | "Initiated by" band on the transfer detail |
| flag-red | #E93353 | route "to" flag; "Dead" pill |
| cyan | #00AFD6 | ID badge, "+" icon on Select Carcass |
| teal-avatar | #00D6C9 | initiator avatar |
| mint-field | #F2FFF8 | location card and select fields |
| form-grey | #EFF5F2 | filter left rail, checklist inputs, empty area of the new-transfer form, necropsy report page |
| checklist-bg | #DAE7DF | checklist page background |
| accordion-sub | #C3CEC7 | open-section sub-header strip |
| upload-bg | #E5F7FB | upload area |
| notes-yellow | #FCF4AE | notes input |
| disabled-btn | #C3CEC7 | disabled Submit Request |
| canceled-bar | #7A8684 | canceled footer |

## 2. Per-screen findings

### IMG_0078 · Mortality list, Animals tab
Our route: `#m/mortality` (`ROUTES.mortality`, tab `animals`). Everything below is different from ours.

**Page**
- Background #FCCBBB. Ours: #EFF5F2.

**Header band #F7DFD7, full-bleed, y 32–267.5.** It sits above the scroll; ours puts these controls in the scrolling body.
- **Bar (y 32–87, 55px tall, then a 1px #EAD4CC rule):**
  - Back arrow: 16px glyph, #44544A, at x 25.
  - Title "Mortality": about 20px, weight 400–500, #44544A, x 72.5. No subtitle.
  - Right side: "Carcass Transfers" as plain text (about 16px, #250E01), then a truck outline icon 20px (dark, with red accents) at x 778–794. Right edge 16.
  - Remove from the bar: the site button, the badge and the pill border.
- **Filter row (y 88–199, then a 1px #EAD4CC rule):**
  - "Last 30 Days" plus a filled ▼ triangle: text dropdown, 14px medium #44544A, x 21, cap top y 108. No calendar icon, no box.
  - Below it, a full-width select at x 16–794, y 129–183 (54 tall): #FFF, radius 6, no border.
  - Select text "All Sites": 15px semibold #44544A at x 36.5. Chevron: 11px #1F515B at x 761.
  - This replaces the site button in the bar.
- **Tabs (y 200–267.5, 67.5 tall):**
  - Three tabs, `justify-content: space-between`, 16px padding each side. Each tab is 84px wide, content centred.
  - Number above label: number about 20px medium, #250E01, cap top y 219.5. Label 14px #250E01 at y 241.
  - Active tab: number #FA6140; underline 2px #FA6140 across the full 84px, flush with the band bottom (y 265.5–267.5).
  - No count chips beside the labels, no green, no bottom border line.

**Search row (starts 12px below the band)**
- Search box: x 16–740, y 279.5–319.5 (40 tall incl. border), 1px #C3CEC7, radius 6, #FFF.
  - Magnifier 20px #1F515B at x 27.
  - Placeholder "Search", 15px medium **#1F515B** (not faint).
- Filter button: x 749–794, y 282–317 (45×35), #FFF, 1px #C3CEC7, radius 6. Sliders icon (three sliders) #44544A, about 24px.
- Gap between search and button: 9px.

**Death card**
- Box: x 16–794 (778 wide), #FFF, radius 8, no border, no shadow. Height 242. Gap to the next card 16. First card is 12px below the search.
- **Line 1:** "Reported by {name}", 14px. "Reported by" #7A8684, name #44544A regular (not bold). x 25, cap top y 347 (card padding: 12px top, 9px left).
- **Photo:** 160×160 at x 24–184, y 370–529. Radius 8.
  - Placeholder background #FFE0E0 (pink tint) with the mark in #839D8D. Keep real photos where we have them.
  - Bottom-right "expand" corner glyph, white, 10px.
- **Badge (top-left of the photo, inset 4):** about 38×21, radius 4, **#4A0415** maroon.
  - Content: white 12px sex code ("ID", "F", "M") plus a small white "deceased" glyph.
  - In the main list the badge is maroon for every sex.
- **Text column** starts at x 192.5 (8px after the photo). Lines, top to bottom:
  1. "AAID: 247289": 16–17px bold #1F515B. The colon is part of the copy.
  2. "Mortality: 28 Sep 2026 • 05:32 PM": 13px semibold **#FA6140**.
  3. Common name: 16px medium #44544A.
  4. Latin: 14px italic #7A8684.
  5. "Site: Mammal site": 16px semibold #44544A.
  6. "Cause: Natural": 16px semibold #44544A.
  - Line pitch about 21px.
- **Footer strip:** full card width inset 1px (x 17–793), y +205 → +241, 36 tall. Bottom corners follow the card radius.
  - Completed: background #E1F9ED. Icon: 16px filled check-circle #37BD69 with white tick, at x 35. Text "Necropsy Completed", 15px medium #006D35, at x 58. Right: NPS id ("NPS21-00109"), 12–13px semibold #006D35, right edge 792.
  - Pending: background #FCF8E8. Icon: clock outline #E4B819. Text "Necropsy Pending", 15px medium #250E01. Right: "Ready to transfer", 12px #E4B819.
- **Differences from ours:** our card is 56px thumb, horizontal, with a chip tag on the right and a chevron. Layout and content order are completely different. Ours has no strip and no "Mortality:" line; we render "Died …" plus site plus cause as one meta line.

**FAB**
- 50×50 at x 728–778, y 922–972 (right 32, bottom 108 from the viewport). Radius 8. #52F990.
- Icon: 20px circle-plus outline #1F515B.
- Shadow about `0 4px 8px rgba(0,0,0,.2)`.
- Not built in ours (reporting a death is not in the prototype). Draw it and have it `toast('Report mortality is not in this prototype')`.

### IMG_0079 · Mortality list, Species tab
Our route: `#m/mortality/species` (broken, B1). Same header, with Species active (underline x 363–447).

**Search row**
- Search narrows to x 16–714, y 279.5–319.5.
- The filter button is replaced by two view toggles:
  - List icon: #37BD69 (active), x 731–749.
  - Stacked-cards icon: #44544A, x 782–798.
  - Both about 18px, no boxes.

**Species row**
- Box: x 16–794, y 331.5–426.5 (95 tall incl. border), 1px #C3CEC7, radius 8, #FFF, no shadow. Gap 16.
- Photo: flush with the left edge, x 16–106 (90×93), left corners radius 8. Placeholder background #E5E5E5.
- Text starts at x 124:
  - Name: 16px medium #44544A, cap top about 13px from the row top.
  - Latin: 13px italic #44544A.
  - Chip row 12px below. Chips about 40×19, radius 4, 13px text, content "F - 1" (letter, space, hyphen, space, count).
    - F: background #FECFC5, text #FA6140.
    - ID/M/U: background #DDEBE9, text #1F515B.
- Count on the right: 16px semibold #006D35, top-aligned with the name, right edge 794−12.
- No chevron. Ours: 48px thumb, a big dark number and a chevron.

### IMG_0080 · Mortality list, Reasons tab
Our route: `#m/mortality/reasons`. Search box is full width (x 16–794); no filter button, no toggles.

**Reason row**
- Box: x 16–794, 55 tall, #FFF, radius 8, no border. Gap 8. First row 16px below the search.
- Name: 16px semibold #44544A at x 29.
- Count: 22px semibold #006D35, right edge about 786, vertically centred.
- No chevron. Ours has a chevron, a 56px min-height, a border and an 18px ink count.

### IMG_0081 · Animal profile, Mortality tab (death detail)
Our route: `#m/mortality/animal/:aaid` (`deathPage`). Our structure is different (summary card plus two kv cards plus an action bar).

**Hero, full-bleed, y 32–361 (329 tall)**
- Species photo as background (placeholder #9DACA3).
- Back arrow white 22px at (20, 59). Star and QR icons, white, top right.
- Overlay card: x 30–780, y 100–291, radius 8, `rgba(0,0,0,.5)` (renders #4E5651).
  - Common name: 34px regular white, cap top y 118.
  - Latin: 13px italic white.
  - "Breed1 • Morph 1": 14px semibold white.
  - Then 14px white rows: "Sex: **Indeterminate**", "Life Stage: **…**", "Encl: **…**", "AAID: **…**", "Last Recorded Weight: …". Value parts are semibold.
- "Dead" pill: 49×25 at (31, 303), radius 12.5, #E93353, 13px white.
- Carousel dots at y 351.

**Tab strip, white, y 362–412 (50 tall)**
- Hamburger icon at the left. Tabs "…sfer, History, Incidents, Diet, Media, Incharges, Tags, **Mortality**": 14px #000.
- Active tab: #006D35 medium with a 2px #006D35 underline (x 641–746).
- We do not have an animal profile. Either omit the strip, or draw a single active "Mortality" tab.

**Body, white**
- "Mortality Report": 18px medium #44544A at x 21, y about 440.
- Card: x 16–794, background **#FFE9E9**, radius 12, padding 16.
- Rows are stacked, one column (not a two-column dl). Each row: label 14px #44544A, then value 16px semibold **#000**. Pitch about 54px.
- Row order and exact labels:
  1. "Suspected Cause of death"
  2. "Date and Time of Death": value "28 Sep 2026 • 05:32 PM"
  3. "Carcass Condition"
  4. "Attachments": 332×148 tile, 1px #C3CEC7, image on top, filename strip at the bottom (48px, #EEF3F1, 14px). **Omit: no data.**
  5. "Notes": "NA" when empty.
  6. "Necropsy Requested": "Yes"
  7. "Reported by"
  8. (continues below the fold)

**Bottom sheet, fixed, white**
- Top radius 16, shadow `0 -2px 6px rgba(0,0,0,.08)`, y 950–1080.
- "Necropsy Status": 14px #7A8684 at x 17.
- Value: 16px medium, colour by state.
  - "Unsuitable for necropsy" and "Necropsy Pending" use #FA6140. For other states use #006D35 when completed, #FA6140 otherwise.
- Button: x 16–794, y 1020–1070 (50 tall), radius 10, #37BD69.
  - Label "View report" (completed or unsuitable) or "Open necropsy" (ours), 16px medium white.
- FAB "+": 56×56, radius 12, #52F990, black 24px plus, at x 738–793, y 933–988.

### IMG_0082 / 0083 · Necropsy report (reached from NPS id / "View report")
This screen belongs to the Necropsy module (`necropsy/case/...`). Listed here so the link lands right.

**Header, #4A0415, y 32–231**
- Nav row: back arrow white; "NPS21-00109" 20px medium white at x 68; download and ⋮ icons white on the right.
- Animal row:
  - Photo 117×115 at (8, 108), radius 8, placeholder #7D7A80. Cyan #00AFD6 "ID" badge 24×24, radius 4.
  - Text at x 134: "AAID: 247289" 16px semibold white; name 16px semibold white; Latin 14px italic #7A8684; "Encl: …" 16px semibold white.

**Body, background #EFF5F2**
- Section headings, 50px bands: "Necropsy suitability", "Carcass details", "Clinical History", "Necropsy Details", "Examination Findings", "Cause of Death". 16px medium #000 at x 17.
- White cards: x 16–794, radius 8.
  - Label: 16px #7A8684. Value: 16px #44544A.
  - Empty value is "--".
- "Necropsy conducted by": user chip, pill #EEF3F1, avatar plus name 14px plus role 12px.

### IMG_0084 / 0085 · Species drill-down
Our routes: `#m/mortality/species/:name` (Reasons tab) and `…/animals`.

**Page**
- Whole page background **#FFE5DD**.
- Bar: 55px, same background, 1px #FFBDA8 rule. Back arrow and "Mortality" in **#1F415B**, 20px. Right: search and ⋮ icons, #1F415B 22px.
- Remove the subtitle ("Last 30 Days") and the site button.

**Species card**
- x 16–794, y 88–171 (83 tall), background #FFE5DD, 1px #FFBDA8 border, radius 10.
- Circle avatar 50px at x 33, background #E7D0C8, mark in #839D8D.
- Name: 16px semibold #000 at x 97.
- Latin in parentheses "(Ursus arctos horribilis)": 14px italic #44544A.

**Stat block (replaces our tabs)**
- x 16–794, y 187–276.5 (89.5 tall), 16px below the card. Background #FFBDA8, radius 10.
- Two tabs, 290px wide each, centred (centres x 267 and 557).
  - Number: 28px bold #250E01.
  - Label: 14px #4A0415 ("Reasons", "Animals").
- Active indicator: 84×6, #FA6140, top radius 3, flush with the block bottom.

**Content**
- Reason rows (0084) start 20px below the block. Same reason row as 0080.
- Animal rows (0085), each:
  - Box: x 16–794, 131 tall, #FFF, radius 12, padding 8, no border. Gap 8.
  - Photo: 115×115, radius 8. Placeholder **#D7F7F5** (cyan tint).
  - Badge: 24×24 at inset 4, radius 4, white 11px. Background by sex: ID #00AFD6, F #FA6140, M #00AFD6.
  - Text at x 150: "AAID: 267158" 16px bold #1F515B; name 16px medium #44544A; Latin 14px italic #7A8684; "Encl: Park 02" 16px semibold #44544A.
  - Chevron: 14px #7A8684 at x 790, vertically centred.
  - No "Reported by", no mortality line, no strip.

### IMG_0086 / 0087 · Reason drill-down
Our routes: `#m/mortality/reason/:cause` (Species tab) and `…/animals`.

- Same page and bar as 0084, but the bar's right side has only ⋮.
- Reason title "Natural": 22px regular #000 at x 17, cap top y 94. Ours: 15px semibold `.mp-h`.
- Stat block: y 130–219.5. Tabs "Species | Animals", same styling as 0084.
- Search row 28px below the block. On the Species tab it has list/card toggles (search x 16–726). On the Animals tab it is a full-width search.
- Rows: species rows as in 0079 (first row 12px below the search); animal rows as in 0085 (16px below, gap 8).

### IMG_0088–0091 · Mortality filters
Ours: `filterSheet()` renders a centred modal 760 wide. The reference is a **full-screen white page**.

**Header**
- y 32–81.5, then a 1px #C3CEC7 rule.
- "Filters (0)": 20px regular #1F415B at x 17.
- Close ✕: thin 24px #44544A at x 785–808.
- No round grey close button.

**Left rail**
- x 0–336, background #EFF5F2. Rows are 38px tall, starting at y 82.5.
- Label: 13px semibold #000 at x 17. Count: 12px semibold #000, right edge 323.
- Selected row: #FFF background. No green inset bar.

**Right pane (padding 12–13px)**
- Search (checkbox facets only): x 349–797, y 95–128 (33 tall), 1px #839D8D, radius 6. Placeholder "Search" 14px #1F515B; magnifier 14px #1F515B on the right.
- Checkbox rows:
  - Pitch 57px (first centre at y 172).
  - Box: 18×18 square, 2px #44544A border, radius 2, at x 358.
  - Label: 16px #000 at x 395.
  - **No per-option counts** (ours shows counts).
- Radio rows (Reporting status):
  - 20px circle, 1.5px #7A8684, at x 356.
  - Label: 16px medium #44544A. Pitch 41 (y 117, 158).

**Footer**
- White, 1px #C3CEC7 top rule at y 1021.
- Only "Apply filters": x 679–798, y 1034–1068 (119×34), radius 8, #37BD69, 16px semibold white, right-aligned.
- **No "Clear all".**

**Facet content**
- Sex: Male, Female, **Indeterminate**, Undetermined. Ours lacks Indeterminate.
- Reporting status: **radio**, "Reported Late (>48 hrs)", "Reported On Time".
- Necropsy Status options: Completed, Pending, Unsuitable, Necropsy Not Required, At Site, Ready to transfer, In Transit, Transfer Pending, At Necropsy Facility. Ours: 4 options with different labels.
- Cause: the full list from data. The reference lists Euthanasia, Natural, Indeterminate, Undetermined, Congential Types, Murder, Old Age, Poisoned, Stray Attack, Suspicious, Foul Play, Attacked, Traumatic Injury (original order, not sorted).

### IMG_0092–0095 · Carcass Transfers list (4 tabs)
Our route: `#m/mortality/transfers/:tab` (`transfersPage`).

**Page and header**
- Page background #FCCBBB. Header band #F7DFD7.
- Bar: y 32–96 (64 tall), then a 1px **#FFBDA8** rule.
  - Back arrow #44544A. "Carcass Transfers": 20px #44544A at x 57.
  - **Nothing on the right**: remove "Sample data" and the site button.
- Tabs: y 97–159 (62 tall), `space-between`, 16px sides. Tab width = label width.
  - Number: 16px semibold #250E01, cap top y 113. Active number #FA6140.
  - Label: 14px #250E01.
  - Underline: 2px #FA6140 across the label width (e.g. 16.5–120 for "Transfer Pending").
  - Labels: "Transfer Pending", "In Transit", "Transfer Completed", "Canceled".

**Search row**
- Search x 16–754, y 171–211. Filter button 45×35 at x 764–808 (same as 0078).
- Placeholder "Search" (ours: "Search transfer or centre").

**Transfer card**
- Box: x 16–794, 164.5 tall plus 4 bottom padding (y 223–391.5). #FFF, radius 6.
- Shadow `0 2px 4px rgba(120,60,40,.25)`: a soft 4px fall-off below, visible as #DCB1A3 → #F5C5B5.
- Gap 12.
- **No truck thumbnail.**
- Row 1 (y about 248):
  - "Requested by **Mohit**": 12px; "Requested by" #44544A regular, name semibold. x 29.
  - Right: "24 Aug 2026 ● 12:10 PM", 12px #44544A, with a 4px #7A8684 dot. Right edge 796.
- CT id "CT21-00163": 17px semibold #1F515B, 20px below row 1.
- "Carcasses: **1**": 16px #44544A, number bold.
- Route, 8px below:
  - Green "pin-line" glyph (6px dot plus 8px line, #37BD69), then site 15px #44544A at x 53.
  - Red "flag" glyph (#E93353), then centre 15px #44544A. Line pitch 20.
- Chevron: 14px #44544A at x 785, vertically centred on the id block.
- Stage strip:
  - x 20–790 (inset 4), 32 tall, 4px above the card bottom. Radius 0 on top, 4 on the bottom.
  - Text 15px medium at x 33, colour by stage:

| Stage | Background | Text |
|---|---|---|
| Loading Pending | #E8F4F2 | #1F515B |
| Security Checkin Pending | #FDF8CE | #250E01 |
| Security Checkout Pending | #CFF5F3 | #1F515B |
| Transfer Completed | #E1F9ED | #006D35 |
| Canceled | #FEF5F6 | #FA6140 |

**FAB**
- 48×48 at x 727–775, y 946–994. Radius 12.
- Background `linear-gradient(180deg, #FA6140, #EC3A50)`. White truck-with-plus glyph, 26px.
- Shadow `0 3px 8px rgba(0,0,0,.25)`.
- **No text label.** Ours: 52px dark pill with "New transfer".

### IMG_0096 · New Carcass Transfer form
Our route: `#m/mortality/new-transfer` (`newTransfer`).

**Page and bar**
- Page #FFF. Bar y 32–76 (44 tall), 1px #C3CEC7 rule. Back arrow #44544A; "Carcass Transfer" 20px #44544A. No subtitle, no sample tag.

**Sections**
- Full-bleed sections separated by 1px #C3CEC7 rules at y 277, 387 and 623.5.
- Each section: title 16px #44544A at x 17 (cap top 24px below the rule), content 16px below, 16px bottom padding.
- **No white cards**: ours wraps them in `.mp-panel`.

**1. "Select Location"**
- One combined card: x 16–794, y 135–261, background #F2FFF8, 1px #C3CEC7, radius 8.
- Left rail at x 38: green dot 7px #37BD69 at the top, a dotted green-to-red line, a red square 8px #E93353 at the bottom.
- Top half:
  - "From Site": 12px #7A8684 at x 50.
  - Value: 15px semibold #006D35.
  - Chevron #1F515B at x 780.
- Inner divider: 1px #C3CEC7 at y 203.5, x 68–773.
- Bottom half:
  - "Destination": 12px #7A8684.
  - Placeholder "Select Necropsy Center": 16px #A4BAAD; when chosen, 15px semibold #006D35.
  - Chevron.
- Keep native selects underneath if wanted, but style them transparent inside this card.

**2. "Select Carcass"**
- Field: x 16–794, y 320–371 (50 tall), background #F2FFF8, 1px #839D8D, radius 8.
- "Select Carcass": 16px semibold #006D35 at x 30. Circle-plus 24px #00AFD6 at x 770.
- Tapping it opens a carcass picker. Ours lists every carcass inline with checkboxes. Move that list into a sheet, or show it below the field only after the tap.
- Picked carcasses appear as animal rows (0085 style) under the field.

**3. "Attachments(Optional)"**
- "(Optional)" in italic #7A8684.
- Area: x 16–794, y 442–607.5 (165 tall), background #E5F7FB, radius 12.
- Dashed box: 72×72, 1px dashed #44544A, radius 8, image-plus icon.
- "Upload Files": 14px semibold #006D35.
- "Supported: JPEG, PNG, PDF, MP4, MP3 (Max 32 MB)": 12px #7A8684.
- Not in ours. Draw it inert, or with toast "Uploads are not in this prototype".

**4. "Notes(Optional)"**
- Input: x 16–794, y 672.5–729.5 (57 tall), background **#FCF4AE**, 1px #839D8D, radius 4.
- Placeholder "Add Notes": 16px #44544A at x 33.

**Empty area and footer**
- Below the sections, background #EFF5F2 down to y 1014.
- Footer #FFF, y 1014–1080. Button x 16–794, y 1022–1072 (50 tall), radius 10.
  - Disabled: #C3CEC7 with white text.
  - Enabled: #37BD69.
  - Label "Submit Request", 16px semibold.

### IMG_0097 / 0098 · Transfer detail
Our route: `#m/mortality/transfer/:id` (`transferPage`). 0097 is Canceled; 0098 is Loading Pending ("Transfer Initiated").

**Maroon header #4A0415, full-bleed**
- 0097: y 32–190. 0098: y 32–174 (no QR row, so shorter).
- Nav row:
  - Back arrow: white 22px at x 17.
  - Title "CT21-00167": **centred**, 20px regular white.
  - Right: ⋮ white in pending/transit states; nothing when canceled.
- "Carcass Transfer": 16px white at x 17, about 16px below the nav.
- Route lines, 16px semibold white, pitch 26: green pin-line glyph plus site; red flag glyph plus centre.
- QR: white-on-maroon, about 46×46 at x 755–800, vertically centred on the route. Show it for transit, done and canceled; hide it for Loading Pending.

**Initiator band, #420413, 86 tall**
- "Initiated by": 12px white at x 17.
- Avatar: 32px circle #00D6C9 with a white initial (14px) at x 17.
- Name: 15px medium white at x 57. Date: "25 Aug 2026 ● 03:54 PM", 13px white.
- Right: two 34px circles, #28020B, white 18px phone and message icons, at x 727 and 768.

**Pink block, #FFEDED**
- "selected carcass" row, 40 tall: black paw icon 20px at x 17, then text 16px **lowercase** #44544A at x 45.
- Carcass card: x 16–794, 131 tall, background **#FFE3E3**, radius 12. Content as the 0085 animal row, **no chevron**.
  - Lines: AAID; optional "Name: 777777"; common name; Latin; Encl.
  - Photo placeholder #D5E9E6. Cyan ID badge.
- 16px bottom padding, then a 1px #FFF rule.
- Checklist row: background #FFEDED, 55 tall (not shown in Loading Pending, 0098).
  - Green filled check-circle 20px #37BD69 at x 17.
  - "Transfer Checklist": 12px #44544A at x 47.
  - "0/7 Filled": 16px medium #44544A.
  - No "Edit" link, no box.

**White area**
- "Comments" row, 42 tall: outline comment icon #7A8684 at x 17, then 15px #000 at x 43.
- Comment input: x 12–812, 49 tall, 1px #C3CEC7, radius 8.
  - Placeholder "Add a comment": 15px #1F515B at x 38.
  - Paper-plane send icon 24px on the right: #C3CEC7 when empty, #1F515B when typed.
  - **No "Send" button.** Ours wraps comments in an `.mp-panel` with an "h3 Comments" heading and a button.

**Footer, by state**
- Canceled (0097):
  - Full-width bar #7A8684, y 1015–1080, top radius 16.
  - Centred "✕  Canceled": ✕ 16px plus text 20px medium, white.
- Active (0098):
  - White sheet, top radius 24, shadow `0 -3px 8px rgba(0,0,0,.12)`, from y 922.
  - "Current Status ● 24 Aug": 14px #7A8684 at x 17.
  - Status name, 20px medium **#1F515B**. Use "Transfer Initiated" for Loading Pending; our stage names for the rest.
  - "See all": 14px #006D35, right edge 792.
  - Button: x 40–770 (40 margin), y 1004–1060 (56 tall), radius 12, **#1F515B**. Label "Fill Transfer Checklist" (or the next step), 20px regular white.
  - **No "Cancel transfer" ghost button in the bar.** Move cancel into the ⋮ menu (a small sheet with "Cancel transfer").

### IMG_0099 / 0100 · Transfer Checklist
Ours: `checklistSheet` renders a modal. The reference is a **full page**.

**Page and header**
- Page background #DAE7DF.
- Header #FFF, y 32–76. Back arrow #1F415B; "Transfer Checklist" 20px medium #1F415B.

**Accordion headers**
- x 16–794, 56 tall, radius 8 (6 when open, square bottom), #1F415B. First at y 88; gap 16.
- White 20px line icon at x 31, one per section: van, convoy car, sun-cloud, diamond-alert, people, scan-search, pulse-doc.
- Label: 15px semibold white at x 65.
- Chevron: white, down or up, at x 783.

**Open section**
- Sub-header strip: 32 tall, #C3CEC7. Section name, 15px #000, at x 24.
- Then a white body, padding 12 each side, 10 top, 16 bottom, bottom radius 8.
  - Inputs: x 28–792, 48 tall plus 1px #839D8D border, radius 4, background #EFF5F2. **The placeholder is the label**, 16px #44544A. No separate label. Gap 16.
  - Convoy fields, exactly: Route mapping, From where, To where, Ambulance no., Distance, Time, Driver name, Contact no, Mission Commander name, **Contact no**. Ours says "Commander contact no".
  - Then two rows, 37 pitch: "Security Pilot" and "Escort", 16px #1F515B, with an 18px square checkbox (2px #44544A) right-aligned at x 769.

**Footer**
- #FFF, from y 1008. Button x 40–770, y 1016–1072 (56), radius 10, #37BD69, "Submit" 20px semibold white.

### IMG_0101–0103 · Carcass Transfers filters
Ours: modal with Timeline (checkboxes) and Facility. The reference is the same full-screen filter page as 0088.

**Facets:** "Timeline", "Site", "Facility".
- **Timeline** (radio, 20px circles, 16px #000 labels, pitch 57):
  - All Time (default)
  - Last 24 hours
  - Last 7 days
  - Last 1 month
  - Last 3 months
  - Custom
- **Site:** one select, x 349–812, y 95–144 (48 tall), background #F2FFF8, 1px #C3CEC7, radius 8.
  - "Select Site": 16px #1F415B at x 360. Chevron #1F415B at x 790.
- **Facility:** search plus checkbox list of centres.

## 3. Implementation plan

### 3a. Shared helpers: decide first; other modules use them

**S1. Per-route page theme, in `render()` / `setBar()`.**
- Let a route return `{ theme, barCenter, barLine, bare, footer }`. In `render()`:
  - `page.dataset.mod = mod`
  - `page.dataset.theme = view.theme || ''`
  - `page.classList.toggle('is-bare', !!view.bare)`
- `setBar({ title, sub, right, center })` toggles `.mpage__bar.is-center`.
- Themes needed:
  - `mort-list`: bar #F7DFD7, rule #EAD4CC.
  - `mort-drill`: page and bar #FFE5DD, rule #FFBDA8, ink #1F415B.
  - `maroon`: bar #4A0415, white ink, centred title, no rule.
  - `white`: bar #FFF, rule #C3CEC7.
  - `checklist`: bar #FFF, page #DAE7DF, title #1F415B.
- CSS, all scoped by `[data-theme]` so Species, Medical, Necropsy and Eggs keep today's look:
  - `.mpage[data-theme] .mpage__bar { min-height: 55px; padding: 0 16px; gap: 20px; background: var(--bar-bg); border-bottom: 1px solid var(--bar-line); }`
  - `.mpage__title { font-size: 20px; font-weight: 400; color: var(--bar-ink); letter-spacing: 0 }`
  - `.mpage__back { color: var(--bar-ink); margin-left: -10px }`
  - Transfers-list bar is 64px tall: use a `bar-h` variable.
  - Centred title: `.mpage__bar.is-center .mpage__head { position: absolute; left: 0; right: 0; text-align: center; pointer-events: none }`.

**S2. `.mpage__body` padding and gap.**
- The mortality screens need `padding: 0` and `gap: 0`, with full-bleed bands.
- Add `.mpage.is-bare .mpage__body { padding: 0; gap: 0 }`. Each screen then wraps its list in `.mt-list { padding: 12px 16px 120px; display: flex; flex-direction: column; gap: 16px }`.
- Also give the mortality themes their own `--mp-bg`:
  - #FCCBBB: mortality list, transfers list.
  - #FFE5DD: drill-downs.
  - #FFF: form, death detail, transfer detail.
  - #DAE7DF: checklist.

**S3. `filterSheet()` becomes the live app's full-screen filter page.**
- This probably matches the other modules' references too; confirm with their auditors before changing the shared look.
- Add an option `filterSheet(facets, picks, apply, { full: true })`.
  - Adds `.msheet.is-full`: `inset: 0`, card `width: 100%; height: 100%; max-height: none; border-radius: 0; box-shadow: none`, no veil.
  - Head: `padding: 0 16px; height: 49.5px; border-bottom: 1px solid #C3CEC7`. h3 20px 400 #1F415B. `.msheet__x`: transparent 28px, stroke 1.6, #44544A.
  - `.mfil { grid-template-columns: 336px 1fr; margin: -20px; min-height: 100% }`.
  - `.mfil__rail`: background #EFF5F2, `padding: 0`, no border. Buttons: `min-height: 38px; padding: 0 13px 0 17px; font: 600 13px; color: #000`. Pressed: `background: #FFF; box-shadow: none`. `b`: 12px 600 #000.
  - `.mfil__opts { padding: 12px 13px 12px 12px }`.
  - `.mfil__opt { min-height: 57px; gap: 19px; font-size: 16px; color: #000; padding-left: 9px }`. Checkbox: 18px, `accent-color: #44544A`, square, radius 2.
  - Hide `small` counts when `full`.
- Per-facet additions:
  - `type: 'radio'` renders 20px circles, border 1.5px #7A8684, label 16px 500 #44544A, pitch 41.
  - `type: 'select'` renders the #F2FFF8 select.
  - `search: true` renders a 33px search: 1px #839D8D, radius 6, placeholder #1F515B 14px, icon on the right.
- Foot: drop Clear all. Button `.mp-btn.is-apply { height: 34px; min-height: 34px; padding: 0 16px; border-radius: 8px; background: #37BD69; font: 600 16px }`, right-aligned. Foot border-top #C3CEC7, padding 13px 12px.

**S4. `tabs()`: add a variant; keep the default for other modules.**
- `tabs(list, on, go, { variant: 'stack' })` renders `<b>` (number) above `<span>` (label), with no chip.
- CSS `.mp-tabs.is-stack`:
  - `justify-content: space-between; gap: 0; padding: 0 16px; border: 0; background: var(--bar-bg); height: 67.5px`. Transfers: `height: 62px`.
  - `.mp-tab { flex-direction: column; justify-content: center; gap: 2px; height: 100%; min-width: 84px }` (transfers: `min-width: 0`).
  - `.mp-tab b { background: none; padding: 0; height: auto; font: 500 20px/24px system-ui; color: #250E01 }` (transfers: 600 16px).
  - `.mp-tab span { font: 400 14px/18px; color: #250E01 }`.
  - Selected: `b { color: #FA6140 }`, `span { color: #250E01; font-weight: 400 }`, `::after { background: #FA6140; height: 2px; bottom: 0; border-radius: 2px 2px 0 0 }`.
- Drill-down stat block: a separate `statTabs(list, on, go)` renders `.mt-stats`:
  - `margin: 16px 16px 0; height: 89.5px; background: #FFBDA8; border-radius: 10px; display: grid; grid-template-columns: repeat(2, 290px); justify-content: center; column-gap: 4px`.
  - `a`: `position: relative; display: flex; flex-direction: column; align-items: center; justify-content: center`. `b`: 28px 700 #250E01. `span`: 14px #4A0415.
  - Active `::after`: `width: 84px; height: 6px; bottom: 0; left: 50%; translate: -50%; background: #FA6140; border-radius: 3px 3px 0 0`.

**S5. `searchRow()`: add a variant.**
- `searchRow(ph, { variant: 'live', toggles: bool, filters })`.
- Variant CSS:
  - `.mp-search { height: 40px; border-color: #C3CEC7; border-radius: 6px; padding: 0 10px; gap: 10px }`, icon 20px #1F515B.
  - `input::placeholder { color: #1F515B; font: 500 15px }`.
  - `.mp-fbtn { width: 45px; height: 35px; border-color: #C3CEC7; border-radius: 6px; color: #44544A; align-self: center }`, with a 3-slider icon.
  - Gap 9.
  - `toggles` renders two 18px icon buttons (list #37BD69 when active, cards #44544A; gap 33) instead of the filter button.

**S6. `animalCard()` is shared (Necropsy uses it).** Do not restyle it. Add new mortality-only templates (3b).

**S7. `.mp-fab` is shared (Eggs etc.).** Add `.mp-fab.is-round` (see 3b) instead of changing the base rule.

### 3b. Mortality-only templates (new CSS prefix `mt-`; CSS goes after the `.mpage` block, near line 4700)

**CSS tokens on `.mpage[data-mod='mortality']`**
- `--mt-ink: #44544A; --mt-dark: #250E01; --mt-teal: #1F515B; --mt-navy: #1F415B; --mt-mute: #7A8684; --mt-red: #FA6140; --mt-green: #006D35; --mt-line: #C3CEC7`.
- `font-family: -apple-system, BlinkMacSystemFont, 'SF Pro Text', var(--font), sans-serif`. Owner call: this matches the screenshots; drop it if V2 must keep its own face.

**1. `ROUTES.mortality`, main list**
- Return `{ theme: 'mort-list', bare: true, title: 'Mortality', right: <a class="mt-ctlink" data-go="mortality/transfers">Carcass Transfers<svg truck/></a> }`.
  - `.mt-ctlink`: 16px #250E01, gap 6, icon 20px. No badge, no site button.
- Body starts with `.mt-head` (background #F7DFD7):
  - `<div class="mt-range">`: a `<select data-range>` styled as text, 14px 500 #44544A, with a ▼ triangle. Padding 13px 16px 9px; the select is 21px from the left.
  - `<button class="mt-site" data-act="site">`: `margin: 0 16px 16px; height: 54px; width: calc(100% - 32px); background: #FFF; border: 0; border-radius: 6px; padding: 0 20px; font: 600 15px; color: #44544A; display: flex; justify-content: space-between`. Chevron 11px #1F515B.
  - `border-bottom: 1px solid #EAD4CC`.
  - Then `tabs(..., { variant: 'stack' })`.
- Then `searchRow('Search', { variant: 'live', toggles: tab === 'species', filters: tab === 'animals' ? n : -1 })`. On the Reasons tab: no button, full width. Margin 12px 16px 0.
- Then `.mt-list`.
- Then FAB: `<button class="mp-fab is-round is-add" data-act="report" aria-label="Report mortality">`. CSS `.mp-fab.is-round { width: 50px; height: 50px; padding: 0; justify-content: center; border-radius: 8px; right: 32px; bottom: 108px; box-shadow: 0 4px 8px rgba(0,0,0,.2) }`; `.is-add { background: #52F990; color: #1F515B }`. On tap: toast.
- Fix B1.

**2. `deathCard(d)`: rewrite as its own template (not `animalCard`)**

```
<a class="mt-dcard" data-go="mortality/animal/{aaid}">
  <span class="mt-dcard__by">Reported by <b>{by}</b></span>
  <span class="mt-dcard__main">{mtThumb(species, sex, {dead:true})}
    <span class="mt-dcard__txt"><b class="mt-aaid">AAID: {aaid}</b><em class="mt-mdate">Mortality: {dd Mon yyyy}{time ? ` • ${hh:mm AM}` : ''}</em>
      <strong>{species}</strong><i>{latin}</i><span>Site: {siteName}</span><span>Cause: {cause}</span></span></span>
  <span class="mt-strip" data-s="{completed|pending|draft|incoming|unsuitable}">{icon}<span>{label}</span><small>{right}</small></span></a>
```

- `.mt-dcard { display: flex; flex-direction: column; background: #FFF; border-radius: 8px; padding: 12px 1px 1px; overflow: hidden }`
- `__by { padding: 0 8px; font: 14px/20px; color: #7A8684 } b { font-weight: 400; color: #44544A }`
- `__main { display: flex; gap: 8px; padding: 10px 8px 7px }`
- `mtThumb` (big): `width: 160px; height: 160px; border-radius: 8px; background: #FFE0E0`. Mark tinted #839D8D.
- `.mt-badge { position: absolute; top: 4px; left: 4px; height: 21px; padding: 0 5px; border-radius: 4px; font: 600 12px/21px; color: #FFF }`
  - Dead variant: background #4A0415, plus a 12px white glyph.
  - Colour variants: `[data-s=id], [data-s=m]` #00AFD6; `[data-s=f]` #FA6140; 24×24.
- `__txt { display: flex; flex-direction: column; gap: 1px; padding-top: 3px }`
  - `.mt-aaid`: 16px/22px 700 #1F515B.
  - `.mt-mdate`: 13px/18px 600 #FA6140, not italic.
  - `strong`: 16px/22px 500 #44544A.
  - `i`: 14px/20px #7A8684.
  - `span`: 16px/22px 600 #44544A.
- `.mt-strip { height: 36px; display: flex; align-items: center; gap: 8px; padding: 0 16px 0 18px; font: 500 15px }`
  - `small { margin-left: auto; font: 600 12px }`
  - Completed: background #E1F9ED, colour #006D35, check-circle #37BD69.
  - Pending / draft: background #FCF8E8, colour #250E01, clock #E4B819; `small` #E4B819.
  - Incoming (In Transit): background #CFF5F3, colour #1F515B.
  - Unsuitable: background #FEF5F6, colour #FA6140.
- Strip labels:
  - "Necropsy Completed"
  - "Necropsy Pending"
  - "Necropsy Draft"
  - "In Transit"
  - "Unsuitable for necropsy" (when `d.report && !d.report.suitable`)
- Strip right-hand text:
  - Transfer id when `d.transfer`.
  - Otherwise "Ready to transfer" when pending.
  - Otherwise blank (see 4 for NPS).
- Delete the chevron and the right-hand tag.
- Keep `animalCard` for Necropsy.

**3. `speciesRow` for mortality: new `mtSpRow`**
- `.mt-sprow { display: flex; height: 95px; border: 1px solid #C3CEC7; border-radius: 8px; background: #FFF; overflow: hidden }`
- Photo: `90px × 100%`, `object-fit: cover`, placeholder #E5E5E5.
- Body: `padding: 13px 12px 0 18px; flex: 1`.
  - `b`: 16px 500 #44544A.
  - `i`: 13px italic #44544A.
  - Chips: margin-top 12.
- `.mt-chip { height: 19px; min-width: 40px; padding: 0 8px; border-radius: 4px; font: 13px/19px; text-align: center }`
  - Text format: "F - 1".
  - `[data-s=f]`: #FECFC5 / #FA6140. Others: #DDEBE9 / #1F515B.
- Count: `align-self: flex-start; margin: 13px 12px 0 0; font: 600 16px; color: #006D35`.
- No chevron. Gap between rows 16.

**4. Reason row: new `mtReason`**
- `.mt-reason { height: 55px; padding: 0 22px 0 13px; background: #FFF; border-radius: 8px; display: flex; align-items: center; justify-content: space-between }`
- `span`: 600 16px #44544A. `b`: 600 22px #006D35.
- No chevron. List gap 8, first row margin-top 16.

**5. Drill-downs (the `view === 'species' | 'reason'` branch)**
- `{ theme: 'mort-drill', bare: true, title: 'Mortality', right: search + ⋮ icon buttons (#1F415B 22px) }`
  - Species: search and ⋮. Reason: ⋮ only.
  - Search toggles an inline search row.
  - No subtitle, no site button.
- Species head:
  - `.mt-spcard { margin: 0 16px; height: 83px; border: 1px solid #FFBDA8; border-radius: 10px; background: #FFE5DD; display: flex; align-items: center; gap: 14px; padding: 0 16px }`
  - Avatar: 50px circle, #E7D0C8.
  - `b`: 16px 600 #000. `i`: 14px italic #44544A, text wrapped in parentheses.
  - It sits 1px below the bar rule.
- Reason head: `<h3 class="mt-rtitle">`, `margin: 6px 17px 18px; font: 400 22px/28px; color: #000`.
- Then `statTabs()`.
- Then:
  - Reasons tab: `mtReason` list (margin-top 20).
  - Species tab: `searchRow({ variant: 'live', toggles: true })` 28px below, then `mtSpRow` list.
  - Animals tab: `searchRow({ variant: 'live' })` (reason) or none (species), then `mtAnimalRow` list.
- `mtAnimalRow`:
  - `.mt-arow { display: flex; gap: 11px; padding: 8px; background: #FFF; border-radius: 12px; align-items: flex-start }`
  - Thumb: 115px square, radius 8, placeholder #D7F7F5, colour badge (not dead-maroon).
  - Text: `padding-top: 2px`.
    - AAID: 16px 700 #1F515B, "AAID: n".
    - Name: 16px 500 #44544A.
    - Latin: 14px italic #7A8684.
    - "Encl: x": 16px 600 #44544A.
  - Chevron: 14px #7A8684, `align-self: center; margin-right: 10px`.
  - Gap 8.

**6. `deathPage(aaid)`: full rewrite**
- `{ theme: 'hero', bare: true }` with **no bar**. Hide `.mpage__bar`; the back button lives inside the hero.
- Hero:
  - `.mt-hero { position: relative; height: 329px; background: #9DACA3 center/cover url(photo) }`.
  - Back button: white, at 17/20.
  - Overlay: `left: 30px; right: 30px; top: 68px; height: auto; min-height: 191px; padding: 12px 8px; border-radius: 8px; background: rgba(0,0,0,.5); color: #FFF`.
    - `h2`: 34px 400.
    - `i`: 13px.
    - "Sex: <b>Undetermined</b>", "Encl: <b>…</b>", "AAID: <b>…</b>": 14px/19px, bold parts 600.
    - We have sex, encl, aaid and site. Skip Breed/Morph/Life stage/Weight.
  - `.mt-deadpill { position: absolute; left: 31px; bottom: 33px; height: 25px; padding: 0 12px; border-radius: 12.5px; background: #E93353; font: 13px/25px; color: #FFF }`, text "Dead".
- Optional 50px white tab strip with one tab "Mortality": 14px 500 #006D35, 2px underline #006D35, bottom border #F0F0F0.
- Section `<h3 class="mt-sec">Mortality Report</h3>`: `margin: 20px 20px 12px; font: 500 18px; color: #44544A`.
- Card: `.mt-report { margin: 0 16px; padding: 16px; background: #FFE9E9; border-radius: 12px; display: flex; flex-direction: column; gap: 14px }`
  - `dt`: 14px/20px #44544A. `dd`: 16px/22px 600 #000, `margin: 2px 0 0`.
  - Rows, in order:
    1. "Suspected Cause of death"
    2. "Date and Time of Death": `28 Sep 2026 • 05:32 PM`, or date only when there is no time.
    3. "Carcass Condition"
    4. "Notes": "NA" when empty.
    5. "Necropsy Requested": "Yes"
    6. "Reported by"
    7. Then ours, reference-styled: "Found on", "Age at death", "Section", "Reporting" (late / on time), "Carcass transfer" (link), "Disposal method".
  - `margin-bottom: 150px` so the fixed sheet does not cover it.
- Fixed bottom sheet:
  - `.mt-foot { position: sticky; bottom: 0; background: #FFF; border-radius: 16px 16px 0 0; box-shadow: 0 -2px 6px rgba(0,0,0,.08); padding: 18px 16px 10px }`
  - `small`: 14px #7A8684, "Necropsy Status".
  - `b`: 16px 500. Colour #FA6140 unless completed-and-suitable (#006D35). Text is the necropsy label.
  - `.mt-btn.is-go { margin-top: 18px; height: 50px; width: 100%; border-radius: 10px; background: #37BD69; font: 500 16px; color: #FFF }`, labelled "View report" (completed) or "Open necropsy", with `data-go="necropsy/case/{aaid}"`.
- FAB "+": `right: 17px; bottom: 92px; 56×56; border-radius: 12px; background: #52F990`, black plus 24px. Toast on tap.

**7. `transfersPage(tab)`**
- `{ theme: 'mort-list', barH: 64, barLine: '#FFBDA8', bare: true, title: 'Carcass Transfers', right: '' }`. Remove `sampleTag` and the site button from the bar; keep a sample note somewhere quiet (see 4).
- Tabs: `tabs(..., { variant: 'stack', compact: true })`.
- Search: `searchRow('Search', { variant: 'live', filters })`.
- New `tCard(t)`:

```
<a class="mt-tcard" data-go="mortality/transfer/{id}">
 <span class="mt-tcard__top"><span>Requested by <b>{by}</b></span><span>{dd Mon yyyy} <i>●</i> {hh:mm AM}</span></span>
 <span class="mt-tcard__mid"><span><b class="mt-ctid">{id}</b><span class="mt-carc">Carcasses: <b>{n}</b></span>
   <span class="mt-route"><span data-end="from">{site}</span><span data-end="to">{centre}</span></span></span><svg chevron/></span>
 <span class="mt-stage" data-st="{loading|checkin|checkout|done|cancel}">{sub}</span></a>
```

  - `.mt-tcard { display: block; background: #FFF; border-radius: 6px; padding: 18px 4px 4px; box-shadow: 0 2px 4px rgba(120,60,40,.25) }`
  - `__top { display: flex; justify-content: space-between; padding: 0 12px 0 9px; font: 12px/16px; color: #44544A }`. `b`: 600. `i`: 4px dot #7A8684, `font-size: 8px`, margin 0 4px.
  - `__mid { display: flex; align-items: center; padding: 18px 12px 8px 9px }`.
  - `.mt-ctid`: 17px/21px 600 #1F515B.
  - `.mt-carc`: 16px/20px #44544A. `b`: 700.
  - `.mt-route { margin-top: 8px; display: flex; flex-direction: column; gap: 4px; font: 15px/20px; color: #44544A }`.
    - `span::before`: 16px-wide glyph with `margin-right: 8px`.
    - From: a 6px dot #37BD69 plus an 8px line.
    - To: a 2px red line plus a 7px square #E93353.
  - Chevron: 14px #44544A, `margin-left: auto`.
  - `.mt-stage { display: block; height: 32px; padding: 0 12px; border-radius: 0 0 4px 4px; font: 500 15px/32px }`, colours by stage as in the 0092–0095 table.
  - Map `t.sub` to `data-st`: Loading Pending → loading, Security Checkin Pending → checkin, Security Checkout Pending → checkout, Transfer Completed → done, Canceled → cancel.
- List gap 12, first card 12px below the search.
- FAB: `<a class="mp-fab is-round is-truck">`, `48×48; border-radius: 12px; right: 35px; bottom: 86px; background: linear-gradient(180deg, #FA6140, #EC3A50)`, white 26px truck-plus. No text.
- Filters: `filterSheet([...], S.f, apply, { full: true })` with facets:
  - `time` (radio): all / 24h / 7d / 1m / 3m / custom (custom behaves like all).
  - `site` (select, over `DB.sites`).
  - `centre` (checkbox plus search, labelled "Facility").
  - Change `pass()` accordingly: 1 / 7 / 30 / 90 days; site = `t.site`.

**8. `transferPage(id)`: rebuild**
- `{ theme: 'maroon', barCenter: true, title: t.id, right: t.stage !== 'cancel' ? '⋮ button (data-act="more")' : '', bare: true }`.
- Body:
  - `.mt-thead { background: #4A0415; color: #FFF; padding: 0 17px 17px; display: flex; justify-content: space-between; align-items: center }`.
    - Left: `<b>Carcass Transfer</b>` (16px 400), then `.mt-route.is-white` (16px 600, pitch 26, white text).
    - Right: the QR, when stage ≠ pending, rendered `fill: #FFF`, 46px, no border or background. `.mp-qr` today is 96px white with a border, so use a new `.mt-qr`.
  - `.mt-tby { background: #420413; color: #FFF; padding: 16px 17px 14px; display: grid; grid-template-columns: 32px 1fr auto; column-gap: 8px }`.
    - `small`: "Initiated by", 12px, spans all columns, margin-bottom 8.
    - Avatar: 32px #00D6C9 circle, white 14px initial.
    - Name: 15px 500. Date: 13px ("dd Mon yyyy ● hh:mm AM").
    - Round buttons: `.mt-rbtn { 34px; border-radius: 50%; background: #28020B; color: #FFF }`, gap 7. Reuses the call/msg handlers.
  - `.mt-pink { background: #FFEDED }`:
    - Row "selected carcass" (lowercase): `height: 40px; padding: 0 17px; gap: 8px; font: 16px; color: #44544A`, black paw icon 20px.
    - Carcass cards: `mtAnimalRow` with a `pink` modifier (background #FFE3E3, margin 0 16px, gap 8), **no chevron**, but still `data-go` to the death page. Bottom padding 16.
    - Checklist row, shown when the stage is not "Loading Pending" and `checklist > 0`, or always on cancel as in the reference:
      - `border-top: 1px solid #FFF; height: 55px; padding: 0 17px; display: flex; gap: 10px; align-items: center`.
      - Check-circle 20px #37BD69.
      - `small`: "Transfer Checklist", 12px #44544A. `b`: "{n}/7 Filled", 16px 500 #44544A.
      - Tapping it opens the checklist page.
  - Comments:
    - Head row `.mt-comhead { height: 42px; padding: 0 17px; gap: 10px; font: 15px; color: #000 }`, icon #7A8684.
    - Existing comments: 14px, `margin: 0 17px 8px`.
    - `.mt-say { margin: 0 12px; height: 49px; border: 1px solid #C3CEC7; border-radius: 8px; display: flex; align-items: center; padding: 0 12px 0 25px }`.
      - Input: transparent, 15px, placeholder #1F515B.
      - Send: icon button 26px, colour #C3CEC7, or #1F515B when there is text.
      - Remove the "Send" `.mp-btn`.
  - Footer:
    - Cancel: `.mt-canbar { position: sticky; bottom: 0; margin-top: auto; height: 65px; background: #7A8684; border-radius: 16px 16px 0 0; display: flex; align-items: center; justify-content: center; gap: 16px; color: #FFF; font: 500 20px }`, content "✕ Canceled".
    - Done: same bar, background #006D35, content "✓ Transfer Completed". Not in the references; follows the cancel bar.
    - Active: `.mt-status { position: sticky; bottom: 0; margin-top: auto; background: #FFF; border-radius: 24px 24px 0 0; box-shadow: 0 -3px 8px rgba(0,0,0,.12); padding: 16px 17px 20px }`.
      - Line 1: `small` "Current Status ● {dd Mon}", 14px #7A8684.
      - Line 2: `b` 20px 500 #1F515B, with "See all" (14px #006D35) on the right. "See all" → toast, or scroll to a stage list.
      - Button `.mt-btn.is-teal { margin: 22px 23px 0; height: 56px; border-radius: 12px; background: #1F515B; font: 400 20px; color: #FFF; width: calc(100% - 46px) }`.
    - Status name map: Loading Pending → "Transfer Initiated". Otherwise `t.sub`.
  - Move "Cancel transfer" into the ⋮ action (a small `sheet` with a red "Cancel transfer" row).
- Keep `wire()` handlers. Change the checklist act to `go('mortality/transfer/{id}/checklist')`.

**9. `checklistSheet`: make it a route**
- Add to `ROUTES.mortality`: `if (view === 'transfer' && sub === 'checklist')`, i.e. parts `['transfer', id, 'checklist']`. That needs `const [view, arg, sub] = parts`, which the destructuring already provides.
- Returns `{ theme: 'checklist', bare: true, title: 'Transfer Checklist' }`.
- Body: `.mt-cl { padding: 12px 16px 100px; display: flex; flex-direction: column; gap: 16px }`, with a `<details class="mt-acc">` per section.
  - `summary { height: 56px; display: flex; align-items: center; gap: 14px; padding: 0 16px 0 15px; background: #1F415B; border-radius: 8px; color: #FFF; font: 600 15px; list-style: none }`.
    - The per-section icon is a 20px white stroke SVG.
    - Chevron at the far right, rotated when open.
  - `[open] summary { border-radius: 6px 6px 0 0 }`.
  - Body: `background: #FFF; border-radius: 0 0 8px 8px; padding: 0 12px 16px`.
    - `.mt-acc__sub { margin: 0 -12px 10px; height: 32px; padding: 0 8px; background: #C3CEC7; font: 15px/32px; color: #000 }`, holding the section name.
    - Inputs: `height: 50px; border: 1px solid #839D8D; border-radius: 4px; background: #EFF5F2; padding: 0 16px; font: 16px; color: #44544A`, placeholder = the field name, no label. Gap 16.
    - Check rows: `height: 37px; display: flex; justify-content: space-between; font: 16px; color: #1F515B`, checkbox 18px square.
  - Fix the CHECKLIST label: 'Commander contact no' → 'Contact no'.
- Footer: `.mt-foot.is-plain { position: sticky; bottom: 0; background: #FFF; padding: 8px 40px }`, button 56px, radius 10, #37BD69, 600 20px, "Submit".
- On submit, keep the current logic, then `go(\`mortality/transfer/${id}\`, { replace: true })`.

**10. `newTransfer()`: rebuild**
- `{ theme: 'white', bare: true, title: 'Carcass Transfer' }`, no sub.
- Sections: `.mt-fsec { padding: 24px 16px 16px; border-bottom: 1px solid #C3CEC7 }`.
  - `h3`: 16px 400 #44544A, margin 0 0 16px.
  - `em`: italic #7A8684, not bold, for "(Optional)".
- Location card: `.mt-loc`, as specified under IMG_0096. Two rows, 67.5 and 55.5 tall. Transparent native `<select>`s overlay each row (`appearance: none; opacity` for the text colours via a mirrored label).
- Select Carcass field: `.mt-pickf`, 50px. On tap, a `sheet({ title: 'Select Carcass' })` with the current checkbox list.
  - Chosen carcasses render below the field as `mtAnimalRow`, with a remove ✕.
- Upload: `.mt-upload`, as specified under IMG_0096.
- Notes: `textarea.mt-notes { height: 57px; background: #FCF4AE; border: 1px solid #839D8D; border-radius: 4px; padding: 16px; font: 16px; color: #44544A }`, placeholder "Add Notes".
- After the sections: `.mt-fill { flex: 1; background: #EFF5F2 }` (on body flex).
- Footer: `.mt-foot.is-plain`, button 50px (`padding: 8px 16px`), radius 10.
  - Disabled #C3CEC7 / enabled #37BD69. White 600 16px "Submit Request".
- Tidy-up: remove `sampleTag` from all four mortality/transfer routes; see 4.

**11. `filters()` in `ROUTES.mortality`**
- Call `filterSheet(..., { full: true })`.
- Sex options: Male, Female, Indeterminate, Undetermined (Indeterminate matches nothing in our data).
- `rep`: type radio.
- `nec` options, in order: Completed, Pending, Unsuitable, Necropsy Not Required, At Site, Ready to transfer, In Transit, Transfer Pending, At Necropsy Facility. Map from data:
  - Completed = stage completed and suitable.
  - Unsuitable = `report.suitable === false`.
  - Pending = pending or draft.
  - Ready to transfer = pending with no transfer.
  - In Transit = incoming with a transit transfer.
  - Transfer Pending = transfer at the 'pending' stage.
  - At Necropsy Facility = done-transfer and not completed.
  - At Site / Not Required: no data, never matches.
- Cause: add `search: true`.

## 4. Data we don't have, and what to show instead
- **Death time:** `deaths[i][4]` is often null. Show "Mortality: 20 May 2026" without the "• time" part.
- **NPS number** (0078 strip right, 0082 title): not in the data. Recommended: completed strips show nothing on the right. Alternative: derive a stable sample id `NPS21-${String(i).padStart(5,'0')}` over completed deaths sorted by date, and flag it as sample like the transfers.
- **Photos:** keep our species photos. Use the tinted placeholders (#FFE0E0 main list, #E5E5E5 species rows, #D7F7F5 drill-down and carcass rows) only when there is no photo.
- **Sex codes:** the data has M, F and U only. Show "U" (chip "U - 3", badge "U" #00AFD6). The reference's "ID" means Indeterminate, which our data does not have.
- **Hero facts** (breed, morph, life stage, weight): not in the data. Show only Sex, Encl, AAID and Site.
- **Attachments** in the mortality report: omit the row.
- **Animal-profile tabs** (History, Diet…): not built. Omit the strip, or show only "Mortality".
- **Initiator phone and avatar:** use the initial of `t.by` on #00D6C9.
- **"See all" status history:** toast, or a small sheet listing the T_STEPS reached.
- **Uploads, the report FAB, the "+" on the death page:** inert, with a toast.
- **Transfers are SAMPLE.** The reference has no "Sample data" chip. Recommended: keep one discreet note at the end of each transfers list (`.mp-note`, 12px #7A8684, "Transfers are sample data built from real pending necropsies"). Do not put it in the bar. This is the owner's call: exact match versus honesty labelling.
- **Numbers:** our counts (1,009 animals / 309 species / 16 reasons in 30 days; transfers 4/17/18/9) stay as they are. The reference's 5/5/2 and 7/42/97/24 are the live app's.
