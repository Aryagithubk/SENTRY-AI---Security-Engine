"""Reliable, state-driven execution topology and interactive SENTRY guardian."""
from __future__ import annotations

from dataclasses import dataclass, field
from html import escape
from typing import Any, Dict, Iterable, Literal

import streamlit as st
import streamlit.components.v1 as components

NodeStatus = Literal["pending", "running", "completed", "error"]
TOPOLOGY = (
    ("input", "QUERY INPUT", "IN", "input", 85, 222),
    ("router", "INTENT ROUTER", "RT", "router", 250, 222),
    ("agent", "SPECIALIST SWARM", "AI", "llm", 465, 88),
    ("tools", "TELEMETRY TOOLS", "TL", "tool", 465, 264),
    ("memory", "CASE MEMORY", "MM", "memory", 465, 350),
    ("synthesis", "EVIDENCE SYNTHESIS", "Σ", "llm", 700, 222),
    ("output", "FINAL RESPONSE", "OK", "output", 905, 222),
)
EDGES = (("input", "router"), ("router", "agent"), ("router", "tools"),
         ("router", "memory"), ("agent", "synthesis"), ("tools", "synthesis"),
         ("memory", "synthesis"), ("synthesis", "output"))
COLORS = {"pending": "#718398", "running": "#00f0ff", "completed": "#00ff66", "error": "#ff3366"}


@dataclass
class ExecutionVisualizer:
    """The serializable UI projection of the backend execution event stream."""

    key: str = "sentry_execution_visualizer"
    nodes: Dict[str, Dict[str, str]] = field(default_factory=dict)
    active_tool: str = "Awaiting investigation"
    specialists: Dict[str, Dict[str, str]] = field(default_factory=dict)
    event_log: list[Dict[str, str]] = field(default_factory=list)

    def __post_init__(self) -> None:
        defaults = {node_id: {"status": "pending", "detail": "Standby"} for node_id, *_ in TOPOLOGY}
        self.nodes = {**defaults, **self.nodes}

    @classmethod
    def from_session(cls, key: str = "sentry_execution_visualizer") -> "ExecutionVisualizer":
        state = st.session_state.get(key, {})
        return cls(
            key=key,
            nodes=state.get("nodes", {}),
            active_tool=state.get("active_tool", "Awaiting investigation"),
            specialists=state.get("specialists", {}),
            event_log=state.get("event_log", []),
        )

    def save(self) -> None:
        st.session_state[self.key] = {
            "nodes": self.nodes,
            "active_tool": self.active_tool,
            "specialists": self.specialists,
            "event_log": self.event_log[-8:],
        }
        st.session_state["sentry_bot_executing"] = any(n["status"] == "running" for n in self.nodes.values())

    def reset(self) -> None:
        self.nodes = {node_id: {"status": "pending", "detail": "Standby"} for node_id, *_ in TOPOLOGY}
        self.active_tool = "Awaiting investigation"
        self.specialists = {}
        self.event_log = []
        self.save()

    def update_node_status(self, node_id: str, status: NodeStatus | str, detail: str = "") -> None:
        if node_id not in self.nodes:
            raise ValueError(f"Unknown topology node: {node_id}")
        status = "completed" if status == "success" else status
        if status not in COLORS:
            raise ValueError(f"Unknown topology status: {status}")
        self.nodes[node_id] = {"status": status, "detail": detail or self.nodes[node_id]["detail"]}
        self.save()

    @staticmethod
    def _node_for_event(event: Dict[str, Any]) -> str:
        return {1: "router", 2: "agent", 3: "tools"}.get(int(event.get("stage", 0) or 0), "synthesis")

    def consume_event(self, event: Dict[str, Any]) -> None:
        kind, node_id = str(event.get("event", "")), self._node_for_event(event)
        detail = str(event.get("detail") or event.get("node") or "Processing")
        actor = str(event.get("node") or (event.get("tool") if kind == "tool_completed" else node_id))
        status_for_kind = {"node_started": "running", "node_completed": "completed", "node_waiting": "error", "tool_completed": "completed"}.get(kind)
        if status_for_kind:
            self.event_log.append({"actor": actor, "detail": detail, "status": status_for_kind, "kind": kind})
        if node_id == "agent" and status_for_kind:
            self.specialists[actor] = {"status": status_for_kind, "detail": detail}
        if kind == "node_started":
            if node_id == "router":
                self.update_node_status("input", "completed", "Query accepted")
            self.update_node_status(node_id, "running", detail)
        elif kind == "tool_completed":
            self.active_tool = str(event.get("tool") or "Telemetry operation")
            self.update_node_status("tools", "completed", self.active_tool)
        elif kind == "node_waiting":
            self.update_node_status(node_id, "error", "Analyst authorization required")
        elif kind == "node_completed":
            self.update_node_status(node_id, "completed", detail)
        else:
            self.save()

    def payload(self) -> Dict[str, Any]:
        return {"nodes": [
            {"id": node_id, "title": title, "badge": badge, "role": role, "x": x, "y": y, **self.nodes[node_id]}
            for node_id, title, badge, role, x, y in TOPOLOGY
        ], "active_tool": self.active_tool, "specialists": self.specialists, "event_log": self.event_log[-4:]}

    def render(self, slot: Any, height: int = 430) -> None:
        render_execution_graph(slot, self.payload(), height)


def _icon(role: str) -> str:
    paths = {
        "input": '<path d="M-12 0h21M4-7l7 7-7 7"/>',
        "router": '<path d="M-11-8h7l5 8-5 8h-7M0 0h11M6-5l5 5-5 5"/>',
        "llm": '<rect x="-8" y="-8" width="16" height="16" rx="2"/><path d="M-12-4h4M-12 4h4M8-4h4M8 4h4M-3-3h6v6h-6z"/>',
        "tool": '<path d="M-10-9l7 7M-6-11l8 8M-4 5l9-9 7 7-9 9zM-10 10l6-6"/>',
        "memory": '<ellipse cx="0" cy="-6" rx="9" ry="3"/><path d="M-9-6v12c0 4 18 4 18 0V-6M-9 0c0 4 18 4 18 0"/>',
        "output": '<rect x="-9" y="-9" width="18" height="18" rx="1"/><path d="M-5 0l4 4 7-8"/>',
    }
    return paths[role]


def _edge_path(source: Dict[str, Any], target: Dict[str, Any]) -> str:
    sx, sy, tx, ty = source["x"] + 32, source["y"], target["x"] - 32, target["y"]
    bend = max(48, abs(tx - sx) * .42)
    return f"M{sx} {sy} C{sx + bend} {sy} {tx - bend} {ty} {tx} {ty}"


def render_execution_graph(slot: Any, payload: Dict[str, Any], height: int = 360) -> None:
    """Render server-built SVG markup, so the topology is never JS-dependent."""
    nodes = {node["id"]: node for node in payload["nodes"]}
    edges = []
    for source_id, target_id in EDGES:
        source, target = nodes[source_id], nodes[target_id]
        status = target["status"]
        color = COLORS[status]
        path = _edge_path(source, target)
        active = status in {"running", "completed"}
        pulse = ""
        if active:
            duration = ".85s" if status == "running" else "1.75s"
            pulse = f'<circle r="{3.5 if status == "running" else 2.5}" fill="{color}" class="pulse"><animateMotion dur="{duration}" repeatCount="indefinite" path="{path}"/></circle>'
        edges.append(f'<path class="edge {"active" if active else ""} {"fault" if status == "error" else ""}" style="--edge:{color}" d="{path}"/>{pulse}')
    node_markup = []
    for node in nodes.values():
        status, color = node["status"], COLORS[node["status"]]
        title, detail = escape(node["title"]), escape(node["detail"])
        state = "READY" if status == "completed" else status.upper()
        node_markup.append(f'''<g class="node {status}" style="--node:{color}" transform="translate({node["x"]} {node["y"]})">
          <title>{title} — {detail}</title><circle class="halo" r="34"/><rect class="plate" x="-28" y="-28" width="56" height="56" rx="8"/>
          <g class="icon">{_icon(node["role"])}</g><text class="badge" y="17">{escape(node["badge"])}</text>
          <text class="node-title" y="45">{title}</text><text class="node-state" y="57">{state}</text></g>''')
    specialist_items = list(payload.get("specialists", {}).items())[-3:]
    if not specialist_items:
        specialist_items = [("Awaiting specialist handoff", {"status": "pending", "detail": "Router will activate the relevant investigation agent."})]
    specialist_rows = []
    for index, (name, item) in enumerate(specialist_items):
        status = item.get("status", "pending")
        color = COLORS.get(status, COLORS["pending"])
        short_name = escape(name[:30] + ("…" if len(name) > 30 else ""))
        short_detail = escape(item.get("detail", "")[:46] + ("…" if len(item.get("detail", "")) > 46 else ""))
        y = 132 + index * 22
        specialist_rows.append(f'''<g class="specialist-row" transform="translate(350 {y})"><rect width="230" height="18" rx="3"/><circle cx="10" cy="9" r="3" fill="{color}"/><text class="specialist-name" x="19" y="12">{short_name}</text><text class="specialist-detail" x="224" y="12">{short_detail}</text></g>''')
    ledger_items = payload.get("event_log", [])
    ledger = []
    for index, item in enumerate(ledger_items[-3:]):
        color = COLORS.get(item.get("status", "pending"), COLORS["pending"])
        actor = escape(item.get("actor", "workflow")[:20])
        detail = escape(item.get("detail", "")[:34])
        x = 38 + index * 318
        ledger.append(f'<g transform="translate({x} 400)"><circle cx="3" cy="0" r="3" fill="{color}"/><text class="ledger-actor" x="12" y="3">{actor}</text><text class="ledger-detail" x="12" y="14">{detail}</text></g>')
    html = f'''<!doctype html><html><body><section class="topology">
      <header><div><i></i>LIVE EXECUTION TOPOLOGY</div><small>{escape(str(payload["active_tool"]))}</small></header>
      <svg viewBox="0 0 1000 430" preserveAspectRatio="xMidYMid meet" aria-label="Multi-agent execution topology" role="img">
       <defs><filter id="glow"><feGaussianBlur stdDeviation="3" result="blur"/><feMerge><feMergeNode in="blur"/><feMergeNode in="SourceGraphic"/></feMerge></filter></defs>
       {''.join(edges)}<text class="swarm-label" x="350" y="120">ACTIVE SPECIALIST WORKERS</text>{''.join(specialist_rows)}<line class="ledger-line" x1="28" y1="384" x2="972" y2="384"/>{''.join(ledger)}{''.join(node_markup)}</svg></section>
      <style>html,body{{margin:0;overflow:hidden;background:transparent}}.topology{{height:{height}px;position:relative;overflow:hidden;border:1px solid rgba(0,240,255,.18);border-radius:10px;background:radial-gradient(ellipse 65% 90% at 50% 20%,rgba(0,240,255,.10),transparent 70%),#080e17;font-family:Inter,Arial,sans-serif}}.topology:after{{content:"";position:absolute;inset:0;pointer-events:none;opacity:.25;background-image:linear-gradient(rgba(100,220,255,.07) 1px,transparent 1px),linear-gradient(90deg,rgba(100,220,255,.07) 1px,transparent 1px);background-size:28px 28px}}header{{position:absolute;z-index:2;top:16px;left:18px;right:18px;display:flex;justify-content:space-between;gap:12px;color:#dffbff;font:700 10px JetBrains Mono,monospace;letter-spacing:1.2px;pointer-events:none}}header i{{display:inline-block;width:6px;height:6px;margin:0 7px 1px 0;border-radius:50%;background:#00ff66;box-shadow:0 0 10px #00ff66}}header small{{max-width:48%;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;color:#8299ad;font:600 9px JetBrains Mono,monospace;letter-spacing:0}}svg{{position:relative;z-index:1;display:block;width:100%;height:100%}}.edge{{fill:none;stroke:rgba(143,167,190,.30);stroke-width:1.4}}.edge.active{{stroke:var(--edge);stroke-width:1.8;filter:url(#glow)}}.edge.fault{{stroke:#ff3366;stroke-dasharray:5 5}}.pulse{{filter:url(#glow)}}.plate{{fill:rgba(12,22,36,.97);stroke:rgba(255,255,255,.12);stroke-width:1.25}}.halo{{fill:none;stroke:none}}.node.running .halo{{stroke:#00f0ff;stroke-width:1;stroke-dasharray:3 5;transform-origin:center;animation:orbit 2.8s linear infinite}}.node.running .plate{{stroke:#00f0ff;filter:url(#glow)}}.node.completed .plate{{stroke:#00ff66}}.node.error .plate{{stroke:#ff3366;filter:url(#glow)}}.icon{{fill:none;stroke:var(--node);stroke-width:1.7;stroke-linecap:round;stroke-linejoin:round}}.badge{{fill:var(--node);font:800 9px JetBrains Mono,monospace;text-anchor:middle}}.node-title{{fill:#e5f6ff;font:700 8px JetBrains Mono,monospace;text-anchor:middle;letter-spacing:.2px}}.node-state{{fill:var(--node);font:700 7px JetBrains Mono,monospace;text-anchor:middle;letter-spacing:.65px}}.swarm-label{{fill:#7c9ab0;font:700 7px JetBrains Mono,monospace;letter-spacing:1px}}.specialist-row rect{{fill:rgba(9,18,29,.94);stroke:rgba(0,240,255,.14);stroke-width:.6}}.specialist-name{{fill:#dff7ff;font:700 7px JetBrains Mono,monospace}}.specialist-detail{{fill:#7894a9;font:500 6px JetBrains Mono,monospace;text-anchor:end}}.ledger-line{{stroke:rgba(0,240,255,.14);stroke-width:1}}.ledger-actor{{fill:#c9f6ff;font:700 7px JetBrains Mono,monospace}}.ledger-detail{{fill:#7591a6;font:500 6px JetBrains Mono,monospace}}@keyframes orbit{{to{{transform:rotate(360deg)}}}}@media(max-width:640px){{header small{{display:none}}}}</style></body></html>'''
    with slot:
        components.html(html, height=height, scrolling=False)


def render_cyber_bot(executing: bool = False, slot: Any | None = None) -> None:
    """Render an interactive Three.js guardian; SVG remains as an offline fallback."""
    html = '''<div id="guardian"><div id="fallback"><svg viewBox="0 0 220 220"><circle cx="110" cy="110" r="82" class="ring"/><path d="M66 106q0-49 44-49t44 49v29q0 28-44 28t-44-28z" class="shell"/><path d="M76 107q34-20 68 0v20q-34 16-68 0z" class="visor"/><circle cx="94" cy="117" r="5"/><circle cx="126" cy="117" r="5"/></svg></div><div class="caption"><b>SENTRY GUARDIAN</b><span>__LABEL__</span></div></div>
    <style>html,body{{margin:0;overflow:visible;background:transparent}}#guardian{{width:220px;height:220px;position:relative;cursor:crosshair;user-select:none;background:radial-gradient(circle at 50% 48%,rgba(0,240,255,.18),transparent 62%)}}#guardian canvas{{position:absolute;inset:0;width:220px!important;height:190px!important}}#fallback{{height:190px;display:grid;place-items:center;filter:drop-shadow(0 0 12px rgba(0,240,255,.52))}}#fallback svg{{width:168px;height:168px}}#fallback .ring{{fill:none;stroke:#00f0ff;stroke-width:1.5;stroke-dasharray:6 8;transform-origin:110px 110px;animation:spin 8s linear infinite}}#fallback .shell{{fill:#dffaff;stroke:#7eefff;stroke-width:3}}#fallback .visor,#fallback circle{{fill:#00f0ff;stroke:#00f0ff}.caption{{position:absolute;left:0;right:0;bottom:2px;text-align:center;font:700 8px JetBrains Mono,monospace;letter-spacing:1.15px;color:#dffbff;text-shadow:0 0 10px #00c8dd}.caption span{{display:block;margin-top:4px;color:#00f0ff;font-size:7px}}@keyframes spin{{to{{transform:rotate(360deg)}}}}</style>
    <script type="module">const frame=window.frameElement,host=frame&&frame.parentElement;if(frame){{frame.style.cssText+='position:fixed!important;right:22px!important;bottom:86px!important;width:220px!important;height:220px!important;z-index:100!important;border:0!important;background:transparent!important;pointer-events:none!important'}if(host)host.style.cssText+='position:fixed!important;right:22px!important;bottom:86px!important;width:220px!important;height:220px!important;z-index:100!important;pointer-events:none!important';try{{const T=await import('https://cdn.jsdelivr.net/npm/three@0.160.0/build/three.module.js'),root=document.querySelector('#guardian'),scene=new T.Scene(),camera=new T.PerspectiveCamera(34,1,.1,100),renderer=new T.WebGLRenderer({{alpha:true,antialias:true,powerPreference:'high-performance'}});camera.position.set(0,.05,6.8);renderer.setSize(220,190);renderer.setPixelRatio(Math.min(devicePixelRatio,2));root.prepend(renderer.domElement);document.querySelector('#fallback').style.display='none';const bot=new T.Group(),white=new T.MeshPhysicalMaterial({{color:0xe9fbff,metalness:.86,roughness:.18,clearcoat:1}}),dark=new T.MeshStandardMaterial({{color:0x0a1724,metalness:.9,roughness:.19}}),cyan=new T.MeshStandardMaterial({{color:0x8dffff,emissive:0x00aac4,emissiveIntensity:__EMISSION__}});const skull=new T.Mesh(new T.SphereGeometry(1.05,40,28),white);skull.scale.set(1,.78,.82);bot.add(skull);const face=new T.Mesh(new T.SphereGeometry(.84,36,24),dark);face.scale.set(1,.43,.46);face.position.z=.68;bot.add(face);const visor=new T.Mesh(new T.BoxGeometry(1.22,.18,.08),cyan);visor.position.set(0,.08,1.05);bot.add(visor);[-.38,.38].forEach(x=>{{const eye=new T.Mesh(new T.SphereGeometry(.09,18,12),cyan);eye.position.set(x,.08,1.11);bot.add(eye)}});const jaw=new T.Mesh(new T.CylinderGeometry(.48,.63,.32,32),white);jaw.position.y=-.83;bot.add(jaw);const core=new T.Mesh(new T.SphereGeometry(.14,20,16),cyan);core.position.set(0,-.78,.62);bot.add(core);for(let i=0;i<3;i++){{const ring=new T.Mesh(new T.TorusGeometry(1.18+i*.16,.014,8,64),cyan);ring.rotation.x=2.43+i*.25;bot.add(ring)}}scene.add(bot,new T.HemisphereLight(0xeaffff,0x05101d,3));const key=new T.PointLight(0xffffff,15,18);key.position.set(2.5,3,4);scene.add(key);let px=0,py=0,time=0;const pointerSource=(frame&&frame.ownerDocument)||document;pointerSource.addEventListener('pointermove',event=>{{const width=pointerSource.defaultView.innerWidth,height=pointerSource.defaultView.innerHeight;px=event.clientX/width-.5;py=event.clientY/height-.5}});function animate(){{time+=.016;bot.position.y=Math.sin(time*1.25)*.11;bot.rotation.y+=(px*.9-bot.rotation.y)*.075;bot.rotation.x+=(-py*.38-bot.rotation.x)*.075;core.scale.setScalar(1+Math.sin(time*__PULSE_RATE__)*.17);bot.children.slice(6).forEach((ring,i)=>ring.rotation.z+=.008*(i+1));renderer.render(scene,camera);requestAnimationFrame(animate)}}animate()}}catch(error){{}}</script>'''
    html = (html.replace("__LABEL__", "ACTIVE SCAN" if executing else "CURSOR TRACKING")
                .replace("__EMISSION__", "3.5" if executing else "1.7")
                .replace("__PULSE_RATE__", "8" if executing else "3")
                .replace("{{", "{").replace("}}", "}"))
    if slot is None:
        components.html(html, height=0, scrolling=False)
    else:
        with slot:
            components.html(html, height=0, scrolling=False)


def render_execution_console(slot: Any, events: Iterable[Dict[str, Any]], complete: bool = False) -> None:
    visualizer, events = ExecutionVisualizer.from_session(), list(events)
    if events and events[0].get("event") == "node_started" and int(events[0].get("stage", 0) or 0) == 1:
        visualizer.reset()
    for event in events:
        visualizer.consume_event(event)
    if complete:
        visualizer.update_node_status("synthesis", "completed", "Evidence package assembled")
        visualizer.update_node_status("output", "completed", "Response ready")
    visualizer.render(slot)


def render_bot(executing: bool | None = None, slot: Any | None = None) -> None:
    """Refresh a single guardian placeholder without changing the page layout."""
    render_cyber_bot(
        bool(st.session_state.get("sentry_bot_executing", False)) if executing is None else executing,
        slot=slot,
    )
