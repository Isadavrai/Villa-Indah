/* One runner and fifteen individual generated residents. Feed the header macaque to start. */
function createMonkeyTroupe({root,toggle,label,reduced,translate}){
 const base='assets/monkeys/generated/',banana=document.getElementById('monkey-banana'),status=document.getElementById('monkey-instruction');
 const perches=[
  ['P02','#pool-perch','right'],['P03','#lounge-perch','left'],['P04','#garden-perch','right'],
  ['P05','#pool-perch','left'],['P06','#lounge-perch','right','hang'],['P07','#garden-perch','left','hang'],
  ['P08','#gallery-perch','right'],['P09','#cinema-perch','right'],['P10','#beach-perch','left'],
  ['P11','#restaurant-perch','left'],['P12','#map-container','right'],['P13','#gallery-perch','left'],
  ['P14','#restaurant-perch','right'],['P15','#enquiry-form','right']
 ];
 let enabled=false,selected=false,timer=0,next=0,frame=0,last=0,runner=null,drag=null,ignoreClick=false;
 const residents=[],pointer={x:innerWidth*.5,y:innerHeight*.55};
 const mobile=()=>matchMedia('(pointer:coarse)').matches||innerWidth<=700;
 const clip=id=>base+id+'.webp',still=id=>base+id+'-still.png';
 function updateResident(r){const src=reduced.matches||!r.visible?still(r.id):clip(r.id);if(r.el.getAttribute('src')!==src)r.el.src=src}
 const observer=new IntersectionObserver(entries=>{for(const entry of entries){const r=residents.find(r=>r.el===entry.target);if(r){r.visible=entry.isIntersecting;updateResident(r)}}},{rootMargin:'100px'});
 function updateLabel(){
  toggle.setAttribute('aria-pressed',String(enabled));toggle.setAttribute('aria-label',translate(enabled?'monkeyOff':'monkeyOn'));
  label.textContent=translate('monkeyShortOff');label.hidden=!enabled;banana.hidden=enabled;
  banana.setAttribute('aria-label',translate('bananaLabel'));banana.setAttribute('aria-pressed',String(selected));
  toggle.classList.toggle('banana-ready',selected);if(selected)status.textContent=translate('bananaReady');
 }
 function headerImage(){toggle.querySelector('img').src=reduced.matches?still('P01'):clip('P01')}
 function stopFrame(){cancelAnimationFrame(frame);frame=0;last=0}
 function runnerMode(){
  if(!runner)return;const anchored=mobile()||reduced.matches;runner.el.className='macaque '+(anchored?'anchored':'follower');runner.el.dataset.side='right';
  (anchored?document.querySelector('#lounge-perch'):root).append(runner.el);
  runner.el.src=reduced.matches?'assets/monkeys/new/F1-still.png':'assets/monkeys/new/F1.webp';
  runner.el.style.transform=anchored?'':`translate3d(${runner.x}px,${runner.y}px,0)`;
 }
 function spawnRunner(){const el=document.createElement('img');el.alt='';el.draggable=false;el.dataset.monkey='F1';runner={el,x:24,y:120,vx:0,vy:0};runnerMode()}
 function addResident(){
  if(!enabled||next>=perches.length)return;
  const [id,selector,side,pose]=perches[next++],host=document.querySelector(selector);
  if(host){const el=document.createElement('img');el.className='macaque anchored resident';el.alt='';el.draggable=false;el.dataset.monkey=id;el.dataset.side=side;el.dataset.pose=pose||'sit';
   el.width=192;el.height=192;const r={id,el,visible:false};residents.push(r);updateResident(r);host.append(el);observer.observe(el)}
  if(next===perches.length){clearInterval(timer);timer=0}
 }
 function enable(){if(enabled)return;enabled=true;selected=false;next=0;status.textContent=translate('bananaFed');root.hidden=false;spawnRunner();updateLabel();timer=setInterval(addResident,7000);if(!mobile()&&!reduced.matches&&!document.hidden)frame=requestAnimationFrame(tick)}
 function disable(){enabled=false;selected=false;clearInterval(timer);timer=0;next=0;stopFrame();runner?.el.remove();runner=null;for(const r of residents){observer.unobserve(r.el);r.el.remove()}residents.length=0;root.replaceChildren();root.hidden=true;updateLabel();status.textContent=''}
 function tick(time){frame=0;if(!enabled||mobile()||reduced.matches||document.hidden||!runner)return;
  const dt=Math.min(.035,(time-(last||time))/1000);last=time;
  const tx=Math.max(6,Math.min(innerWidth-82,pointer.x-95)),ty=Math.max(90,Math.min(innerHeight-86,pointer.y+25));
  const dx=tx-runner.x,dy=ty-runner.y,dist=Math.hypot(dx,dy),speed=Math.min(245,dist*3),alpha=1-Math.exp(-6*dt);
  runner.vx+=((dist>2?dx/dist*speed:0)-runner.vx)*alpha;runner.vy+=((dist>2?dy/dist*speed:0)-runner.vy)*alpha;
  runner.x=Math.max(6,Math.min(innerWidth-82,runner.x+runner.vx*dt));runner.y=Math.max(90,Math.min(innerHeight-86,runner.y+runner.vy*dt));
  runner.el.style.transform=`translate3d(${runner.x}px,${runner.y}px,0) scaleX(${runner.vx< -12?-1:1})`;frame=requestAnimationFrame(tick);
 }
 function overMonkey(x,y){const b=toggle.getBoundingClientRect();return x>=b.left&&x<=b.right&&y>=b.top&&y<=b.bottom}
 function clearDrag(){banana.style.transform='';banana.classList.remove('dragging');toggle.classList.remove('drop-target');drag=null}
 banana.addEventListener('pointerdown',e=>{if(enabled||e.button!==0)return;drag={id:e.pointerId,x:e.clientX,y:e.clientY,moved:false};banana.setPointerCapture(e.pointerId)});
 banana.addEventListener('pointermove',e=>{if(!drag||e.pointerId!==drag.id)return;const dx=e.clientX-drag.x,dy=e.clientY-drag.y;if(Math.hypot(dx,dy)>5)drag.moved=true;if(drag.moved){banana.classList.add('dragging');banana.style.transform=`translate(${dx}px,${dy}px)`;toggle.classList.toggle('drop-target',overMonkey(e.clientX,e.clientY))}});
 banana.addEventListener('pointerup',e=>{if(!drag||e.pointerId!==drag.id)return;const moved=drag.moved,drop=moved&&overMonkey(e.clientX,e.clientY);ignoreClick=moved;if(moved)setTimeout(()=>ignoreClick=false,0);clearDrag();if(drop)enable()});
 banana.addEventListener('pointercancel',clearDrag);banana.addEventListener('lostpointercapture',()=>{if(drag)clearDrag()});
 banana.addEventListener('click',()=>{if(ignoreClick){ignoreClick=false;return}selected=!selected;status.textContent=translate(selected?'bananaReady':'bananaDrop');updateLabel()});
 toggle.addEventListener('click',()=>{if(enabled)disable();else if(selected)enable();else status.textContent=translate('bananaDrop')});
 addEventListener('pointermove',e=>{if(enabled&&!mobile()){pointer.x=e.clientX;pointer.y=e.clientY}},{passive:true});
 addEventListener('resize',()=>{if(!enabled)return;stopFrame();runnerMode();if(!mobile()&&!reduced.matches&&!document.hidden)frame=requestAnimationFrame(tick)});
 document.addEventListener('visibilitychange',()=>{stopFrame();if(enabled&&!document.hidden&&!mobile()&&!reduced.matches)frame=requestAnimationFrame(tick)});
 reduced.addEventListener('change',()=>{headerImage();for(const r of residents)updateResident(r);stopFrame();runnerMode();if(enabled&&!mobile()&&!reduced.matches&&!document.hidden)frame=requestAnimationFrame(tick)});
 toggle.querySelector('img').dataset.monkey='P01';toggle.setAttribute('aria-describedby','monkey-instruction');banana.setAttribute('aria-describedby','monkey-instruction');headerImage();updateLabel();return {updateLabel};
}
