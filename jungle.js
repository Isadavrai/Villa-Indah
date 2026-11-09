/* Feathered regions of the same photograph: no separate foliage panels. */
function createLivingJungle(){
 const hero=document.querySelector('.hero'),photo=document.querySelector('.hero-photo'),trigger=document.querySelector('#monkey-toggle'),motion=matchMedia('(prefers-reduced-motion: reduce)');
 document.querySelector('#living-jungle')?.remove();
 for(let i=0;i<3;i++){const layer=document.createElement('img');layer.src=photo.src;layer.alt='';layer.setAttribute('aria-hidden','true');layer.className=`canopy-layer canopy-${i}`;photo.after(layer);}
 let visible=true;
 function layout(){const w=hero.clientWidth,h=hero.clientHeight,iw=photo.naturalWidth||1536,ih=photo.naturalHeight||1024,scale=Math.max(w/iw,h/ih),mobile=innerWidth<=700,a=mobile?{x:.455,y:.11}:{x:.365,y:.145};const x=a.x*iw*scale+(w-iw*scale)*(mobile?.53:.5),y=a.y*ih*scale+(h-ih*scale)*.5;trigger.style.left=`${Math.max(10,Math.min(w-trigger.offsetWidth-10,x-trigger.offsetWidth*.6))}px`;trigger.style.top=`${Math.max(12,y-trigger.offsetWidth*.9)}px`;}
 function sync(){hero.classList.toggle('jungle-paused',!visible||document.hidden||motion.matches);}
 new ResizeObserver(layout).observe(hero);new IntersectionObserver(([e])=>{visible=e.isIntersecting;sync();}).observe(hero);document.addEventListener('visibilitychange',sync);motion.addEventListener('change',sync);photo.decode().then(layout).catch(()=>{});layout();sync();
}
