const DEMO = {
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
