from pathlib import Path
import zipfile, textwrap

root = Path(__file__).resolve().parent
root.mkdir(exist_ok=True)

index_html = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>BloomNet — Friendship Graph</title>
  <link rel="stylesheet" href="style.css" />
</head>
<body>
  <header class="topbar">
    <div>
      <p class="eyebrow">BLOOMNET</p>
      <h1>My Friendship Graph <span>♡</span></h1>
      <p class="subtitle">A visual social network powered by graph data structures.</p>
    </div>
    <button id="resetBtn" class="ghost-btn">Reset demo</button>
  </header>

  <main class="layout">
    <section class="card graph-card">
      <div class="section-head">
        <div>
          <h2>Network</h2>
          <p>Drag a person, then click a node to inspect their relationship.</p>
        </div>
        <div class="legend">
          <span><i class="dot best"></i>Best friend</span>
          <span><i class="dot sister"></i>Like a sister</span>
          <span><i class="dot friend"></i>Friend</span>
        </div>
      </div>
      <div id="graphWrap" class="graph-wrap">
        <svg id="graph" viewBox="0 0 900 560" role="img" aria-label="BloomNet friendship graph"></svg>
      </div>
    </section>

    <aside class="side">
      <section class="card">
        <h2>Connection finder</h2>
        <p class="muted">BFS finds the shortest path through the network.</p>
        <div class="field">
          <label for="fromSelect">From</label>
          <select id="fromSelect"></select>
        </div>
        <div class="field">
          <label for="toSelect">To</label>
          <select id="toSelect"></select>
        </div>
        <button id="pathBtn" class="primary-btn">Find shortest connection</button>
        <div id="pathResult" class="result">Choose two people to explore the graph.</div>
      </section>

      <section class="card">
        <h2>Person details</h2>
        <div id="details" class="details empty">Click a node to see their details.</div>
      </section>

      <section class="card">
        <h2>Network analytics</h2>
        <div class="stats">
          <div><strong id="peopleCount">0</strong><span>people</span></div>
          <div><strong id="edgeCount">0</strong><span>connections</span></div>
          <div><strong id="avgStrength">0</strong><span>avg. strength</span></div>
          <div><strong id="strongest">—</strong><span>strongest bond</span></div>
        </div>
      </section>
    </aside>
  </main>

  <footer>BloomNet · Graph theory + data visualization · built as a CS portfolio project</footer>
  <script src="script.js"></script>
</body>
</html>
"""

style_css = """@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Playfair+Display:wght@600;700&display=swap');

:root {
  --bg: #fff7fb;
  --card: rgba(255,255,255,.9);
  --ink: #30252e;
  --muted: #806d79;
  --pink: #e96d9d;
  --pink-dark: #c64f7e;
  --lavender: #a98de8;
  --line: #eadce5;
  --shadow: 0 18px 50px rgba(117, 71, 99, .10);
}

* { box-sizing: border-box; }
body {
  margin: 0;
  min-height: 100vh;
  font-family: "DM Sans", sans-serif;
  color: var(--ink);
  background:
    radial-gradient(circle at 8% 8%, #ffe1ed 0 10%, transparent 28%),
    radial-gradient(circle at 90% 20%, #eee5ff 0 9%, transparent 25%),
    var(--bg);
}
.topbar {
  max-width: 1400px; margin: 0 auto; padding: 38px 32px 20px;
  display:flex; justify-content:space-between; gap:20px; align-items:flex-start;
}
.eyebrow { margin:0 0 5px; letter-spacing:.22em; font-size:12px; font-weight:700; color:var(--pink-dark); }
h1,h2,p { margin-top:0; }
h1 { font: 700 42px "Playfair Display", serif; margin-bottom:8px; }
h1 span { color:var(--pink); }
h2 { font-size:19px; margin-bottom:7px; }
.subtitle,.muted,.section-head p { color:var(--muted); font-size:14px; }
button,select { font:inherit; }
.ghost-btn,.primary-btn {
  border:0; border-radius:14px; padding:12px 16px; cursor:pointer; font-weight:700;
}
.ghost-btn { background:#fff; border:1px solid var(--line); color:var(--ink); }
.primary-btn { width:100%; background:var(--pink); color:#fff; box-shadow:0 8px 20px rgba(233,109,157,.25); }
.primary-btn:hover { background:var(--pink-dark); }
.layout {
  max-width:1400px; margin:0 auto; padding:0 32px 30px;
  display:grid; grid-template-columns:minmax(0, 1fr) 350px; gap:22px;
}
.card {
  background:var(--card); border:1px solid rgba(234,220,229,.85);
  border-radius:24px; box-shadow:var(--shadow); backdrop-filter:blur(10px);
}
.graph-card { padding:22px; }
.section-head { display:flex; justify-content:space-between; gap:20px; align-items:flex-start; }
.legend { display:flex; flex-wrap:wrap; gap:10px 14px; color:var(--muted); font-size:12px; }
.legend span { display:flex; align-items:center; gap:5px; }
.dot { width:8px; height:8px; border-radius:50%; display:inline-block; }
.dot.best { background:#e96d9d; } .dot.sister { background:#a98de8; } .dot.friend { background:#73a8d8; }
.graph-wrap { margin-top:15px; border-radius:20px; overflow:hidden; background:linear-gradient(145deg,#fffafd,#fbf7ff); border:1px solid #f0e6ed; }
svg { width:100%; height:auto; min-height:560px; display:block; }
.edge { stroke:#d8cbd4; stroke-width:2.5; }
.edge.highlight { stroke:var(--pink); stroke-width:5; }
.edge-label { font-size:11px; fill:#907b88; text-anchor:middle; pointer-events:none; }
.node { cursor:grab; }
.node:active { cursor:grabbing; }
.node circle { stroke:#fff; stroke-width:5; filter:drop-shadow(0 7px 10px rgba(100,60,90,.18)); }
.node text { text-anchor:middle; font-weight:700; fill:var(--ink); pointer-events:none; font-size:13px; }
.node .role { font-size:10px; font-weight:500; fill:#8c7784; }
.side { display:flex; flex-direction:column; gap:22px; }
.side .card { padding:20px; }
.field { margin:14px 0; }
label { display:block; font-size:12px; font-weight:700; margin-bottom:6px; color:var(--muted); }
select {
  width:100%; padding:11px 12px; border:1px solid var(--line); border-radius:12px;
  background:#fff; color:var(--ink); outline:none;
}
.result { margin-top:13px; padding:12px; border-radius:13px; background:#fff5f9; color:#745666; font-size:13px; line-height:1.5; }
.details.empty { color:var(--muted); font-size:14px; line-height:1.5; }
.detail-name { font:700 25px "Playfair Display",serif; margin-bottom:4px; }
.pill { display:inline-block; padding:5px 9px; border-radius:999px; background:#fff0f6; color:#b44c76; font-size:11px; font-weight:700; margin:7px 0 12px; }
.detail-row { display:flex; justify-content:space-between; gap:12px; padding:9px 0; border-top:1px solid #f0e6ed; font-size:13px; }
.detail-row span:first-child { color:var(--muted); }
.stats { display:grid; grid-template-columns:1fr 1fr; gap:10px; }
.stats div { padding:13px; border-radius:15px; background:#fff7fa; }
.stats strong { display:block; font-size:22px; }
.stats span { color:var(--muted); font-size:11px; }
footer { text-align:center; color:#9a8792; font-size:12px; padding:0 20px 25px; }
@media(max-width:950px) {
  .layout { grid-template-columns:1fr; }
  .side { display:grid; grid-template-columns:1fr 1fr; }
  .side .card:last-child { grid-column:1/-1; }
}
@media(max-width:650px) {
  .topbar { padding:25px 18px 15px; } .layout { padding:0 18px 25px; }
  h1 { font-size:32px; } .topbar { flex-direction:column; }
  .side { display:flex; } svg { min-height:420px; }
}
"""

script_js = r"""const DEMO = {
  people: [
    { id:"you", name:"You", role:"Center", strength:100 },
    { id:"briana", name:"Briana Njambi", role:"Best friend", strength:98 },
    { id:"helsey", name:"Helsey", role:"Like a sister", strength:94 },
    { id:"genti", name:"Genti", role:"University friend", strength:72 },
    { id:"ian", name:"Ian", role:"Boy best friend", strength:97 },
    { id:"njambi", name:"Njambi", role:"High-school friend", strength:88 }
  ],
  edges: [
    ["you","briana","Best friend",98],
    ["you","helsey","Like a sister",94],
    ["you","genti","University friend",72],
    ["you","ian","Boy best friend",97],
    ["you","njambi","High-school friend",88],
    ["briana","njambi","Friend",82],
    ["briana","helsey","Friend",74],
    ["briana","ian","Friend",76]
  ]
};

const STORAGE = "bloomnet-demo-v1";
let data = load();
let selected = null;
let drag = null;

const svg = document.getElementById("graph");
const NS = "http://www.w3.org/2000/svg";

function load() {
  try { return JSON.parse(localStorage.getItem(STORAGE)) || structuredClone(DEMO); }
  catch { return structuredClone(DEMO); }
}
function save() { localStorage.setItem(STORAGE, JSON.stringify(data)); }

function positions() {
  const p = {};
  p.you = {x:450,y:280};
  const others = data.people.filter(x => x.id !== "you");
  const radius = 195;
  others.forEach((person,i) => {
    const a = -Math.PI/2 + i * (Math.PI*2 / Math.max(others.length,1));
    p[person.id] = {x:450 + radius*Math.cos(a), y:280 + radius*.78*Math.sin(a)};
  });
  return p;
}
let pos = positions();

function make(tag, attrs={}) {
  const el = document.createElementNS(NS, tag);
  Object.entries(attrs).forEach(([k,v]) => el.setAttribute(k,v));
  return el;
}
function colorFor(role) {
  if (role.toLowerCase().includes("best")) return "#e96d9d";
  if (role.toLowerCase().includes("sister")) return "#a98de8";
  if (role.toLowerCase().includes("university")) return "#73a8d8";
  if (role.toLowerCase().includes("high")) return "#e5a56e";
  return "#9bb5a6";
}

function render() {
  pos = {...positions(), ...pos};
  const ids = new Set(data.people.map(p=>p.id));
  Object.keys(pos).forEach(id => { if(!ids.has(id)) delete pos[id]; });
  svg.innerHTML = "";

  const edgeLayer = make("g"), labelLayer = make("g"), nodeLayer = make("g");
  svg.append(edgeLayer,labelLayer,nodeLayer);

  data.edges.forEach((e, idx) => {
    if (!ids.has(e[0]) || !ids.has(e[1])) return;
    const a=pos[e[0]], b=pos[e[1]];
    const line=make("line",{x1:a.x,y1:a.y,x2:b.x,y2:b.y,class:"edge"});
    line.dataset.edge=idx; edgeLayer.appendChild(line);

    const mx=(a.x+b.x)/2, my=(a.y+b.y)/2;
    const label=make("text",{x:mx,y:my-7,class:"edge-label"});
    label.textContent=e[2]; labelLayer.appendChild(label);
  });

  data.people.forEach(person => {
    const g=make("g",{class:"node",transform:`translate(${pos[person.id].x},${pos[person.id].y})`});
    const r=person.id==="you"?38:30;
    const c=make("circle",{r,fill:colorFor(person.role)});
    if(person.id===selected) c.setAttribute("stroke","#30252e");
    g.appendChild(c);
    const name=make("text",{y:5}); name.textContent=person.name; g.appendChild(name);
    const role=make("text",{y:22,class:"role"}); role.textContent=person.role; g.appendChild(role);
    g.addEventListener("click", e => { e.stopPropagation(); selected=person.id; showDetails(person.id); render(); });
    g.addEventListener("pointerdown", e => startDrag(e,person.id,g));
    nodeLayer.appendChild(g);
  });

  updateSelects(); updateStats();
}
function startDrag(e,id,g) {
  drag={id, g};
  g.setPointerCapture?.(e.pointerId);
  const move = ev => {
    if(!drag) return;
    const rect=svg.getBoundingClientRect();
    pos[id] = {
      x: Math.max(45,Math.min(855,(ev.clientX-rect.left)/rect.width*900)),
      y: Math.max(45,Math.min(515,(ev.clientY-rect.top)/rect.height*560))
    };
    render();
  };
  const up = () => { drag=null; window.removeEventListener("pointermove",move); window.removeEventListener("pointerup",up); save(); };
  window.addEventListener("pointermove",move);
  window.addEventListener("pointerup",up);
}
function showDetails(id) {
  const p=data.people.find(x=>x.id===id); if(!p) return;
  const connections=data.edges.filter(e=>e[0]===id||e[1]===id);
  const names=connections.map(e=>{
    const other=e[0]===id?e[1]:e[0];
    return data.people.find(p=>p.id===other)?.name;
  }).filter(Boolean);
  document.getElementById("details").className="details";
  document.getElementById("details").innerHTML =
    `<div class="detail-name">${escapeHtml(p.name)}</div>
     <span class="pill">${escapeHtml(p.role)}</span>
     <div class="detail-row"><span>Bond strength</span><strong>${p.strength}%</strong></div>
     <div class="detail-row"><span>Direct connections</span><strong>${names.length}</strong></div>
     <div class="detail-row"><span>Connected to</span><strong>${escapeHtml(names.join(", ") || "—")}</strong></div>`;
}
function updateSelects() {
  const ids=["fromSelect","toSelect"];
  ids.forEach(selId=>{
    const s=document.getElementById(selId), old=s.value;
    s.innerHTML="";
    data.people.forEach(p=>{ const o=document.createElement("option"); o.value=p.id; o.textContent=p.name; s.appendChild(o); });
    if(data.people.some(p=>p.id===old)) s.value=old;
  });
}
function updateStats() {
  document.getElementById("peopleCount").textContent=data.people.length-1;
  document.getElementById("edgeCount").textContent=data.edges.length;
  const bonds=data.edges.map(e=>e[3]);
  const avg=bonds.length?Math.round(bonds.reduce((a,b)=>a+b,0)/bonds.length):0;
  document.getElementById("avgStrength").textContent=avg+"%";
  const best=data.edges.slice().sort((a,b)=>b[3]-a[3])[0];
  document.getElementById("strongest").textContent=best ? `${nameOf(best[0])} ↔ ${nameOf(best[1])}` : "—";
}
function nameOf(id){ return data.people.find(p=>p.id===id)?.name || id; }

function bfs(start,target) {
  const adj={};
  data.people.forEach(p=>adj[p.id]=[]);
  data.edges.forEach(([a,b])=>{ if(adj[a]&&adj[b]) {adj[a].push(b); adj[b].push(a);} });
  const q=[[start,[start]]], seen=new Set([start]);
  while(q.length){
    const [cur,path]=q.shift();
    if(cur===target) return path;
    for(const next of adj[cur]||[]){
      if(!seen.has(next)){seen.add(next);q.push([next,[...path,next]]);}
    }
  }
  return null;
}

document.getElementById("pathBtn").addEventListener("click",()=>{
  const a=document.getElementById("fromSelect").value, b=document.getElementById("toSelect").value;
  const path=bfs(a,b), box=document.getElementById("pathResult");
  if(!path){ box.textContent="No connection found."; return; }
  box.innerHTML=`<strong>${path.length-1} edge${path.length-1===1?"":"s"}</strong><br>${path.map(nameOf).join(" → ")}`;
});
document.getElementById("resetBtn").addEventListener("click",()=>{
  data=structuredClone(DEMO); selected=null; save(); document.getElementById("details").className="details empty";
  document.getElementById("details").textContent="Click a node to see their details."; render();
});
svg.addEventListener("click",()=>{selected=null; render();});
function escapeHtml(s){return String(s).replace(/[&<>"']/g,m=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#039;"}[m]));}

render();
"""

readme = """# BloomNet v1

BloomNet is a feminine-styled friendship graph visualizer built as a Computer Science portfolio project.

## Run it
Open `index.html` in a browser. No server or installation is required.

## What is implemented
- Graph data model using vertices and edges
- Interactive SVG network
- Your supplied people and relationships
- Clickable person details
- Draggable nodes
- Relationship labels
- BFS shortest-path finder
- Basic network analytics
- LocalStorage persistence
- Reset-to-demo button

## Current demo network
- You ↔ Briana Njambi — Best friend
- You ↔ Helsey — Like a sister
- You ↔ Genti — University friend
- You ↔ Ian — Boy best friend
- You ↔ Njambi — High-school friend
- Briana Njambi ↔ Njambi — Friend
- Briana Njambi ↔ Helsey — Friend
- Briana Njambi ↔ Ian — Friend

## Next upgrades
1. Add/edit/delete people and relationships through forms.
2. Add DFS and connected-components analysis.
3. Add relationship history and timestamps.
4. Add community detection.
5. Add an AI layer that summarizes network patterns.
"""

for name, content in {
    "index.html": index_html, "style.css": style_css, "script.js": script_js, "README.md": readme
}.items():
    (root/name).write_text(content, encoding="utf-8")

zip_path = root / "bloomnet_v1.zip"
with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as z:
    for p in root.iterdir():
        z.write(p, arcname=f"BloomNet/{p.name}")

print(f"Created {zip_path} with {len(list(root.iterdir()))} files.")
