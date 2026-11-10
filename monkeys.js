/* Optional macaques: follow, approach a real ledge, jump, sit and look around.
 * Character footage is replaceable in monkey-clips.js; fallback poses are previews. */
function createMonkeyTroupe({root, toggle, label, reduced, translate, rest, clips}) {
  const MAX_MONKEYS = 10, ARRIVAL_MS = 7000;
  const runners = [], perches = [...document.querySelectorAll('.pool-photo,.garden-photo,.rooms .photo,.experience-photo')];
  let enabled = false, busy = false, frame = 0, lastFrame = 0;
  let visibleMs = 0, visibleSince = null, growthTimer;
  let pointer = {x: innerWidth / 2, y: innerHeight / 2}, lastPointerTime = 0;
  const sheet = new Image();sheet.src = 'assets/monkey-run.png';
  const seat = new Image();seat.src = 'assets/monkey-sit.png';
  const loadedClips = new Map();
  const now = () => visibleMs + (visibleSince === null ? 0 : performance.now() - visibleSince);
  function updateLabel() {
    toggle.setAttribute('aria-pressed', String(enabled));
    toggle.setAttribute('aria-label', translate('monkeyInvite'));
    label.textContent = translate(enabled ? 'monkeyOff' : 'monkeyOn');
    rest.textContent = translate('monkeyRest');
  }
  function bounds(x, y, size) {
    return {x: Math.max(4, Math.min(Math.max(4, innerWidth - size - 4), x)),
      y: Math.max(100, Math.min(Math.max(100, innerHeight - size - (innerWidth <= 700 ? 92 : 55)), y))};
  }
  function preloadClips() {
    for (const [name, clip] of Object.entries(clips)) {
      if (!clip.src || loadedClips.has(name)) continue;
      const image = new Image();image.src = clip.src;
      image.decode().then(() => loadedClips.set(name, image.src)).catch(() => {});
    }
  }
  function showPose(r, state) {
    r.node.dataset.state = state;
    const src = !reduced.matches && loadedClips.get(state);
    const key = src || '';
    if (r.clipKey !== key) {
      r.clipKey = key;
      r.node.classList.toggle('has-clip', Boolean(src));
      if (src) {const image = document.createElement('img');image.className='monkey-clip';image.alt='';image.draggable=false;image.src=src;r.clip.replaceWith(image);r.clip=image;}
      else r.clip.removeAttribute('src');
    }
    if (state !== 'sit' && state !== 'look') {
      const pose = state === 'jump' ? 3 : r.speed > 12 && !reduced.matches ? Math.floor(r.phase) % 4 : 1;
      r.sprite.style.backgroundPosition = ['0% 0%','100% 0%','0% 100%','100% 100%'][pose];
    } else r.sprite.style.backgroundPosition = 'center';
  }
  function render(r, state) {
    r.node.style.transform = `translate3d(${r.x.toFixed(2)}px,${r.y.toFixed(2)}px,0)`;
    r.node.classList.toggle('face-left', r.facing < 0);
    r.node.classList.add('arrived');
    showPose(r, reduced.matches ? 'sit' : state);
  }
  function addRunner(origin) {
    const i = runners.length, node = document.createElement('div'), sprite = document.createElement('div'), clip = document.createElement('img');
    node.className = 'monkey-runner';sprite.className = 'monkey-sprite';clip.className = 'monkey-clip';clip.alt = '';clip.draggable = false;
    sprite.append(clip);node.append(sprite);root.append(node);
    const scale = .88 + ((i * 7) % 5) * .04, size = (innerWidth <= 700 ? 65 : 78) * scale;
    node.style.width = node.style.height = `${size}px`;
    const p = origin || bounds(i % 2 ? innerWidth - size : 6, pointer.y + 60, size);
    runners.push({i,node,sprite,clip,size,scale,x:p.x,y:p.y,vx:0,vy:0,phase:i*.71,speed:0,facing:i%2?-1:1,
      angle:i*2.399963,radius:i===0?0:38+Math.sqrt(i)*24,pace:175+(i*17)%65,
      mode:'follow',perch:null,nextRest:now()+7000+(i*2300)%7000,clipKey:''});
  }
  function syncCount() {
    if (!enabled || document.hidden) return;
    const desired = Math.min(MAX_MONKEYS, 1 + Math.floor(now() / ARRIVAL_MS));
    while (runners.length < desired) addRunner();
    root.dataset.count = String(runners.length);
  }
  function targetFor(r, time) {
    const moving = time - lastPointerTime < 1400 && !reduced.matches ? 1 : 0;
    const dx = Math.cos(r.angle)*r.radius + Math.sin(time/1000*.8+r.angle)*11*moving;
    const dy = Math.sin(r.angle)*r.radius*.55 + Math.sin(time/1000*.6+r.angle*2)*8*moving;
    return bounds(pointer.x-95+dx, pointer.y-30+dy, r.size);
  }
  function perchPoint(r) {
    const rect = r.perch.getBoundingClientRect();
    return {x: rect.left+Math.min(rect.width-r.size-14, 18+(r.i%3)*rect.width*.22), y: rect.top-r.size*.91};
  }
  function release(r) {
    r.mode='follow';r.perch=null;r.node.style.visibility='';r.vx=r.vy=0;
    const p=bounds(r.x,r.y,r.size);r.x=p.x;r.y=p.y;r.nextRest=now()+10000+(r.i*1700)%8000;
  }
  function choosePerch(r,time) {
    if (reduced.matches || r.i%3===2 || time<r.nextRest) return;
    const occupied=runners.filter(m=>m.perch);
    if(occupied.length>=Math.min(3,Math.ceil(runners.length/3))) return;
    const available=perches.filter(el=>{
      if(occupied.some(m=>m.perch===el))return false;
      const b=el.getBoundingClientRect();return b.width>130&&b.top>165&&b.top<innerHeight-125&&b.right>100&&b.left<innerWidth-100;
    });
    if(!available.length)return;
    r.perch=available[r.i%available.length];r.mode='approach';r.approachStart=time;
  }
  function step(r,goal,dt,separation=true) {
    let dx=goal.x-r.x,dy=goal.y-r.y;
    if(separation)for(const other of runners){
      if(other===r||other.mode!=='follow')continue;
      const sx=r.x+r.size/2-other.x-other.size/2,sy=r.y+r.size/2-other.y-other.size/2;
      const d=Math.hypot(sx,sy),space=(r.size+other.size)*.24;
      if(d>.1&&d<space){const force=(space-d)*2;dx+=sx/d*force;dy+=sy/d*force;}
    }
    const distance=Math.hypot(dx,dy),speed=distance<3?0:Math.min(r.pace,distance*3.1),smoothing=1-Math.exp(-6*dt);
    r.vx+=((distance>.1?dx/distance*speed:0)-r.vx)*smoothing;
    r.vy+=((distance>.1?dy/distance*speed:0)-r.vy)*smoothing;
    const p=bounds(r.x+r.vx*dt,r.y+r.vy*dt,r.size);r.x=p.x;r.y=p.y;r.speed=Math.hypot(r.vx,r.vy);
    if(Math.abs(r.vx)>18)r.facing=Math.sign(r.vx);
    r.phase+=r.speed*dt/(24*r.scale);
    if(r.speed>10)r.lastMoving=now();
    const fast=r.node.dataset.state==='run'?85:110;
    render(r,r.speed>fast?'run':r.speed>10||now()-(r.lastMoving||0)<1000?'walk':'sit');
  }
  function tick(timestamp) {
    frame=0;
    if(!enabled||document.hidden||reduced.matches)return;
    const dt=Math.min(.04,(timestamp-(lastFrame||timestamp))/1000),time=now();lastFrame=timestamp;
    syncCount();
    for(const r of runners){
      if(r.mode==='follow')choosePerch(r,time);
      if(r.perch){
        const dest=perchPoint(r);
        if(r.mode==='approach'){
          if(dest.y<100||dest.y>innerHeight-100||time-r.approachStart>10000){release(r);}
          else {
            const stage=bounds(dest.x-45,dest.y+35,r.size);step(r,stage,dt,false);
            if(Math.hypot(stage.x-r.x,stage.y-r.y)<12){r.mode='jump';r.jumpStart=time;r.from={x:r.x,y:r.y+scrollY};r.facing=dest.x>=r.x?1:-1;}
            continue;
          }
        }
        if(r.mode==='jump'){
          const duration=clips.jump.duration||700,p=Math.min(1,(time-r.jumpStart)/duration),ease=p*p*(3-2*p);
          r.x=r.from.x+(dest.x-r.from.x)*ease;
          r.y=(r.from.y-scrollY)+(dest.y-(r.from.y-scrollY))*ease-Math.sin(p*Math.PI)*35;
          render(r,'jump');
          if(p===1){r.mode='rest';r.sitStart=time;r.until=time+15000+(r.i*3700)%13000;r.vx=r.vy=r.speed=0;}
          continue;
        }
        if(r.mode==='rest'){
          if(time>=r.until){release(r);}
          else {
            r.x=dest.x;r.y=dest.y;
            r.node.style.visibility=dest.y<82||dest.y>innerHeight-80?'hidden':'';
            const elapsed=time-r.sitStart;
            render(r,elapsed>4000&&elapsed<4000+clips.look.duration?'look':'sit');
            continue;
          }
        }
      }
      step(r,targetFor(r,time),dt);
    }
    frame=requestAnimationFrame(tick);
  }
  function settle() {
    runners.forEach(r=>{r.mode='follow';r.perch=null;r.node.style.visibility='';const p=targetFor(r,now());r.x=p.x;r.y=p.y;r.vx=r.vy=r.speed=0;render(r,'sit');});
  }
  function restart() {
    cancelAnimationFrame(frame);frame=0;lastFrame=0;
    if(!enabled||document.hidden)return;
    syncCount();if(reduced.matches)settle();else frame=requestAnimationFrame(tick);
  }
  function disable() {
    enabled=false;visibleMs=0;visibleSince=null;root.hidden=true;rest.hidden=true;
    runners.length=0;root.replaceChildren();root.dataset.count='0';clearInterval(growthTimer);
    updateLabel();restart();
  }
  toggle.addEventListener('click',async()=>{
    if(busy||enabled)return;busy=true;
    try{await Promise.all([sheet.decode(),seat.decode()]);}catch{busy=false;return;}
    busy=false;
    const rect=toggle.getBoundingClientRect();
    pointer={x:Math.min(innerWidth-30,rect.right+140),y:Math.min(innerHeight-100,rect.bottom+120)};
    visibleMs=0;visibleSince=document.hidden?null:performance.now();lastPointerTime=0;
    enabled=true;root.hidden=false;rest.hidden=false;addRunner({x:rect.left+30,y:rect.top+40});
    preloadClips();updateLabel();restart();scheduleGrowth();
  });
  rest.addEventListener('click',()=>{disable();if(toggle.getBoundingClientRect().bottom>0)toggle.focus({preventScroll:true});});
  function onPointer(e) {
    if(!enabled||e.target.closest?.('#monkey-toggle,#monkey-rest'))return;
    pointer={x:e.clientX,y:e.clientY};lastPointerTime=now();if(reduced.matches)settle();
  }
  addEventListener('pointermove',onPointer,{passive:true});addEventListener('pointerdown',onPointer,{passive:true});
  addEventListener('touchmove',e=>{const t=e.touches[0];if(t)onPointer({clientX:t.clientX,clientY:t.clientY,target:e.target});},{passive:true});
  addEventListener('resize',()=>{
    for(const r of runners){r.size=(innerWidth<=700?65:78)*r.scale;r.node.style.width=r.node.style.height=`${r.size}px`;const p=r.perch?perchPoint(r):bounds(r.x,r.y,r.size);r.x=p.x;r.y=p.y;render(r,r.node.dataset.state||'sit');}
  });
  document.addEventListener('visibilitychange',()=>{
    if(document.hidden&&visibleSince!==null){visibleMs+=performance.now()-visibleSince;visibleSince=null;}
    else if(enabled&&!document.hidden&&visibleSince===null)visibleSince=performance.now();restart();
  });
  reduced.addEventListener('change',restart);
  function scheduleGrowth(){clearInterval(growthTimer);growthTimer=setInterval(()=>{if(enabled&&!document.hidden){syncCount();if(reduced.matches)settle();}},1000);}
  addEventListener('pagehide',()=>{if(visibleSince!==null){visibleMs+=performance.now()-visibleSince;visibleSince=null;}cancelAnimationFrame(frame);frame=0;clearInterval(growthTimer);});
  addEventListener('pageshow',()=>{if(enabled){if(!document.hidden&&visibleSince===null)visibleSince=performance.now();scheduleGrowth();restart();}});
  return {updateLabel};
}
