/* Interactive progressive enhancement for SAVINGS5:
 * 1. Dark/Light theme toggle
 * 2. Live search, category filter, column sorting, and CSV download on every table
 * 3. Custom Deposit Size, Investment Lifespan (anchored to 2026-10-22), Ownership Category
 *    ($250k Single / $500k Joint / $1.25M 5-Beneficiary Trust), and Multi-Charter FDIC Allocator
 *    with clickable official primary source links on EVERY generated table row.
 */
(function () {
  "use strict";

  const savedTheme = localStorage.getItem("savings5-theme");
  if (savedTheme === "dark") {
    document.documentElement.setAttribute("data-theme", "dark");
  }

  function fmtMoney(x, cents) {
    if (x === null || x === undefined || Number.isNaN(x)) return "—";
    return "$" + Number(x).toLocaleString("en-US", {
      minimumFractionDigits: cents ? 2 : 0,
      maximumFractionDigits: cents ? 2 : 0,
    });
  }

  function fmtPct(x, dp) {
    if (x === null || x === undefined || Number.isNaN(x)) return "—";
    return Number(x).toFixed(dp === undefined ? 2 : dp) + "%";
  }

  function esc(str) {
    return String(str == null ? "" : str)
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;");
  }

  function parseCellValue(td) {
    const raw = (td.textContent || "").trim();
    if (!raw || raw === "—" || /not published|not stated/i.test(raw)) return { num: -Infinity, str: raw.toLowerCase() };
    const cleaned = raw.replace(/[$,%×bp+,]/g, "").trim();
    const m = cleaned.match(/^-?\d+(\.\d+)?/);
    if (m && (td.classList.contains("num") || /^[$+-]?\d/.test(raw))) {
      return { num: parseFloat(m[0]), str: raw.toLowerCase() };
    }
    return { num: NaN, str: raw.toLowerCase() };
  }

  function enhanceTables() {
    document.querySelectorAll(".tablewrap").forEach(function (wrap, idx) {
      const table = wrap.querySelector("table");
      if (!table || wrap.dataset.enhanced) return;
      wrap.dataset.enhanced = "1";
      const tbody = table.querySelector("tbody");
      if (!tbody) return;
      const rows = Array.from(tbody.querySelectorAll("tr"));

      if (rows.length >= 6 && !wrap.closest(".sim-panel")) {
        const bar = document.createElement("div");
        bar.className = "tbl-tools";
        bar.innerHTML =
          '<div style="display:flex;gap:8px;align-items:center;flex-wrap:wrap">' +
          '<input type="search" class="tbl-search" placeholder="Filter banks, terms, conditions..." aria-label="Filter table rows">' +
          '<span class="muted small tbl-count">' + rows.length + " rows</span>" +
          "</div>" +
          '<button type="button" class="btn-sm tbl-csv">Download CSV</button>';
        wrap.insertBefore(bar, table);

        const input = bar.querySelector(".tbl-search");
        const countEl = bar.querySelector(".tbl-count");
        input.addEventListener("input", function () {
          const q = input.value.trim().toLowerCase();
          let shown = 0;
          Array.from(tbody.querySelectorAll("tr")).forEach(function (tr) {
            const ok = !q || tr.textContent.toLowerCase().indexOf(q) !== -1;
            tr.style.display = ok ? "" : "none";
            if (ok) shown += 1;
          });
          countEl.textContent = shown + " of " + tbody.querySelectorAll("tr").length + " rows";
        });

        bar.querySelector(".tbl-csv").addEventListener("click", function () {
          const lines = [];
          table.querySelectorAll("tr").forEach(function (tr) {
            if (tr.style.display === "none") return;
            const cols = Array.from(tr.querySelectorAll("th,td")).map(function (c) {
              const link = c.querySelector("a.src");
              let txt = c.textContent.replace(/\s+/g, " ").trim();
              if (link && link.href && txt === link.textContent.trim()) {
                txt = link.href;
              }
              return '"' + txt.replace(/"/g, '""') + '"';
            });
            lines.push(cols.join(","));
          });
          const blob = new Blob([lines.join("\n")], { type: "text/csv;charset=utf-8" });
          const url = URL.createObjectURL(blob);
          const a = document.createElement("a");
          a.href = url;
          a.download = (document.title.split("·")[0].trim().toLowerCase().replace(/[^a-z0-9]+/g, "-") || "table") + "-" + (idx + 1) + ".csv";
          document.body.appendChild(a);
          a.click();
          a.remove();
          URL.revokeObjectURL(url);
        });
      }

      table.querySelectorAll("thead th").forEach(function (th, colIdx) {
        th.title = "Click to sort column";
        th.addEventListener("click", function () {
          const cur = th.getAttribute("data-sort-dir");
          const dir = cur === "desc" ? "asc" : "desc";
          table.querySelectorAll("thead th").forEach(function (h) {
            h.removeAttribute("data-sort-dir");
          });
          th.setAttribute("data-sort-dir", dir);
          const allRows = Array.from(tbody.querySelectorAll("tr"));
          allRows.sort(function (a, b) {
            const ca = a.children[colIdx];
            const cb = b.children[colIdx];
            if (!ca || !cb) return 0;
            const va = parseCellValue(ca);
            const vb = parseCellValue(cb);
            let cmp = 0;
            if (!Number.isNaN(va.num) && !Number.isNaN(vb.num)) {
              cmp = va.num - vb.num;
            } else {
              cmp = va.str.localeCompare(vb.str);
            }
            return dir === "asc" ? cmp : -cmp;
          });
          allRows.forEach(function (r) {
            tbody.appendChild(r);
          });
        });
      });
    });
  }

  function initSimulator() {
    const root = document.getElementById("savings5-simulator");
    const dataEl = document.getElementById("savings5-model-data");
    if (!root || !dataEl) return;
    let model;
    try {
      model = JSON.parse(dataEl.textContent);
    } catch (e) {
      return;
    }

    const depInput = document.getElementById("sim-deposit");
    const horizonSel = document.getElementById("sim-horizon");
    const ownerSel = document.getElementById("sim-ownership");
    const modeSel = document.getElementById("sim-mode");
    const bonusChk = document.getElementById("sim-bonus");
    const capModeChk = document.getElementById("sim-principal-buffer");
    const outStats = document.getElementById("sim-stats");
    const outLadder = document.getElementById("sim-ladder-body");
    const outSingle = document.getElementById("sim-accounts-body");
    const outNote = document.getElementById("sim-ladder-note");

    const HORIZONS = {
      "0.25": { label: "3 Months", years: 0.25, end: "2027-01-22", tsy: 4.25 },
      "0.5": { label: "6 Months", years: 0.5, end: "2027-04-22", tsy: 4.35 },
      "1": { label: "1 Year", years: 1, end: "2027-10-22", tsy: 4.52 },
      "2": { label: "2 Years", years: 2, end: "2028-10-22", tsy: 4.81 },
      "3": { label: "3 Years", years: 3, end: "2029-10-22", tsy: 4.89 },
      "5": { label: "5 Years", years: 5, end: "2031-10-22", tsy: 4.95 },
      "10": { label: "10 Years", years: 10, end: "2036-10-22", tsy: 5.13 },
    };

    function accountYield(acct, deposit, years, allowCond) {
      let ongoing = acct.std_apy;
      let condText = "";
      if (allowCond) {
        (acct.tiers || []).forEach(function (t) {
          if (t.transient) return;
          const lo = t.min_usd || 0;
          const hi = t.max_usd;
          if (deposit >= lo && (hi === null || hi === undefined || deposit <= hi)) {
            if (t.apy_pct > ongoing) {
              ongoing = t.apy_pct;
              condText = t.requires || "";
            }
          }
        });
      } else if (acct.id === "cit-platinum-savings" && deposit >= 5000) {
        ongoing = 3.75;
        condText = "Balance >= $5,000";
      } else if (acct.id === "barclays-tiered-savings" && deposit >= 250000 && deposit < 1000000) {
        ongoing = 3.65;
        condText = "Balance $250k-$999,999.99";
      }

      if (!allowCond && acct.id === "barclays-select-savings") {
        return null; // requires AARP membership
      }

      let balance;
      let effApy = ongoing;
      if (allowCond && acct.id === "cit-platinum-savings" && deposit >= 5000) {
        const boostM = Math.min(years, 0.5);
        const remY = Math.max(0, years - 0.5);
        balance = deposit * Math.pow(1.0425, boostM) * Math.pow(1 + ongoing / 100, remY);
        condText = "BOOST50 4.25% (6 mo) -> 3.75% ongoing";
      } else if (allowCond && acct.id === "sofi-savings") {
        const boostM = Math.min(years, 0.5);
        const remY = Math.max(0, years - 0.5);
        balance = deposit * Math.pow(1.044, boostM) * Math.pow(1.033, remY);
        condText = "4.40% DD boost (6 mo) -> 3.30% ongoing DD";
      } else if (allowCond && acct.id === "marcus-online-savings") {
        const capped = Math.min(deposit, 1000000);
        const excess = Math.max(0, deposit - 1000000);
        const boostY = Math.min(years, 0.25);
        const remY = Math.max(0, years - 0.25);
        balance =
          capped * Math.pow(1.045, boostY) * Math.pow(1.035, remY) +
          excess * Math.pow(1.035, years);
        condText = "+1.00% referral boost (3 mo) -> 3.50% ongoing";
      } else {
        balance = deposit * Math.pow(1 + ongoing / 100, years);
      }
      effApy = (Math.pow(balance / deposit, 1 / years) - 1) * 100;

      let bonus = 0;
      if (bonusChk && bonusChk.checked && years >= 0.25) {
        (acct.bonuses || []).forEach(function (b) {
          if (bonus === 0 && deposit >= b.min_dep && (allowCond || !b.dd_required)) {
            bonus = b.usd;
          }
        });
      }
      return {
        ongoing: ongoing,
        effApy: effApy,
        balance: balance + bonus,
        interest: balance - deposit,
        bonus: bonus,
        totalGain: balance - deposit + bonus,
        condText: condText || "No condition",
      };
    }

    function render() {
      const deposit = Math.max(100, Math.min(50000000, parseFloat(depInput.value) || 250000));
      const h = HORIZONS[horizonSel.value] || HORIZONS["1"];
      const perBankLimit = parseFloat(ownerSel.value) || 250000;
      const allowCond = modeSel.value === "max";
      const reserveInterestHeadroom = capModeChk && capModeChk.checked;

      // Build deduplicated 1-per-CERT mobile-app FDIC allocation plan
      const candidates = [];
      model.accounts.forEach(function (a) {
        if (a.mobile_app !== "yes") return;
        const probeCap = Math.min(deposit, perBankLimit);
        const y = accountYield(a, probeCap, h.years, allowCond);
        if (!y) return;
        candidates.push({ acct: a, y: y });
      });
      candidates.sort(function (a, b) {
        return b.y.totalGain - a.y.totalGain || b.y.effApy - a.y.effApy;
      });

      const seenCerts = new Set();
      const allocations = [];
      let remaining = deposit;
      candidates.forEach(function (item) {
        if (remaining <= 0.009) return;
        if (seenCerts.has(item.acct.cert)) return;
        seenCerts.add(item.acct.cert);
        const approxRate = item.y.effApy / 100;
        const safeCap = reserveInterestHeadroom
          ? Math.floor((perBankLimit / Math.pow(1 + approxRate, Math.min(1, h.years))) * 100) / 100
          : perBankLimit;
        const amt = Math.min(remaining, safeCap);
        const calc = accountYield(item.acct, amt, h.years, allowCond);
        remaining -= amt;
        allocations.push({ acct: item.acct, amt: amt, calc: calc, safeCap: safeCap });
      });

      const insuredPrincipal = allocations.reduce(function (s, x) { return s + x.amt; }, 0);
      const ladderGain = allocations.reduce(function (s, x) { return s + x.calc.totalGain; }, 0);
      const ladderInterest = allocations.reduce(function (s, x) { return s + x.calc.interest; }, 0);
      const ladderBonus = allocations.reduce(function (s, x) { return s + x.calc.bonus; }, 0);
      const blendedApy = insuredPrincipal > 0
        ? (Math.pow((insuredPrincipal + ladderInterest) / insuredPrincipal, 1 / h.years) - 1) * 100
        : 0;
      const natGain = deposit * (Math.pow(1 + model.fdic_savings_avg / 100, h.years) - 1);
      const tsyGain = deposit * (Math.pow(1 + h.tsy / 100, h.years) - 1);

      outStats.innerHTML =
        '<div class="sim-stat"><div class="k">Optimal Insured Gain (' + esc(h.label) + ')</div>' +
        '<div class="v">' + fmtMoney(ladderGain) + '</div>' +
        '<div class="s">Open 2026-10-22 &rarr; ' + esc(h.end) + (ladderBonus > 0 ? " (incl. " + fmtMoney(ladderBonus) + " bonuses)" : "") + "</div></div>" +
        '<div class="sim-stat"><div class="k">Blended APY Across ' + allocations.length + " Bank" + (allocations.length === 1 ? "" : "s") + '</div>' +
        '<div class="v">' + fmtPct(blendedApy) + '</div>' +
        '<div class="s">vs FDIC avg ' + fmtPct(model.fdic_savings_avg) + " (+" + fmtMoney(ladderGain - natGain) + " extra)</div></div>" +
        '<div class="sim-stat"><div class="k">FDIC Insured Principal</div>' +
        '<div class="v">' + fmtMoney(insuredPrincipal) + '</div>' +
        '<div class="s">' + (remaining > 1 ? '<span style="color:var(--bad);font-weight:700">' + fmtMoney(remaining) + " exceeds " + allocations.length + "-bank charter pool</span>" : "100% covered across distinct FDIC CERTs") + "</div></div>" +
        '<div class="sim-stat"><div class="k">Matched U.S. Treasury (' + fmtPct(h.tsy) + ')</div>' +
        '<div class="v">' + fmtMoney(tsyGain) + '</div>' +
        '<div class="s">' + (ladderGain >= tsyGain ? "+" + fmtMoney(ladderGain - tsyGain) + " ahead of Treasury" : fmtMoney(tsyGain - ladderGain) + " Treasury yield premium") + "</div></div>";

      outLadder.innerHTML = allocations.map(function (x, i) {
        return (
          "<tr>" +
          "<td><span class='rank'>" + (i + 1) + "</span></td>" +
          "<td><strong>" + esc(x.acct.brand) + "</strong><br><span class='muted small'>" + esc(x.acct.account_name) + " · CERT " + x.acct.cert + "</span></td>" +
          "<td class='num'>" + fmtMoney(x.amt) + "</td>" +
          "<td class='num'><strong>" + fmtPct(x.calc.effApy) + "</strong><br><span class='muted small'>ongoing " + fmtPct(x.calc.ongoing) + "</span></td>" +
          "<td class='num'>" + fmtMoney(x.calc.interest) + "</td>" +
          "<td class='num'>" + (x.calc.bonus > 0 ? fmtMoney(x.calc.bonus) : "—") + "</td>" +
          "<td class='num'><strong>" + fmtMoney(x.amt + x.calc.totalGain) + "</strong></td>" +
          "<td><span class='small'>" + esc(x.calc.condText) + "</span></td>" +
          "<td><a class='src' href='" + esc(x.acct.source) + "' target='_blank' rel='noopener'>official page</a></td>" +
          "</tr>"
        );
      }).join("");

      outNote.textContent =
        "Anchored to Account Open Date 2026-10-22 through " + h.end + " (" + h.label + "). Strictly one account per FDIC Certificate (CERT) across mobile-app-verified banks; per-bank insurance cap set to " +
        fmtMoney(perBankLimit) + (reserveInterestHeadroom ? " (Day-1 principal discounted so full Year-1 compounded interest also stays <= ceiling)." : " principal ceiling.");

      if (outSingle) {
        const singleRows = model.accounts
          .map(function (a) {
            return { acct: a, calc: accountYield(a, deposit, h.years, allowCond) };
          })
          .filter(function (x) { return x.calc !== null; })
          .sort(function (a, b) { return b.calc.totalGain - a.calc.totalGain; });

        outSingle.innerHTML = singleRows.map(function (x) {
          const uninsured = Math.max(0, deposit - perBankLimit);
          const barW = Math.min(100, Math.round((x.calc.effApy / 4.5) * 100));
          return (
            "<tr>" +
            "<td><strong>" + esc(x.acct.brand) + "</strong><br><span class='muted small'>" + esc(x.acct.account_name) + (x.acct.mobile_app !== "yes" ? " · Web-only (no mobile app)" : "") + "</span></td>" +
            "<td class='num'><div class='apy-bar-wrap'><span class='apy-bar'><i style='width:" + barW + "%'></i></span><strong>" + fmtPct(x.calc.effApy) + "</strong></div></td>" +
            "<td class='num'>" + fmtPct(x.calc.ongoing) + "</td>" +
            "<td class='num'>" + fmtMoney(x.calc.interest) + "</td>" +
            "<td class='num'>" + (x.calc.bonus > 0 ? fmtMoney(x.calc.bonus) : "—") + "</td>" +
            "<td class='num'><strong>" + fmtMoney(deposit + x.calc.totalGain) + "</strong></td>" +
            "<td class='num'>" + (uninsured > 0 ? "<span class='badge warn'>" + fmtMoney(uninsured) + " uninsured single-bank</span>" : "<span class='badge good'>100% insured</span>") + "</td>" +
            "<td><a class='src' href='" + esc(x.acct.source) + "' target='_blank' rel='noopener'>source</a></td>" +
            "</tr>"
          );
        }).join("");
      }
    }

    document.querySelectorAll("[data-dep-preset]").forEach(function (btn) {
      btn.addEventListener("click", function () {
        depInput.value = btn.getAttribute("data-dep-preset");
        document.querySelectorAll("[data-dep-preset]").forEach(function (b) { b.classList.remove("active"); });
        btn.classList.add("active");
        render();
      });
    });

    [depInput, horizonSel, ownerSel, modeSel, bonusChk, capModeChk].forEach(function (el) {
      if (el) el.addEventListener("input", render);
      if (el) el.addEventListener("change", render);
    });

    render();
  }

  document.addEventListener("DOMContentLoaded", function () {
    const btn = document.getElementById("theme-toggle");
    if (btn) {
      const syncLabel = function () {
        btn.textContent = document.documentElement.getAttribute("data-theme") === "dark" ? "Light mode" : "Dark mode";
      };
      syncLabel();
      btn.addEventListener("click", function () {
        const next = document.documentElement.getAttribute("data-theme") === "dark" ? "light" : "dark";
        if (next === "dark") {
          document.documentElement.setAttribute("data-theme", "dark");
        } else {
          document.documentElement.removeAttribute("data-theme");
        }
        localStorage.setItem("savings5-theme", next);
        syncLabel();
      });
    }
    enhanceTables();
    initSimulator();
  });
})();
