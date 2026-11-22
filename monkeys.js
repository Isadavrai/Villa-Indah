/* Feed the header macaque: all twenty residents appear, with one cursor follower. */
function createMonkeyTroupe({root,toggle,label,reduced,translate}){
 const base='assets/monkeys/generated/',banana=document.getElementById('monkey-banana'),status=document.getElementById('monkey-instruction');
 const perches=[
  ['P02','#pool-perch',78,'sit',68],['P03','#lounge-perch',12,'sit',70],['P04','#garden-perch',86,'sit',66],
  ['P05','#cinema-perch',83,'sit',64],['P06','#lounge-perch',80,'hang',84],['P07','#garden-perch',18,'hang',80],
  ['P08','gallery:0',68,'sit',72],['P09','gallery:1',22,'dangle',66],['P10','#restaurant-perch',14,'sit',70],
  ['P11','#gallery-perch',84,'sit',64],['P12','#faq-expand-perch',56,'sit',62],['P13','#enquiry-form',72,'sit',70],
  ['P14','.direct-contact',93,'sit',66],['P15','#map-container',14,'sit',68],
  ['A1','gallery:2',84,'sit',68],['A2','.faq-contact',82,'hang',80],['A3','.contact-actions',78,'sit',62],
  ['A4','footer',36,'sit',70],['A5','#map-container',74,'sit',62]
 ];
 let enabled=false,selected=false,next=0,frame=0,last=0,runner=null,drag=null,ignoreClick=false;
 const residents=[],pointer={x:innerWidth*.5,y:innerHeight*.55,lastMove:null};
 const mobile=()=>matchMedia('(pointer:coarse)').matches||innerWidth<=700;
 const clip=id=>id.startsWith('A')?'assets/monkeys/new/'+id+(['A1','A2'].includes(id)?'.gif':'.webp'):base+id+'.webp',still=id=>(id.startsWith('A')?'assets/monkeys/new/':base)+id+'-still.png';
 function updateResident(r){const src=reduced.matches||!r.visible?still(r.id):clip(r.id);if(r.el.getAttribute('src')!==src)r.el.src=src}
 const observer=new IntersectionObserver(entries=>{for(const entry of entries){const r=residents.find(r=>r.el===entry.target);if(r){r.visible=entry.isIntersecting;updateResident(r)}}},{rootMargin:'100px'});
 function updateLabel(){
  toggle.setAttribute('aria-pressed',String(enabled));toggle.setAttribute('aria-label',translate(enabled?'monkeyOff':'monkeyOn'));
  label.textContent=translate('monkeyShortOff');label.hidden=!enabled;banana.hidden=enabled;document.getElementById('banana-gesture').hidden=enabled;document.body.classList.toggle('monkeys-active',enabled);
  banana.setAttribute('aria-label',translate('bananaLabel'));banana.title=translate('bananaLabel');banana.setAttribute('aria-pressed',String(selected));
  toggle.classList.toggle('banana-ready',selected);if(selected)status.textContent=translate('bananaReady');
 }
 function headerImage(){toggle.querySelector('img').src=reduced.matches?still('P01'):clip('P01')}
 function stopFrame(){cancelAnimationFrame(frame);frame=0;last=0}
 function runnerMode(){
  if(!runner)return;const anchored=mobile()||reduced.matches;runner.el.className='macaque '+(anchored?'anchored':'follower');runner.el.dataset.side='right';
  (anchored?document.querySelector('#lounge-perch'):root).append(runner.el);
  runnerMotion(false);
  runner.el.style.transform=anchored?'':`translate3d(${runner.x}px,${runner.y}px,0)`;
 }
 function runnerMotion(moving){if(!runner)return;const src=moving&&!mobile()&&!reduced.matches?'assets/monkeys/new/F1.webp':'assets/monkeys/new/F1-still.png';if(runner.el.getAttribute('src')!==src)runner.el.src=src;runner.el.dataset.motion=moving?'running':'idle'}
 function hostFor(selector){if(!selector.startsWith('gallery:'))return document.querySelector(selector);const groups=document.querySelectorAll('#photo-grid .gallery-group');return groups[Math.min(Number(selector.split(':')[1]),groups.length-1)]||document.querySelector('#gallery-perch')}
 function placeResident(r){const host=hostFor(r.selector);if(!host)return;host.classList.add('monkey-perch-host');const single=r.selector.startsWith('gallery:')&&document.querySelectorAll('#photo-grid .gallery-group').length===1;r.el.style.setProperty('--perch-x',(single?([14,50,86][Number(r.selector.split(':')[1])]):r.position)+'%');host.append(r.el)}
 function spawnRunner(){const el=document.createElement('img');el.alt='';el.draggable=false;el.dataset.monkey='F1';runner={el,x:24,y:120,vx:0,vy:0,facing:1};runnerMode()}
 function addResident(){
  if(!enabled||next>=perches.length)return;
  const [id,selector,position,pose,size]=perches[next++],host=hostFor(selector);
  if(host){const el=document.createElement('img');el.className='macaque anchored resident';el.alt='';el.draggable=false;el.dataset.monkey=id;el.dataset.pose=pose||'sit';el.style.setProperty('--perch-x',position+'%');el.style.setProperty('--perch-size',size+'px');
   el.width=192;el.height=192;const r={id,el,selector,position,visible:false};residents.push(r);updateResident(r);placeResident(r);observer.observe(el)}
 }
 function enable(){if(enabled)return;enabled=true;selected=false;next=0;pointer.lastMove=null;status.textContent=translate('bananaFed');root.hidden=false;spawnRunner();updateLabel();while(next<perches.length)addResident();if(!mobile()&&!reduced.matches&&!document.hidden)frame=requestAnimationFrame(tick)}
 function disable(){enabled=false;selected=false;next=0;stopFrame();runner?.el.remove();runner=null;for(const r of residents){observer.unobserve(r.el);r.el.remove()}residents.length=0;root.replaceChildren();root.hidden=true;updateLabel();status.textContent=''}
 function tick(time){frame=0;if(!enabled||mobile()||reduced.matches||document.hidden||!runner)return;
  if(pointer.lastMove===null){runner.vx=0;runner.vy=0;runnerMotion(false);last=0;return}
  const dt=Math.min(.035,(time-(last||time))/1000);last=time;
  const tx=Math.max(6,Math.min(innerWidth-82,pointer.x-95)),ty=Math.max(90,Math.min(innerHeight-86,pointer.y+25));
  const dx=tx-runner.x,dy=ty-runner.y,dist=Math.hypot(dx,dy),speed=Math.min(245,dist*3),alpha=1-Math.exp(-6*dt);
  if(dist<=2){runner.x=tx;runner.y=ty;runner.vx=0;runner.vy=0;runnerMotion(false);last=0;runner.el.style.transform=`translate3d(${tx}px,${ty}px,0) scaleX(${runner.facing})`;return}
  runnerMotion(true);
  runner.vx+=(dx/dist*speed-runner.vx)*alpha;runner.vy+=(dy/dist*speed-runner.vy)*alpha;
  runner.x=Math.max(6,Math.min(innerWidth-82,runner.x+runner.vx*dt));runner.y=Math.max(90,Math.min(innerHeight-86,runner.y+runner.vy*dt));
  if(Math.abs(runner.vx)>12)runner.facing=runner.vx<0?-1:1;
  runner.el.style.transform=`translate3d(${runner.x}px,${runner.y}px,0) scaleX(${runner.facing})`;frame=requestAnimationFrame(tick);
 }
 function overMonkey(x,y){const b=toggle.getBoundingClientRect();return x>=b.left&&x<=b.right&&y>=b.top&&y<=b.bottom}
 function clearDrag(){banana.style.transform='';banana.classList.remove('dragging');document.getElementById('banana-gesture').classList.remove('dragging');toggle.classList.remove('drop-target');drag=null}
 banana.addEventListener('pointerdown',e=>{if(enabled||e.button!==0)return;drag={id:e.pointerId,x:e.clientX,y:e.clientY,moved:false};banana.setPointerCapture(e.pointerId)});
 banana.addEventListener('pointermove',e=>{if(!drag||e.pointerId!==drag.id)return;const dx=e.clientX-drag.x,dy=e.clientY-drag.y;if(Math.hypot(dx,dy)>5)drag.moved=true;if(drag.moved){banana.classList.add('dragging');document.getElementById('banana-gesture').classList.add('dragging');banana.style.transform=`translate(${dx}px,${dy}px)`;toggle.classList.toggle('drop-target',overMonkey(e.clientX,e.clientY))}});
 banana.addEventListener('pointerup',e=>{if(!drag||e.pointerId!==drag.id)return;const moved=drag.moved,drop=moved&&overMonkey(e.clientX,e.clientY);ignoreClick=moved;if(moved)setTimeout(()=>ignoreClick=false,0);clearDrag();if(drop)enable()});
 banana.addEventListener('pointercancel',clearDrag);banana.addEventListener('lostpointercapture',()=>{if(drag)clearDrag()});
 banana.addEventListener('click',()=>{if(ignoreClick){ignoreClick=false;return}selected=!selected;status.textContent=translate(selected?'bananaReady':'bananaDrop');updateLabel()});
 toggle.addEventListener('click',()=>{if(enabled)disable();else if(selected)enable();else status.textContent=translate('bananaDrop')});
 addEventListener('pointermove',e=>{if(enabled&&!mobile()&&(e.clientX!==pointer.x||e.clientY!==pointer.y)){pointer.x=e.clientX;pointer.y=e.clientY;pointer.lastMove=performance.now();if(!frame)frame=requestAnimationFrame(tick)}},{passive:true});
 addEventListener('resize',()=>{if(!enabled)return;stopFrame();runnerMode();if(!mobile()&&!reduced.matches&&!document.hidden)frame=requestAnimationFrame(tick)});
 document.addEventListener('visibilitychange',()=>{stopFrame();runnerMotion(false);if(enabled&&!document.hidden&&!mobile()&&!reduced.matches)frame=requestAnimationFrame(tick)});
 reduced.addEventListener('change',()=>{headerImage();for(const r of residents)updateResident(r);stopFrame();runnerMode();if(enabled&&!mobile()&&!reduced.matches&&!document.hidden)frame=requestAnimationFrame(tick)});
 const galleryChanges=new MutationObserver(()=>{if(enabled)residents.filter(r=>r.selector.startsWith('gallery:')).forEach(placeResident)});galleryChanges.observe(document.getElementById('photo-grid'),{childList:true});
 toggle.querySelector('img').dataset.monkey='P01';toggle.setAttribute('aria-describedby','monkey-instruction');banana.setAttribute('aria-describedby','monkey-instruction');headerImage();updateLabel();return {updateLabel};
}
