from fastapi import APIRouter
from fastapi.responses import HTMLResponse

router = APIRouter()


@router.get("/dashboard", response_class=HTMLResponse)
def dashboard():
    """Serve the single-page dashboard UI that consumes `/threads/{email}`."""
    return r"""
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Email Agent</title>
<link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700&family=IBM+Plex+Mono:wght@400;500&display=swap" rel="stylesheet">
<style>
  :root {
    --bg: #121318;
    --surface: #1b1d24;
    --surface-2: #22252e;
    --surface-3: #181a20;
    --border: #2a2d37;
    --border-light: #32363f;
    --text: #dcdfe6;
    --text-2: #9ca0ad;
    --text-3: #6b7080;
    --accent: #5b8af5;
    --accent-dim: rgba(91,138,245,0.1);
    --green: #3ecf8e;
    --green-dim: rgba(62,207,142,0.1);
    --amber: #e5a84b;
    --amber-dim: rgba(229,168,75,0.1);
    --red: #ef6461;
    --red-dim: rgba(239,100,97,0.1);
    --purple: #a78bfa;
    --purple-dim: rgba(167,139,250,0.1);
    --action-row: rgba(229,168,75,0.03);
    --radius: 10px;
    --radius-sm: 6px;
  }
  * { margin:0; padding:0; box-sizing:border-box; }
  body {
    font-family: 'Plus Jakarta Sans', sans-serif;
    background: var(--bg); color: var(--text);
    min-height: 100vh; -webkit-font-smoothing: antialiased;
  }
  .app { max-width: 1360px; margin: 0 auto; padding: 0 28px; }

  /* TOPBAR */
  .topbar {
    display: flex; align-items: center; justify-content: space-between;
    padding: 26px 0 22px;
  }
  .topbar-left { display: flex; align-items: center; gap: 12px; }
  .logo {
    width: 32px; height: 32px; background: var(--accent);
    border-radius: 8px; display: grid; place-items: center;
    font-weight: 700; font-size: 14px; color: #fff;
  }
  .topbar h1 { font-size: 17px; font-weight: 700; }
  .topbar h1 span { color: var(--text-3); font-weight: 400; }
  .btn-ref {
    background: var(--surface); color: var(--text-2);
    border: 1px solid var(--border); padding: 7px 14px;
    border-radius: var(--radius-sm); font-family: 'Plus Jakarta Sans', sans-serif;
    font-size: 12px; font-weight: 500; cursor: pointer;
    transition: all 0.15s; display: flex; align-items: center; gap: 5px;
  }
  .btn-ref:hover { border-color: var(--accent); color: var(--accent); }
  .btn-ref.loading svg { animation: spin 0.7s linear infinite; }
  @keyframes spin { to { transform: rotate(360deg); } }

  /* STATS */
  .stats { display: flex; gap: 14px; margin-bottom: 22px; }
  .stat-card {
    background: var(--surface); border: 1px solid var(--border);
    border-radius: var(--radius); padding: 16px 20px; flex: 1;
  }
  .stat-card .sv {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 26px; font-weight: 700; letter-spacing: -1px;
  }
  .stat-card .sl {
    font-size: 11px; text-transform: uppercase; letter-spacing: 0.8px;
    color: var(--text-3); font-weight: 500; margin-top: 2px;
  }
  .sv-a { color: var(--accent); }
  .sv-g { color: var(--green); }
  .sv-o { color: var(--amber); }

  /* FILTERS */
  /* TABLE */
  .table-wrap {
    background: var(--surface); border: 1px solid var(--border);
    border-radius: var(--radius); overflow: hidden; margin-bottom: 40px;
  }
  table { width: 100%; border-collapse: collapse; table-layout: fixed; }
  thead th {
    text-align: left; padding: 10px 14px;
    font-size: 10px; font-weight: 600; text-transform: uppercase;
    letter-spacing: 1.2px; color: var(--text-3);
    border-bottom: 1px solid var(--border); background: var(--surface-2);
    white-space: nowrap; overflow: hidden;
  }
  tbody tr.mr {
    border-bottom: 1px solid var(--border);
    transition: background 0.1s; cursor: pointer;
  }
  tbody tr.mr:hover { background: rgba(91,138,245,0.02); }
  tbody tr.mr.ra { background: var(--action-row); }
  tbody tr.mr.ra:hover { background: rgba(229,168,75,0.05); }
  tbody tr.mr.ex { background: rgba(91,138,245,0.04); }
  tbody td { padding: 11px 14px; font-size: 13px; vertical-align: middle; }

  .ei { width: 16px; height: 16px; color: var(--text-3); transition: transform 0.2s; }
  tr.ex .ei { transform: rotate(90deg); color: var(--accent); }

  .ce {
    display: flex; flex-direction: column; gap: 1px;
  }
  .ce-name {
    font-size: 13px; font-weight: 600; color: var(--text);
  }
  .ce-email {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 11px; color: var(--text-3); font-weight: 400;
  }

  /* TAGS */
  .tg {
    display: inline-block; padding: 2px 8px; border-radius: 4px;
    font-size: 11px; font-weight: 600; white-space: nowrap;
  }
  .tg-ob { background: var(--accent-dim); color: var(--accent); }
  .tg-ib { background: var(--purple-dim); color: var(--purple); }
  .tg-warm { background: var(--green-dim); color: var(--green); }
  .tg-cold { background: rgba(107,112,128,0.1); color: var(--text-3); }
  .tg-closed { background: var(--red-dim); color: var(--red); }
  .tg-paused { background: var(--amber-dim); color: var(--amber); }
  .tg-reroute { background: var(--purple-dim); color: var(--purple); }
  .tg-neutral { background: rgba(107,112,128,0.1); color: var(--text-3); }

  .ct { font-size: 12px; color: var(--text-2); }

  .sm { font-size: 12px; font-weight: 500; color: var(--text-2); }
  .sm.overdue { color: var(--red); font-weight: 600; }
  .sm.due { color: var(--amber); font-weight: 600; }
  .sm.nr { color: var(--green); font-weight: 600; }
  .sm.tm { color: var(--accent); }
  .sm.dn { color: var(--text-3); }

  .dc { font-family: 'IBM Plex Mono', monospace; font-size: 11px; color: var(--text-3); }

  /* FU dots */
  .fb { display: flex; align-items: center; gap: 3px; }
  .fd { width: 18px; height: 4px; border-radius: 2px; background: var(--border); }
  .fd.sent { background: var(--green); }
  .fd.due { background: var(--amber); }
  .fd.over { background: var(--red); }
  .fl { font-family: 'IBM Plex Mono', monospace; font-size: 11px; color: var(--text-3); margin-left: 6px; }

  /* ACTION BTNS */
  .bd {
    display: inline-flex; align-items: center; gap: 4px;
    padding: 5px 12px; border-radius: var(--radius-sm);
    font-size: 11px; font-weight: 600;
    background: var(--accent); border: none; color: #fff;
    font-family: 'Plus Jakarta Sans', sans-serif;
    cursor: pointer; transition: all 0.12s;
    text-decoration: none; white-space: nowrap;
  }
  .bd:hover { background: #4a7ae0; }
  .btn-view {
    display: inline-flex; align-items: center; gap: 4px;
    padding: 5px 10px; border-radius: var(--radius-sm);
    font-size: 11px; font-weight: 500;
    background: transparent; border: 1px solid var(--border);
    color: var(--text-2); font-family: 'Plus Jakarta Sans', sans-serif;
    cursor: pointer; transition: all 0.12s;
    text-decoration: none; white-space: nowrap;
  }
  .btn-view:hover { border-color: var(--accent); color: var(--accent); }
  .act-wrap { display: flex; gap: 6px; align-items: center; }
  .na { color: var(--text-3); }

  /* DETAIL ROW */
  tr.dr { display: none; }
  tr.dr.open { display: table-row; }
  tr.dr td {
    padding: 0 14px 14px 42px;
    background: var(--surface-3); border-bottom: 1px solid var(--border);
  }
  .dc-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 14px; padding-top: 10px; }
  .dc-grid.single { grid-template-columns: 1fr; }
  .db {
    background: var(--surface-2); border: 1px solid var(--border);
    border-radius: var(--radius-sm); overflow: hidden;
  }
  .dbh {
    padding: 7px 12px; font-size: 10px; font-weight: 600;
    text-transform: uppercase; letter-spacing: 1px; color: var(--text-3);
    background: rgba(255,255,255,0.02); border-bottom: 1px solid var(--border);
    display: flex; align-items: center; gap: 6px;
  }
  .dbh .dt { width: 5px; height: 5px; border-radius: 50%; }
  .dt-m { background: var(--accent); }
  .dt-d { background: var(--green); }
  .dbb {
    padding: 12px; font-size: 13px; line-height: 1.7;
    color: var(--text-2); white-space: pre-wrap; word-wrap: break-word;
    max-height: 200px; overflow-y: auto;
  }
  .dfb { border-color: rgba(62,207,142,0.2); }
  .dmr { display: flex; gap: 16px; padding-top: 10px; flex-wrap: wrap; }
  .dmi { font-size: 11px; color: var(--text-3); }
  .dmi strong { color: var(--text-2); font-weight: 600; }

  /* Timeline cards in expanded row */
  .timeline {
    display: flex; gap: 12px; padding-top: 14px; margin-bottom: 14px;
    flex-wrap: wrap;
  }
  .tl-card {
    background: var(--surface-2); border: 1px solid var(--border);
    border-radius: var(--radius-sm); padding: 12px 16px;
    min-width: 160px; flex: 1;
  }
  .tl-card .tl-label {
    font-size: 10px; text-transform: uppercase; letter-spacing: 1px;
    color: var(--text-3); font-weight: 600; margin-bottom: 4px;
    display: flex; align-items: center; gap: 6px;
  }
  .tl-card .tl-label .tl-dot {
    width: 6px; height: 6px; border-radius: 50%;
  }
  .tl-dot-blue { background: var(--accent); }
  .tl-dot-green { background: var(--green); }
  .tl-dot-amber { background: var(--amber); }
  .tl-dot-red { background: var(--red); }
  .tl-card .tl-value {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 14px; font-weight: 600; color: var(--text);
  }
  .tl-card .tl-sub {
    font-size: 11px; color: var(--text-3); margin-top: 2px;
  }
  .tl-card.tl-due {
    border-color: var(--amber);
    background: var(--amber-dim);
  }
  .tl-card.tl-overdue {
    border-color: var(--red);
    background: var(--red-dim);
  }
  .dol {
    display: inline-flex; align-items: center; gap: 4px;
    margin-top: 8px; padding: 5px 12px; border-radius: var(--radius-sm);
    font-size: 11px; font-weight: 600;
    background: var(--accent); color: #fff;
    text-decoration: none; transition: all 0.12s;
  }
  .dol:hover { background: #4a7ae0; }

  .empty { text-align: center; padding: 50px 20px; color: var(--text-3); font-size: 14px; }

  /* ANALYTICS BAR */
  .analytics-bar {
    display: flex; gap: 14px; margin-bottom: 22px; flex-wrap: wrap;
  }
  .an-card {
    background: var(--surface); border: 1px solid var(--border);
    border-radius: var(--radius); padding: 14px 18px;
    flex: 1; min-width: 120px;
  }
  .an-card .an-v {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 20px; font-weight: 700; letter-spacing: -0.5px; color: var(--text);
  }
  .an-card .an-l {
    font-size: 10px; text-transform: uppercase; letter-spacing: 0.8px;
    color: var(--text-3); font-weight: 500; margin-top: 2px;
  }
  .an-card .an-v.an-green { color: var(--green); }
  .an-card .an-v.an-amber { color: var(--amber); }

  /* ACTION ITEMS BANNER */
  .action-banner {
    background: var(--amber-dim); border: 1px solid rgba(229,168,75,0.25);
    border-radius: var(--radius-sm); padding: 10px 14px;
    margin-bottom: 12px; display: flex; align-items: center; gap: 8px;
    font-size: 12px; font-weight: 600; color: var(--amber);
  }
  .action-banner svg { flex-shrink: 0; }

  /* MEETING INTENT TAG in table row */
  .meeting-tag {
    display: inline-flex; align-items: center; gap: 3px;
    padding: 2px 7px; border-radius: 4px;
    font-size: 10px; font-weight: 600;
    background: var(--amber-dim); color: var(--amber);
    margin-left: 6px; vertical-align: middle;
  }

  /* FILTER DROPDOWN */
  .filter-bar {
    display: flex; align-items: center; justify-content: space-between;
    margin-bottom: 14px; position: relative;
  }
  .filter-bar h2 { font-size: 14px; font-weight: 600; color: var(--text); }
  .filter-bar .active-filters {
    display: flex; gap: 6px; flex-wrap: wrap; align-items: center;
    margin-left: 14px;
  }
  .active-tag {
    display: inline-flex; align-items: center; gap: 4px;
    padding: 3px 10px; border-radius: 14px;
    font-size: 11px; font-weight: 500;
    background: var(--accent-dim); color: var(--accent);
    cursor: pointer; transition: all 0.12s;
  }
  .active-tag:hover { background: rgba(91,138,245,0.2); }
  .active-tag .x { font-size: 13px; line-height: 1; opacity: 0.6; }
  .active-tag .x:hover { opacity: 1; }

  .filter-btn {
    display: flex; align-items: center; gap: 5px;
    padding: 7px 14px; border-radius: var(--radius-sm);
    font-size: 12px; font-weight: 500;
    background: var(--surface); color: var(--text-2);
    border: 1px solid var(--border);
    font-family: 'Plus Jakarta Sans', sans-serif;
    cursor: pointer; transition: all 0.12s;
    position: relative;
  }
  .filter-btn:hover { border-color: var(--accent); color: var(--accent); }
  .filter-btn.has-filters { border-color: var(--accent); color: var(--accent); }
  .filter-btn .fbadge {
    background: var(--accent); color: #fff;
    font-size: 10px; font-weight: 700; padding: 1px 6px;
    border-radius: 8px; margin-left: 2px;
  }

  .filter-panel {
    display: none; position: absolute; top: calc(100% + 6px); right: 0;
    background: var(--surface); border: 1px solid var(--border);
    border-radius: var(--radius); padding: 16px 20px;
    z-index: 50; min-width: 720px;
    box-shadow: 0 8px 30px rgba(0,0,0,0.3);
  }
  .filter-panel.open { display: block; }
  .filter-panel h3 {
    font-size: 12px; font-weight: 600; color: var(--text);
    margin-bottom: 14px;
  }
  .fp-grid {
    display: grid; grid-template-columns: 1fr 1fr 1fr 1fr 1fr;
    gap: 0;
  }
  .fp-col { }
  .fp-col-title {
    font-size: 10px; text-transform: uppercase; letter-spacing: 1px;
    color: var(--text-3); font-weight: 600;
    padding-bottom: 8px; margin-bottom: 6px;
    border-bottom: 1px solid var(--border);
  }
  .fp-item {
    display: flex; align-items: center; gap: 8px;
    padding: 5px 0; cursor: pointer; font-size: 12px;
    color: var(--text-2); transition: color 0.1s;
  }
  .fp-item:hover { color: var(--text); }
  .fp-cb {
    width: 16px; height: 16px; border-radius: 3px;
    border: 1.5px solid var(--border-light);
    background: transparent; flex-shrink: 0;
    display: grid; place-items: center;
    transition: all 0.12s;
  }
  .fp-item.checked .fp-cb {
    background: var(--accent); border-color: var(--accent);
  }
  .fp-cb-tick {
    display: none; width: 10px; height: 10px;
  }
  .fp-item.checked .fp-cb-tick { display: block; }
  .fp-actions {
    display: flex; gap: 8px; margin-top: 14px;
    padding-top: 12px; border-top: 1px solid var(--border);
  }
  .fp-actions button {
    padding: 6px 14px; border-radius: var(--radius-sm);
    font-size: 12px; font-weight: 500; cursor: pointer;
    font-family: 'Plus Jakarta Sans', sans-serif; transition: all 0.12s;
  }
  .fp-apply {
    background: var(--accent); color: #fff; border: none;
  }
  .fp-apply:hover { background: #4a7ae0; }
  .fp-clear {
    background: transparent; color: var(--text-3); border: 1px solid var(--border);
  }
  .fp-clear:hover { color: var(--text); border-color: var(--text-3); }
  .toast {
    position: fixed; bottom: 24px; right: 24px;
    background: var(--green); color: #000;
    padding: 10px 18px; border-radius: var(--radius-sm);
    font-size: 13px; font-weight: 600; z-index: 300;
    transform: translateY(60px); opacity: 0;
    transition: all 0.25s ease;
  }
  .toast.show { transform: translateY(0); opacity: 1; }
  @keyframes fu { from { opacity:0; transform:translateY(8px); } to { opacity:1; transform:translateY(0); } }
  .an { animation: fu 0.3s ease-out forwards; opacity: 0; }

  @media (max-width: 1000px) {
    .app { padding: 0 14px; }
    .dc-grid { grid-template-columns: 1fr; }
    .stats { flex-wrap: wrap; }
  }
</style>
</head>
<body>
<div class="app">
  <div class="topbar">
    <div class="topbar-left">
      <div class="logo">R</div>
      <h1>Email Agent <span>/ Pipeline</span></h1>
    </div>
    <button class="btn-ref" id="refreshBtn" onclick="refreshData()">
      <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><polyline points="23 4 23 10 17 10"/><path d="M20.49 15a9 9 0 1 1-2.12-9.36L23 10"/></svg>
      Refresh
    </button>
  </div>

  <div class="stats an" style="animation-delay:0.04s">
    <div class="stat-card"><div class="sv sv-a" id="mT">&mdash;</div><div class="sl">Total Leads</div></div>
    <div class="stat-card"><div class="sv sv-g" id="mW">&mdash;</div><div class="sl">Warm Leads</div></div>
    <div class="stat-card"><div class="sv sv-o" id="mP">&mdash;</div><div class="sl">In Pipeline</div></div>
  </div>

  <div class="analytics-bar an" style="animation-delay:0.07s" id="analyticsBar">
    <div class="an-card"><div class="an-v" id="anOutbound">&mdash;</div><div class="an-l">Outbound Sent</div></div>
    <div class="an-card"><div class="an-v an-green" id="anReplied">&mdash;</div><div class="an-l">Replied</div></div>
    <div class="an-card"><div class="an-v an-green" id="anRate">&mdash;</div><div class="an-l">Reply Rate</div></div>
    <div class="an-card"><div class="an-v an-amber" id="anAvgTime">&mdash;</div><div class="an-l">Avg Reply Time</div></div>
  </div>

  <div class="filter-bar">
    <div style="display:flex;align-items:center;">
      <h2>Threads</h2>
      <div class="active-filters" id="activeTags"></div>
    </div>
    <div style="position:relative;">
      <button class="filter-btn" id="filterBtn" onclick="toggleFilterPanel()">
        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polygon points="22 3 2 3 10 12.46 10 19 14 21 14 12.46 22 3"/></svg>
        Filters
        <span class="fbadge" id="filterBadge" style="display:none">0</span>
      </button>
      <div class="filter-panel" id="filterPanel">
        <h3>Filter Threads</h3>
        <div class="fp-grid">
          <div class="fp-col">
            <div class="fp-col-title">Type</div>
            <div class="fp-item" data-key="type" data-val="outbound" onclick="toggleCheck(this)"><div class="fp-cb"><svg class="fp-cb-tick" viewBox="0 0 24 24" fill="none" stroke="#fff" stroke-width="3"><polyline points="20 6 9 17 4 12"/></svg></div>Outbound</div>
            <div class="fp-item" data-key="type" data-val="inbound" onclick="toggleCheck(this)"><div class="fp-cb"><svg class="fp-cb-tick" viewBox="0 0 24 24" fill="none" stroke="#fff" stroke-width="3"><polyline points="20 6 9 17 4 12"/></svg></div>Inbound</div>
          </div>
          <div class="fp-col">
            <div class="fp-col-title">Lead State</div>
            <div class="fp-item" data-key="lead_state" data-val="warm" onclick="toggleCheck(this)"><div class="fp-cb"><svg class="fp-cb-tick" viewBox="0 0 24 24" fill="none" stroke="#fff" stroke-width="3"><polyline points="20 6 9 17 4 12"/></svg></div>Warm</div>
            <div class="fp-item" data-key="lead_state" data-val="cold" onclick="toggleCheck(this)"><div class="fp-cb"><svg class="fp-cb-tick" viewBox="0 0 24 24" fill="none" stroke="#fff" stroke-width="3"><polyline points="20 6 9 17 4 12"/></svg></div>Cold</div>
            <div class="fp-item" data-key="lead_state" data-val="paused" onclick="toggleCheck(this)"><div class="fp-cb"><svg class="fp-cb-tick" viewBox="0 0 24 24" fill="none" stroke="#fff" stroke-width="3"><polyline points="20 6 9 17 4 12"/></svg></div>Paused</div>
            <div class="fp-item" data-key="lead_state" data-val="reroute" onclick="toggleCheck(this)"><div class="fp-cb"><svg class="fp-cb-tick" viewBox="0 0 24 24" fill="none" stroke="#fff" stroke-width="3"><polyline points="20 6 9 17 4 12"/></svg></div>Reroute</div>
            <div class="fp-item" data-key="lead_state" data-val="closed" onclick="toggleCheck(this)"><div class="fp-cb"><svg class="fp-cb-tick" viewBox="0 0 24 24" fill="none" stroke="#fff" stroke-width="3"><polyline points="20 6 9 17 4 12"/></svg></div>Closed</div>
            <div class="fp-item" data-key="lead_state" data-val="neutral" onclick="toggleCheck(this)"><div class="fp-cb"><svg class="fp-cb-tick" viewBox="0 0 24 24" fill="none" stroke="#fff" stroke-width="3"><polyline points="20 6 9 17 4 12"/></svg></div>Neutral</div>
          </div>
          <div class="fp-col">
            <div class="fp-col-title">Reply Category</div>
            <div class="fp-item" data-key="reply_category" data-val="positive" onclick="toggleCheck(this)"><div class="fp-cb"><svg class="fp-cb-tick" viewBox="0 0 24 24" fill="none" stroke="#fff" stroke-width="3"><polyline points="20 6 9 17 4 12"/></svg></div>Positive</div>
            <div class="fp-item" data-key="reply_category" data-val="requesting_more_info" onclick="toggleCheck(this)"><div class="fp-cb"><svg class="fp-cb-tick" viewBox="0 0 24 24" fill="none" stroke="#fff" stroke-width="3"><polyline points="20 6 9 17 4 12"/></svg></div>Requested Info</div>
            <div class="fp-item" data-key="reply_category" data-val="negative" onclick="toggleCheck(this)"><div class="fp-cb"><svg class="fp-cb-tick" viewBox="0 0 24 24" fill="none" stroke="#fff" stroke-width="3"><polyline points="20 6 9 17 4 12"/></svg></div>Negative</div>
            <div class="fp-item" data-key="reply_category" data-val="out_of_office" onclick="toggleCheck(this)"><div class="fp-cb"><svg class="fp-cb-tick" viewBox="0 0 24 24" fill="none" stroke="#fff" stroke-width="3"><polyline points="20 6 9 17 4 12"/></svg></div>Out of Office</div>
            <div class="fp-item" data-key="reply_category" data-val="wrong_person" onclick="toggleCheck(this)"><div class="fp-cb"><svg class="fp-cb-tick" viewBox="0 0 24 24" fill="none" stroke="#fff" stroke-width="3"><polyline points="20 6 9 17 4 12"/></svg></div>Wrong Person</div>
            <div class="fp-item" data-key="reply_category" data-val="unsubscribe" onclick="toggleCheck(this)"><div class="fp-cb"><svg class="fp-cb-tick" viewBox="0 0 24 24" fill="none" stroke="#fff" stroke-width="3"><polyline points="20 6 9 17 4 12"/></svg></div>Unsubscribe</div>
            <div class="fp-item" data-key="reply_category" data-val="Waiting for reply" onclick="toggleCheck(this)"><div class="fp-cb"><svg class="fp-cb-tick" viewBox="0 0 24 24" fill="none" stroke="#fff" stroke-width="3"><polyline points="20 6 9 17 4 12"/></svg></div>Waiting for Reply</div>
          </div>
          <div class="fp-col">
            <div class="fp-col-title">Status</div>
            <div class="fp-item" data-key="reply_detected" data-val="true" onclick="toggleCheck(this)"><div class="fp-cb"><svg class="fp-cb-tick" viewBox="0 0 24 24" fill="none" stroke="#fff" stroke-width="3"><polyline points="20 6 9 17 4 12"/></svg></div>Has Reply</div>
            <div class="fp-item" data-key="reply_detected" data-val="false" onclick="toggleCheck(this)"><div class="fp-cb"><svg class="fp-cb-tick" viewBox="0 0 24 24" fill="none" stroke="#fff" stroke-width="3"><polyline points="20 6 9 17 4 12"/></svg></div>No Reply</div>
            <div class="fp-item" data-key="followup_due" data-val="true" onclick="toggleCheck(this)"><div class="fp-cb"><svg class="fp-cb-tick" viewBox="0 0 24 24" fill="none" stroke="#fff" stroke-width="3"><polyline points="20 6 9 17 4 12"/></svg></div>Follow-Up Due</div>
            <div class="fp-item" data-key="meeting_intent" data-val="true" onclick="toggleCheck(this)"><div class="fp-cb"><svg class="fp-cb-tick" viewBox="0 0 24 24" fill="none" stroke="#fff" stroke-width="3"><polyline points="20 6 9 17 4 12"/></svg></div>Meeting Intent</div>
            <div class="fp-item" data-key="has_draft" data-val="true" onclick="toggleCheck(this)"><div class="fp-cb"><svg class="fp-cb-tick" viewBox="0 0 24 24" fill="none" stroke="#fff" stroke-width="3"><polyline points="20 6 9 17 4 12"/></svg></div>Has Draft</div>
          </div>
          <div class="fp-col">
            <div class="fp-col-title">Exclude</div>
            <div class="fp-item" data-key="exclude_unsubscribe" data-val="true" onclick="toggleCheck(this)"><div class="fp-cb"><svg class="fp-cb-tick" viewBox="0 0 24 24" fill="none" stroke="#fff" stroke-width="3"><polyline points="20 6 9 17 4 12"/></svg></div>Hide Unsubscribes</div>
            <div class="fp-item" data-key="exclude_irrelevant" data-val="true" onclick="toggleCheck(this)"><div class="fp-cb"><svg class="fp-cb-tick" viewBox="0 0 24 24" fill="none" stroke="#fff" stroke-width="3"><polyline points="20 6 9 17 4 12"/></svg></div>Hide Non-Leads</div>
          </div>
        </div>
        <div class="fp-actions">
          <button class="fp-apply" onclick="applyFilters()">Apply Filters</button>
          <button class="fp-clear" onclick="clearFilters()">Clear All</button>
        </div>
      </div>
    </div>
  </div>

  <div class="table-wrap an" style="animation-delay:0.1s">
    <table>
      <thead><tr>
        <th style="width:28px"></th>
        <th style="width:19%">Contact</th>
        <th style="width:8%">Type</th>
        <th style="width:7%">Lead</th>
        <th style="width:10%">Reply</th>
        <th style="width:20%">Status</th>
        <th style="width:9%">Follow-Ups</th>
        <th style="width:8%">Sent</th>
        <th style="width:14%">Action</th>
      </tr></thead>
      <tbody id="tB"><tr><td colspan="9"><div class="empty">Loading...</div></td></tr></tbody>
    </table>
  </div>
</div>
<div class="toast" id="toast"></div>

<script>
var D=[],EX={},AN={};
var ACTIVE_EMAIL=null;
var EMAIL_STORAGE_KEY="email_agent_mailbox";
var LAST_AUTO_REFRESH_AT=0;
var AUTO_REFRESH_COOLDOWN_MS=6000;

// Active filters: { "lead_state": ["warm","cold"], "reply_category": ["positive"], ... }
var FILTERS = {};

function fC(c){var m={positive:"Positive",negative:"Negative",requesting_more_info:"Requested Info",out_of_office:"Out of Office",wrong_person:"Wrong Person",unsubscribe:"Unsubscribe",neutral:"Neutral","Waiting for reply":"Waiting"};return m[c]||c||"\u2014"}
function lC(s){var m={warm:"tg-warm",cold:"tg-cold",neutral:"tg-neutral",closed:"tg-closed",paused:"tg-paused",reroute:"tg-reroute"};return m[s]||"tg-neutral"}
function lL(s){var m={cold:"Cold",warm:"Warm",closed:"Closed",paused:"Paused",reroute:"Reroute",neutral:"Neutral"};return m[s]||"\u2014"}
function sC(t){var m=(t.status_message||"").toLowerCase();if(m.indexOf("overdue")!==-1)return"overdue";if(m.indexOf("needs reply")!==-1||(t.action_required&&t.reply_detected))return"nr";if(m.indexOf("tomorrow")!==-1)return"tm";if(m.indexOf("ready to send")!==-1||t.followup_due)return"due";if(m.indexOf("all follow-ups")!==-1)return"dn";return""}

// Filter panel functions
function toggleFilterPanel(){
  document.getElementById("filterPanel").classList.toggle("open");
}
function toggleCheck(el){
  el.classList.toggle("checked");
}

function applyFilters(){
  FILTERS = {};
  var items = document.querySelectorAll(".fp-item.checked");
  for(var i=0;i<items.length;i++){
    var key=items[i].getAttribute("data-key");
    var val=items[i].getAttribute("data-val");
    if(!FILTERS[key])FILTERS[key]=[];
    FILTERS[key].push(val);
  }
  document.getElementById("filterPanel").classList.remove("open");
  updateFilterUI();
  render();
}

function clearFilters(){
  FILTERS = {};
  var items = document.querySelectorAll(".fp-item.checked");
  for(var i=0;i<items.length;i++) items[i].classList.remove("checked");
  document.getElementById("filterPanel").classList.remove("open");
  updateFilterUI();
  render();
}

function removeFilter(key,val){
  if(FILTERS[key]){
    FILTERS[key]=FILTERS[key].filter(function(v){return v!==val});
    if(FILTERS[key].length===0) delete FILTERS[key];
  }
  // Uncheck the matching checkbox
  var items=document.querySelectorAll('.fp-item[data-key="'+key+'"][data-val="'+val+'"]');
  for(var i=0;i<items.length;i++) items[i].classList.remove("checked");
  updateFilterUI();
  render();
}

function updateFilterUI(){
  var count=0;
  var keys=Object.keys(FILTERS);
  for(var i=0;i<keys.length;i++) count+=FILTERS[keys[i]].length;

  var badge=document.getElementById("filterBadge");
  var btn=document.getElementById("filterBtn");
  if(count>0){
    badge.textContent=count;badge.style.display="inline";
    btn.classList.add("has-filters");
  } else {
    badge.style.display="none";
    btn.classList.remove("has-filters");
  }

  // Render active filter tags
  var tagHtml="";
  var labelMap={
    type:{outbound:"Outbound",inbound:"Inbound"},
    lead_state:{warm:"Warm",cold:"Cold",paused:"Paused",reroute:"Reroute",closed:"Closed",neutral:"Neutral"},
    reply_category:{positive:"Positive",requesting_more_info:"Requested Info",negative:"Negative",out_of_office:"OOO",wrong_person:"Wrong Person",unsubscribe:"Unsubscribe","Waiting for reply":"Waiting"},
    reply_detected:{"true":"Has Reply","false":"No Reply"},
    followup_due:{"true":"Follow-Up Due"},
    meeting_intent:{"true":"Meeting Intent"},
    has_draft:{"true":"Has Draft"},
    exclude_unsubscribe:{"true":"Hide Unsubscribes"},
    exclude_irrelevant:{"true":"Hide Non-Leads"}
  };
  for(var i=0;i<keys.length;i++){
    var k=keys[i];
    for(var j=0;j<FILTERS[k].length;j++){
      var v=FILTERS[k][j];
      var label=(labelMap[k]&&labelMap[k][v])||v;
      tagHtml+='<span class="active-tag" onclick="removeFilter(\''+k+'\',\''+v+'\')">'+label+' <span class="x">\u00d7</span></span>';
    }
  }
  document.getElementById("activeTags").innerHTML=tagHtml;
}

// Check if a thread passes all active filters (AND between groups, OR within group)
function passFilter(t){
  var keys=Object.keys(FILTERS);
  if(keys.length===0) return true;
  for(var i=0;i<keys.length;i++){
    var key=keys[i];
    var vals=FILTERS[key];
    var match=false;

    // Exclusion filters work in reverse — if checked, hide matching threads
    if(key==="exclude_unsubscribe"){
      if(vals.indexOf("true")!==-1 && t.reply_category==="unsubscribe") return false;
      continue;
    }
    if(key==="exclude_irrelevant"){
      if(vals.indexOf("true")!==-1 && t.lead_relevant===false) return false;
      continue;
    }

    for(var j=0;j<vals.length;j++){
      var val=vals[j];
      if(key==="has_draft"){
        if(val==="true"&&!!t.draft_link) match=true;
      } else if(key==="reply_detected"||key==="followup_due"||key==="meeting_intent"){
        var boolVal=(val==="true");
        if(t[key]===boolVal) match=true;
      } else {
        if(String(t[key])===val) match=true;
      }
    }
    if(!match) return false;
  }
  return true;
}

// Close panel on outside click
document.addEventListener("click",function(e){
  var panel=document.getElementById("filterPanel");
  var btn=document.getElementById("filterBtn");
  if(panel.classList.contains("open")&&!panel.contains(e.target)&&!btn.contains(e.target)){
    panel.classList.remove("open");
  }
});

// Extract display name from email like "sarah.chen@company.com" -> "Sarah Chen"
function getName(email){
  if(!email)return"Unknown";
  // If it has "Name <email>" format
  var angle=email.match(/^(.+?)\s*<[^>]+>$/);
  if(angle)return angle[1].replace(/"/g,"").trim();
  // Plain email: derive from local part
  var at=email.indexOf("@");
  if(at===-1)return email;
  var local=email.substring(0,at);
  return local.replace(/[._-]/g," ").replace(/\b\w/g,function(c){return c.toUpperCase()});
}

// Format a Date object to "Mar 4, 2026"
function fmtDate(d){
  var months=["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"];
  return months[d.getMonth()]+" "+d.getDate()+", "+d.getFullYear();
}

// Compute a date from days_ago and return formatted string
function dateFromDaysAgo(daysAgo){
  if(daysAgo===null||daysAgo===undefined)return null;
  var d=new Date();
  d.setDate(d.getDate()-daysAgo);
  return fmtDate(d);
}

function cP(r){if(!r)return"\u2014";var c=r.replace(/\r\n/g," ").replace(/\n/g," ").trim();c=c.replace(/From:.*?(Subject:|$)/i,"").trim();c=c.replace(/Subject:.*$/i,"").trim();c=c.replace(/On .+ wrote:.*$/i,"").trim();if(c.length>65)c=c.substring(0,62)+"...";return c||"\u2014"}
function cB(r){if(!r)return"No content.";var c=r.replace(/\r\n/g,"\n").trim();c=c.replace(/^From:.*$/gm,"").replace(/^Subject:.*$/gm,"").trim();return c||"No content."}
function esc(s){if(!s)return"";var d=document.createElement("div");d.appendChild(document.createTextNode(s));return d.innerHTML}
function toast(m){var e=document.getElementById("toast");e.textContent=m;e.classList.add("show");setTimeout(function(){e.classList.remove("show")},2200)}
function tog(id){if(EX[id])delete EX[id];else EX[id]=true;render()}
function buildThreadUrl(threadId){
  var authUser=ACTIVE_EMAIL?encodeURIComponent(ACTIVE_EMAIL):"0";
  return "https://mail.google.com/mail/u/?authuser="+authUser+"#inbox/"+threadId;
}
function resolveActiveEmail(){
  var urlEmail=new URLSearchParams(window.location.search).get("email");
  if(urlEmail){
    ACTIVE_EMAIL=urlEmail;
    localStorage.setItem(EMAIL_STORAGE_KEY,urlEmail);
    return Promise.resolve(urlEmail);
  }

  var storedEmail=localStorage.getItem(EMAIL_STORAGE_KEY);
  if(storedEmail){
    ACTIVE_EMAIL=storedEmail;
    return Promise.resolve(storedEmail);
  }

  return fetch("/threads/default-email")
    .then(function(r){if(!r.ok)throw new Error(r.status);return r.json()})
    .then(function(data){
      if(data&&data.email){
        ACTIVE_EMAIL=data.email;
        localStorage.setItem(EMAIL_STORAGE_KEY,data.email);
        return data.email;
      }
      return null;
    })
    .catch(function(){return null;});
}
function silentRefresh(force){
  var now=Date.now();
  if(!force&&now-LAST_AUTO_REFRESH_AT<AUTO_REFRESH_COOLDOWN_MS)return Promise.resolve();
  LAST_AUTO_REFRESH_AT=now;
  return load().catch(function(){});
}
function openDraft(e){
  e.stopPropagation();
  // Gmail draft removal can take a moment after send; check twice.
  setTimeout(function(){silentRefresh(true)},2500);
  setTimeout(function(){silentRefresh(true)},6000);
}

function dots(t){
  var s=t.followups_sent||0,st=t.followup_stage||0,du=t.followup_due,m=(t.status_message||"").toLowerCase();
  var h='<div class="fb">';
  for(var i=1;i<=3;i++){var c="fd";if(i<=s)c+=" sent";else if(i===st&&du)c+=(m.indexOf("overdue")!==-1)?" over":" due";h+='<div class="'+c+'"></div>'}
  h+='<span class="fl">'+s+'/3</span></div>';return h;
}

function render(){
  // Analytics bar
  if(AN.total_outbound!=null){
    document.getElementById("anOutbound").textContent=AN.total_outbound;
    document.getElementById("anReplied").textContent=AN.total_replied;
    document.getElementById("anRate").textContent=AN.reply_rate_pct+"%";
    document.getElementById("anAvgTime").textContent=AN.avg_reply_time_days!=null?AN.avg_reply_time_days+"d":"\u2014";
  }

  var aF=D.filter(function(t){return t.lead_relevant!==false});
  var wF=D.filter(function(t){return t.lead_state==="warm"});
  var pL=D.filter(function(t){return t.type==="outbound"&&!t.reply_detected&&t.lead_state!=="closed"});

  document.getElementById("mT").textContent=aF.length;
  document.getElementById("mW").textContent=wF.length;
  document.getElementById("mP").textContent=pL.length;

  var fl=D.filter(passFilter);
  var tb=document.getElementById("tB");
  if(!fl.length){tb.innerHTML='<tr><td colspan="9"><div class="empty">No threads here.</div></td></tr>';return}

  var h="";
  for(var i=0;i<fl.length;i++){
    var t=fl[i],em=t.contact_email||"\u2014",ob=t.contact_type==="outbound";
    var sm=t.status_message||"\u2014",sc=sC(t);
    var rc=(t.action_required||t.followup_due)?"ra":"",ex=!!EX[t.thread_id],ec=ex?"ex":"";
    var sd=t.last_email_date||"\u2014",sn=t.followups_sent||0;

    // Build Gmail thread URL using the active mailbox.
    var threadUrl=buildThreadUrl(t.thread_id);

    var ac='<div class="act-wrap">';
    if(t.draft_link){
      ac+='<a href="'+t.draft_link+'" target="_blank" class="bd" onclick="openDraft(event);">'+
        '<svg width="11" height="11" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><path d="M22 2L11 13"/><path d="M22 2L15 22L11 13L2 9L22 2Z"/></svg>'+
        ' Draft</a>';
    }
    ac+='<a href="'+threadUrl+'" target="_blank" class="btn-view" onclick="event.stopPropagation();">'+
      '<svg width="11" height="11" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6"/><polyline points="15 3 21 3 21 9"/><line x1="10" y1="14" x2="21" y2="3"/></svg>'+
      ' View</a>';
    ac+='</div>';

    h+='<tr class="mr '+rc+' '+ec+'" onclick="tog(\''+t.thread_id+'\')">';
    h+='<td><svg class="ei" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><polyline points="9 18 15 12 9 6"/></svg></td>';
    h+='<td><div class="ce"><span class="ce-name">'+esc(getName(em))+'</span><span class="ce-email">'+esc(em)+'</span></div></td>';
    h+='<td><span class="tg '+(ob?'tg-ob':'tg-ib')+'">'+(ob?'Outbound':'Inbound')+'</span></td>';
    h+='<td><span class="tg '+lC(t.lead_state)+'">'+lL(t.lead_state)+'</span></td>';
    h+='<td><span class="ct">'+fC(t.reply_category)+'</span>';
    if(t.meeting_intent){h+='<span class="meeting-tag">Meeting</span>'}
    h+='</td>';
    h+='<td><span class="sm '+sc+'">'+esc(sm)+'</span></td>';
    h+='<td>'+dots(t)+'</td>';
    h+='<td><span class="dc">'+sd+'</span></td>';
    h+='<td>'+ac+'</td>';
    h+='</tr>';

    // detail
    var dO=ex?"open":"";
    h+='<tr class="dr '+dO+'"><td colspan="9">';

    // ── TIMELINE CARDS (prominent date display) ──
    h+='<div class="timeline">';

    // Card 1: First email sent
    var firstDate="\u2014",firstSub="";
    if(t.days_since_first_email!=null){
      firstDate=dateFromDaysAgo(t.days_since_first_email);
      firstSub=t.days_since_first_email===0?"Today":t.days_since_first_email+"d ago";
    }
    h+='<div class="tl-card"><div class="tl-label"><span class="tl-dot tl-dot-blue"></span>First Email Sent</div>';
    h+='<div class="tl-value">'+firstDate+'</div>';
    if(firstSub)h+='<div class="tl-sub">'+firstSub+'</div>';
    h+='</div>';

    // Card 2: Last email sent — same date format as first
    var lastDateStr="\u2014",lastSub="";
    if(t.days_since_last_email!=null){
      lastDateStr=dateFromDaysAgo(t.days_since_last_email);
      lastSub=t.days_since_last_email===0?"Today":t.days_since_last_email+"d ago";
      if(sn>0)lastSub="Follow-up "+sn+" \u2022 "+lastSub;
      else lastSub="Original email \u2022 "+lastSub;
    }
    h+='<div class="tl-card"><div class="tl-label"><span class="tl-dot tl-dot-green"></span>Last Email Sent</div>';
    h+='<div class="tl-value">'+lastDateStr+'</div>';
    if(lastSub)h+='<div class="tl-sub">'+lastSub+'</div>';
    h+='</div>';

    // Card 3: Next follow-up due date
    if(ob&&!t.reply_detected&&sn<3){
      var nextNum=sn+1;
      var nextDue="\u2014",nextSub="",cardClass="tl-card";
      var thresholds=[3,7,14];
      if(t.days_since_first_email!=null&&nextNum<=3){
        var targetDay=thresholds[nextNum-1];
        var daysLeft=targetDay-t.days_since_first_email;
        var dd=new Date();dd.setDate(dd.getDate()+daysLeft);
        nextDue=fmtDate(dd);
        if(daysLeft<0){nextSub="Overdue by "+Math.abs(daysLeft)+"d";cardClass="tl-card tl-overdue"}
        else if(daysLeft===0){nextSub="Due today";cardClass="tl-card tl-due"}
        else if(daysLeft===1){nextSub="Due tomorrow";cardClass="tl-card tl-due"}
        else{nextSub="In "+daysLeft+" days"}
      }
      h+='<div class="'+cardClass+'"><div class="tl-label"><span class="tl-dot tl-dot-amber"></span>Follow-Up '+nextNum+' Due</div>';
      h+='<div class="tl-value">'+nextDue+'</div>';
      if(nextSub)h+='<div class="tl-sub">'+nextSub+'</div>';
      h+='</div>';
    } else if(ob&&!t.reply_detected&&sn>=3){
      h+='<div class="tl-card"><div class="tl-label"><span class="tl-dot tl-dot-green"></span>Sequence Complete</div>';
      h+='<div class="tl-value">All 3 sent</div>';
      h+='<div class="tl-sub">Waiting for reply</div></div>';
    }

    // Card 4: Reply status
    h+='<div class="tl-card"><div class="tl-label"><span class="tl-dot '+(t.reply_detected?'tl-dot-green':'tl-dot-red')+'"></span>Reply</div>';
    h+='<div class="tl-value">'+(t.reply_detected?'<span style="color:var(--green)">Received</span>':'<span style="color:var(--text-3)">None yet</span>')+'</div>';
    if(t.reply_detected&&t.reply_category)h+='<div class="tl-sub">'+fC(t.reply_category)+'</div>';
    h+='</div>';

    h+='</div>';

    // ── Action items (meeting intent, etc) ──
    if(t.action_items&&t.action_items.length>0){
      for(var ai=0;ai<t.action_items.length;ai++){
        h+='<div class="action-banner">';
        h+='<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/></svg>';
        h+=esc(t.action_items[ai]);
        h+='</div>';
      }
    }

    // ── Additional meta (small, below timeline) ──
    h+='<div class="dmr">';
    h+='<div class="dmi"><strong>Thread:</strong> '+t.thread_id+'</div>';
    h+='<div class="dmi"><strong>Direction:</strong> '+(ob?"We reached out":"They contacted us")+'</div>';
    h+='<div class="dmi"><strong>Follow-ups sent:</strong> '+sn+' of 3</div>';
    h+='<div class="dmi"><a href="'+threadUrl+'" target="_blank" style="color:var(--accent);text-decoration:none;font-weight:600;">Open in Gmail \u2197</a></div>';
    h+='</div>';

    var hM=t.last_message_preview&&t.last_message_preview.trim().length>0;
    var hD=t.draft_followup&&t.draft_followup.trim().length>0;
    if(hM||hD){
      var gc=(hM&&hD)?"":" single";
      h+='<div class="dc-grid'+gc+'">';
      if(hM){
        // Clear sender attribution
        var msgSender,msgColor,msgIcon;
        if(t.reply_detected){
          msgSender=getName(em)+" replied";
          msgColor="var(--green)";
          msgIcon='<svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="'+msgColor+'" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><polyline points="9 10 4 15 9 20"/><path d="M20 4v7a4 4 0 0 1-4 4H4"/></svg>';
        } else {
          msgSender="You sent";
          msgColor="var(--accent)";
          msgIcon='<svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="'+msgColor+'" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><line x1="22" y1="2" x2="11" y2="13"/><polygon points="22 2 15 22 11 13 2 9 22 2"/></svg>';
        }
        h+='<div class="db"><div class="dbh">'+msgIcon+' <span style="color:'+msgColor+'">'+msgSender+'</span></div>';
        h+='<div class="dbb">'+esc(cB(t.last_message_preview))+'</div></div>';
      }
      if(hD){
        h+='<div class="db dfb"><div class="dbh"><svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="var(--green)" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><path d="M12 20h9"/><path d="M16.5 3.5a2.121 2.121 0 0 1 3 3L7 19l-4 1 1-4L16.5 3.5z"/></svg> <span style="color:var(--green)">AI-Drafted Reply</span></div>';
        h+='<div class="dbb">'+esc(t.draft_followup)+'</div>';
        if(t.draft_link){h+='<div style="padding:0 12px 10px;"><a href="'+t.draft_link+'" target="_blank" class="dol">Open in Gmail</a></div>'}
        h+='</div>';
      }
      h+='</div>';
    }
    h+='</td></tr>';
  }
  tb.innerHTML=h;
}

function load(){
  return resolveActiveEmail()
    .then(function(email){
      if(!email)throw new Error("No authenticated mailbox found.");
      return fetch("/threads/"+encodeURIComponent(email));
    })
    .then(function(r){if(!r.ok)throw new Error(r.status);return r.json()})
    .then(function(data){
      // Support both old format (array) and new format ({threads, analytics})
      if(Array.isArray(data)){
        D=data;AN={};
      } else {
        D=data.threads||[];
        AN=data.analytics||{};
      }
      render();
    })
    .catch(function(e){
      console.warn("Demo mode.",e);
      if(String(e.message||"").indexOf("No authenticated mailbox found")!==-1){
        toast("No mailbox found. Run /login first.");
      }
      var dd=demoData();
      D=dd.threads;AN=dd.analytics;
      render();
    });
}
function refreshData(){
  var b=document.getElementById("refreshBtn");b.classList.add("loading");
  load().then(function(){b.classList.remove("loading");toast("Refreshed.")});
}
window.addEventListener("focus",function(){silentRefresh(false)});
document.addEventListener("visibilitychange",function(){
  if(document.visibilityState==="visible")silentRefresh(false);
});

function demoData(){return{
  threads:[
    {thread_id:"t1",contact_email:"sarah@creatornexus.io",contact_type:"outbound",type:"outbound",lead_relevant:true,reply_detected:true,action_required:true,lead_state:"warm",reply_category:"requesting_more_info",days_since_first_email:4,days_since_last_email:1,followup_stage:1,followups_sent:1,followup_due:false,draft_followup:"Thanks for your interest! Here are the campaign details.\n\nCould we schedule a call this week?",last_message_preview:"Yes, I would be interested. Can you send more details?",status_message:"",draft_link:"https://mail.google.com/mail/#inbox/t1",last_email_date:"2026-03-06",subject:"Partnership Opportunity",meeting_intent:false,action_items:[]},
    {thread_id:"t2",contact_email:"brand@startup.io",contact_type:"outbound",type:"outbound",lead_relevant:true,reply_detected:false,action_required:false,lead_state:"cold",reply_category:"Waiting for reply",days_since_first_email:3,days_since_last_email:3,followup_stage:1,followups_sent:0,followup_due:true,draft_followup:"Hi,\n\nJust following up on my previous message. Would love to connect.\n\nBest regards",last_message_preview:"Would you be open to a quick demo next week?",status_message:"Follow-up 1 ready to send.",draft_link:"https://mail.google.com/mail/#inbox/t2",last_email_date:"2026-03-04",subject:"Quick Demo?",meeting_intent:false,action_items:[]},
    {thread_id:"t3",contact_email:"partner@agency.com",contact_type:"outbound",type:"outbound",lead_relevant:true,reply_detected:false,action_required:false,lead_state:"cold",reply_category:"Waiting for reply",days_since_first_email:10,days_since_last_email:4,followup_stage:1,followups_sent:1,followup_due:false,draft_followup:null,last_message_preview:"Following up on my earlier message about brand integration.",status_message:"Waiting for reply. Follow-up 2 in 4 days.",draft_link:null,last_email_date:"2026-03-03",subject:"Brand Integration",meeting_intent:false,action_items:[]},
    {thread_id:"t4",contact_email:"creator@influencer.co",contact_type:"outbound",type:"outbound",lead_relevant:true,reply_detected:false,action_required:false,lead_state:"cold",reply_category:"Waiting for reply",days_since_first_email:2,days_since_last_email:2,followup_stage:0,followups_sent:0,followup_due:false,draft_followup:"Hi,\n\nJust wanted to follow up on my previous email.\n\nWould love to chat!",last_message_preview:"We love your content and would like to collaborate.",status_message:"Follow-up 1 due tomorrow. Draft ready.",draft_link:"https://mail.google.com/mail/#inbox/t4",last_email_date:"2026-03-05",subject:"Collaboration",meeting_intent:false,action_items:[]},
    {thread_id:"t5",contact_email:"james@talentforge.co",contact_type:"outbound",type:"outbound",lead_relevant:true,reply_detected:true,action_required:false,lead_state:"paused",reply_category:"out_of_office",days_since_first_email:5,days_since_last_email:3,followup_stage:0,followups_sent:0,followup_due:false,draft_followup:null,last_message_preview:"I am currently out of the office until March 15th.",status_message:"",draft_link:null,last_email_date:"2026-03-04",subject:"Creator Tools",meeting_intent:false,action_items:[]},
    {thread_id:"t6",contact_email:"david@pixelcollective.co",contact_type:"outbound",type:"outbound",lead_relevant:true,reply_detected:true,action_required:true,lead_state:"warm",reply_category:"positive",days_since_first_email:3,days_since_last_email:0,followup_stage:0,followups_sent:0,followup_due:false,draft_followup:null,last_message_preview:"Yes! Can we do next Tuesday at 2pm EST? I would love to see a demo.",status_message:"",draft_link:null,last_email_date:"2026-03-07",subject:"Creator CRM Demo",meeting_intent:true,action_items:["Schedule meeting \u2014 reply contains scheduling intent"]},
    {thread_id:"t7",contact_email:"aisha@growthlabs.io",contact_type:"outbound",type:"outbound",lead_relevant:true,reply_detected:true,action_required:false,lead_state:"closed",reply_category:"negative",days_since_first_email:8,days_since_last_email:6,followup_stage:1,followups_sent:1,followup_due:false,draft_followup:null,last_message_preview:"Signed with a different vendor. Best of luck!",status_message:"",draft_link:null,last_email_date:"2026-03-01",subject:"Outreach Tools",meeting_intent:false,action_items:[]},
    {thread_id:"t8",contact_email:"tom@viralventures.net",contact_type:"outbound",type:"outbound",lead_relevant:true,reply_detected:true,action_required:true,lead_state:"reroute",reply_category:"wrong_person",days_since_first_email:3,days_since_last_email:2,followup_stage:0,followups_sent:0,followup_due:false,draft_followup:"Hi Kelly,\n\nTom pointed me your way. We build outreach tools for creator agencies.\n\nFree for a quick chat?",last_message_preview:"Not the right person. Reach out to Kelly at kelly@viralventures.net.",status_message:"",draft_link:"https://mail.google.com/mail/#inbox/t8",last_email_date:"2026-03-05",subject:"Partnership",meeting_intent:false,action_items:[]},
    {thread_id:"t9",contact_email:"nina@creatoreconomy.co",contact_type:"outbound",type:"outbound",lead_relevant:true,reply_detected:false,action_required:false,lead_state:"cold",reply_category:"Waiting for reply",days_since_first_email:16,days_since_last_email:2,followup_stage:3,followups_sent:3,followup_due:false,draft_followup:null,last_message_preview:"Final follow-up on the creator analytics platform.",status_message:"All follow-ups sent. Waiting for reply.",draft_link:null,last_email_date:"2026-03-05",subject:"Analytics Platform",meeting_intent:false,action_items:[]},
    {thread_id:"t10",contact_email:"newsletter@google.com",contact_type:"inbound",type:"inbound",lead_relevant:false,reply_detected:false,action_required:false,lead_state:"cold",reply_category:"unsubscribe",days_since_first_email:null,days_since_last_email:null,followup_stage:0,followups_sent:0,followup_due:false,draft_followup:null,last_message_preview:"Weekly business tips from Google.",status_message:"",draft_link:null,last_email_date:null,subject:"Business Tips",meeting_intent:false,action_items:[]}
  ],
  analytics:{
    total_outbound:9,
    total_replied:5,
    reply_rate_pct:55.6,
    avg_reply_time_days:3.8,
    category_breakdown:{positive:1,requesting_more_info:1,negative:1,out_of_office:1,wrong_person:1,"Waiting for reply":4,unsubscribe:1}
  }
}}

load();
</script>
</body>
</html>
"""
