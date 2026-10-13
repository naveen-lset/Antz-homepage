/* Modules section · Style 1 | Style 2 (Sourav, 12 Oct 2026).
   Sets <html data-mstyle> from ?ms=1|2, else the last choice on this device,
   else 2; and puts a small switch beside the Modules heading. */
(function () {
  var KEY = 'antz-mstyle';
  var root = document.documentElement;
  function read() {
    var q = new URLSearchParams(location.search).get('ms');
    if (q === '1' || q === '2') return q;
    try { return localStorage.getItem(KEY) || '2'; } catch (e) { return '2'; }
  }
  function set(v) {
    root.setAttribute('data-mstyle', v);
    try { localStorage.setItem(KEY, v); } catch (e) {}
    document.querySelectorAll('.mstyle-switch button').forEach(function (b) {
      b.setAttribute('aria-pressed', String(b.dataset.ms === v));
    });
  }
  set(read());

  function mount() {
    var actions = document.querySelector('#modulesHead .section-head__actions');
    if (!actions || actions.querySelector('.mstyle-switch')) return !!actions;
    var sw = document.createElement('span');
    sw.className = 'mstyle-switch';
    sw.setAttribute('role', 'group');
    sw.setAttribute('aria-label', 'Modules style');
    sw.innerHTML = '<button type="button" data-ms="1">Style 1</button><button type="button" data-ms="2">Style 2</button>';
    sw.addEventListener('click', function (e) {
      var b = e.target.closest('button');
      if (b) set(b.dataset.ms);
    });
    actions.insertBefore(sw, actions.firstChild);
    set(root.getAttribute('data-mstyle'));
    return true;
  }
  // the heading is rendered by the app after load; try until it is there
  var tries = 0;
  (function wait() { if (!mount() && tries++ < 50) setTimeout(wait, 100); })();
})();
