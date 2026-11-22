// Country labels are native/localised. No geolocation or external flag service.
const phoneCountries='ID:62 RU:7 UA:380 BY:375 KZ:7 GB:44 US:1 CA:1 AU:61 NZ:64 DE:49 FR:33 ES:34 IT:39 PT:351 NL:31 BE:32 CH:41 AT:43 IE:353 SE:46 NO:47 DK:45 FI:358 PL:48 CZ:420 SK:421 HU:36 RO:40 BG:359 GR:30 HR:385 SI:386 RS:381 ME:382 TR:90 CY:357 EE:372 LV:371 LT:370 GE:995 AM:374 AZ:994 IL:972 AE:971 SA:966 QA:974 BH:973 OM:968 KW:965 IN:91 PK:92 BD:880 LK:94 NP:977 CN:86 HK:852 TW:886 JP:81 KR:82 SG:65 MY:60 TH:66 VN:84 PH:63 KH:855 LA:856 MM:95 MV:960 MN:976 UZ:998 KG:996 TJ:992 MX:52 BR:55 AR:54 CL:56 CO:57 PE:51 UY:598 EC:593 PA:507 CR:506 DO:1 ZA:27 EG:20 MA:212 TN:216 KE:254 NG:234 MU:230 SC:248'.split(' ').map(entry=>{const [country,dial]=entry.split(':');return {country,dial:'+'+dial}});
function renderPhoneCountries(){
 const select=document.getElementById('phone-country'),selected=select.value||'ID',names=new Intl.DisplayNames([lang],{type:'region'});
 select.replaceChildren();
 for(const item of phoneCountries){const option=document.createElement('option');option.value=item.country;option.dataset.dial=item.dial;const flag=[...item.country].map(c=>String.fromCodePoint(c.charCodeAt(0)+127397)).join('');option.textContent=flag+' '+item.dial+' — '+names.of(item.country);select.append(option)}
 select.value=selected;select.setAttribute('aria-label',t('phoneCountry'));
}
function enquiryPhone(){
 const input=document.querySelector('[name=phone]'),raw=input.value.replace(/[\s().-]/g,'');if(!raw)return '';
 if(raw.startsWith('+'))return raw;
 const select=document.getElementById('phone-country'),dial=select.selectedOptions[0]?.dataset.dial||'+62';
 // Italy retains a leading zero; other listed national trunk zeros are omitted.
 return dial+(select.value==='IT'?raw:raw.replace(/^0+/,''));
}
