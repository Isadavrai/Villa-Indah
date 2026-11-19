/* Basic Consent Mode: no Google tag or measurement requests before opt-in. */
window.indahAnalytics=(()=>{
 const id=villaConfig.gaMeasurementId,events=new Set(['click_telegram','booking_form_start','generate_lead','click_email']);
 let allowed=false,tag=null,ready=false,configured=false,pageViewed=false,pending=[];
 window.dataLayer=window.dataLayer||[];
 function gtag(){window.dataLayer.push(arguments)}
 window.gtag=gtag;window['ga-disable-'+id]=true;
 const denied={analytics_storage:'denied',ad_storage:'denied',ad_user_data:'denied',ad_personalization:'denied'};
 gtag('consent','default',denied);
 function parameters(){return {send_to:id,page_location:villaConfig.productionUrl,page_referrer:'',page_title:'Villa Indah',language:['ru','en','es'].includes(document.documentElement.lang)?document.documentElement.lang:'ru'}}
 function emit(name){if(allowed&&ready)gtag('event',name,parameters())}
 function start(){
  if(!allowed||!ready)return;
  gtag('consent','update',{...denied,analytics_storage:'granted'});
  if(!configured){
   gtag('js',new Date());
   gtag('config',id,{send_page_view:false,page_location:villaConfig.productionUrl,page_referrer:'',page_title:'Villa Indah',ignore_referrer:true,allow_google_signals:false,allow_ad_personalization_signals:false,cookie_prefix:'indah',cookie_flags:'SameSite=Lax;Secure'});
   configured=true;
  }
  if(!pageViewed){emit('page_view');pageViewed=true}
  const queue=pending;pending=[];queue.forEach(emit);
 }
 function clearCookies(){
  let names;try{names=document.cookie.split(';').map(v=>v.trim().split('=')[0]).filter(n=>/^indah_ga(?:_|$)/.test(n))}catch{return}
  const host=location.hostname,domains=new Set(['',host,'.'+host]);const parts=host.split('.');
  for(let i=1;i<parts.length-1;i++){domains.add(parts.slice(i).join('.'));domains.add('.'+parts.slice(i).join('.'))}
  for(const name of names)for(const domain of domains)try{document.cookie=name+'=; Max-Age=0; Path=/; SameSite=Lax'+(domain?'; Domain='+domain:'')+(location.protocol==='https:'?'; Secure':'')}catch{};
 }
 function load(){
  if(tag||ready)return;
  tag=document.createElement('script');tag.id='ga4-tag';tag.async=true;tag.src='https://www.googletagmanager.com/gtag/js?id='+encodeURIComponent(id);
  tag.onload=()=>{ready=true;start()};tag.onerror=()=>{tag.remove();tag=null;pending=[]};document.head.append(tag);
 }
 function setConsent(value){
  allowed=value===true;window['ga-disable-'+id]=!allowed;
  if(allowed){if(ready)start();else load()}
  else{pending=[];gtag('consent','update',denied);clearCookies()}
 }
 function track(name){if(!allowed||!events.has(name))return;if(ready)emit(name);else pending.push(name)}
 return {setConsent,track};
})();
