// locale.js - sostituto di Firebase per la modalità LOCALE (stesse funzioni usate dalle pagine, ma parla col server locale)
const CID=Math.random().toString(36).slice(2),LIS=new Set(),Q=[],PEND={};let busy=0;
const idOf=p=>p.slice(p.lastIndexOf('/')+1),mkd=(p,d,pend)=>({id:idOf(p),ref:{path:p,id:idOf(p),_t:'doc'},data:()=>d,exists:()=>d!=null,metadata:{fromCache:false,hasPendingWrites:!!pend}});
async function flush(){if(busy)return;busy=1;while(Q.length){const[u,b,ok,ko]=Q[0];try{const r=await fetch(u,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({...b,c:CID})});if(r.status>=500)throw 0;Q.shift();r.ok?ok():ko(new Error('http '+r.status))}catch(e){await new Promise(r=>setTimeout(r,2000))}}busy=0}
const post=(u,b)=>new Promise((ok,ko)=>{Q.push([u,b,ok,ko]);flush()});
function emit(L,ch,pend){if(L.col){const ds=[];ch.forEach(c=>{const o=L.m.get(c.id),t=c.d==null?'removed':o===undefined?'added':'modified';if(t=='removed'&&o===undefined)return;if(t=='modified'&&!pend&&JSON.stringify(o)==JSON.stringify(c.d))return;ds.push({type:t,doc:mkd(L.p+'/'+c.id,c.d==null?o:c.d,pend)});c.d==null?L.m.delete(c.id):L.m.set(c.id,c.d)});
  if(!ds.length&&L.sent)return;L.sent=1;const docs=[...L.m].map(([i,d])=>mkd(L.p+'/'+i,d,pend));L.cb({docs,size:docs.length,empty:!docs.length,docChanges:()=>ds,forEach:f=>docs.forEach(f),metadata:{fromCache:false,hasPendingWrites:!!pend}})}
 else{L.last=ch[0].d;L.sent=1;L.cb(mkd(L.p,L.last,pend))}}
const track=(p,merge,pr)=>{if(!merge){PEND[p]=(PEND[p]||0)+1;pr.then(()=>PEND[p]--,()=>PEND[p]--)}return pr};
function local(p,d,merge){LIS.forEach(L=>{const id=idOf(p);if(L.col&&p.slice(0,p.lastIndexOf('/'))==L.p){const o=L.m.get(id);emit(L,[{id,d:d==null?null:merge&&o?{...o,...d}:d}],1)}else if(!L.col&&L.p==p)emit(L,[{d:d==null?null:merge&&L.last?{...L.last,...d}:d}],1)})}
export const initializeApp=()=>({}),getAuth=()=>({currentUser:{uid:'locale'},authStateReady:()=>Promise.resolve()}),signInAnonymously=a=>Promise.resolve({user:a.currentUser}),
 initializeFirestore=()=>({}),getFirestore=()=>({}),persistentLocalCache=()=>({}),
 doc=(db,...s)=>({path:s.join('/'),id:s[s.length-1],_t:'doc'}),collection=(db,...s)=>({path:s.join('/'),id:s[s.length-1],_t:'col'}),
 setDoc=(r,d,o)=>{const merge=!!(o&&o.merge);local(r.path,d,merge);return track(r.path,merge,post('/api/set',{p:r.path,d,merge}))},
 deleteDoc=r=>{local(r.path,null);return track(r.path,0,post('/api/del',{p:r.path}))},
 getDocsFromServer=async r=>{const a=await fetch('/api/get?p='+encodeURIComponent(r.path)).then(x=>x.json()),docs=a.map(x=>mkd(r.path+'/'+x.id,x.d));return{docs,size:docs.length,empty:!docs.length,forEach:f=>docs.forEach(f)}},
 onSnapshot=(r,cb,err)=>{const L={p:r.path,col:r._t=='col',cb,m:new Map(),sent:0,last:undefined};LIS.add(L);if(!PATHS.has(L.p))PATHS.set(L.p,new Set());PATHS.get(L.p).add(L);reopen();
  return()=>{LIS.delete(L);const s=PATHS.get(L.p);s.delete(L);if(!s.size)PATHS.delete(L.p);reopen()}};
// una sola connessione in tempo reale per pagina, qualunque sia il numero di ascolti
const PATHS=new Map();let es=null,tm=0;
function reopen(){clearTimeout(tm);tm=setTimeout(()=>{if(es){es.close();es=null}if(!PATHS.size)return;es=new EventSource('/api/watch?'+[...PATHS.keys()].map(p=>'p='+encodeURIComponent(p)).join('&'));es.onmessage=e=>{const m=JSON.parse(e.data);(PATHS.get(m.w)||[]).forEach(L=>handle(L,m))}},0)}
function handle(L,m){if(m.c&&m.c==CID){const p=m.t=='ch'?L.p+'/'+m.id:m.p,cur=m.t=='ch'?L.m.get(m.id):L.last;if(JSON.stringify(cur??null)==JSON.stringify(m.d??null)||PEND[p]>0)return}
 if(m.t=='init'){if(L.col){const ids=new Set(m.docs.map(x=>x.id));emit(L,[...m.docs.map(x=>({id:x.id,d:x.d})),...[...L.m.keys()].filter(i=>!ids.has(i)).map(i=>({id:i,d:null}))])}else if(!L.sent||JSON.stringify(L.last??null)!=JSON.stringify(m.d??null))emit(L,[{d:m.d}])}
 else if(L.col&&m.t=='ch')emit(L,[{id:m.id,d:m.d}]);else if(!L.col&&m.t=='doc')emit(L,[{d:m.d}])}
