// No remote SDK. Optional Google iframe is created only after explicit permission.
let privacyChoice=null;
try{const saved=JSON.parse(localStorage.getItem('indah-privacy-v1'));if(saved&&typeof saved.map==='boolean')privacyChoice=saved}catch{}
let activePolicy='',policyFocus;
function loadConsentedMap(){
 const host=document.querySelector('#map-container');
 if(privacyChoice?.map&&!host.querySelector('iframe')&&villaConfig.mapsEmbedUrl){
  const frame=document.createElement('iframe');frame.src=villaConfig.mapsEmbedUrl;frame.loading='lazy';frame.title=t('mapHeading');frame.referrerPolicy='no-referrer';frame.allowFullscreen=true;
  host.querySelector('.map-placeholder').hidden=true;host.append(frame);
 }
}
function choosePrivacy(map){
 privacyChoice={map};try{localStorage.setItem('indah-privacy-v1',JSON.stringify(privacyChoice))}catch{}
 document.querySelector('#cookie-banner').hidden=true;
 if(map)loadConsentedMap();else{document.querySelector('#map-container iframe')?.remove();document.querySelector('.map-placeholder').hidden=false}
}
function renderPolicy(){
 const title=activePolicy==='privacy'?'privacyTitle':activePolicy==='terms'?'termsTitle':'cookiesTitle';
 document.querySelector('#policy-title').textContent=t(title);
 const body=document.querySelector('#policy-body');body.replaceChildren();
 for(const [heading,text] of legalContent[lang][activePolicy]){const h=document.createElement('h3'),p=document.createElement('p');h.textContent=heading;p.textContent=text;body.append(h,p)}
 if(activePolicy==='cookies'||activePolicy==='privacy'){
  const reset=document.createElement('button');reset.className='outline-dark';reset.textContent=t('privacyReset');
  const status=document.createElement('p');status.setAttribute('role','status');
  reset.addEventListener('click',()=>{for(const key of ['indah-language','indah-privacy-v1'])try{localStorage.removeItem(key)}catch{}privacyChoice=null;document.querySelector('#map-container iframe')?.remove();document.querySelector('.map-placeholder').hidden=false;document.querySelector('#cookie-banner').hidden=false;status.textContent=t('resetDone')});body.append(reset,status);
 }
 if(activePolicy==='cookies')for(const [title,url] of [['GitHub Privacy','https://docs.github.com/en/site-policy/privacy-policies/github-general-privacy-statement'],['Google Privacy','https://policies.google.com/privacy'],['Google Cookies','https://policies.google.com/technologies/cookies']]){const a=document.createElement('a');a.textContent=title;a.href=url;a.target='_blank';a.rel='noopener noreferrer';a.className='policy-link';body.append(a)}
}
function openPolicy(name,trigger){activePolicy=name;policyFocus=trigger;renderPolicy();document.querySelector('#policy-dialog').showModal()}
function updatePrivacyLanguage(){
 document.querySelector('#policy-close').setAttribute('aria-label',t('close'));
 for(const [id,key] of [['lightbox-close','close'],['lightbox-prev','previousPhoto'],['lightbox-next','nextPhoto']])document.getElementById(id).setAttribute('aria-label',t(key));
 if(activePolicy)renderPolicy();
 document.querySelector('#enquiry-submit').title=villaConfig.formEndpoint?'':t('formPending');
}
function initialisePrivacyMap(){document.querySelector('#map-pending').hidden=true;document.querySelector('#cookie-banner').hidden=!!privacyChoice;loadConsentedMap()}
document.querySelectorAll('[data-policy]').forEach(b=>b.addEventListener('click',()=>openPolicy(b.dataset.policy,b)));
document.querySelector('#privacy-settings').addEventListener('click',e=>openPolicy('cookies',e.currentTarget));
document.querySelector('#policy-close').addEventListener('click',()=>document.querySelector('#policy-dialog').close());
document.querySelector('#policy-dialog').addEventListener('close',()=>{activePolicy='';policyFocus?.focus()});
document.querySelector('#essential-only').addEventListener('click',()=>choosePrivacy(false));
for(const id of ['allow-map','enable-map'])document.getElementById(id).addEventListener('click',()=>choosePrivacy(true));
