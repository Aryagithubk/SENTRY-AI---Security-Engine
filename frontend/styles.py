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
