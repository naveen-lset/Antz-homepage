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
