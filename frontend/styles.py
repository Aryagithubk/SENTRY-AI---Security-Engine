MAIN_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500;700&display=swap');

/* Color Tokens */
:root {
    --bg-almost-black: #06070B;
    --bg-card: rgba(14, 15, 23, 0.75);
    --primary-violet: #A855F7;
    --primary-violet-glow: rgba(168, 85, 247, 0.4);
    --secondary-cyan: #06B6D4;
    --secondary-cyan-glow: rgba(6, 182, 212, 0.4);
    --accent-pink: #EC4899;
    --accent-pink-glow: rgba(236, 72, 153, 0.4);
    --text-primary: #F8FAFC;
    --text-muted: #94A3B8;
    --border-glow: rgba(168, 85, 247, 0.25);
}

html, body, [class*="css"] {
    font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif;
    color: var(--text-primary);
}

/* Background canvas mesh */
.stApp {
    background: radial-gradient(circle at 50% 10%, #130B24 0%, #06070B 60%, #030406 100%);
    background-attachment: fixed;
}

/* Neural Network Background Canvas overlay */
#neural-canvas {
    position: fixed;
    top: 0;
    left: 0;
    width: 100vw;
    height: 100vh;
    z-index: 0;
    pointer-events: none;
    opacity: 0.25;
}

/* Rotating Security Shield Container */
.shield-container {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    position: relative;
}

.rotating-shield {
    width: 42px;
    height: 42px;
    animation: rotateShield 12s linear infinite, pulseGlow 3s ease-in-out infinite alternate;
}

@keyframes rotateShield {
    from { transform: rotate(0deg); }
    to { transform: rotate(360deg); }
}

@keyframes pulseGlow {
    0% { filter: drop-shadow(0 0 8px var(--primary-violet-glow)); }
    50% { filter: drop-shadow(0 0 16px var(--secondary-cyan-glow)); }
    100% { filter: drop-shadow(0 0 20px var(--accent-pink-glow)); }
}

/* Header layout */
.soc-header {
    display: flex;
    align-items: center;
    gap: 16px;
    padding: 1rem 0 0.5rem 0;
}

.soc-title-text {
    font-size: 2.2rem;
    font-weight: 800;
    background: linear-gradient(135deg, var(--secondary-cyan) 0%, var(--primary-violet) 50%, var(--accent-pink) 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    letter-spacing: -0.8px;
    margin: 0;
}

.soc-tagline {
    font-size: 0.95rem;
    font-weight: 500;
    color: var(--secondary-cyan);
    letter-spacing: 0.5px;
    margin-bottom: 1.5rem;
    display: flex;
    align-items: center;
    gap: 8px;
}

/* Metric boxes */
.metric-box {
    background: var(--bg-card);
    border: 1px solid var(--border-glow);
    border-radius: 14px;
    padding: 1rem;
    box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.5), inset 0 0 12px rgba(168, 85, 247, 0.05);
    backdrop-filter: blur(12px);
    text-align: center;
    transition: all 0.3s ease;
}

.metric-box:hover {
    border-color: var(--secondary-cyan);
    box-shadow: 0 0 20px var(--secondary-cyan-glow);
}

.metric-val {
    font-size: 1.8rem;
    font-weight: 800;
    color: var(--secondary-cyan);
}

.metric-lbl {
    font-size: 0.75rem;
    color: var(--text-muted);
    text-transform: uppercase;
    letter-spacing: 1px;
}

/* Chat Message Cards with glowing borders */
[data-testid="stChatMessage"] {
    background: var(--bg-card) !important;
    border: 1px solid var(--border-glow) !important;
    border-radius: 16px !important;
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.4), inset 0 0 15px rgba(168, 85, 247, 0.04) !important;
    backdrop-filter: blur(12px) !important;
    margin-bottom: 1rem !important;
    padding: 1rem 1.25rem !important;
    transition: border-color 0.3s ease, box-shadow 0.3s ease !important;
}

[data-testid="stChatMessage"]:hover {
    border-color: rgba(168, 85, 247, 0.5) !important;
    box-shadow: 0 0 25px rgba(168, 85, 247, 0.25) !important;
}

/* Trace Badge */
.trace-badge {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    background: rgba(6, 182, 212, 0.12);
    border: 1px solid rgba(6, 182, 212, 0.35);
    color: var(--secondary-cyan);
    padding: 4px 12px;
    border-radius: 20px;
    font-size: 0.75rem;
    font-family: 'JetBrains Mono', monospace;
    font-weight: 600;
    margin-right: 6px;
    margin-bottom: 8px;
}

/* AI Avatar Shield Badge */
.ai-avatar-shield {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    width: 32px;
    height: 32px;
    background: radial-gradient(circle, var(--primary-violet) 0%, rgba(168, 85, 247, 0.2) 70%);
    border: 1px solid var(--primary-violet);
    border-radius: 50%;
    box-shadow: 0 0 15px var(--primary-violet-glow);
}

/* Buttons */
.stButton > button {
    background: linear-gradient(135deg, rgba(168, 85, 247, 0.2) 0%, rgba(6, 182, 212, 0.2) 100%) !important;
    border: 1px solid rgba(168, 85, 247, 0.4) !important;
    color: var(--text-primary) !important;
    border-radius: 12px !important;
    font-weight: 600 !important;
    transition: all 0.3s ease !important;
}

.stButton > button:hover {
    background: linear-gradient(135deg, var(--primary-violet) 0%, var(--secondary-cyan) 100%) !important;
    border-color: var(--secondary-cyan) !important;
    box-shadow: 0 0 20px var(--primary-violet-glow) !important;
    color: #FFFFFF !important;
    transform: translateY(-1px) !important;
}

/* Live agent execution console */
.execution-console {
    position: relative; overflow: hidden; margin: .7rem 0 1.1rem; padding: 1rem;
    border: 1px solid rgba(48, 219, 240, .25); border-radius: 18px;
    background: linear-gradient(115deg, rgba(8, 17, 31, .94), rgba(20, 10, 40, .82));
    box-shadow: 0 15px 45px rgba(0,0,0,.28), inset 0 1px rgba(255,255,255,.06);
}
.execution-console:before { content:""; position:absolute; inset:0; pointer-events:none; background:linear-gradient(105deg,transparent 30%,rgba(70,234,255,.09) 48%,transparent 65%); transform:translateX(-120%); animation:consoleSweep 3s ease-in-out infinite; }
@keyframes consoleSweep { to { transform:translateX(120%); } }
.console-top,.execution-readout { display:flex; align-items:center; justify-content:space-between; gap:12px; position:relative; z-index:1; }
.console-kicker,.console-id { color:#70e9f5; font:700 .64rem 'JetBrains Mono',monospace; letter-spacing:1.4px; }.console-id {color:#8895ae}
.live-dot { display:inline-block; width:7px; height:7px; border-radius:50%; background:#45f4d5; box-shadow:0 0 0 0 rgba(69,244,213,.75); margin-right:8px; animation:livePulse 1.5s infinite; }
@keyframes livePulse { 70% {box-shadow:0 0 0 7px rgba(69,244,213,0)} 100% {box-shadow:0 0 0 0 rgba(69,244,213,0)} }
.flow-rail { display:grid; grid-template-columns:repeat(4,1fr); gap:8px; margin:16px 0 13px; position:relative; z-index:1; }
.flow-node { min-width:0; padding:9px 8px; border:1px solid rgba(135,151,179,.15); border-radius:10px; background:rgba(3,7,16,.32); display:flex; align-items:center; gap:7px; opacity:.46; transition:.35s ease; }.flow-node b,.flow-node small{display:block;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}.flow-node b{font-size:.69rem}.flow-node small{font:600 .55rem 'JetBrains Mono',monospace;color:#8f9bb0;letter-spacing:.7px;margin-top:2px}.flow-num {font:700 .58rem 'JetBrains Mono',monospace;color:#77839c}.flow-node em {width:6px;height:6px;border-radius:50%;background:#59647a;margin-left:auto;flex:none}
.flow-node.done { opacity:1; border-color:rgba(71,238,191,.3); }.flow-node.done em {background:#47eebf;box-shadow:0 0 8px #47eebf}.flow-node.active {opacity:1; transform:translateY(-2px); border-color:#45dbf0; background:linear-gradient(135deg,rgba(18,198,226,.16),rgba(168,85,247,.13));box-shadow:0 0 20px rgba(60,217,240,.17)}.flow-node.active em{background:#65edff;box-shadow:0 0 12px #65edff;animation:livePulse 1.1s infinite}
.execution-readout { border-top:1px solid rgba(143,170,205,.14); padding-top:10px; justify-content:flex-start; }.readout-pulse{color:#b76dff;font-size:1rem;animation:spinOrbit 2s linear infinite}@keyframes spinOrbit{to{transform:rotate(360deg)}}.execution-readout b{font-size:.76rem}.execution-readout small{display:block;color:#94a3b8;font-size:.68rem;margin-top:2px}.tool-list{margin-left:auto;display:flex;gap:5px;flex-wrap:wrap;justify-content:flex-end}.tool-chip{font:600 .59rem 'JetBrains Mono',monospace;color:#7deafa;background:rgba(11,181,210,.1);border:1px solid rgba(47,211,234,.22);border-radius:20px;padding:4px 7px}.tool-chip.muted{color:#8490a5;border-color:rgba(130,144,165,.18)}.is-complete .live-dot{background:#47eebf;animation:none}.is-complete:before{animation:none}
@media(max-width:720px){.flow-rail{grid-template-columns:repeat(2,1fr)}.execution-readout{align-items:flex-start}.tool-list{margin-left:0}.console-id{display:none}}
@media(prefers-reduced-motion:reduce){.execution-console:before,.live-dot,.readout-pulse,.flow-node.active em{animation:none!important}}

/* Command sidebar: compact, restrained, and operations-focused */
[data-testid="stSidebar"] { background:linear-gradient(180deg,#090d16 0%,#0b1020 55%,#080b12 100%)!important; border-right:1px solid rgba(111,144,180,.18); }
[data-testid="stSidebar"] > div:first-child { padding:1.2rem .85rem 2rem; }
.side-brand { padding:.3rem .35rem 1.05rem; border-bottom:1px solid rgba(130,154,185,.14); }.side-eyebrow,.side-section-label { color:#71819c; font:700 .58rem 'JetBrains Mono',monospace; letter-spacing:1.45px; }.side-eyebrow span{display:inline-block;width:6px;height:6px;border-radius:50%;background:#4bf1c5;box-shadow:0 0 10px #4bf1c5;margin-right:7px}.side-brand h2 { margin:.45rem 0 1rem; font-size:1.15rem;letter-spacing:.4px;color:#edf5ff}.side-brand h2 b{color:#54e4f5;font-weight:500}.operator-card{position:relative;display:flex;align-items:center;gap:9px;padding:.7rem;border:1px solid rgba(125,153,191,.17);border-radius:10px;background:rgba(21,31,49,.56)}.operator-avatar{width:28px;height:28px;border-radius:8px;display:grid;place-items:center;font-weight:800;font-size:.73rem;background:linear-gradient(135deg,#247eaf,#834ec9)}.operator-card strong,.operator-card small{display:block}.operator-card strong{font-size:.74rem}.operator-card small{font-size:.6rem;color:#8798b3;margin-top:2px}.operator-card i{position:absolute;right:8px;top:8px;font:700 .48rem 'JetBrains Mono',monospace;color:#4bf1c5;font-style:normal}.side-section-label{margin:1.15rem .35rem .48rem}
[data-testid="stSidebar"] .stRadio > div { gap:3px; }[data-testid="stSidebar"] .stRadio label { border-left:2px solid transparent;border-radius:0!important;padding:.45rem .55rem!important;background:transparent!important;color:#91a0b8!important;font-size:.76rem!important;transition:.2s ease }[data-testid="stSidebar"] .stRadio label:has(input:checked){border-left-color:#56ddec!important;background:linear-gradient(90deg,rgba(49,202,221,.12),transparent)!important;color:#effbff!important}[data-testid="stSidebar"] .stRadio label div:first-child{display:none}
[data-testid="stSidebar"] [data-testid="stSelectbox"] > div > div {border-radius:8px!important;background:#111928!important;border:1px solid rgba(127,157,196,.2)!important;font-size:.73rem!important}.posture-grid{display:grid;grid-template-columns:1fr 1fr;border:1px solid rgba(125,153,191,.17);border-radius:10px;overflow:hidden;background:rgba(17,25,40,.6)}.posture-grid div{padding:.62rem .7rem;border-right:1px solid rgba(125,153,191,.12);border-bottom:1px solid rgba(125,153,191,.12)}.posture-grid div:nth-child(even){border-right:0}.posture-grid div:nth-child(n+3){border-bottom:0}.posture-grid b,.posture-grid span{display:block}.posture-grid b{font:700 1rem 'JetBrains Mono',monospace;color:#e8f6ff}.posture-grid span{margin-top:3px;color:#7890ae;font:700 .5rem 'JetBrains Mono',monospace;letter-spacing:.7px}
[data-testid="stSidebar"] .stButton > button{justify-content:flex-start;background:transparent!important;border:1px solid rgba(125,153,191,.15)!important;border-radius:8px!important;color:#aebbd0!important;font-size:.7rem!important;min-height:2rem!important;margin:1px 0}[data-testid="stSidebar"] .stButton > button:hover{transform:none!important;background:rgba(68,210,229,.1)!important;border-color:rgba(78,222,239,.4)!important;color:#f3fdff!important;box-shadow:none!important}.side-footer{margin:1.1rem .1rem .55rem;color:#7285a2;font:700 .52rem 'JetBrains Mono',monospace;letter-spacing:.55px}.side-footer span{color:#4bf1c5}
div[data-testid="stMetric"] {background:rgba(13,21,35,.72);border:1px solid rgba(125,153,191,.17);border-radius:10px;padding:.8rem}div[data-testid="stMetricLabel"]{font:700 .62rem 'JetBrains Mono',monospace!important;color:#8393ac!important;letter-spacing:.7px}div[data-testid="stMetricValue"]{font-size:1.45rem!important;color:#e8f7ff!important}
.dashboard-hero{display:flex;justify-content:space-between;align-items:flex-end;padding:1.35rem 1.45rem;margin:.15rem 0 1.35rem;border:1px solid rgba(125,153,191,.19);border-radius:14px;background:linear-gradient(115deg,rgba(15,27,47,.9),rgba(17,16,40,.68));box-shadow:inset 0 1px rgba(255,255,255,.05)}.dashboard-hero span{font:700 .59rem 'JetBrains Mono',monospace;letter-spacing:1.3px;color:#68ddec}.dashboard-hero h1{margin:.38rem 0 .18rem;font-size:1.65rem;letter-spacing:-.6px}.dashboard-hero p{margin:0;color:#93a4bc;font-size:.76rem}.hero-status{color:#72e9c6;font:700 .61rem 'JetBrains Mono',monospace;letter-spacing:1px}.hero-status i{display:inline-block;width:7px;height:7px;border-radius:50%;background:#47edbf;box-shadow:0 0 9px #47edbf;margin-right:6px}@media(max-width:700px){.dashboard-hero{align-items:flex-start;gap:14px;flex-direction:column}}
[data-testid="stSidebar"] .execution-console{margin:1rem 0 .2rem;padding:.72rem;border-radius:10px}[data-testid="stSidebar"] .flow-rail{grid-template-columns:repeat(2,1fr);gap:5px;margin:10px 0}[data-testid="stSidebar"] .flow-node{padding:6px;gap:4px}[data-testid="stSidebar"] .flow-node b{font-size:.58rem}[data-testid="stSidebar"] .execution-readout{display:block}[data-testid="stSidebar"] .tool-list{margin:7px 0 0;justify-content:flex-start}
</style>

<!-- Animated Neural Network Canvas Script -->
<script>
window.addEventListener('load', function() {
    if (document.getElementById('neural-canvas')) return;
    const canvas = document.createElement('canvas');
    canvas.id = 'neural-canvas';
    document.body.appendChild(canvas);
    const ctx = canvas.getContext('2d');

    let width = canvas.width = window.innerWidth;
    let height = canvas.height = window.innerHeight;

    window.addEventListener('resize', () => {
        width = canvas.width = window.innerWidth;
        height = canvas.height = window.innerHeight;
    });

    const particles = [];
    const numParticles = 45;

    for (let i = 0; i < numParticles; i++) {
        particles.push({
            x: Math.random() * width,
            y: Math.random() * height,
            vx: (Math.random() - 0.5) * 0.6,
            vy: (Math.random() - 0.5) * 0.6,
            radius: Math.random() * 2 + 1
        });
    }

    function draw() {
        ctx.clearRect(0, 0, width, height);

        for (let i = 0; i < numParticles; i++) {
            const p = particles[i];
            p.x += p.vx;
            p.y += p.vy;

            if (p.x < 0 || p.x > width) p.vx *= -1;
            if (p.y < 0 || p.y > height) p.vy *= -1;

            ctx.beginPath();
            ctx.arc(p.x, p.y, p.radius, 0, Math.PI * 2);
            ctx.fillStyle = '#A855F7';
            ctx.fill();

            for (let j = i + 1; j < numParticles; j++) {
                const p2 = particles[j];
                const dx = p.x - p2.x;
                const dy = p.y - p2.y;
                const dist = Math.sqrt(dx * dx + dy * dy);

                if (dist < 130) {
                    ctx.beginPath();
                    ctx.moveTo(p.x, p.y);
                    ctx.lineTo(p2.x, p2.y);
                    ctx.strokeStyle = `rgba(6, 182, 212, ${1 - dist / 130})`;
                    ctx.lineWidth = 0.6;
                    ctx.stroke();
                }
            }
        }
        requestAnimationFrame(draw);
    }
    draw();
});
</script>
"""
