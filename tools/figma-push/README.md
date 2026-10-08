# Push app screens to Figma with auto layout (30 Sep 2026)

1. `python3 tools/figma-push/run.py tools/figma-push x` (from the repo root, server on :8000).
   It serialises V2 Home, the Quick Access Menu and both feed pages into `<key>.json`.
   `ser.js` turns flex into auto layout, CSS grid into Figma GRID, and positioned boxes into absolute children.
   Names come from `names.json` (blocks) and `elem.json` (BEM elements).
2. `python3 tools/figma-push/payload.py qa ann notes home` writes `carrier_<key>.svg` (the payload as SVG text) and downloads the images.
3. Upload each carrier with the Figma MCP `upload_assets` tool (SVG), then run `builder.js` in `use_figma`
   with `__KEY__/__X__/__Y__` replaced. The builder reads the carrier, builds the frame, and deletes the carrier.
4. Upload the images with `upload_assets` and `nodeIds` (one per unique image), then copy the fills to the other nodes.
The plugin runtime has no `fetch`, which is why the payload travels as a text layer.

## Lessons from the 30 Sep push (fixed by hand in the file; the builder now covers the first)
- Icons must never FILL. The app's SVGs use preserveAspectRatio="none", so a 32px glyph stretched to 130px.
- CSS `::before`/`::after` scrims belong between the photo and the text. Check their order after a build.
- Give the root frame the `<html>` background (ser.js now does), or exports show black bands.
- The Pending Actions corkboard wraps two notes to a row only with an 8px gap.
- A <button> centres its label natively. ser.js now does the same; the site tabs and three segment options were fixed by hand.

## 1 Oct 2026: the review site's Home → frame `862:2` "Home · Review (1 Oct)" (x 3328)
Serialised from the REVIEW BUILD (`tools/review-build/build.py` into scratch, served, `?v=2`), not index.html, because the screen asked for was the review link's.
- **Rename the root before building.** builder.js deletes any page frame with the root's name, so a root called "Home" would delete Home 816:2.
- Skip the ticker's `.hstrip__set[aria-hidden]` copy and any open sheet (`.gsx-sheet, .gsx-scrim`).
- What still needed fixing by hand after this build (the builder does not do it yet):
  - A horizontally scrolling lane comes out VERTICAL and centres its tape off-frame. Make it HORIZONTAL / MIN.
  - `::after` scrims land ABOVE the text (favourites, note plates); a `::before` scrim lands BELOW the photo (Species card). Order: photo → scrim → content.
  - CSS-mask icons (the pencils) and `::before` dots come out as empty frames.
  - Fixed-width single-line text wraps or truncates: the "°" of "29°", "Observation Notes", the Key Insights titles. These need HUG.
  - Transforms are not carried (the corkboard's tilts).
  - Negative margins are lost (fav-band −16).
- **`insertChild(i, n)` on a node that is already a child counts the index before the move.** To push a layer down, move the layer *under* it to 0 instead.

## 5 Oct 2026: Home · Tablet `902:2` (x 200) and Home · Mobile `903:2` (x 1044)
Serialised from the Selected-Modules clone (`?v=2`, served on :8731) at 744 and 390; page 0:1 now also holds the designer's `Section 1`.
Fixed in ser.js / builder.js this time (no hand fixes needed for these any more):
- **Paste builder.js with its ` ` escape intact.** A literal NBSP in the restore regex became a space when pasted inline, so every SVG failed to parse (empty icon frames) and text broke mid-word.
- Paint order: every node carries a `zk` key (non-positioned −0.5, else z-index); siblings are re-appended in that order when in-flow keys already ascend (deck peeks, scrims under text).
- A box whose single child is wider than it (the ticker lane) is HORIZONTAL; ellipsis truncation only when the browser actually cut the line.
- Gradient stops outside 0–100% are resampled at the edges; `color(srgb …)` parses; an empty box drawn by a `::before` SVG background becomes that icon; inline margins become spaces.
- A bare frame whose first child sits above it (negative margin) grows upward instead of clamping; leftover spacers become neighbour padding with the frame gap set to the most common total.
- builder's same-name cleanup removes while iterating `page.children` and can skip frames — check for leftovers.
Still by hand: Page and Home Header were set to auto layout after the build (Page gap −10), the Modules pencil was added (its button has an sr-only label), and CSS-derived names were renamed (L V2sn → Pending, Hstrip → Audit Ticker).
Image fills can be re-applied by `imageHash` from an earlier upload in the same file — no re-upload needed for a rebuild.
