/* Ten owner-supplied animations: one accessible trigger, five followers, four more perches. */
function createMonkeyTroupe({root,toggle,label,reduced,translate}){
 const base='assets/monkeys/new/';
 const followers=['F1','F2','F3','F4','F5'];
 const anchors=['A2','A3','A4','A5'];
 const sections=['.intro','.story','.living','.resort','.editorial-gallery'];
 const perchSections=['.story','.living','.resort','.editorial-gallery'];
 const targets=[];let enabled=false,frame=0,last=0,zones=[],zonesAt=0,pointer={x:innerWidth*.5,y:innerHeight*.55};
 const mobile=()=>matchMedia('(pointer:coarse)').matches || innerWidth<=700;
 const asset=id=>base+id+(id==='A1'||id==='A2'?'.gif':'.webp');
 const still=id=>base+id+'-still.png';
 function updateLabel(){toggle.setAttribute('aria-pressed',String(enabled));toggle.setAttribute('aria-label',translate(enabled?'monkeyOff':'monkeyOn'));label.textContent=translate('monkeyShortOff');label.hidden=!enabled;}
 function setTrigger(){toggle.querySelector('img').src=reduced.matches?still('A1'):asset('A1');}
 function spawn(id,holder,kind,index){
  const el=document.createElement('img');el.className='macaque '+kind;el.alt='';el.draggable=false;el.decoding='async';el.dataset.monkey=id;el.src=reduced.matches?still(id):asset(id);el.style.setProperty('--index',index);holder.append(el);
  const size=mobile()?64:76;
  targets.push({id,el,kind,index,x:index%2?innerWidth-size-8:8,y:Math.min(innerHeight-size-90,120+index*55),vx:0,vy:0,delay:index*24,speed:120+index*24});
 }
 function stop(){cancelAnimationFrame(frame);frame=0;last=0;}
 function disable(){enabled=false;stop();root.replaceChildren();root.hidden=true;document.querySelectorAll('.macaque.anchored').forEach(el=>el.remove());targets.length=0;updateLabel();}
 function enable(){enabled=true;root.hidden=false;
  followers.forEach((id,i)=>spawn(id,mobile()?document.querySelector(sections[i]):root,mobile()?'anchored':'follower',i));
  anchors.forEach((id,i)=>spawn(id,document.querySelector(perchSections[i]),'anchored',i+5));
  updateLabel();if(!mobile()&&!reduced.matches&&!document.hidden)frame=requestAnimationFrame(tick);
 }
 function tick(time){frame=0;if(!enabled||mobile()||reduced.matches||document.hidden)return;
  const dt=Math.min(.035,(time-(last||time))/1000);last=time;
  if(time-zonesAt>250){zonesAt=time;zones=[...document.querySelectorAll('.hero h1,.hero .private,.hero-sub,.hero-cta,.intro h2,.intro-copy,.facts,.story-heading,.story-text,.section-heading,.rooms,.resort h2,.resort-copy,.stay-scopes,.experiences,.gallery-filters,.gallery,.faq details,.contact form,.map-section')].map(el=>el.getBoundingClientRect()).filter(b=>b.bottom>70&&b.top<innerHeight&&b.width>0);}
  for(const r of targets){if(r.kind!=='follower')continue;
   const phase=time/1000*.65+r.index*2.4,rad=105+r.index*24;
   let tx=pointer.x+Math.cos(r.index*2.4)*rad+Math.sin(phase)*11-38;
   let ty=pointer.y+Math.sin(r.index*2.4)*rad*.65+Math.cos(phase*.7)*8-38;
   for(const z of zones){const pad=48;if(tx+76>z.left-pad&&tx<z.right+pad&&ty+76>z.top-pad&&ty<z.bottom+pad){const left=Math.abs(tx-(z.left-76-pad)),right=Math.abs(tx-(z.right+pad));tx=left<right?z.left-76-pad:z.right+pad;}}
   tx=Math.max(6,Math.min(innerWidth-82,tx));ty=Math.max(88,Math.min(innerHeight-86,ty));
   let dx=tx-r.x,dy=ty-r.y;
   for(const q of targets){if(q===r||q.kind!=='follower')continue;const sx=r.x-q.x,sy=r.y-q.y,d=Math.hypot(sx,sy);if(d>1&&d<70){dx+=sx/d*(70-d)*1.6;dy+=sy/d*(70-d)*1.6;}}
   const dist=Math.hypot(dx,dy),speed=Math.min(r.speed,dist*2.2),alpha=1-Math.exp(-4*dt);
   r.vx+=((dist>1?dx/dist*speed:0)-r.vx)*alpha;r.vy+=((dist>1?dy/dist*speed:0)-r.vy)*alpha;
   r.x=Math.max(6,Math.min(innerWidth-82,r.x+r.vx*dt));r.y=Math.max(88,Math.min(innerHeight-86,r.y+r.vy*dt));
   r.el.style.opacity=zones.some(z=>r.x+76>z.left&&r.x<z.right&&r.y+76>z.top&&r.y<z.bottom)?'0':'1';
   r.el.style.transform=`translate3d(${r.x}px,${r.y}px,0) scaleX(${r.vx < -12?-1:1})`;
  }
  frame=requestAnimationFrame(tick);
 }
 toggle.addEventListener('click',()=>enabled?disable():enable());
 addEventListener('pointermove',e=>{if(!enabled||mobile())return;pointer={x:e.clientX,y:e.clientY};},{passive:true});
 addEventListener('resize',()=>{if(enabled){disable();enable();}});
 document.addEventListener('visibilitychange',()=>{if(document.hidden)stop();else if(enabled&&!mobile()&&!reduced.matches)frame=requestAnimationFrame(tick);});
 reduced.addEventListener('change',()=>{setTrigger();if(enabled)targets.forEach(r=>{r.el.src=reduced.matches?still(r.id):asset(r.id);});stop();if(enabled&&!mobile()&&!reduced.matches)frame=requestAnimationFrame(tick);});
 setTrigger();updateLabel();return {updateLabel};
}
