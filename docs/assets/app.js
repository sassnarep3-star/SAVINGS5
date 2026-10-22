/* Lightweight table sorting - no dependencies, no network calls. */
(function () {
  function cellValue(row, i) {
    var td = row.children[i];
    if (!td) return '';
    var t = td.textContent.trim();
    var m = t.replace(/[,$\u00d7+]/g, '').match(/-?\d+(\.\d+)?/);
    if (m && /[\d]/.test(t)) return parseFloat(m[0]);
    return t.toLowerCase();
  }
  document.querySelectorAll('table[data-sortable]').forEach(function (table) {
    var ths = table.querySelectorAll('thead th');
    ths.forEach(function (th, i) {
      var dir = 0;
      th.addEventListener('click', function () {
        dir = dir === 1 ? -1 : 1;
        var tb = table.tBodies[0];
        var rows = Array.prototype.slice.call(tb.rows);
        rows.sort(function (a, b) {
          var x = cellValue(a, i), y = cellValue(b, i);
          if (x === y) return 0;
          if (typeof x === 'number' && typeof y === 'number') return (x - y) * dir;
          return (String(x) < String(y) ? -1 : 1) * dir;
        });
        rows.forEach(function (r) { tb.appendChild(r); });
        ths.forEach(function (o) { o.removeAttribute('aria-sort'); });
        th.setAttribute('aria-sort', dir === 1 ? 'ascending' : 'descending');
      });
    });
  });
  var tgl = document.querySelector('.navtoggle');
  var nav = document.querySelector('.mainnav');
  if (tgl && nav) {
    tgl.addEventListener('click', function () {
      var open = nav.classList.toggle('open');
      tgl.setAttribute('aria-expanded', String(open));
    });
  }
})();
