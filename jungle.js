/* Feathered regions of the same photograph: no separate foliage panels. */
function createLivingJungle(){
 const hero=document.querySelector('.hero'),photo=document.querySelector('.hero-photo'),trigger=document.querySelector('#monkey-toggle'),motion=matchMedia('(prefers-reduced-motion: reduce)');
 document.querySelector('#living-jungle')?.remove();
 for(let i=0;i<3;i++){const layer=document.createElement('img');layer.src=photo.src;layer.alt='';layer.setAttribute('aria-hidden','true');layer.className=`canopy-layer canopy-${i}`;photo.after(layer);}
 let visible=true;
 function sync(){hero.classList.toggle('jungle-paused',!visible||document.hidden||motion.matches);}
 new IntersectionObserver(([e])=>{visible=e.isIntersecting;sync();}).observe(hero);document.addEventListener('visibilitychange',sync);motion.addEventListener('change',sync);sync();
}
