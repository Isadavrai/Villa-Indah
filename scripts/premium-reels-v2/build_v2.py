#!/usr/bin/env python3
"""Villa Indah reference-led premium vertical edit (RU + EN)."""
import argparse, json, math, subprocess, hashlib
from pathlib import Path
import cv2, numpy as np
from PIL import Image, ImageDraw, ImageFont
from scipy.signal import butter, sosfilt
from scipy.io.wavfile import write as wavwrite

P=argparse.ArgumentParser();P.add_argument('--repo',default='work/Villa-Indah');P.add_argument('--out',default='output/premium-v2');P.add_argument('--preview',action='store_true');A=P.parse_args()
REPO=Path(A.repo);OUT=Path(A.out);OUT.mkdir(parents=True,exist_ok=True);TMP=Path('work/premium_v2/render');TMP.mkdir(parents=True,exist_ok=True)
W,H,FPS=1080,1920,30
SERIF='/usr/share/fonts/truetype/noto/NotoSerifDisplay-Regular.ttf';SANS='/usr/share/fonts/truetype/noto/NotoSans-Regular.ttf'
GOLD=(204,181,132,255);WHITE=(248,246,240,255)

# Authored focal points keep architecture, beds and pools straight and centered.
SCENES=[
('Private Swimming Pool/02.webp',.50,.52,1),('Private Swimming Pool/05.webp',.52,.52,-1),('Private Swimming Pool/04.webp',.49,.52,1),
('Private Swimming Pool/03.webp',.50,.51,-1),('Private Swimming Pool/01.webp',.55,.53,1),('Private Swimming Pool/07.webp',.72,.52,-1),
('Master Bedroom/01.webp',.52,.50,1),('Master Bedroom/07.webp',.50,.51,-1),('Pool View Bedroom/04.webp',.46,.52,1),
('Pool View Bedroom/02.webp',.50,.50,-1),('Terrace bedroom/08.webp',.53,.50,1),('Twin Bedroom/01.webp',.47,.50,-1),
('Living room/03.webp',.50,.50,1),('Living room/01.webp',.50,.51,-1),('Living room/04.webp',.52,.50,1),
('Outdoor lounge Area/01.webp',.50,.53,-1),('Outdoor lounge Area/02.webp',.58,.52,1),('Villa Grounds/02.webp',.50,.50,-1),
('Villa Grounds/01.webp',.52,.51,1),('Resort Facilities/04.webp',.51,.53,-1),('Beach/01.webp',.58,.51,1),
('Beach/03.webp',.50,.52,-1),('Private Swimming Pool/06.webp',.53,.52,1),('Private Swimming Pool/03.webp',.50,.51,-1),
('Private Swimming Pool/02.webp',.50,.52,1),
]
DUR=45;N=len(SCENES)*DUR;DURATION=N/FPS
WHIPS={3,6,12,18,22}

def smooth(x):x=np.clip(x,0,1);return x*x*(3-2*x)
def load_scene(spec):
 name,fx,fy,d=spec;rgb=np.asarray(Image.open(REPO/'assets/photos-new'/name).convert('RGB'))
 return {'name':name,'src':rgb,'fx':fx,'fy':fy,'d':d}
DATA=[load_scene(s) for s in SCENES]

def render_photo(i,n):
 s=DATA[i];src=s['src'];sh,sw=src.shape[:2];local=(n-i*DUR)/max(1,DUR-1);e=float(smooth(local))
 # 2.6% continuous zoom plus a restrained authored pan. Absolute-time math only.
 z=1.012+.026*(e if s['d']>0 else 1-e);scale=max(W/sw,H/sh)*z
 cx=sw*(s['fx']+.004*(e-.5)*s['d']);cy=sh*s['fy']
 tx=np.clip(W/2-scale*cx,W-sw*scale,0);ty=np.clip(H/2-scale*cy,H-sh*scale,0)
 m=np.array([[scale,0,tx],[0,scale,ty]],np.float64)
 out=cv2.warpAffine(src,m,(W,H),flags=cv2.INTER_LANCZOS4,borderMode=cv2.BORDER_REPLICATE)
 # Editorial grade: slight warmth, restrained contrast and soft vignette.
 f=out.astype(np.float32)/255;f=np.clip((f-.5)*1.035+.5,0,1);f[:,:,0]*=1.015;f[:,:,2]*=.985
 yy,xx=np.ogrid[:H,:W];v=1-.12*np.clip(((xx-W/2)/(W*.72))**2+((yy-H/2)/(H*.85))**2,0,1)
 return np.uint8(np.clip(f*v[:,:,None],0,1)*255)

def base(n):
 i=min(len(DATA)-1,n//DUR);cur=render_photo(i,n)
 if i and i in WHIPS and n-i*DUR<7:
  k=n-i*DUR;a=float(smooth((k+1)/7));old=render_photo(i-1,n)
  # Controlled horizontal motion blur only during five transition frames.
  direction=1 if i%2 else -1;shift=int(direction*(1-a)*150);shift_old=int(-direction*a*150)
  M1=np.float32([[1,0,shift_old],[0,1,0]]);M2=np.float32([[1,0,shift],[0,1,0]])
  old=cv2.warpAffine(old,M1,(W,H),borderMode=cv2.BORDER_REFLECT);cur=cv2.warpAffine(cur,M2,(W,H),borderMode=cv2.BORDER_REFLECT)
  old=cv2.GaussianBlur(old,(0,0),sigmaX=5*(1-a)+.2);cur=cv2.GaussianBlur(cur,(0,0),sigmaX=5*a+.2)
  cur=cv2.addWeighted(old,1-a,cur,a,0)
 return cur

def tracked(draw,text,font,y,fill,tracking):
 widths=[draw.textlength(c,font=font) for c in text];total=sum(widths)+tracking*(len(text)-1);x=(W-total)/2
 for c,w in zip(text,widths):draw.text((x,y),c,font=font,fill=fill,anchor='lt');x+=w+tracking

def title_layer(title,subtitle,final=False):
 im=Image.new('RGBA',(W,H));d=ImageDraw.Draw(im)
 f1=ImageFont.truetype(SERIF,128 if not final else 118);f2=ImageFont.truetype(SANS,44 if not final else 38)
 y=770 if not final else 700;tracked(d,title,f1,y,WHITE,12)
 d.rounded_rectangle((455,y+168,625,y+172),radius=2,fill=GOLD)
 d.text((W/2,y+212),subtitle,font=f2,fill=WHITE,anchor='mt',align='center')
 if final:
  f3=ImageFont.truetype(SANS,34);d.text((W/2,y+305),'VILLA-INDAH.COM',font=f3,fill=GOLD,anchor='mt')
 return np.asarray(im)

def message_layer(lines):
 im=Image.new('RGBA',(W,H));d=ImageDraw.Draw(im);font=ImageFont.truetype(SANS,54)
 heights=[]
 for txt,color in lines:heights.append(d.textbbox((0,0),txt,font=font)[3])
 gap=24;total=sum(heights)+gap*(len(lines)-1);y=(H-total)/2-25
 for (txt,color),hh in zip(lines,heights):
  d.text((W/2,y),txt,font=font,fill=color,anchor='mt',align='center');y+=hh+gap
 return np.asarray(im)

COPY={
'RU':[
(0,4.5,title_layer('INDAH','ВАША ЧАСТНАЯ ВИЛЛА НА БАЛИ')),
(4.5,9.0,message_layer([('СВОЙ БАССЕЙН',WHITE)])),
(9.0,15.0,message_layer([('4 СПАЛЬНИ',WHITE),('ДО 8 ГОСТЕЙ',GOLD)])),
(15.0,21.0,message_layer([('ПРОСТРАНСТВО',WHITE),('ДЛЯ СВОИХ',GOLD)])),
(21.0,27.0,message_layer([('ТИШИНА. ПРИВАТНОСТЬ.',WHITE),('БАЛИ.',GOLD)])),
(27.0,32.0,message_layer([('УЛУВАТУ',WHITE),('БАЛИ',GOLD)])),
(32.0,DURATION,title_layer('VILLA INDAH','ВАШ ОТДЫХ НА БАЛИ НАЧИНАЕТСЯ ЗДЕСЬ',True)),],
'EN':[
(0,4.5,title_layer('INDAH','YOUR PRIVATE VILLA IN BALI')),
(4.5,9.0,message_layer([('YOUR OWN POOL',WHITE)])),
(9.0,15.0,message_layer([('4 BEDROOMS',WHITE),('UP TO 8 GUESTS',GOLD)])),
(15.0,21.0,message_layer([('SPACE TOGETHER',WHITE),('JUST FOR YOU',GOLD)])),
(21.0,27.0,message_layer([('CALM. PRIVACY.',WHITE),('BALI.',GOLD)])),
(27.0,32.0,message_layer([('ULUWATU',WHITE),('BALI',GOLD)])),
(32.0,DURATION,title_layer('VILLA INDAH','YOUR BALI ESCAPE STARTS HERE',True)),]}

def overlay(frame,n,lang):
 t=n/FPS;out=frame.astype(np.float32)
 for a,b,png in COPY[lang]:
  if a<=t<b:
   fi=float(smooth((t-a)/.28));fo=float(smooth((b-t)/.28));op=min(fi,fo) if a else fo
   # Static central readability wash; only opacity changes, text coordinates never move.
   yy=np.arange(H);wash=.34*np.exp(-((yy-H/2)/(H*.22))**4)*op;out*=1-wash[:,None,None]
   alpha=png[:,:,3:4].astype(np.float32)/255*op;out=out*(1-alpha)+png[:,:,:3]*alpha
 return np.uint8(np.clip(out,0,255))

def music():
 sr=48000;count=round(DURATION*sr);rng=np.random.default_rng(817);mix=np.zeros((count,2),np.float64)
 def add(sig,start,pan=0):
  k=round(start*sr);e=min(count,k+len(sig));sig=sig[:e-k]
  if len(sig):mix[k:e,0]+=sig*np.sqrt((1-pan)/2);mix[k:e,1]+=sig*np.sqrt((1+pan)/2)
 # 80 BPM: every scene cut lands exactly on two beats.
 beat=.75;chords=[[45,52,57,60,64],[41,48,53,57,60],[43,50,55,59,62],[40,47,52,55,59]]
 for bar,start in enumerate(np.arange(0,DURATION,6)):
  notes=chords[bar%4];tt=np.arange(round(min(6,DURATION-start)*sr))/sr;env=np.minimum(tt/.8,1)*np.minimum((len(tt)/sr-tt)/1.2,1)
  for j,note in enumerate(notes):
   hz=440*2**((note-69)/12);sig=(np.sin(2*np.pi*hz*tt)+.18*np.sin(2*np.pi*hz*2*tt))*.018*env;add(sig,float(start),(j-2)*.18)
 for bi,t in enumerate(np.arange(0,DURATION,beat)):
  tt=np.arange(round(.30*sr))/sr;kick=np.sin(2*np.pi*(48*tt+5*(1-np.exp(-tt*18))))*np.exp(-tt*17)*.06;add(kick,float(t))
  if bi%2:
   tt=np.arange(round(.16*sr))/sr;noise=rng.normal(size=len(tt));noise=np.r_[0,np.diff(noise)]*np.exp(-tt*35)*.008;add(noise,float(t),.25)
  if bi%4 in (1,3):
   note=[69,72,64,67][(bi//4)%4];tt=np.arange(round(1.5*sr))/sr;hz=440*2**((note-69)/12)
   pluck=(np.sin(2*np.pi*hz*tt)+.25*np.sin(2*np.pi*hz*2.01*tt))*np.exp(-tt*3.5)*(1-np.exp(-tt*90))*.045;add(pluck,float(t+.08),(-1)**bi*.3)
 dry=mix.copy()
 for delay,gain in [(.23,.14),(.47,.09),(.78,.05)]:o=round(delay*sr);mix[o:]+=dry[:-o,::-1]*gain
 mix=sosfilt(butter(2,7000,fs=sr,output='sos'),mix,axis=0);tt=np.arange(count)/sr;mix*= (smooth(tt/1.0)*smooth((DURATION-tt)/1.8))[:,None]
 mix*=.55/max(np.max(np.abs(mix)),1e-9);wavwrite(str(TMP/'original_premium_score.wav'),sr,(mix*32767).astype(np.int16))

def manifest():
 m={'duration':DURATION,'fps':FPS,'resolution':[W,H],'references_analyzed':['вилла на пхукете…#shorts.mp4','Стамбул…Недвижимость в Стамбуле.mp4'],'style_findings':['1–2 second visual rhythm','full-screen vertical imagery','large concise typography','beat-synced clean cuts','selective directional blur'],'lounger_copy_present':False,'scenes':[]}
 for i,s in enumerate(DATA):
  p=REPO/'assets/photos-new'/s['name'];m['scenes'].append({'index':i+1,'start':i*DUR/FPS,'source':s['name'],'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'focal_point':[s['fx'],s['fy']]})
 (OUT/'production_manifest_v2.json').write_text(json.dumps(m,indent=2,ensure_ascii=False))

def contact(lang):
 sheet=Image.new('RGB',(1350,3200),'#111815');d=ImageDraw.Draw(sheet);f=ImageFont.truetype(SANS,17)
 for i in range(len(DATA)):
  n=i*DUR+DUR//2;im=Image.fromarray(overlay(base(n),n,lang));im.thumbnail((260,462));x=i%5*270;y=i//5*630;sheet.paste(im,(x,y));d.text((x+5,y+472),f'{i+1:02}  {n/FPS:04.1f}s',font=f,fill='#d4c098')
 sheet.save(OUT/f'Villa_Indah_V2_Contact_{lang}.jpg',quality=92)

if __name__=='__main__':
 manifest()
 for lang in ('RU','EN'):
  Image.fromarray(overlay(base(15),15,lang)).save(OUT/f'Villa_Indah_V2_Preview_{lang}.jpg',quality=95);contact(lang)
 if A.preview:raise SystemExit()
 music();procs={};logs={}
 for lang in ('RU','EN'):
  logs[lang]=open(TMP/f'{lang}.log','w');path=OUT/f'Villa_Indah_Premium_V2_{lang}.mp4'
  cmd=['ffmpeg','-y','-v','warning','-f','rawvideo','-pix_fmt','rgb24','-s',f'{W}x{H}','-r',str(FPS),'-i','pipe:0','-i',str(TMP/'original_premium_score.wav'),'-c:v','libx264','-preset','fast','-crf','18','-pix_fmt','yuv420p','-r','30','-fps_mode','cfr','-color_primaries','bt709','-color_trc','bt709','-colorspace','bt709','-color_range','tv','-bsf:v','h264_metadata=colour_primaries=1:transfer_characteristics=1:matrix_coefficients=1:video_full_range_flag=0','-c:a','aac','-b:a','192k','-af','loudnorm=I=-19:TP=-2:LRA=9','-t',str(DURATION),'-movflags','+faststart',str(path)]
  procs[lang]=subprocess.Popen(cmd,stdin=subprocess.PIPE,stderr=logs[lang])
 for n in range(N):
  f=base(n)
  for lang,p in procs.items():p.stdin.write(overlay(f,n,lang).tobytes())
  if n%90==0:print(f'{n}/{N} ({n/FPS:.1f}s)',flush=True)
 for lang,p in procs.items():p.stdin.close();assert p.wait()==0;logs[lang].close()
 print('V2 exports complete',flush=True)
