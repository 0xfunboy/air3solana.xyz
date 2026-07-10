/* AIR3: live vault & tracking telemetry.
   Source: AIRdApp backend (public GET, CORS open).
     · AIRTrading: /api/auto-trading/read-model  (one coherent snapshot)
     · AIRTrack:   /api/reports                  (all-time totals)
   Policy: refresh on page visit with a 5-minute localStorage cache;
   on failure keep serving the last valid snapshot (never show zeros). */
(function () {
  "use strict";

  if (!document.querySelector("[data-live]")) return;

  var API = "https://airdapp.airewardrop.xyz/api";
  var KEY = "air3_live_v1";
  var TTL = 5 * 60 * 1000; // 5 minutes

  /* Equity-curve baseline from GET /api/pnl (first point, isBaseline:true).
     Historical constant: the AIRTrack record starts here. */
  var TRACK_SINCE = Date.parse("2025-12-23T01:36:47Z");

  /* ---------------- formatting ---------------- */
  function nUsd(v) {
    if (v == null || isNaN(v)) return null;
    return Number(v).toLocaleString("en-US", { minimumFractionDigits: 2, maximumFractionDigits: 2 }) + " $";
  }
  function nPct(v, signed) {
    if (v == null || isNaN(v)) return null;
    var s = Number(v).toFixed(2) + "%";
    if (signed && v > 0) s = "+" + s;
    return s;
  }
  function nInt(v) {
    if (v == null || isNaN(v)) return null;
    return Number(v).toLocaleString("en-US");
  }
  function signClass(el, v) {
    el.classList.remove("pos", "neg");
    if (v > 0) el.classList.add("pos");
    if (v < 0) el.classList.add("neg");
  }

  function put(key, text, signVal) {
    document.querySelectorAll('[data-live="' + key + '"]').forEach(function (el) {
      if (text == null) return;
      el.textContent = text;
      if (signVal !== undefined) signClass(el, signVal);
    });
  }

  /* ---------------- render ---------------- */
  var cutoffAt = null;

  function render(state) {
    var rm = state.rm, tk = state.tk;

    if (rm && rm.vaultHeadline) {
      var h = rm.vaultHeadline;
      put("vault_capital", nUsd(h.vaultCapitalUsd));
      put("active_season", nUsd(h.activeThisSeasonUsd));
      if (h.globalVaultPnlUsd != null) {
        var gp = (h.globalVaultPnlUsd > 0 ? "+" : "") + nUsd(h.globalVaultPnlUsd) + " · " + nPct(h.globalVaultPnlPct, true);
        put("global_pnl", gp, h.globalVaultPnlUsd);
      }
      if (h.currentSeasonPnlUsd != null) {
        var sp = (h.currentSeasonPnlUsd > 0 ? "+" : "") + nUsd(h.currentSeasonPnlUsd) + " · " + nPct(h.currentSeasonPnlPct, true);
        put("season_pnl", sp, h.currentSeasonPnlUsd);
      }
    }
    if (rm && rm.seasonStats) {
      var s = rm.seasonStats;
      if (s.totalSeasons != null && s.winRatePct != null) {
        put("seasons_wr", nInt(s.totalSeasons) + " · " + nPct(s.winRatePct));
      }
      if (s.profitSeasons != null && s.lossSeasons != null) {
        put("seasons_pl", nInt(s.totalSeasons) + " · " + s.profitSeasons + " profit / " + s.lossSeasons + " loss");
      }
    }
    if (rm && rm.vaultFlowHistory && rm.vaultFlowHistory.totalBuybackRoutedUsd != null) {
      put("buyback", nUsd(rm.vaultFlowHistory.totalBuybackRoutedUsd));
    }
    if (rm && rm.seasonPreview && rm.seasonPreview.currentSeason && rm.seasonPreview.currentSeason.cutoffAt) {
      cutoffAt = new Date(rm.seasonPreview.currentSeason.cutoffAt).getTime();
      tickCountdown();
    }
    if (rm && rm.meta && rm.meta.fetchedAt) {
      var d = new Date(rm.meta.fetchedAt);
      if (!isNaN(d)) {
        put("fetched_at", d.toISOString().slice(0, 16).replace("T", " ") + " UTC");
      }
    }

    if (tk && tk.totals) {
      var t = tk.totals;
      var total = (t.open || 0) + (t.pending || 0) + (t.closed || 0) + (t.discarded || 0);
      put("tk_total", nInt(total));
      put("tk_open_pending", nInt(t.open) + " · " + nInt(t.pending));
      put("tk_closed", nInt(t.closed));
      put("tk_discarded", nInt(t.discarded));
    }
    if (tk && tk.pnl_realized_pct_sum != null) {
      put("tk_pnl", nPct(tk.pnl_realized_pct_sum, true), tk.pnl_realized_pct_sum);
    }
  }

  /* time since the first tracked trade (months + days), computed client-side */
  (function () {
    var ms = Date.now() - TRACK_SINCE;
    if (ms <= 0) return;
    var days = Math.floor(ms / 86400000);
    var mo = Math.floor(days / 30.44);
    var d = Math.round(days - mo * 30.44);
    if (d >= 30) { mo += 1; d = 0; }
    put("tk_since", (mo > 0 ? mo + "mo " + d + "d" : days + "d"));
    put("tk_since_days", days + " days");
  })();

  /* live countdown to the weekly cutoff, kept alive between refreshes */
  function tickCountdown() {
    if (!cutoffAt) return;
    var ms = cutoffAt - Date.now();
    if (ms <= 0) { put("season_ends", "settling now"); return; }
    var d = Math.floor(ms / 86400000);
    var hh = Math.floor(ms / 3600000) % 24;
    var mm = Math.floor(ms / 60000) % 60;
    var ss = Math.floor(ms / 1000) % 60;
    put("season_ends", d + "d " + hh + "h " + mm + "m " + ss + "s");
  }
  setInterval(tickCountdown, 1000);

  /* ---------------- cache ---------------- */
  function load() {
    try { return JSON.parse(localStorage.getItem(KEY)) || {}; } catch (e) { return {}; }
  }
  function save(state) {
    try { localStorage.setItem(KEY, JSON.stringify(state)); } catch (e) {}
  }

  /* ---------------- fetch ---------------- */
  function get(path) {
    var ctl = ("AbortController" in window) ? new AbortController() : null;
    if (ctl) setTimeout(function () { ctl.abort(); }, 15000);
    return fetch(API + path, { signal: ctl && ctl.signal, headers: { Accept: "application/json" } })
      .then(function (r) { if (!r.ok) throw new Error("HTTP " + r.status); return r.json(); });
  }

  var state = load();
  if (state.rm || state.tk) render(state); // last valid snapshot, instantly

  var fresh = state.t && (Date.now() - state.t) < TTL;
  if (!fresh) {
    Promise.allSettled([get("/auto-trading/read-model"), get("/reports")]).then(function (res) {
      var ok = false;
      if (res[0].status === "fulfilled" && res[0].value && res[0].value.vaultHeadline) {
        state.rm = res[0].value; ok = true;
      }
      if (res[1].status === "fulfilled" && res[1].value && res[1].value.totals) {
        state.tk = res[1].value; ok = true;
      }
      if (ok) {
        state.t = Date.now();
        save(state);
        render(state);
      }
    });
  }
})();
