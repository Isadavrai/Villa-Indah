// Map and analytics are independent opt-ins; retain an existing v1 map choice.
let privacyChoice={map:false,analytics:null};
function storedPrivacy(key){try{return JSON.parse(localStorage.getItem(key))}catch{return null}}
const savedPrivacy=storedPrivacy('indah-privacy-v2');
if(savedPrivacy&&typeof savedPrivacy.map==='boolean'&&(typeof savedPrivacy.analytics==='boolean'||savedPrivacy.analytics===null))privacyChoice={map:savedPrivacy.map,analytics:savedPrivacy.analytics};
else{const legacy=storedPrivacy('indah-privacy-v1');if(legacy&&typeof legacy.map==='boolean')privacyChoice.map=legacy.map}
let activePolicy='',policyFocus;
function loadConsentedMap(eager=false){
 const host=document.querySelector('#map-container');
 if(privacyChoice.map&&!host.querySelector('iframe')&&villaConfig.mapsEmbedUrl){
  const frame=document.createElement('iframe');frame.src=villaConfig.mapsEmbedUrl;frame.loading=eager?'eager':'lazy';frame.title=t('mapHeading');frame.referrerPolicy='no-referrer';frame.allowFullscreen=true;
  host.querySelector('.map-placeholder').hidden=true;host.append(frame);
 }
}
function applyPrivacy(){
 if(privacyChoice.map)loadConsentedMap(true);
 else{document.querySelector('#map-container iframe')?.remove();document.querySelector('.map-placeholder').hidden=false}
 window.indahAnalytics.setConsent(privacyChoice.analytics===true);
 document.querySelector('#cookie-banner').hidden=privacyChoice.analytics!==null;
}
function choosePrivacy(patch){
 privacyChoice={...privacyChoice,...patch};
 try{localStorage.setItem('indah-privacy-v2',JSON.stringify(privacyChoice));localStorage.removeItem('indah-privacy-v1')}catch{}
 applyPrivacy();
}
function renderPolicy(){
 const title=activePolicy==='privacy'?'privacyTitle':activePolicy==='terms'?'termsTitle':'cookiesTitle';
 document.querySelector('#policy-title').textContent=t(title);
 const body=document.querySelector('#policy-body');body.replaceChildren();
 if(activePolicy==='cookies'){
  const heading=document.createElement('h3');heading.textContent=t('privacySettings');body.append(heading);
  const necessary=document.createElement('p');necessary.textContent=t('necessaryStorage');body.append(necessary);
  for(const [key,label] of [['map','mapPermission'],['analytics','analyticsPermission']]){
   const row=document.createElement('label'),checkbox=document.createElement('input'),text=document.createElement('span');row.className='consent-label';checkbox.type='checkbox';checkbox.id='privacy-'+key;checkbox.checked=privacyChoice[key]===true;text.textContent=t(label);row.append(checkbox,text);body.append(row);
  }
  const save=document.createElement('button');save.className='solid';save.id='save-privacy';save.type='button';save.textContent=t('savePrivacy');
  const status=document.createElement('p');status.setAttribute('role','status');
  save.addEventListener('click',()=>{choosePrivacy({map:document.querySelector('#privacy-map').checked,analytics:document.querySelector('#privacy-analytics').checked});status.textContent=t('privacySaved')});body.append(save,status);
 }
 for(const [heading,text] of legalContent[lang][activePolicy]){const h=document.createElement('h3'),p=document.createElement('p');h.textContent=heading;p.textContent=text;body.append(h,p)}
 if(activePolicy==='cookies'||activePolicy==='privacy'){
  const reset=document.createElement('button');reset.className='outline-dark';reset.textContent=t('privacyReset');reset.type='button';
  const status=document.createElement('p');status.setAttribute('role','status');
  reset.addEventListener('click',()=>{privacyChoice={map:false,analytics:null};applyPrivacy();for(const key of ['indah-language','indah-privacy-v1','indah-privacy-v2'])try{localStorage.removeItem(key)}catch{}if(activePolicy==='cookies'){document.querySelector('#privacy-map').checked=false;document.querySelector('#privacy-analytics').checked=false}status.textContent=t('resetDone')});body.append(reset,status);
 }
 if(activePolicy==='cookies'||activePolicy==='privacy')for(const [title,url] of [['GitHub Privacy','https://docs.github.com/en/site-policy/privacy-policies/github-general-privacy-statement'],['Formspree Privacy','https://formspree.io/legal/privacy-policy/'],['Google Privacy','https://policies.google.com/privacy'],['Google Cookies','https://policies.google.com/technologies/cookies'],['Telegram Privacy','https://telegram.org/privacy']]){const a=document.createElement('a');a.textContent=title;a.href=url;a.target='_blank';a.rel='noopener noreferrer';a.className='policy-link';body.append(a)}
}
function openPolicy(name,trigger){activePolicy=name;policyFocus=trigger;renderPolicy();document.querySelector('#policy-dialog').showModal()}
function updatePrivacyLanguage(){
 document.querySelector('#policy-close').setAttribute('aria-label',t('close'));
 for(const [id,key] of [['lightbox-close','close'],['lightbox-prev','previousPhoto'],['lightbox-next','nextPhoto']])document.getElementById(id).setAttribute('aria-label',t(key));
 if(activePolicy)renderPolicy();
 document.querySelector('#enquiry-submit').title=villaConfig.formEndpoint?'':t('formPending');
}
function initialisePrivacyMap(){document.querySelector('#map-pending').hidden=true;document.querySelector('#cookie-banner').hidden=privacyChoice.analytics!==null;loadConsentedMap();window.indahAnalytics.setConsent(privacyChoice.analytics===true)}
document.querySelectorAll('[data-policy]').forEach(b=>b.addEventListener('click',()=>openPolicy(b.dataset.policy,b)));
for(const id of ['privacy-settings','banner-privacy-settings'])document.getElementById(id).addEventListener('click',e=>openPolicy('cookies',e.currentTarget));
document.querySelector('#policy-close').addEventListener('click',()=>document.querySelector('#policy-dialog').close());
document.querySelector('#policy-dialog').addEventListener('close',()=>{activePolicy='';policyFocus?.focus()});
document.querySelector('#accept-analytics').addEventListener('click',()=>choosePrivacy({analytics:true}));
document.querySelector('#reject-analytics').addEventListener('click',()=>choosePrivacy({analytics:false}));
document.querySelector('#enable-map').addEventListener('click',()=>choosePrivacy({map:true}));
// Consent changes in another tab must also stop tracking in this one.
addEventListener('storage',e=>{if(e.key!=='indah-privacy-v2'&&e.key!==null)return;try{const saved=e.newValue&&JSON.parse(e.newValue);privacyChoice=saved&&typeof saved.map==='boolean'&&(typeof saved.analytics==='boolean'||saved.analytics===null)?{map:saved.map,analytics:saved.analytics}:{map:false,analytics:null};applyPrivacy();if(activePolicy)renderPolicy()}catch{privacyChoice={map:false,analytics:null};applyPrivacy()}});
