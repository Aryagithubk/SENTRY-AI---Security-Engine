"""Live workflow visualisation components for the SENTRY copilot."""

from html import escape
from typing import Any, Dict, List

import streamlit.components.v1 as components


WORKFLOW_NODES = [
    ("Supervisor Agent", "01", "ROUTE"),
    ("Specialist Agent", "02", "INVESTIGATE"),
    ("Telemetry Tool", "03", "QUERY"),
    ("SENTRY Synthesis", "04", "SYNTHESIZE"),
]


def render_bot() -> None:
    """Render a self-contained Three.js security bot docked to the viewport."""
    components.html(
        """
        <div id="bot-stage"><div class="bot-label"><i></i> SENTRY CORE <span>ONLINE</span></div></div>
        <style>
          html,body{margin:0;background:transparent;overflow:hidden}#bot-stage{height:176px;position:relative;background:radial-gradient(circle at 50% 45%,rgba(8,198,220,.16),transparent 53%)}
          .bot-label{position:absolute;z-index:2;bottom:8px;left:50%;transform:translateX(-50%);white-space:nowrap;color:#dceeff;font:700 9px/1.5 Arial;letter-spacing:2px}.bot-label i{display:inline-block;width:6px;height:6px;background:#38f8d7;border-radius:50%;box-shadow:0 0 10px #38f8d7;margin-right:6px}.bot-label span{color:#62e7ff;margin-left:6px}
        </style>
        <script type="module">
          import * as THREE from 'https://unpkg.com/three@0.160.0/build/three.module.js';
          const frame=window.frameElement, host=frame && frame.parentElement;
          if(frame){frame.style.cssText+='position:fixed!important;right:20px!important;bottom:18px!important;width:184px!important;height:176px!important;z-index:99999!important;border:0!important;background:transparent!important;pointer-events:auto!important';}
          if(host){host.style.cssText+='position:fixed!important;right:20px!important;bottom:18px!important;width:184px!important;height:176px!important;z-index:99999!important;pointer-events:none!important';}
          const stage=document.getElementById('bot-stage'), scene=new THREE.Scene();
          const camera=new THREE.PerspectiveCamera(38,stage.clientWidth/stage.clientHeight,.1,100);camera.position.set(0,.1,7);
          const renderer=new THREE.WebGLRenderer({alpha:true,antialias:true});renderer.setPixelRatio(Math.min(devicePixelRatio,2));renderer.setSize(stage.clientWidth,stage.clientHeight);stage.appendChild(renderer.domElement);
          const bot=new THREE.Group(), cyan=new THREE.MeshStandardMaterial({color:0x0ccde5,metalness:.75,roughness:.2,emissive:0x063a56,emissiveIntensity:.9}), dark=new THREE.MeshStandardMaterial({color:0x12152a,metalness:.9,roughness:.25}), violet=new THREE.MeshStandardMaterial({color:0xa855f7,emissive:0x4a126d,emissiveIntensity:1});
          const head=new THREE.Mesh(new THREE.SphereGeometry(1.03,32,20),dark);head.scale.set(1,.8,.85);bot.add(head);
          const visor=new THREE.Mesh(new THREE.SphereGeometry(.77,32,16,0,Math.PI*2,0,Math.PI*.48),cyan);visor.scale.set(1,.42,.5);visor.position.set(0,.05,.72);bot.add(visor);
          const eyeGeo=new THREE.SphereGeometry(.09,16,12);[-.34,.34].forEach(x=>{const eye=new THREE.Mesh(eyeGeo,violet);eye.position.set(x,.11,1.08);bot.add(eye)});
          const neck=new THREE.Mesh(new THREE.CylinderGeometry(.48,.65,.38,24),dark);neck.position.y=-.9;bot.add(neck);
          const ring=new THREE.Mesh(new THREE.TorusGeometry(1.25,.018,8,64),cyan);ring.rotation.x=Math.PI/2.6;ring.position.y=-.08;bot.add(ring);
          scene.add(bot,new THREE.HemisphereLight(0x65eaff,0x150821,2.6));const light=new THREE.PointLight(0xbc65ff,8,20);light.position.set(2,3,4);scene.add(light);
          let t=0;function animate(){t+=.016;bot.rotation.y=Math.sin(t*.7)*.3;bot.position.y=Math.sin(t*1.3)*.09;ring.rotation.z=t*.8;renderer.render(scene,camera);requestAnimationFrame(animate)}animate();
          addEventListener('resize',()=>{camera.aspect=stage.clientWidth/stage.clientHeight;camera.updateProjectionMatrix();renderer.setSize(stage.clientWidth,stage.clientHeight)});
        </script>
        """,
        height=176,
    )


def render_execution_console(slot: Any, events: List[Dict[str, Any]], complete: bool = False) -> None:
    """Update the live execution panel from graph lifecycle events."""
    active = next((event for event in reversed(events) if event["event"] in {"node_started", "node_waiting"}), None)
    completed_stages = {event.get("stage") for event in events if event["event"] == "node_completed"}
    tool_events = [event for event in events if event["event"] == "tool_completed"]
    active_name = active.get("node") if active and not complete else "SENTRY Synthesis"
    active_detail = (active or {"detail": "Finalizing secure response"}).get("detail", "Preparing workflow")

    node_html = []
    for name, number, label in WORKFLOW_NODES:
        is_tool = name == "Telemetry Tool"
        stage = int(number)
        state = "pending"
        if (is_tool and tool_events) or (stage in completed_stages):
            state = "done"
        if not complete and (name == active_name or (active_name not in {n[0] for n in WORKFLOW_NODES} and name == "Specialist Agent")):
            state = "active"
        node_html.append(f'<div class="flow-node {state}"><span class="flow-num">{number}</span><span><b>{name}</b><small>{label}</small></span><em></em></div>')

    recent_tools = "".join(
        f'<span class="tool-chip">⌁ {escape(str(event.get("tool", "telemetry")))}</span>' for event in tool_events[-3:]
    ) or '<span class="tool-chip muted">Ready for telemetry</span>'
    status = "COMPLETE" if complete else "LIVE EXECUTION"
    slot.markdown(
        f'''<section class="execution-console {'is-complete' if complete else ''}">
          <div class="console-top"><div><span class="live-dot"></span><span class="console-kicker">{status}</span></div><span class="console-id">RUN // {len(events):02d} EVENTS</span></div>
          <div class="flow-rail">{''.join(node_html)}</div>
          <div class="execution-readout"><span class="readout-pulse">◈</span><div><b>{escape(str(active_name))}</b><small>{escape(str(active_detail))}</small></div><div class="tool-list">{recent_tools}</div></div>
        </section>''',
        unsafe_allow_html=True,
    )
