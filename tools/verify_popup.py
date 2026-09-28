"""The note popup's carousel, filmed frame by frame (28 Sep 2026).

The owner kept seeing "old notes coming and going" while checks that sampled
positions AFTER a turn all passed — the glitch lived between frames. So this
records every animation frame inside the page (each card's note, centre, width,
opacity) through real gestures, then follows each NOTE across frames, whatever
element happens to draw it, and fails on anything a person would see:

  · a note that appears or vanishes in the middle of the screen
  · a note that jumps more than a frame's worth of travel
  · a sudden change of size or opacity outside full screen's own growth
  · a gesture that turns more or fewer than the notes it should

    python3 tools/verify_popup.py [base-url]      (default http://127.0.0.1:8080/)

Needs the page served over http; `reduced_motion=False` or there is nothing
to film.
"""
import sys, time
from cdp import Chrome

BASE = (sys.argv[1] if len(sys.argv) > 1 else "http://127.0.0.1:8080/").rstrip("/") + "/"
fails = []


def check(name, ok, detail=""):
    print(f"  {'PASS' if ok else 'FAIL'}  {name}" + (f"  — {detail}" if detail and not ok else ""))
    if not ok:
        fails.append(name)


REC = r"""
window.__f=[];window.__t0=performance.now();
/* READ AFTER THE PAINT: a rAF callback may run before or after the carousel's
   own in any frame, so reading inside rAF sometimes logs the previous frame's
   position and doubles the next step. A task queued from rAF runs after that
   frame is painted — it sees exactly what was on screen. */
(function f(ts){
  setTimeout(()=>{
    const cards=[...document.querySelectorAll('.dpop')].map(e=>{const r=e.getBoundingClientRect(),cs=getComputedStyle(e);
      return {t:(e.querySelector('.dpop__title')?.textContent||''), x:r.left+r.width/2, w:r.width,
              o:+cs.opacity, full:e.classList.contains('is-full')}});
    __f.push({ms:(ts ?? performance.now())-__t0, c:cards});
  }, 0);
  if(__f.length<1500) requestAnimationFrame(f)})(); 1"""
TITLE = "document.querySelector('.dpop:not(.dpop--peek) #dpopTitle')?.textContent"
FULL = "document.querySelector('.dpop:not(.dpop--peek)')?.classList.contains('is-full')"


def glitches(frames, W):
    """Follow each note on screen; report what a person would see as a glitch."""
    def vis(fr):
        return {c["t"]: c for c in fr["c"] if c["o"] > .05 and c["t"] and c["x"] + c["w"] / 2 > 0 and c["x"] - c["w"] / 2 < W}
    out, prev = [], None
    for fr in frames:
        cur = vis(fr)
        if prev is not None:
            dt = max(16.0, fr["ms"] - prev_ms)   # no screen shows frames closer than 16ms
            for t, a in cur.items():
                b = prev.get(t)
                if b is None:
                    if a["x"] - a["w"] / 2 > 40 and a["x"] + a["w"] / 2 < W - 40:
                        out.append(f"{fr['ms']:.0f}ms {t!r} appeared mid-screen")
                    continue
                # the fastest spring here peaks near 3px/ms; twice that between two
                # frames is a teleport, not motion
                if abs(a["x"] - b["x"]) > max(90, 6 * dt):
                    out.append(f"{fr['ms']:.0f}ms {t!r} jumped {b['x']:.0f}->{a['x']:.0f} in {dt:.0f}ms")
                if not a["full"] and not b["full"] and abs(a["w"] - b["w"]) > max(90, 6 * dt):
                    out.append(f"{fr['ms']:.0f}ms {t!r} size jumped {b['w']:.0f}->{a['w']:.0f}")
            for t, b in prev.items():
                if t not in cur and not b["full"] and b["x"] - b["w"] / 2 > 40 and b["x"] + b["w"] / 2 < W - 40:
                    out.append(f"{fr['ms']:.0f}ms {t!r} vanished mid-screen")
        prev, prev_ms = cur, fr["ms"]
    return out


def session(W, run):
    with Chrome(width=W, height=900, port=9471, reduced_motion=False) as c:
        c.goto(BASE + "index.html?v=2", settle=1.8)
        c.eval("document.querySelectorAll('.obs')[1].scrollIntoView({block:'center'}); 1"); time.sleep(.4)
        c.eval("document.querySelectorAll('.obs')[1].click(); 1"); time.sleep(.9)
        start = c.eval(TITLE)
        c.eval(REC)
        run(c, W // 2)
        frames = c.eval("__f")
        return start, c.eval(TITLE), c.eval(FULL), glitches(frames, W), c.errors()


def wheel(c, x, dx, dy=0):
    c.cmd("Input.dispatchMouseEvent", type="mouseWheel", x=x, y=600, deltaX=dx, deltaY=dy)


def swipe_with_tail(gap):
    def run(c, X):
        for k in range(12):
            wheel(c, X, 30, 1 if k % 3 else 0); time.sleep(.008)
        time.sleep(gap)
        d = 26.0
        for k in range(45):
            wheel(c, X, max(1, round(d)), 1 if k % 5 == 0 else 0); d *= .9; time.sleep(.008)
        time.sleep(1.1)
    return run


def key_turns(c, X):
    for key, code in (("ArrowRight", 39), ("ArrowRight", 39), ("ArrowLeft", 37)):
        c.cmd("Input.dispatchKeyEvent", type="keyDown", key=key, code=key, windowsVirtualKeyCode=code); time.sleep(1.0)


def flick_then_short(c, X):
    c.cmd("Input.dispatchTouchEvent", type="touchStart", touchPoints=[{"x": X + 150, "y": 500}])
    for k in range(1, 12):
        c.cmd("Input.dispatchTouchEvent", type="touchMove", touchPoints=[{"x": X + 150 - k * 24, "y": 501}]); time.sleep(.012)
    c.cmd("Input.dispatchTouchEvent", type="touchEnd", touchPoints=[]); time.sleep(1.1)
    # a short, slow drag back: under halfway, so it must spring home
    c.cmd("Input.dispatchTouchEvent", type="touchStart", touchPoints=[{"x": X - 100, "y": 500}])
    for k in range(1, 6):
        c.cmd("Input.dispatchTouchEvent", type="touchMove", touchPoints=[{"x": X - 100 + k * 14, "y": 500}]); time.sleep(.03)
    time.sleep(.15)
    c.cmd("Input.dispatchTouchEvent", type="touchEnd", touchPoints=[]); time.sleep(1.1)


def read_scroll(c, X):
    for k in range(14):
        wheel(c, X, 0, 40); time.sleep(.008)
    time.sleep(1.0)
    for k in range(30):
        wheel(c, X, 0, -40); time.sleep(.008)
    time.sleep(1.1)


def quick_presses(c, X):
    """→ pressed again while the first turn is still landing: the case that
    once leapt two cards in one frame."""
    for pause in (.18, 1.2):
        c.cmd("Input.dispatchKeyEvent", type="keyDown", key="ArrowRight", code="ArrowRight", windowsVirtualKeyCode=39); time.sleep(pause)


NOTES = ["Deep Flank Wound", "Metal Work", "Coat Condition", "Feed Refusal"]

for W in (1024, 744):
    print(f"\nthe note popup's carousel at {W}px")
    for gap in (0.0, 0.25):
        s, e, full, g, err = session(W, swipe_with_tail(gap))
        check(f"a trackpad swipe with its momentum tail (pause {gap}s) turns exactly one note",
              s == NOTES[1] and e == NOTES[2], f"{s} -> {e}")
        check("…never goes full screen", not full)
        check("…and nothing jumps, flashes, appears or vanishes on the way", not g, "; ".join(g[:4]))
        check("…with no errors", not err, str(err))
    s, e, full, g, err = session(W, key_turns)
    check("→ → ← lands one along", s == NOTES[1] and e == NOTES[2], f"{s} -> {e}")
    check("…glitch-free", not g, "; ".join(g[:4]))
    s, e, full, g, err = session(W, quick_presses)
    check("→ pressed again mid-turn lands two along", s == NOTES[1] and e == NOTES[3], f"{s} -> {e}")
    check("…flowing on, not leaping", not g, "; ".join(g[:4]))
    s, e, full, g, err = session(W, flick_then_short)
    check("a flick turns, a short slow drag springs home", s == NOTES[1] and e == NOTES[2], f"{s} -> {e}")
    check("…glitch-free", not g, "; ".join(g[:4]))
    s, e, full, g, err = session(W, read_scroll)
    check("reading scroll down and back: same note, centred again", s == e == NOTES[1] and not full, f"{s} -> {e}, full={full}")
    check("…glitch-free", not g, "; ".join(g[:4]))

print(f"\n{len(fails)} FAILED" + (": " + ", ".join(fails) if fails else ""))
sys.exit(1 if fails else 0)
