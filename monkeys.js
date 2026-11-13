/* Ten owner-supplied animations: one accessible trigger, five followers, four more perches. */
function createMonkeyTroupe({root,toggle,label,reduced,translate}){
 const base='assets/monkeys/new/';
 const followers=['F1','F2','F3','F4','F5'];
 const anchors=['A2','A3','A4','A5'];
 const sections=['.intro','.story','.living','.resort','.editorial-gallery'];
 const perchSections=['.story','.living','.resort','.editorial-gallery'];
 const queue=['F1','A2','F2','A3','F3','A4','F4','A5','F5'];
 let timer=0,next=0;const history=[];
 const targets=[];let enabled=false,frame=0,last=0,pointer={x:innerWidth*.5,y:innerHeight*.55};
 const mobile=()=>matchMedia('(pointer:coarse)').matches || innerWidth<=700;
 const asset=id=>base+id+(id==='A1'||id==='A2'?'.gif':'.webp');
 const still=id=>base+id+'-still.png';
 function updateLabel(){toggle.setAttribute('aria-pressed',String(enabled));toggle.setAttribute('aria-label',translate(enabled?'monkeyOff':'monkeyOn'));label.textContent=translate('monkeyShortOff');label.hidden=!enabled;}
 function setTrigger(){toggle.querySelector('img').src=reduced.matches?still('A1'):asset('A1');}
 function spawn(id,holder,kind,index){
  const el=document.createElement('img');el.className='macaque '+kind;el.alt='';el.draggable=false;el.decoding='async';el.dataset.monkey=id;el.src=reduced.matches?still(id):asset(id);el.style.setProperty('--index',index);holder.append(el);
  const size=mobile()?64:76;
  targets.push({id,el,kind,index,x:index%2?innerWidth-size-8:8,y:Math.min(innerHeight-size-90,120+index*55),vx:0,vy:0,delay:80+index*120,speed:120+index*24});
 }
 function stop(){cancelAnimationFrame(frame);frame=0;last=0;}
 function disable(){enabled=false;clearInterval(timer);timer=0;next=0;history.length=0;stop();root.replaceChildren();root.hidden=true;document.querySelectorAll('.macaque.anchored').forEach(el=>el.remove());targets.length=0;updateLabel();}
 function addNext(){
  if(!enabled||next>=queue.length)return;
  const id=queue[next++],fi=followers.indexOf(id),ai=anchors.indexOf(id);
  const anchored=fi<0||mobile();
  spawn(id,anchored?document.querySelector(fi<0?perchSections[ai]:sections[fi]):root,anchored?'anchored':'follower',fi<0?ai+5:fi);
  const r=targets.at(-1);if(!anchored)r.el.style.transform=`translate3d(${r.x}px,${r.y}px,0)`;
  if(next===queue.length){clearInterval(timer);timer=0;}
 }
 function enable(){enabled=true;root.hidden=false;updateLabel();timer=setInterval(addNext,7000);if(!mobile()&&!reduced.matches&&!document.hidden)frame=requestAnimationFrame(tick);}
 function tick(time){frame=0;if(!enabled||mobile()||reduced.matches||document.hidden)return;
  const dt=Math.min(.035,(time-(last||time))/1000);last=time;
  history.push({time,...pointer});while(history.length>1&&history[1].time<time-1000)history.shift();
  for(const r of targets){if(r.kind!=='follower')continue;
   const delayed=history.findLast(p=>p.time<=time-r.delay)||history[0]||pointer;
   const phase=time/1000*.65+r.index*2.4,rad=105+r.index*24;
   let tx=delayed.x+Math.cos(r.index*2.4)*rad+Math.sin(phase)*11-38;
   let ty=delayed.y+Math.sin(r.index*2.4)*rad*.65+Math.cos(phase*.7)*8-38;
   tx=Math.max(6,Math.min(innerWidth-82,tx));ty=Math.max(88,Math.min(innerHeight-86,ty));
   let dx=tx-r.x,dy=ty-r.y;
   for(const q of targets){if(q===r||q.kind!=='follower')continue;const sx=r.x-q.x,sy=r.y-q.y,d=Math.hypot(sx,sy);if(d>1&&d<70){dx+=sx/d*(70-d)*1.6;dy+=sy/d*(70-d)*1.6;}}
   const dist=Math.hypot(dx,dy),speed=Math.min(r.speed,dist*2.2),alpha=1-Math.exp(-4*dt);
   r.vx+=((dist>1?dx/dist*speed:0)-r.vx)*alpha;r.vy+=((dist>1?dy/dist*speed:0)-r.vy)*alpha;
   r.x=Math.max(6,Math.min(innerWidth-82,r.x+r.vx*dt));r.y=Math.max(88,Math.min(innerHeight-86,r.y+r.vy*dt));
   r.el.style.transform=`translate3d(${r.x}px,${r.y}px,0) scaleX(${r.vx < -12?-1:1})`;
  }
  frame=requestAnimationFrame(tick);
 }
 toggle.addEventListener('click',()=>enabled?disable():enable());
 addEventListener('pointermove',e=>{if(!enabled||mobile())return;pointer={x:e.clientX,y:e.clientY};},{passive:true});
 addEventListener('resize',()=>{if(!enabled)return;for(const r of targets){const fi=followers.indexOf(r.id);if(fi<0)continue;r.kind=mobile()?'anchored':'follower';r.el.className='macaque '+r.kind;(mobile()?document.querySelector(sections[fi]):root).append(r.el);r.el.style.transform=mobile()?'':`translate3d(${r.x}px,${r.y}px,0)`;}stop();if(!mobile()&&!reduced.matches)frame=requestAnimationFrame(tick);});
 document.addEventListener('visibilitychange',()=>{if(document.hidden)stop();else if(enabled&&!mobile()&&!reduced.matches)frame=requestAnimationFrame(tick);});
 reduced.addEventListener('change',()=>{setTrigger();if(enabled)targets.forEach(r=>{r.el.src=reduced.matches?still(r.id):asset(r.id);});stop();if(enabled&&!mobile()&&!reduced.matches)frame=requestAnimationFrame(tick);});
 setTrigger();updateLabel();return {updateLabel};
}
