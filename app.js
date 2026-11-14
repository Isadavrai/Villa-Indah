const $=s=>document.querySelector(s), $$=s=>[...document.querySelectorAll(s)];
let lang='ru';try{lang=localStorage.getItem('indah-language')||'ru'}catch{}if(!copy[lang])lang='ru';
const reduced=matchMedia('(prefers-reduced-motion: reduce)');
let filter='Master Bedroom',expanded=false,visiblePhotos=[],currentPhoto=0,lastGalleryFocus;
const lightbox=$('#lightbox'),form=$('#enquiry-form'),errorBox=$('#form-error');
function t(key){return copy[lang][key]||key}
function setLanguage(value){lang=copy[value]?value:'ru';document.documentElement.lang=lang;$$('[data-i]').forEach(el=>el.textContent=t(el.dataset.i));$$('[data-lang]').forEach(el=>el.setAttribute('aria-pressed',String(el.dataset.lang===lang)));document.title='Private Villa Indah · '+({ru:'Улувату, Бали',en:'Uluwatu, Bali',es:'Uluwatu, Bali'}[lang]);$('meta[name=description]').content=copy[lang].intro;$$('[data-alt]').forEach(img=>{img.alt=copy[lang][img.dataset.alt]||roomIdLabel(lang,img.dataset.room)});renderFilters();renderGallery();if(villaConfig.mapsDirectionsUrl&&!villaConfig.mapsEmbedUrl)$('#map-pending').textContent=t('mapLinkNote');if($('#map-container iframe'))$('#map-container iframe').title=t('mapHeading');if(lightbox.open)showPhoto(currentPhoto);errorBox.textContent='';$('#copy-status').textContent='';updateMonkeyControl();try{localStorage.setItem('indah-language',lang)}catch{}}
$$('[data-lang]').forEach(el=>el.addEventListener('click',()=>setLanguage(el.dataset.lang)));
$('#year').textContent=new Date().getFullYear();
// Navigation, with native links remaining usable without JavaScript.
const menu=$('#menu-toggle'),nav=$('#main-nav');function closeMenu(){menu.setAttribute('aria-expanded','false');nav.classList.remove('open')}
menu.addEventListener('click',()=>{const open=menu.getAttribute('aria-expanded')!=='true';menu.setAttribute('aria-expanded',String(open));nav.classList.toggle('open',open);if(open)nav.querySelector('a').focus()});nav.addEventListener('click',e=>{if(e.target.closest('a'))closeMenu()});
document.addEventListener('keydown',e=>{if(e.key==='Escape'&&nav.classList.contains('open')){closeMenu();menu.focus()}if(e.key==='Tab'&&nav.classList.contains('open')){const links=[menu,...nav.querySelectorAll('a')];if(e.shiftKey&&document.activeElement===menu){e.preventDefault();links.at(-1).focus()}else if(!e.shiftKey&&document.activeElement===links.at(-1)){e.preventDefault();menu.focus()}}});
$$('.booking').forEach(b=>b.addEventListener('click',()=>{closeMenu();$('#enquiry').scrollIntoView({behavior:reduced.matches?'instant':'smooth'});form.elements.checkin.focus({preventScroll:true})}));
let scrollPending=false;function scrollEffects(){scrollPending=false;$('#site-header').classList.toggle('scrolled',scrollY>30);const progress=reduced.matches?0:Math.min(1,scrollY/innerHeight);$('.hero').style.setProperty('--reveal',progress);document.body.classList.toggle('hide-mobile-cta',lightbox.open||$('#enquiry').getBoundingClientRect().top<innerHeight||$('footer').getBoundingClientRect().top<innerHeight)}
addEventListener('scroll',()=>{if(!scrollPending){scrollPending=true;requestAnimationFrame(scrollEffects)}},{passive:true});addEventListener('resize',scrollEffects);reduced.addEventListener('change',scrollEffects);scrollEffects();
// Gallery: categories, keyboard navigation, native modal focus and swipe.
const grid=$('#photo-grid');
function renderGallery(){
  visiblePhotos=photos.filter(p=>p.roomId===filter);
  grid.replaceChildren();
  const shown=expanded?visiblePhotos:visiblePhotos.slice(0,12);
  // Small complete groups keep each tab compact, without empty grid cells.
  for(let start=0;start<shown.length;){
    const remaining=shown.length-start;
    const count=remaining===4?2:Math.min(3,remaining);
    const group=shown.slice(start,start+count);
    const portraits=group.filter(p=>p.height>p.width);
    const mixed=count===3&&portraits.length===1;
    const row=document.createElement('div');
    row.className='gallery-group'+(mixed?' mixed':'')+(count===3?' three':'');
    row.style.setProperty('--columns',count);
    let landscapeRow=0;
    group.forEach((p,offset)=>{
      const index=start+offset;
      const button=document.createElement('button');
      button.className='gallery-item';
      button.setAttribute('aria-label',p.alt[lang]+' · '+(index+1)+' / '+visiblePhotos.length);
      if(mixed){
        if(p.height>p.width){button.style.gridColumn='2';button.style.gridRow='1 / 3'}
        else{button.style.gridColumn='1';button.style.gridRow=String(++landscapeRow)}
      }
      const img=document.createElement('img');
      img.src=p.file;img.alt=p.alt[lang];img.loading='lazy';img.width=p.width;img.height=p.height;
      button.append(img);
      button.addEventListener('click',()=>{lastGalleryFocus=button;currentPhoto=index;showPhoto(index);lightbox.showModal();scrollEffects()});
      row.append(button);
    });
    grid.append(row);start+=count;
  }
  $('#show-all').hidden=expanded||visiblePhotos.length<=12;
  $$('[data-filter]').forEach(b=>b.setAttribute('aria-pressed',String(b.dataset.filter===filter)));
}
function renderFilters(){const host=$('#gallery-filters');host.replaceChildren();roomTabs.forEach(id=>{const button=document.createElement('button');button.dataset.filter=id;button.textContent=id==='all'?t('allPhotos'):roomIdLabel(lang,id);button.setAttribute('aria-pressed',String(id===filter));button.addEventListener('click',()=>{filter=id;expanded=false;renderGallery()});host.append(button)})}
$('#show-all').addEventListener('click',()=>{expanded=true;renderGallery();grid.querySelectorAll('.gallery-item')[12]?.focus()});
function showPhoto(index){currentPhoto=(index+visiblePhotos.length)%visiblePhotos.length;const p=visiblePhotos[currentPhoto];$('#lightbox-image').src=p.file;$('#lightbox-image').alt=p.alt[lang];$('#lightbox-caption').textContent=p.alt[lang]+' · '+t(p.scope==='shared'?'photoScopeShared':'photoScopePrivate');$('#lightbox-counter').textContent=`${currentPhoto+1} / ${visiblePhotos.length}`}
$('#lightbox-prev').addEventListener('click',()=>showPhoto(currentPhoto-1));$('#lightbox-next').addEventListener('click',()=>showPhoto(currentPhoto+1));$('#lightbox-close').addEventListener('click',()=>lightbox.close());lightbox.addEventListener('keydown',e=>{if(e.key==='ArrowLeft'){e.preventDefault();showPhoto(currentPhoto-1)}if(e.key==='ArrowRight'){e.preventDefault();showPhoto(currentPhoto+1)}});lightbox.addEventListener('close',()=>{lastGalleryFocus?.focus();scrollEffects()});lightbox.addEventListener('click',e=>{if(e.target===lightbox)lightbox.close()});let touchX;$('#lightbox-image').addEventListener('touchstart',e=>touchX=e.changedTouches[0].clientX,{passive:true});$('#lightbox-image').addEventListener('touchend',e=>{const delta=e.changedTouches[0].clientX-touchX;if(Math.abs(delta)>45)showPhoto(currentPhoto+(delta<0?1:-1))},{passive:true});
// Calendar dates are compared as YYYY-MM-DD strings; never converted to UTC.
function baliToday(){const parts=new Intl.DateTimeFormat('en-US',{timeZone:villaConfig.timezone,year:'numeric',month:'2-digit',day:'2-digit'}).formatToParts(new Date());const get=type=>parts.find(p=>p.type===type).value;return `${get('year')}-${get('month')}-${get('day')}`}
function nextDay(value){if(!/^\d{4}-\d{2}-\d{2}$/.test(value))return '';const [y,m,d]=value.split('-').map(Number);const date=new Date(Date.UTC(y,m-1,d+1));return date.toISOString().slice(0,10)}
function syncDateLimits(){form.elements.checkin.min=baliToday();form.elements.checkout.min=nextDay(form.elements.checkin.value||baliToday())}syncDateLimits();form.elements.checkin.addEventListener('input',syncDateLimits);
function validateEnquiry(){
 const f=form.elements;$$('#enquiry-form [aria-invalid]').forEach(e=>e.removeAttribute('aria-invalid'));
 let key='',field;const name=f.name.value.trim(),email=f.email.value.trim(),phone=f.phone.value.replace(/[\s().-]/g,'');
 if(!name){key='errorName';field=f.name}
 else if(!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)){key='errorEmail';field=f.email}
 else if(!/^\+[1-9]\d{7,14}$/.test(phone)){key='errorPhone';field=f.phone}
 else if(!f.checkin.value||!f.checkout.value){key='errorDates';field=!f.checkin.value?f.checkin:f.checkout}
 else if(f.checkin.value<baliToday()){key='errorPast';field=f.checkin}
 else if(f.checkout.value<=f.checkin.value){key='errorOrder';field=f.checkout}
 else {const a=Number(f.adults.value),c=Number(f.children.value);if(f.adults.value===''||f.children.value===''||!Number.isInteger(a)||!Number.isInteger(c)||a<1||c<0||a+c>villaConfig.maxGuests){key='errorGuests';field=f.adults}}
 errorBox.textContent=key?t(key):'';if(field){field.setAttribute('aria-invalid','true');field.focus();return false}return true
}
const submit=$('#enquiry-submit');
if(!villaConfig.formEndpoint){submit.disabled=true;submit.title=copy[lang].formPending}
else{$('#form-config-note').hidden=true}
form.addEventListener('submit',async e=>{
 e.preventDefault();if(!villaConfig.formEndpoint)return;if(!validateEnquiry())return;
 const status=$('#form-status');status.textContent=t('formSending');submit.disabled=true;
 try{const response=await fetch(villaConfig.formEndpoint,{method:'POST',body:new FormData(form),headers:{Accept:'application/json'}});if(!response.ok)throw Error(String(response.status));status.textContent=t('formSuccess');form.reset();syncDateLimits();}
 catch{status.textContent=t('formFailure')}finally{submit.disabled=false}
});
if(villaConfig.whatsapp){const b=$('#whatsapp-action');b.hidden=false;b.href='https://wa.me/'+villaConfig.whatsapp.replace(/\D/g,'')}
$$('.copy-email').forEach(b=>b.addEventListener('click',async()=>{try{await navigator.clipboard.writeText($('.direct-contact .email').textContent.trim());$('#copy-status').textContent=t('copied');b.textContent=t('copied')}catch{$('#copy-status').textContent=t('copyFailed');b.textContent=t('copyFailed')}}));
// Optional video: no request until a real source is configured; static poster otherwise.
const video=$('#hero-video'),videoButton=$('#video-toggle');if(villaConfig.video){video.src=villaConfig.video;video.hidden=false;videoButton.hidden=false;videoButton.textContent=t('play');videoButton.addEventListener('click',async()=>{if(video.paused){try{await video.play();videoButton.textContent=t('pause')}catch{videoButton.textContent=t('play')}}else{video.pause();videoButton.textContent=t('play')}});if(!reduced.matches&&!navigator.connection?.saveData)video.play().then(()=>videoButton.textContent=t('pause')).catch(()=>{});reduced.addEventListener('change',()=>{if(reduced.matches)video.pause()})}
// The opt-in troupe controller is isolated from gallery and booking code.
const monkeyTroupe = createMonkeyTroupe({
  root: $('#monkey'), toggle: $('#monkey-toggle'), label: $('#monkey-label'),
  reduced, translate: t
});
function updateMonkeyControl(){ monkeyTroupe.updateLabel(); }
setLanguage(lang);
// The hero shows the actual villa photograph; no generated foliage overlays it.
if(villaConfig.mapsDirectionsUrl){$('#map-directions').href=villaConfig.mapsDirectionsUrl;$('#map-directions').hidden=false;$('#map-pending').textContent=t('mapLinkNote')}
if(villaConfig.mapsEmbedUrl && villaConfig.mapsDirectionsUrl){const frame=document.createElement('iframe');frame.src=villaConfig.mapsEmbedUrl;frame.loading='lazy';frame.referrerPolicy='no-referrer-when-downgrade';frame.title=t('mapHeading');frame.allowFullscreen=true;$('#map-container').append(frame);$('#map-pending').hidden=true}
