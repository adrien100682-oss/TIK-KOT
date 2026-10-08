/* TIK-KOT extra.js : 🎨 Couleurs, 🔍 À sonder, recherche LBC avec la console. Chargé par index.html. */
(function(){
const bar=document.querySelector(".bar"),ab=$("ab");
const st=document.createElement("style");
st.textContent=`#xo{display:none;position:fixed;inset:0;z-index:60;background:var(--bg);color:var(--fg);overflow:auto;padding:14px}
#xo .w{max-width:900px;margin:0 auto}#xo .xb{border:0;border-radius:8px;padding:8px 12px;font-weight:700;cursor:pointer;font-size:14px;background:var(--card);color:var(--fg);border:1px solid var(--mut)}
#xo .xs{display:flex;gap:8px;margin:10px 0}#xo .xs div{flex:1;background:var(--card);border:1px solid var(--line);border-radius:10px;padding:6px;text-align:center;font-size:11px;color:var(--mut)}#xo .xs b{display:block;font-size:20px;color:var(--fg)}
#xo .xg{background:var(--card);border:1px solid var(--line);border-radius:14px;padding:12px;text-align:center;max-width:520px;margin:10px auto}
#xo .xcv{height:min(46vh,340px);border-radius:10px;position:relative;overflow:hidden;background:#222;display:flex;align-items:center;justify-content:center}
#xo .xcv .bg{position:absolute;inset:-20px;background-size:cover;background-position:center;filter:blur(20px) brightness(.5)}#xo .xcv img{position:relative;max-width:100%;max-height:100%}
#xo .xn{font-size:22px;font-weight:800;margin:10px 0 2px}
#xo .xbt{display:grid;grid-template-columns:repeat(5,1fr);gap:8px;margin-top:12px}#xo .xbt button{height:64px;font-size:30px;font-weight:900;border:3px solid #0006;border-radius:12px;cursor:pointer}#xo .xbt small{display:block;font-size:11px;font-weight:600}#xo .xbt button:disabled{opacity:.35}
#xo .big{font-size:44px;font-weight:900}#xo .nx{background:var(--acc);color:#111;border:0;border-radius:10px;padding:12px 22px;font-weight:800;font-size:16px;cursor:pointer;margin-top:8px}
#xo .ctl{display:flex;gap:10px 16px;flex-wrap:wrap;align-items:center;margin:10px 0;font-size:14px;color:var(--mut)}
#xo .row{background:var(--card);border:1px solid var(--line);border-radius:10px;padding:10px 12px;display:flex;align-items:center;gap:10px;margin-bottom:8px;flex-wrap:wrap}#xo .row.none{opacity:.4}#xo .row.fav{border-color:var(--acc)}
#xo .tl2{width:34px;height:34px;border-radius:9px;display:flex;align-items:center;justify-content:center;font-weight:900;font-size:20px;flex:none}
#xo .inf2{flex:1;min-width:170px}#xo .pr{font-weight:800;font-size:17px;color:var(--acc);white-space:nowrap}
#xo a.sb2{color:#fff;text-decoration:none;font-weight:800;font-size:13px;border-radius:8px;padding:8px 11px}#xo .act{display:flex;gap:6px;flex-wrap:wrap}
#xo .no{background:#444;color:#fff;border:0;border-radius:8px;padding:8px 10px;font-weight:700;cursor:pointer}#xo .ok{background:#1f9d55;color:#fff;border:0;border-radius:8px;padding:8px 10px;font-weight:700;cursor:pointer}
#xo pre{white-space:pre-wrap;font-family:inherit}
#xo.gm{padding:8px}#xo.gm .w{max-width:none;height:calc(100vh - 16px);display:flex;flex-direction:column;gap:6px}#xo.gm h2{font-size:18px}
#xo.gm #xb{flex:1;min-height:0;display:flex;flex-direction:column;gap:6px}
#xo.gm .xs{margin:0;gap:18px;align-items:center;font-size:13px;color:var(--mut);flex:none;flex-wrap:wrap}#xo.gm .xs b{color:var(--fg);font-size:18px}
#xo .xph{flex:1;min-height:0;display:flex;gap:8px}
#xo .xp{flex:1;min-width:0;position:relative;overflow:hidden;border-radius:10px;background:#222;display:flex;align-items:center;justify-content:center}
#xo .xp .bg{position:absolute;inset:-20px;background-size:cover;background-position:center;filter:blur(20px) brightness(.5)}
#xo .xp img{position:relative;width:100%;height:100%;object-fit:contain}
#xo .cap2{position:absolute;left:0;right:0;bottom:0;background:#000b;color:#fff;font-size:12px;padding:4px 8px;z-index:2}#xo #gph{cursor:pointer}
#xo .xn{flex:none;font-size:clamp(18px,3vh,28px);text-align:center}
#xo.gm .xbt{flex:none;margin:0}#xo.gm .xbt button{height:clamp(54px,9vh,84px);font-size:clamp(28px,5vh,44px)}
#xo #gr{flex:none;min-height:60px;display:flex;align-items:center;justify-content:center;gap:16px}#xo #gr .big{font-size:40px}#xo #gr .nx{margin:0}
body.raffle .card:not(.rev) .conbar .rk,body.raffle .card:not(.rev) .conbar .nf,body.raffle .card:not(.rev) .gt .badge{visibility:hidden}
body.raffle #feed{scrollbar-width:none}body.raffle #feed::-webkit-scrollbar{display:none}`;
document.head.appendChild(st);
const mk=(id,t,bg)=>{const b=document.createElement("button");b.id=id;b.type="button";b.textContent=t;b.style.cssText="border:0;border-radius:8px;padding:7px 12px;font-weight:700;cursor:pointer;font-size:14px;color:#fff;background:"+bg;bar.insertBefore(b,ab);return b};
const ov=document.createElement("div");ov.id="xo";document.body.appendChild(ov);
let MODE="",KEYH=null;
const names=()=>SEL.length?SEL:CONS.map(c=>c.key);
function xpool(minN){const L=[];names().forEach(k=>{const l=LD[k];if(!l)return;(l.games||[]).forEach(g=>{
 const e=ents(g).find(x=>x.cond==mcOf(k)&&x.lang=="FR"&&!x.sp&&x.n);if(!e||e.n<minN||!e.min)return;
 L.push({c:k,uid:g.uid,t:g.t,n:e.n,min:e.min,p:e.ref||e.min,cover:g.cover,fame:g.fame,imgs:e.imgs&&e.imgs.length?e.imgs:(e.top&&e.top[0]&&e.top[0][2]?[e.top[0][2]]:[])})})});return L}
function xopen(m){if(RF.on)rfStop();auto(false);MODE=m;
 ov.innerHTML='<div class="w"><div style="display:flex;justify-content:space-between;align-items:center"><h2 id="xt" style="margin:0;color:var(--acc)"></h2><button class="xb" id="xc">✕ Fermer</button></div><div id="xb"></div></div>';
 $("xc").onclick=xclose;ov.classList.toggle("gm",m=="g");ov.style.display="block";ov.scrollTop=0;KEYH=null;
 if(!names().some(k=>LD[k])){$("xb").innerHTML='<div class="sub" style="padding:20px">Données pas encore chargées, réessaie dans un instant.</div>';return}
 m=="g"?game():sonde()}
function xclose(){MODE="";KEYH=null;ov.style.display="none"}
document.addEventListener("keydown",e=>{if(!MODE)return;
 if(e.key=="Escape"){xclose();return}
 if(e.target.tagName==="SELECT"||e.target.tagName==="INPUT")return;
 e.stopPropagation();if(e.key===" ")e.preventDefault();if(KEYH)KEYH(e)},true);
mk("xgb","🎨 Couleurs","#0b8f6a").onclick=()=>xopen("g");
mk("xsb","🔍 À sonder","#c26a00").onclick=()=>xopen("s");

/* ---------- 🎨 jeu des couleurs ---------- */
function game(){$("xt").textContent="🎨 Jeu des couleurs";
 let S={ok:0,n:0,st:0,bs:0};try{S=Object.assign(S,JSON.parse(localStorage.getItem("tikkot_couleurs")||"{}"))}catch(e){}
 let L=xpool(2).filter(r=>tierOf(r.min));const W=L.filter(r=>r.imgs.length);if(W.length>=10)L=W;
 const T=[...TI].sort((a,b)=>a.t-b.t);let cur=null,done=true,last=null,pi=0;
 $("xb").innerHTML=`<div class="xs"><span>Score <b id="g1"></b></span><span>Série <b id="g2"></b></span><span>Record <b id="g3"></b></span><span>Touches D C B A S · Espace = suivant · clic sur la photo de l'annonce = photo suivante</span></div>
 <div class="xph"><div class="xp" id="gcv"></div><div class="xp" id="gph"></div></div>
 <div class="xn"><b id="gn"></b> <span class="sub" id="gk"></span></div>
 <div class="xbt">${T.map(x=>`<button data-k="${x.k}" style="background:${x.c};color:${ink(x.c)}">${x.k}<small>dès ${x.t} €</small></button>`).join("")}</div><div id="gr"></div>`;
 const stats=()=>{$("g1").textContent=S.ok+"/"+S.n;$("g2").textContent=S.st;$("g3").textContent=S.bs};
 const btns=()=>[...document.querySelectorAll("#xb .xbt button")];
 const pan=(src,cap)=>src?`<div class="bg" style="background-image:url('${safe(src)}')"></div><img src="${safe(src)}" alt=""><div class="cap2">${cap}</div>`:`<span class="sub">${cap}</span>`;
 const showPh=()=>{const im=cur.imgs;$("gph").innerHTML=pan(im[pi]||"",im.length?"📷 Photo de l'annonce "+(pi+1)+"/"+im.length+(im.length>1?" · clique pour la suivante":""):"Pas de photo d'annonce")};
 function next(){if(!L.length){$("gn").textContent="Aucun jeu disponible (coche des consoles).";return}
  let g;do{g=L[Math.floor(Math.random()*L.length)]}while(L.length>1&&g===last);last=cur=g;done=false;pi=0;
  $("gcv").innerHTML=pan(g.cover?IMG+g.cover+".jpg":"","Jaquette officielle (IGDB)");showPh();
  $("gn").textContent=g.t;$("gk").textContent="· "+cname(g.c);$("gr").innerHTML="";btns().forEach(b=>b.disabled=false)}
 function ans(k){if(done||!cur)return;done=true;const t=tierOf(cur.min),ok=t.k==k;S.n++;
  if(ok){S.ok++;S.st++;if(S.st>S.bs)S.bs=S.st}else S.st=0;jset("tikkot_couleurs",S);stats();btns().forEach(b=>b.disabled=true);
  $("gr").innerHTML=`<div class="big" style="color:${t.c}">${eur(cur.min)}</div><div>${ok?"✔ Bravo !":"✘ Raté"} : c'était <b style="color:${t.c}">${t.k}</b>${ok?"":" (tu avais choisi "+k+")"}</div><button class="nx" id="gnx">Suivant ▶</button>`;$("gnx").onclick=next}
 $("gph").onclick=()=>{if(!cur||cur.imgs.length<2)return;pi=(pi+1)%cur.imgs.length;showPh()};
 $("xb").onclick=e=>{const b=e.target.closest("button[data-k]");if(b)ans(b.dataset.k)};
 KEYH=e=>{const k=e.key.toUpperCase();if(["D","C","B","A","S"].includes(k)&&!e.ctrlKey&&!e.metaKey)ans(k);else if((e.key===" "||e.key==="Enter")&&done)next()};
 stats();next()}

/* ---------- 🔍 À sonder ---------- */
let S2=jget("tikkot_sonde");
const isN=u=>S2[u]&&S2[u].s=="n"&&Date.now()-S2[u].d<6048e5,isF=u=>S2[u]&&S2[u].s=="f";
function sonde(){$("xt").textContent="🔍 À sonder";
 $("xb").innerHTML=`<div class="sub">Jeux de rang A/S avec un prix fiable (≥ 3 annonces). Ouvre LBC / Vinted : si rien, « Rien trouvé » (caché 7 jours) ; si affaire possible, « Intéressant » (⭐ en tête). Consoles cochées dans 🎮 Consoles.</div>
 <div class="ctl"><label>Mode <select id="sm"><option value="s">À sonder (A/S, ≥ 3 ann.)</option><option value="t">Tous (valeur mini)</option></select></label>
 <label>Valeur mini <input type="number" id="sn" value="40" step="5" style="width:70px;background:var(--bg);color:var(--fg);border:1px solid var(--mut);border-radius:6px;padding:4px"> €</label>
 <label><input type="checkbox" id="sf"> 🕵 Méconnus seulement</label><label><input type="checkbox" id="sg"> Montrer « rien trouvé »</label>
 <button class="xb" id="sa">🔔 Liste d'alertes</button><span>Jeux : <b id="sc" style="color:var(--fg)"></b></span></div><div id="sal"></div><div id="sl"></div>`;
 const BGp=()=>Math.max(10,Math.min(100,+$("bg").value||60))/100,all=xpool(1);
 const mx=r=>Math.max(1,Math.round(r.p*BGp())),qn=r=>shortTitle(r.t)+" "+cname(r.c);
 function draw(){const s=$("sm").value=="s",mn=+$("sn").value||0;
  const L=all.filter(r=>{if($("sf").checked&&r.fame!==0)return false;if(!$("sg").checked&&isN(r.uid))return false;
   if(s){const t=tierOf(r.p);return t&&(t.k=="A"||t.k=="S")&&r.n>=3}return r.p>=mn})
   .sort((a,b)=>(isF(b.uid)?1:0)-(isF(a.uid)?1:0)||b.p-a.p);
  $("sc").textContent=L.length;
  $("sl").innerHTML=L.length?L.map(r=>{const t=tierOf(r.p),m=mx(r);
   return `<div class="row${isN(r.uid)?" none":""}${isF(r.uid)?" fav":""}"><div class="tl2" style="background:${t?t.c:"#6b7080"};color:${t?ink(t.c):"#fff"}">${t?t.k:"·"}</div>
   <div class="inf2"><b>${isF(r.uid)?"⭐ ":""}${esc(r.t)}${r.fame===0?" 🕵":""}</b><div class="sub">${esc(cname(r.c))} · ${r.n} ann. eBay</div></div><div class="pr">${Math.round(r.p)} €</div>
   <div class="act"><a class="sb2" style="background:#ff6e14" href="${esc(lbcUrl(qn(r),m))}" target="_blank" rel="noopener">LBC ↗ ≤${m}€</a><a class="sb2" style="background:#09b1ba" href="${esc(vintedUrl(shortTitle(r.t),m))}" target="_blank" rel="noopener">Vinted ↗ ≤${m}€</a>
   <button class="no" data-a="n" data-u="${esc(r.uid)}">Rien trouvé</button><button class="ok" data-a="f" data-u="${esc(r.uid)}">${isF(r.uid)?"✔ Intéressant":"Intéressant"}</button></div></div>`}).join(""):'<div class="sub" style="padding:20px">Aucun jeu avec ces réglages.</div>'}
 $("sl").onclick=e=>{const b=e.target.closest("button[data-u]");if(!b)return;const u=b.dataset.u;
  if(b.dataset.a=="n"){if(isN(u))delete S2[u];else S2[u]={s:"n",d:Date.now()}}else{if(isF(u))delete S2[u];else S2[u]={s:"f",d:Date.now()}}
  jset("tikkot_sonde",S2);draw()};
 ["sm","sn","sf","sg"].forEach(i=>$(i).onchange=draw);
 $("sa").onclick=()=>{const a=$("sal");if(a.innerHTML){a.innerHTML="";return}
  let L=all.filter(r=>isF(r.uid)),src="tes jeux ⭐";
  if(!L.length){src="les 30 jeux méconnus A/S les plus chers (rien de ⭐ pour l'instant)";L=all.filter(r=>{const t=tierOf(r.p);return r.fame===0&&t&&(t.k=="A"||t.k=="S")&&r.n>=3}).sort((x,y)=>y.p-x.p).slice(0,30)}
  const lines=L.map(r=>qn(r)+" — max "+mx(r)+" €");
  a.innerHTML=`<div class="xg" style="max-width:none;text-align:left"><b>🔔 Alertes à créer sur LBC et Vinted</b> (${lines.length}, d'après ${esc(src)})<div class="sub">Sur chaque site : fais la recherche, catégorie jeux vidéo, prix max, puis « Créer une alerte ».</div><pre>${esc(lines.join("\n"))||"Rien à lister."}</pre><button class="nx" id="scp">📋 Copier</button></div>`;
  $("scp").onclick=()=>navigator.clipboard.writeText(lines.join("\n")).then(()=>{$("scp").textContent="✔ Copié"})};
 draw()}

/* ---------- LBC : on ajoute le nom de la console à la recherche des fiches ---------- */
new MutationObserver(()=>{document.querySelectorAll("#feed a.sb.lbc:not([data-x])").forEach(a=>{a.dataset.x=1;
 const s=a.closest(".card"),g=s&&findGame(s.dataset.id);if(!g)return;
 try{const u=new URL(a.href);u.searchParams.set("text",(u.searchParams.get("text")||"")+" "+cname(g.c));a.href=u.toString()}catch(e){}})}).observe($("feed"),{childList:true,subtree:true});
})();
