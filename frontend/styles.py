"""Centralised, browser-theme-safe design system for the Streamlit interface."""

MAIN_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=JetBrains+Mono:wght@500;600&display=swap');

:root {
  color-scheme: dark;
  --bg-app: #0a1020;
  --bg-surface: #101a2e;
  --bg-surface-elevated: #16233b;
  --bg-card: #172640;
  --bg-card-hover: #1d3150;
  --bg-input: #0e192b;
  --bg-sidebar: #0c1629;
  --text-primary: #f1f6ff;
  --text-secondary: #c1d0e5;
  --text-muted: #8fa4c2;
  --text-inverse: #0a1730;
  --border-subtle: #233653;
  --border-default: #3a5376;
  --border-strong: #6487b6;
  --accent-primary: #49a6ff;
  --accent-secondary: #8b7cff;
  --accent-hover: #74bcff;
  --success: #35c98a;
  --warning: #f2b84b;
  --danger: #f06d7a;
  --info: #62b7ff;
  --shadow-sm: 0 2px 8px rgba(0, 0, 0, .20);
  --shadow-md: 0 10px 24px rgba(0, 0, 0, .24);
  --shadow-lg: 0 18px 42px rgba(0, 0, 0, .32);
  --radius-sm: 8px;
  --radius-md: 12px;
  --radius-lg: 18px;
}

* { box-sizing: border-box; }
html, body, [data-testid="stAppViewContainer"] {
  color-scheme: dark !important;
  background: var(--bg-app) !important;
  color: var(--text-primary) !important;
  font-family: "DM Sans", Inter, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif !important;
}
.stApp {
  min-height: 100vh;
  background:
    radial-gradient(900px 500px at 76% -20%, rgba(73,166,255,.12), transparent 66%),
    radial-gradient(700px 460px at 8% 0%, rgba(139,124,255,.08), transparent 64%),
    var(--bg-app) !important;
  color: var(--text-primary) !important;
}
.stApp p, .stApp li, .stApp span, .stApp div, .stApp label { color: inherit; }
.main .block-container { max-width: 1560px; padding: 1.6rem 2rem 8rem; }

/* Browser-theme and accessibility guardrails. */
input, textarea, select, button { color-scheme: dark; }
@media (forced-colors: active) {
  * { forced-color-adjust: auto; }
  [data-testid="stChatMessage"], .security-card, .login-panel, .hitl-panel { border: 1px solid CanvasText !important; }
}
@media (prefers-reduced-motion: reduce) {
  *, *::before, *::after { animation-duration: .01ms !important; transition-duration: .01ms !important; scroll-behavior: auto !important; }
}

/* Scrollbars */
* { scrollbar-width: thin; scrollbar-color: var(--border-strong) var(--bg-surface); }
::-webkit-scrollbar { width: 9px; height: 9px; }
::-webkit-scrollbar-track { background: var(--bg-surface); }
::-webkit-scrollbar-thumb { background: var(--border-strong); border: 2px solid var(--bg-surface); border-radius: 999px; }

/* Header and product identity */
[data-testid="stHeader"] { background: rgba(10,16,32,.94) !important; border-bottom: 1px solid var(--border-subtle); }
.soc-header { display: flex; align-items: center; gap: 13px; padding: .15rem 0; }
.rotating-shield { width: 42px; height: 42px; filter: drop-shadow(0 4px 10px rgba(73,166,255,.28)); }
.soc-title-text { color: var(--text-primary); font-size: 1.7rem; font-weight: 700; letter-spacing: -.05em; }
.soc-role { margin-top: 1px; color: var(--text-secondary); font: 600 .76rem "JetBrains Mono", monospace; }
.soc-role b { color: var(--accent-hover); }
.soc-tagline { margin: .45rem 0 1.35rem; color: var(--text-muted); font: 600 .68rem "JetBrains Mono", monospace; letter-spacing: .045em; }

/* Side navigation */
[data-testid="stSidebar"] { background: var(--bg-sidebar) !important; border-right: 1px solid var(--border-subtle); }
[data-testid="stSidebar"] > div:first-child { padding: 1.25rem .9rem 2rem; }
.side-brand { padding: .25rem .35rem 1.1rem; border-bottom: 1px solid var(--border-subtle); }
.side-eyebrow, .side-section-label { color: var(--text-muted); font: 600 .63rem "JetBrains Mono", monospace; letter-spacing: .11em; }
.side-eyebrow span { display:inline-block; width:7px; height:7px; margin-right:7px; border-radius:50%; background:var(--success); box-shadow:0 0 0 3px rgba(53,201,138,.12); }
.side-brand h2 { margin:.52rem 0 .95rem; color:var(--text-primary); font-size:1.12rem; letter-spacing:-.03em; }
.side-brand h2 b { color:var(--accent-primary); }
.operator-card { position:relative; display:flex; gap:9px; align-items:center; padding:.72rem; background:var(--bg-surface-elevated); border:1px solid var(--border-subtle); border-radius:var(--radius-md); }
.operator-avatar { display:grid; place-items:center; width:30px; height:30px; color:#fff; background:linear-gradient(135deg,var(--accent-primary),var(--accent-secondary)); border-radius:9px; font-weight:700; }
.operator-card strong,.operator-card small { display:block; color:var(--text-primary); }.operator-card strong { font-size:.76rem; }.operator-card small { margin-top:2px; color:var(--text-muted); font-size:.62rem; }.operator-card i { position:absolute; top:8px; right:8px; color:var(--success); font:600 .54rem "JetBrains Mono",monospace; font-style:normal; }
.side-section-label { margin:1.25rem .35rem .5rem; }
[data-testid="stSidebar"] .stRadio label { min-height:38px; padding:.55rem .65rem !important; color:var(--text-secondary) !important; border:1px solid transparent; border-radius:var(--radius-sm); transition:background .16s ease,border-color .16s ease,color .16s ease; }
[data-testid="stSidebar"] .stRadio label:hover { background:var(--bg-surface-elevated); color:var(--text-primary) !important; }
[data-testid="stSidebar"] .stRadio label:has(input:checked) { background:#193255; border-color:#315a89; color:#fff !important; }
/* Streamlit changes the radio label's child order between releases; never hide a child by position. */
[data-testid="stSidebar"] .stRadio label > div,
[data-testid="stSidebar"] .stRadio label p,
[data-testid="stSidebar"] .stRadio label span { display:initial; color:var(--text-secondary) !important; opacity:1 !important; }
[data-testid="stSidebar"] .stRadio label:has(input:checked) > div,
[data-testid="stSidebar"] .stRadio label:has(input:checked) p,
[data-testid="stSidebar"] .stRadio label:has(input:checked) span { color:var(--text-primary) !important; }
.posture-grid { display:grid; grid-template-columns:1fr 1fr; overflow:hidden; border:1px solid var(--border-subtle); border-radius:var(--radius-md); background:var(--bg-surface); }.posture-grid div { padding:.72rem; border-right:1px solid var(--border-subtle); border-bottom:1px solid var(--border-subtle); }.posture-grid div:nth-child(even){border-right:0}.posture-grid div:nth-child(n+3){border-bottom:0}.posture-grid b,.posture-grid span{display:block}.posture-grid b{color:var(--text-primary);font:600 1rem "JetBrains Mono",monospace}.posture-grid span{margin-top:4px;color:var(--text-muted);font:600 .52rem "JetBrains Mono",monospace;letter-spacing:.07em}.side-footer{margin:1.2rem .15rem .55rem;color:var(--text-muted);font:600 .56rem "JetBrains Mono",monospace;letter-spacing:.06em}.side-footer span{color:var(--success)}

/* Surface system */
.security-card, .dashboard-hero, .login-panel, .hitl-panel, .audit-event, .attack-chain-node, .timeline-event,
div[data-testid="stMetric"], [data-testid="stExpander"], [data-testid="stStatusWidget"] { background:var(--bg-card) !important; border:1px solid var(--border-subtle) !important; border-radius:var(--radius-md) !important; box-shadow:var(--shadow-sm); }
.security-card, .login-panel, .hitl-panel, .audit-event, .attack-chain-node, .timeline-event { padding:1rem 1.1rem; }
.dashboard-hero { display:flex; align-items:flex-end; justify-content:space-between; gap:1rem; padding:1.35rem 1.45rem; margin:.15rem 0 1.35rem; background:linear-gradient(135deg,#172946,#14223a) !important; }.dashboard-hero span{color:var(--accent-hover);font:600 .62rem "JetBrains Mono",monospace;letter-spacing:.1em}.dashboard-hero h1{margin:.4rem 0 .22rem;color:var(--text-primary);font-size:1.7rem;letter-spacing:-.04em}.dashboard-hero p{margin:0;color:var(--text-secondary);font-size:.88rem}.hero-status{color:var(--success);font:600 .66rem "JetBrains Mono",monospace;letter-spacing:.06em}.hero-status i{display:inline-block;width:7px;height:7px;margin-right:6px;border-radius:50%;background:var(--success)}
div[data-testid="stMetric"] { min-height:106px; padding:1rem !important; background:var(--bg-card) !important; } div[data-testid="stMetric"]::before{content:"";display:block;width:32px;height:3px;margin-bottom:10px;background:var(--accent-primary);border-radius:2px}[data-testid="stMetricLabel"]{color:var(--text-secondary)!important;font:600 .66rem "JetBrains Mono",monospace!important;letter-spacing:.045em}[data-testid="stMetricValue"]{color:var(--text-primary)!important;font-size:1.4rem!important}[data-testid="stMetricDelta"]{color:var(--text-muted)!important}

/* Chat workspace */
[data-testid="stChatMessage"] { margin:.75rem 0 !important; padding:1rem 1.1rem !important; background:var(--bg-card) !important; border:1px solid var(--border-subtle) !important; border-radius:var(--radius-md) !important; box-shadow:var(--shadow-sm); color:var(--text-primary) !important; }
[data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarUser"]) { background:#193255 !important; border-color:#315f92 !important; }
[data-testid="stChatMessage"] [data-testid="stMarkdownContainer"], [data-testid="stChatMessage"] [data-testid="stMarkdownContainer"] * { color:var(--text-primary) !important; line-height:1.62; }
[data-testid="stChatMessage"] strong { color:#a8d8ff !important; }
[data-testid="stChatMessage"] code, .timeline-event code, .audit-event code { color:#bce3ff; background:#0b1525; border:1px solid var(--border-subtle); border-radius:5px; padding:.1rem .32rem; font-family:"JetBrains Mono",monospace; }
[data-testid="stChatMessage"] pre { background:#091321; border:1px solid var(--border-default); border-radius:var(--radius-sm); color:#eaf5ff; padding:.75rem; }
.trace-badge { display:inline-flex; align-items:center; padding:4px 8px; margin:2px 4px 2px 0; color:#b8e4ff; background:#112640; border:1px solid #2c527a; border-radius:999px; font:600 .63rem "JetBrains Mono",monospace; }

/* Controls - explicitly styled to resist browser dark-mode substitution. */
[data-testid="stTextInput"] input,[data-testid="stTextArea"] textarea,[data-testid="stNumberInput"] input,[data-testid="stChatInput"],[data-testid="stSelectbox"] > div > div,[data-testid="stMultiSelect"] > div > div { background:var(--bg-input) !important; color:var(--text-primary) !important; border:1px solid var(--border-default) !important; border-radius:var(--radius-sm) !important; box-shadow:none !important; }
[data-testid="stForm"] { padding:1.15rem !important; background:var(--bg-card) !important; border:1px solid var(--border-subtle) !important; border-radius:var(--radius-md) !important; box-shadow:var(--shadow-sm) !important; }
[data-testid="stCaptionContainer"], [data-testid="stCaptionContainer"] p, .stCaption { color:var(--text-muted) !important; }
[data-testid="stChatInput"] { padding:2px 8px !important; border-radius:var(--radius-md) !important; box-shadow:var(--shadow-md) !important; }
[data-testid="stChatInput"] textarea { min-height:52px !important; background:transparent !important; color:var(--text-primary) !important; border:0 !important; font-size:.92rem !important; }
input::placeholder, textarea::placeholder { color:var(--text-muted) !important; opacity:1 !important; }
[data-testid="stTextInput"] input:focus,[data-testid="stTextArea"] textarea:focus,[data-testid="stNumberInput"] input:focus,[data-testid="stChatInput"]:focus-within { border-color:var(--accent-primary) !important; outline:3px solid rgba(73,166,255,.20) !important; outline-offset:1px; }
[data-testid="stChatInput"] button { color:var(--accent-hover) !important; background:transparent !important; border:0 !important; box-shadow:none !important; }
.stButton > button, [data-testid="stFormSubmitButton"] > button { min-height:42px; color:#fff !important; background:linear-gradient(135deg,#287fcd,#4c83d9) !important; border:1px solid #61aafa !important; border-radius:var(--radius-sm) !important; font:600 .78rem "DM Sans",sans-serif !important; box-shadow:0 7px 16px rgba(35,119,201,.22) !important; transition:transform .16s ease,filter .16s ease,box-shadow .16s ease !important; }.stButton > button:hover,[data-testid="stFormSubmitButton"] > button:hover{transform:translateY(-1px)!important;filter:brightness(1.08);box-shadow:0 9px 20px rgba(35,119,201,.30)!important}.stButton > button:focus-visible,[data-testid="stFormSubmitButton"] > button:focus-visible{outline:3px solid rgba(116,188,255,.45)!important;outline-offset:2px!important}.stButton > button:disabled{color:#aab9ce!important;background:#29364b!important;border-color:#465774!important;box-shadow:none!important;cursor:not-allowed!important}
/* BaseWeb select widgets set their own foreground in light browser mode. */
[data-testid="stSelectbox"] [data-baseweb="select"],
[data-testid="stSelectbox"] [data-baseweb="select"] > div,
[data-testid="stSelectbox"] [data-baseweb="select"] input,
[data-testid="stSelectbox"] [data-baseweb="select"] span,
[data-testid="stMultiSelect"] [data-baseweb="select"],
[data-testid="stMultiSelect"] [data-baseweb="select"] > div,
[data-testid="stMultiSelect"] [data-baseweb="select"] input,
[data-testid="stMultiSelect"] [data-baseweb="select"] span { color:var(--text-primary) !important; -webkit-text-fill-color:var(--text-primary) !important; opacity:1 !important; }
[data-testid="stSelectbox"] [data-baseweb="select"] input::placeholder,
[data-testid="stMultiSelect"] [data-baseweb="select"] input::placeholder { color:var(--text-muted) !important; -webkit-text-fill-color:var(--text-muted) !important; }
[data-testid="stSelectbox"] [data-baseweb="select"] svg,
[data-testid="stMultiSelect"] [data-baseweb="select"] svg { color:var(--accent-hover) !important; fill:var(--accent-hover) !important; }
/* Current Streamlit uses role=combobox for the rendered selected value. */
[data-testid="stSelectbox"] [role="combobox"],
[data-testid="stMultiSelect"] [role="combobox"],
[data-testid="stSelectbox"] select,
[data-testid="stMultiSelect"] select {
  color:var(--text-primary) !important;
  -webkit-text-fill-color:var(--text-primary) !important;
  background-color:var(--bg-input) !important;
  border-color:var(--border-default) !important;
  opacity:1 !important;
}
[data-testid="stSelectbox"] [role="combobox"] *,
[data-testid="stMultiSelect"] [role="combobox"] * {
  color:var(--text-primary) !important;
  -webkit-text-fill-color:var(--text-primary) !important;
  opacity:1 !important;
}
[data-testid="stSelectbox"] option,
[data-testid="stMultiSelect"] option { color:var(--text-primary) !important; background:var(--bg-surface-elevated) !important; }
/* Last-resort scope override for Streamlit versions that inject the value colour inline. */
[data-testid="stSelectbox"] [role="combobox"],
[data-testid="stSelectbox"] [role="combobox"] *,
[data-testid="stSidebar"] [data-testid="stSelectbox"] *,
[data-testid="stForm"] [data-testid="stSelectbox"] * { color:#f1f6ff !important; -webkit-text-fill-color:#f1f6ff !important; }
[data-baseweb="select"] *, [data-baseweb="popover"] *, [role="listbox"] * { color:var(--text-primary) !important; } [data-baseweb="menu"], [role="listbox"] { background:var(--bg-surface-elevated) !important; border:1px solid var(--border-default) !important; }

/* Information components */
[data-testid="stTabs"] [data-baseweb="tab-list"]{gap:8px;border-bottom:1px solid var(--border-subtle)}[data-testid="stTabs"] button{color:var(--text-secondary)!important;font:600 .72rem "JetBrains Mono",monospace!important}[data-testid="stTabs"] button[aria-selected="true"]{color:var(--accent-hover)!important;border-bottom:2px solid var(--accent-primary)!important}[data-testid="stExpander"]{overflow:hidden!important;background:var(--bg-surface)!important}[data-testid="stExpander"] summary{color:var(--text-primary)!important;font-weight:600!important}.stAlert{color:var(--text-primary)!important;background:var(--bg-surface-elevated)!important;border:1px solid var(--border-default)!important;border-radius:var(--radius-sm)!important}.stAlert *{color:inherit!important}[data-testid="stDataFrame"],[data-testid="stTable"]{overflow:hidden;border:1px solid var(--border-default)!important;border-radius:var(--radius-sm)!important;background:var(--bg-card)!important}

/* Login, approval, investigation and audit components */
.login-brand { text-align:center; padding:2.2rem 0 1.3rem; }.login-emblem { display:grid; place-items:center; width:72px; height:72px; margin:0 auto 1rem; background:linear-gradient(145deg,#1b3557,#17233f); border:1px solid #4b79b1; border-radius:22px; box-shadow:var(--shadow-md); }.login-brand h1 { margin:0; color:var(--text-primary); font-size:2.2rem; letter-spacing:-.06em; }.login-brand p{margin:.35rem auto 0;max-width:470px;color:var(--text-secondary);font-size:.9rem}.login-panel{max-width:600px;margin:auto;padding:1.35rem}.login-panel h3{margin:.1rem 0 .35rem;color:var(--text-primary)}.login-panel .login-caption{color:var(--text-secondary);margin-bottom:1rem}.login-notice{max-width:600px;margin:1rem auto;color:var(--text-muted);font-size:.78rem;line-height:1.6}
.hitl-panel{margin:1rem 0;background:linear-gradient(135deg,#351d28,#22213a)!important;border-color:#a55568!important}.hitl-eyebrow{color:#ffb7bf;font:600 .68rem "JetBrains Mono",monospace;letter-spacing:.08em}.hitl-panel h3{margin:.35rem 0;color:#fff}.hitl-panel p,.hitl-panel li{color:#f3dce0}.hitl-meta{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:.6rem;margin-top:.85rem}.hitl-meta div{padding:.65rem;background:rgba(9,16,32,.44);border:1px solid rgba(255,193,202,.20);border-radius:var(--radius-sm)}.hitl-meta span{display:block;color:#f0a9b4;font:600 .59rem "JetBrains Mono",monospace}.hitl-meta b{color:#fff;font-size:.78rem}
.attack-chain-node{margin-bottom:.65rem;background:var(--bg-card)!important}.attack-chain-head,.audit-event-head{display:flex;justify-content:space-between;gap:1rem;align-items:center}.attack-chain-title{color:var(--accent-hover);font-size:1rem;font-weight:700}.severity-badge,.result-badge{display:inline-flex;padding:3px 8px;border-radius:999px;font:600 .63rem "JetBrains Mono",monospace}.severity-badge{color:#ffd2d8;background:#4d2230;border:1px solid #a84e60}.attack-chain-node p,.audit-event-detail{margin:.45rem 0 0;color:var(--text-secondary);font-size:.88rem}.chain-connector{text-align:center;color:var(--accent-secondary);font-weight:700}.timeline-event{margin-bottom:.75rem;border-left:3px solid var(--warning)!important}.timeline-event.critical{border-left-color:var(--danger)!important}.timeline-meta,.audit-event-meta{color:var(--accent-hover);font:600 .69rem "JetBrains Mono",monospace}.timeline-title,.audit-event-title{margin:.28rem 0;color:var(--text-primary);font-weight:700}.audit-event{margin-bottom:.55rem}.result-success{color:#baf6d7;background:#173a2c;border:1px solid #3e9b70}.result-failure{color:#ffd0d5;background:#4b2430;border:1px solid #ad5666}

@media (max-width: 720px) { .main .block-container{padding:1rem 1rem 6rem}.dashboard-hero{align-items:flex-start;flex-direction:column}.hitl-meta{grid-template-columns:1fr}.soc-title-text{font-size:1.45rem}[data-testid="stChatMessage"]{padding:.85rem!important}.login-brand{padding-top:1.3rem} }
</style>
"""
