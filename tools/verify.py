"""Pre-ship verification for the ANTZ home page — SESSION_HANDOFF §8.4.

    python3 tools/verify.py            # everything
    python3 tools/verify.py sweep      # just the six-width overflow sweep
    python3 tools/verify.py drag       # just the drag checks

Runs against the working copy over file://, in headless Chrome, driven by CDP.
Reduced motion is forced: WAAPI promises never settle under a virtual-time
budget, which leaves dismissed cards in the DOM at their old coordinates and
quietly corrupts anything measured from a node's position.
"""
import os, sys, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from cdp import Chrome

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
URL = "file://" + ROOT.replace(" ", "%20") + "/index.html"
WIDTHS = [1920, 1024, 900, 768, 640, 500]

fails = []


def check(name, ok, detail=""):
    print(f"  {'PASS' if ok else 'FAIL'}  {name}{('  — ' + detail) if detail else ''}")
    if not ok:
        fails.append(name)


def tag(c, js, name):
    """Give the element this expression returns a stable id, and return a selector."""
    got = c.eval(f"(()=>{{const e={js};if(!e)return null;e.id={name!r};return true}})()")
    return f"#{name}" if got else None


# ── the catalogue and the default page agree ───────────────────────────────
def defaults(c):
    print("\ndefault layout")
    problems = c.eval("antz.checkDefaults()")
    check("catalogue agrees with the seeded page", problems == [],
          "; ".join(problems) if problems else "")


# ── every variant at every size, at six widths ─────────────────────────────
PROBE = r"""
(() => {
  const rows = [];
  for (const slot of document.querySelectorAll('.slot')) {
    if (!slot.dataset.uid.startsWith('x')) continue;
    const card = slot.querySelector('.card'); if (!card) continue;
    const id = card.dataset.variant + ' @' + card.dataset.size;
    const root = card.querySelector('[class^="l-"]');
    if (root && root.scrollHeight > root.clientHeight + 1)
      rows.push(`OVERFLOW  ${id}  ${root.className} ${root.scrollHeight}px in ${root.clientHeight}px`);
    for (const el of card.querySelectorAll('*')) {
      if (!el.firstChild || el.children.length || !el.textContent.trim()) continue;
      /* A VISUALLY-HIDDEN LABEL IS A 1px BOX ON PURPOSE, so `scrollWidth >
         clientWidth` is its defining property rather than a defect — every
         `.sr-only` in the product reports 30-100px of text inside one pixel,
         by construction. This check existed to catch a LABEL being cut, and
         it was counting the screen-reader text that exists precisely because
         the visible label might be. Measured on a clean checkout of HEAD
         before this line was added: 30 of these per width, on notes.recent
         alone, at all six widths — the suite has been failing on its own
         false positive, which is why nobody could read the sweep. */
      if (el.classList.contains('sr-only')) continue;
      if (el.scrollWidth > el.clientWidth + 1)
        rows.push(`TRUNCATED ${id}  ${el.className} ${el.scrollWidth}>${el.clientWidth} “${el.textContent.trim().slice(0,40)}”`);
    }
  }
  return rows;
})()
"""


def sweep(c):
    print("\noverflow and truncation, every variant at every size")
    for w in WIDTHS:
        c.set_viewport(w, 2000)
        time.sleep(0.35)
        c.eval("antz.allVariants()")
        time.sleep(0.6)
        n = c.eval("document.querySelectorAll('.slot[data-uid^=x]').length")
        rows = c.eval(PROBE)
        check(f"{w}px · {c.eval('antz.columns()')} cols · {n} cards", not rows,
              "" if not rows else f"{len(rows)} defects")
        for r in rows[:12]:
            print(f"        {r}")
    c.set_viewport(1024, 2000)
    c.eval("antz.reset()")
    time.sleep(0.6)


# ── drag reorders the store, by mouse and by finger ────────────────────────
def enter_edit(c):
    c.click("#avatarBtn")
    time.sleep(0.3)
    sel = tag(c, "[...document.querySelectorAll('.pmenu__label')]"
                 ".find(e=>e.textContent.trim()==='Edit Modules')?.closest('button,[role=menuitem],li,a')",
              "t_edit")
    if not sel:
        raise RuntimeError("could not find Edit Modules in the account menu")
    c.click(sel)
    time.sleep(0.5)
    if not c.eval("document.body.classList.contains('is-editing')"):
        raise RuntimeError("Edit Modules did not put the page into edit mode")


def order(c):
    return c.eval("antz.state().cards.map(d=>d.uid)")


def drag_case(c, kind):
    # Touch listeners are attached at load, so emulation has to be on before the
    # page boots — and off again before the mouse case, or the two interleave.
    c.cmd("Emulation.setTouchEmulationEnabled", enabled=(kind == "touch"), maxTouchPoints=5)
    c.goto(URL)
    c.eval("antz.reset()")
    time.sleep(0.5)
    enter_edit(c)
    before = order(c)
    a = tag(c, "document.querySelectorAll('.slot')[0]", "t_a")
    b = tag(c, "document.querySelectorAll('.slot')[3]", "t_b")
    (c.touch_drag if kind == "touch" else c.drag)(a, b)
    after = order(c)
    moved = before[0] != after[0] and sorted(before) == sorted(after)
    check(f"{kind} drag reorders the store", moved, f"{before[:4]} → {after[:4]}")
    leaked = c.eval("document.querySelectorAll('.is-dragging, .drag-proxy').length")
    check(f"{kind} drag tears down cleanly", leaked == 0, f"{leaked} nodes left behind")


def drag(c):
    print("\ndrag, through the browser's own input pipeline")
    drag_case(c, "mouse")
    drag_case(c, "touch")


if __name__ == "__main__":
    want = sys.argv[1] if len(sys.argv) > 1 else "all"
    with Chrome(width=1024, height=2000) as c:
        c.goto(URL)
        if c.eval("typeof window.antz") != "object":
            sys.exit(f"the page did not boot at {URL} — is index.html beside tools/?")
        if want in ("all", "defaults"):
            defaults(c)
        if want in ("all", "sweep"):
            sweep(c)
        if want in ("all", "drag"):
            drag(c)
        print("\nconsole")
        errs = c.errors()
        check("no errors or exceptions", not errs, "; ".join(t[:120] for _, t in errs))
    print(f"\n{'ALL PASS' if not fails else str(len(fails)) + ' FAILED: ' + ', '.join(fails)}")
    sys.exit(1 if fails else 0)
