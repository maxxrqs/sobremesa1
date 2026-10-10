/* Habla – voix neuronale du traducteur (Piper int8 + onnxruntime-web) */
var BASE=self.location.href.replace(/[^\/]*(\?.*)?$/,'');
var V='?v=3';
var NP={"es":3,"ca":2,"eu":2,"fr":2,"en":2,"it":2,"de":2,"pt":2};
var NPW=1;
var MODEL={es:'es',ca:'ca',va:'ca',gl:'ca',eu:'eu',fr:'fr',en:'en',it:'it',de:'de',pt:'pt'};
var EV={es:'es',ca:'ca',va:'ca-va',eu:'eu',fr:'fr',en:'en-us',it:'it',de:'de',pt:'pt'};
var IDM=null,PH=null,ORTR=null,SESS={};
function post(o,t){self.postMessage(o,t||[])}
async function gunzip(u8){
  var ds=new DecompressionStream('gzip'),w=ds.writable.getWriter();w.write(u8);w.close();
  return new Uint8Array(await new Response(ds.readable).arrayBuffer());
}
async function fetchParts(pre,n,k){
  var parts=[],tot=0;
  for(var i=0;i<n;i++){if(k)post({t:'prog',k:k,p:i/n*0.9});var b=await fetchBuf(BASE+pre+'.'+i+'.wav'+V);parts.push(b);tot+=b.length}
  var all=new Uint8Array(tot),o=0;parts.forEach(function(b){all.set(b,o);o+=b.length});
  return gunzip(all);
}
function ldOrt(){
  if(ORTR)return ORTR;
  ORTR=(async function(){
    importScripts(BASE+'ort.min.js'+V);
    ort.env.wasm.numThreads=1;ort.env.wasm.proxy=false;ort.env.wasm.simd=true;var wu=BASE+'ortw.wasm'+V;ort.env.wasm.wasmPaths={'ort-wasm-simd.wasm':wu,'ort-wasm.wasm':wu,'ort-wasm-simd-threaded.wasm':wu,'ort-wasm-threaded.wasm':wu};
    return ort;
  })();
  ORTR.catch(function(){ORTR=null});
  return ORTR;
}
function ldPh(){
  if(PH)return PH;
  importScripts(BASE+'phonemize.js'+V);
  var cur=null;
  PH=createPiperPhonemize({print:function(l){if(cur)cur.push(l)},printErr:function(){},
    locateFile:function(f){return BASE+(f.indexOf('.wasm')>0?'phonemize.wasm':f)+V}}).then(function(m){m._cur=function(a){cur=a};return m});
  return PH;
}
async function fetchBuf(u){var r=await fetch(u);if(!r.ok)throw new Error('HTTP '+r.status+' '+u);return new Uint8Array(await r.arrayBuffer())}
async function ldModel(k){
  if(SESS[k])return SESS[k];
  SESS[k]=(async function(){
    await ldOrt();
    if(!IDM)IDM=await (await fetch(BASE+'idm.json'+V)).json();
    var all=await fetchParts('m-'+k,NP[k],k);
    post({t:'prog',k:k,p:1});
    return ort.InferenceSession.create(all.buffer,{executionProviders:['wasm'],graphOptimizationLevel:'all'});
  })();
  SESS[k].catch(function(){delete SESS[k]});
  return SESS[k];
}
/* ---- G2P galicien (port de glg.py) ---- */
var GV='aeiouáéíóúüï';
function inS(ch,set){return ch!==''&&set.indexOf(ch)>=0}
function glWord(w){
  w=w.normalize('NFC').toLowerCase();
  var toks=[],i=0,n=w.length;
  function nx(k){return k<n?w[k]:''}
  while(i<n){
    var c=w[i],two=w.substr(i,2);
    if(two==='ch'){toks.push(['C','tʃ']);i+=2;continue}
    if(two==='ll'){toks.push(['C','ʎ']);i+=2;continue}
    if(two==='nh'){toks.push(['C','ŋ']);i+=2;continue}
    if(two==='rr'){toks.push(['C','r']);i+=2;continue}
    if(two==='qu'&&inS(nx(i+2),'eiéí')){toks.push(['C','k']);i+=2;continue}
    if(two==='gu'&&inS(nx(i+2),'eiéí')){toks.push(['C','g']);i+=2;continue}
    if(c==='ñ')toks.push(['C','ɲ']);
    else if(c==='x'||c==='j')toks.push(['C','ʃ']);
    else if(c==='z'||c==='ç')toks.push(['C','s']);
    else if(c==='c')toks.push(['C',inS(nx(i+1),'eiéí')?'s':'k']);
    else if(c==='g')toks.push(['C',inS(nx(i+1),'eiéí')?'ʃ':'g']);
    else if(c==='h'){}
    else if(c==='v')toks.push(['C','b']);
    else if(c==='y')toks.push(['C','ʝ']);
    else if(c==='r'){var pv=toks.length?toks[toks.length-1][1]:'';toks.push(['C',(i===0||pv==='n'||pv==='l'||pv==='s')?'r':'ɾ'])}
    else if(c==='s')toks.push(['C','s']);
    else if(c==='q')toks.push(['C','k']);
    else if(c==='w')toks.push(['C','u']);
    else if('bdfklmnpt'.indexOf(c)>=0)toks.push(['C',c]);
    else if(GV.indexOf(c)>=0)toks.push(['V',c]);
    else toks.push(['P',c]);
    i++;
  }
  for(var k=0;k<toks.length;k++){
    var t=toks[k][0],ch=toks[k][1];
    if(t==='V'){
      var weak=ch==='i'||ch==='u';
      var p=k>0?toks[k-1]:['X',''],q=k+1<toks.length?toks[k+1]:['X',''];
      if(weak&&(q[0]==='V'||p[0]==='V'))toks[k]=['G',ch];
    }
  }
  for(k=0;k<toks.length-1;k++)if(toks[k][0]==='G'&&toks[k+1][0]==='G')toks[k+1]=['V',toks[k+1][1]];
  for(k=0;k<toks.length;k++)if(toks[k][0]==='G'){
    var has=false;for(var j=Math.max(0,k-1);j<Math.min(toks.length,k+2);j++)if(toks[j][0]==='V')has=true;
    if(!has)toks[k]=['V',toks[k][1]];
  }
  var nuc=[];toks.forEach(function(x,k){if(x[0]==='V')nuc.push(k)});
  var acc=nuc.filter(function(k){return 'áéíóú'.indexOf(toks[k][1])>=0}),st=null;
  if(acc.length)st=acc[0];
  else if(!nuc.length)st=null;
  else if(nuc.length===1)st=nuc[0];
  else{var last=toks[toks.length-1],endv=last[0]==='V'||last[0]==='G'||last[1]==='n'||last[1]==='s'||last[1]==='ŋ';st=endv?nuc[nuc.length-2]:nuc[nuc.length-1]}
  var base={'á':'a','é':'e','í':'i','ó':'o','ú':'u','ü':'u','ï':'i'},res='';
  toks.forEach(function(x,k){
    var t=x[0],c=x[1];
    if(t==='V'||t==='G'){
      var v=base[c]||c;
      if(t==='G')v=v==='i'?'j':'w';else if(k===st)res+='ˈ';
      res+=v;
    }else{if(t==='C'&&c==='n'&&k===toks.length-1)c='ŋ';res+=c}
  });
  return res;
}
function glG2P(text){
  var parts=text.match(/[A-Za-zÀ-ÿñÑçÇ]+|\s+|[^\sA-Za-zÀ-ÿ]/g)||[];
  return parts.map(function(p){return /\p{L}/u.test(p[0])?glWord(p):(/\s/.test(p[0])?' ':p)}).join('');
}
/* ---- synthèse ---- */
var MAPC={'g':'\u0261'};
function toIds(phon,map){
  var ids=[map['^']];
  for(var ch of phon.normalize('NFD')){if(map[ch]===undefined&&MAPC[ch])ch=MAPC[ch];if(map[ch]!==undefined){ids.push(map[ch]);ids.push(0)}}
  ids.push(map['$']);return ids;
}
function splitS(t){
  var out=[],cur='';
  t.replace(/\s+/g,' ').trim().split(/(?<=[.!?…;:])\s+/).forEach(function(s){
    if(!s)return;
    if(s.length>200){var p=s.split(/(?<=,)\s+/);p.forEach(function(x){if(cur&&(cur+x).length>160){out.push(cur);cur=''}cur=cur?cur+' '+x:x});if(cur){out.push(cur);cur=''}}
    else out.push(s);
  });
  return out;
}
async function phSent(lang,s){
  if(lang==='gl')return [glG2P(s)];
  var m=await ldPh(),acc=[];m._cur(acc);
  m.callMain(['-l',EV[lang],'--input',JSON.stringify([{text:s}]),'--espeak_data','/espeak-ng-data']);m._cur(null);
  var res=[];
  acc.forEach(function(l){l=l.trim();if(l[0]==='{'){try{var o=JSON.parse(l);res.push(o.phonemes.join(''))}catch(e){}}});
  return res;
}
async function synth(id,lang,text,speed){
  var k=MODEL[lang],sess=await ldModel(k),cfg=IDM[k],names=sess.inputNames;
  post({t:'state',id:id,s:'syn'});
  var sents=splitS(text),chunks=[],total=0;
  for(var si=0;si<sents.length;si++){
    var phs=await phSent(lang,sents[si]);
    for(var pi=0;pi<phs.length;pi++){
      var ids=toIds(phs[pi],cfg.ids);if(ids.length<4)continue;
      var f={input:new ort.Tensor('int64',BigInt64Array.from(ids.map(BigInt)),[1,ids.length]),
        input_lengths:new ort.Tensor('int64',BigInt64Array.from([BigInt(ids.length)]),[1]),
        scales:new ort.Tensor('float32',Float32Array.from([cfg.ns,speed||1.05,cfg.nw]),[3])};
      if(names.indexOf('sid')>=0)f.sid=new ort.Tensor('int64',BigInt64Array.from([0n]),[1]);
      var r=await sess.run(f),o=r[sess.outputNames[0]].data;
      chunks.push(o);total+=o.length;
      var gap=new Float32Array(Math.round(cfg.sr*0.22));chunks.push(gap);total+=gap.length;
    }
    post({t:'part',id:id,p:(si+1)/sents.length});
  }
  var out=new Float32Array(total),o=0;chunks.forEach(function(c){out.set(c,o);o+=c.length});
  return {pcm:out,sr:cfg.sr};
}
var Q=Promise.resolve();
self.onmessage=function(e){
  var d=e.data;
  if(d.t==='warm'){Q=Q.then(function(){return ldModel(MODEL[d.lang])}).then(function(){post({t:'warm',lang:d.lang})},function(er){post({t:'err',id:0,m:String(er)})});return}
  if(d.t==='say'){Q=Q.then(async function(){
    try{var r=await synth(d.id,d.lang,d.text,d.speed);post({t:'pcm',id:d.id,pcm:r.pcm,sr:r.sr},[r.pcm.buffer])}
    catch(er){post({t:'err',id:d.id,m:String(er&&er.message||er)})}
  })}
};
