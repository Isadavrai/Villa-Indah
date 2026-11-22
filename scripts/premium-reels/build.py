#!/usr/bin/env python3
"""Villa Indah, 42-second bilingual editorial film. No generated property imagery.
Run: python build.py --repo /path/to/Villa-Indah --out dist/reels
Dependencies: Python 3, numpy, Pillow, opencv-python-headless, scipy; FFmpeg.
"""
import argparse, json, subprocess, math, hashlib, shutil
from pathlib import Path
import numpy as np
import cv2
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from scipy.signal import butter, sosfilt
from scipy.io.wavfile import write as wavwrite

P=argparse.ArgumentParser(); P.add_argument('--repo',default='work/Villa-Indah'); P.add_argument('--out',default='output/dist/reels'); P.add_argument('--preview',action='store_true'); A=P.parse_args()
REPO=Path(A.repo); OUT=Path(A.out); OUT.mkdir(parents=True,exist_ok=True)
WORK=Path('work/production/render');WORK.mkdir(parents=True,exist_ok=True)
W,H,FPS,N=1080,1920,30,1260
cv2.setNumThreads(1)
SANS=str(Path(__file__).parent/'fonts/NotoSans-Regular.ttf') if (Path(__file__).parent/'fonts/NotoSans-Regular.ttf').exists() else '/usr/share/fonts/truetype/noto/NotoSans-Regular.ttf'
BRAND=str(REPO/'assets/fonts/AlumniSansPinstripe-Regular.ttf')
# Every focal point and motion is authored for the original photograph.
SPECS=[
 ('Private Swimming Pool/02.webp','wide',.50,.50,1),
 ('Private Swimming Pool/05.webp','wide',.50,.52,-1),
 ('Private Swimming Pool/04.webp','wide',.47,.52,1),
 ('Private Swimming Pool/01.webp','wide',.55,.52,-1),
 ('Master Bedroom/01.webp','wide',.52,.50,1),
 ('Master Bedroom/07.webp','wide',.50,.51,-1),
 ('Pool View Bedroom/04.webp','wide',.47,.53,1),
 ('Terrace bedroom/08.webp','wide',.53,.50,-1),
 ('Twin Bedroom/01.webp','wide',.48,.50,1),
 ('Living room/03.webp','full',.50,.50,-1),
 ('Outdoor lounge Area/01.webp','wide',.50,.53,1),
 ('Private Swimming Pool/07.webp','full',.77,.50,-1),
 ('Villa Grounds/02.webp','full',.51,.50,1),
 ('Resort Facilities/04.webp','wide',.51,.52,-1),
 ('Beach/01.webp','full',.57,.50,1),
 ('Beach/03.webp','wide',.50,.52,-1),
 ('Private Swimming Pool/03.webp','wide',.50,.51,1),
 ('Private Swimming Pool/02.webp','wide',.50,.50,-1),
]
STARTS=[i*66 for i in range(18)] # 2.2s cadence, 0.4s overlapping dissolves
ENDS=[s+78 for s in STARTS[:-1]]+[N]
def smooth(x):
 x=np.clip(x,0,1);return x*x*(3-2*x)

def photo(path):
 # Original RGB pixels, no recolouring or property edits.
 return np.array(Image.open(path).convert('RGB'))

SCENES=[]
for i,(name,mode,fx,fy,direction) in enumerate(SPECS):
 src=photo(REPO/'assets/photos-new'/name); sh,sw=src.shape[:2]
 if mode=='wide':
  vw=W;vh=round(W*sh/sw);vy=round(960-vh/2)
  thumb=Image.fromarray(src);thumb=thumb.resize((270,round(270*sh/sw)))
  ratio=max(W/thumb.width,H/thumb.height)
  thumb=thumb.resize((math.ceil(thumb.width*ratio),math.ceil(thumb.height*ratio)))
  x=(thumb.width-W)//2;y=(thumb.height-H)//2
  bg=np.array(thumb.crop((x,y,x+W,y+H)).filter(ImageFilter.GaussianBlur(65)))
  bg=(bg.astype(np.float32)*.23+np.array([9,22,17],np.float32)*.63).clip(0,255).astype(np.uint8)
 else:vw,vh,vy=W,H,0;bg=None
 # Supersample source once, then use floating affine coordinates per absolute frame.
 src=cv2.resize(src,None,fx=1.5,fy=1.5,interpolation=cv2.INTER_CUBIC)
 SCENES.append(dict(name=name,mode=mode,src=src,vw=vw,vh=vh,vy=vy,bg=bg,fx=fx,fy=fy,d=direction,start=STARTS[i],end=ENDS[i]))

def transform(s,n):
 u=(n-s['start'])/max(1,s['end']-s['start']-1);e=float(smooth(u))
 sh,sw=s['src'].shape[:2];vw,vh=s['vw'],s['vh']
 z=1.008+.032*(e if s['d']==1 else 1-e)
 scale=max(vw/sw,vh/sh)*z
 # Pan never exceeds 0.6% of source width; anchored around individually chosen focus.
 cx=sw*(s['fx']+.006*(e-.5)*s['d']);cy=sh*s['fy']
 tx=np.clip(vw/2-scale*cx,vw-sw*scale,0)
 ty=np.clip(vh/2-scale*cy,vh-sh*scale,0)
 return np.array([[scale,0,tx],[0,scale,ty]],np.float64)

def frame_scene(i,n):
 s=SCENES[i];m=transform(s,n)
 im=cv2.warpAffine(s['src'],m,(s['vw'],s['vh']),flags=cv2.INTER_CUBIC,borderMode=cv2.BORDER_REPLICATE)
 if s['mode']=='wide':
  out=s['bg'].copy();out[s['vy']:s['vy']+s['vh']]=im;return out
 # Fixed neutral gradient, independent of camera, keeps text legible.
 yy=np.arange(H,dtype=np.float32)
 opacity=.38*np.exp(-((yy-310)/360)**2)+.31*np.exp(-((yy-1470)/300)**2)
 return np.uint8(im*(1-opacity[:,None,None]))

def base_frame(n):
 idx=min(n//66,17);f=frame_scene(idx,n)
 if idx>0 and n<STARTS[idx]+12:
  a=float(smooth((n-STARTS[idx]+.5)/12));f=cv2.addWeighted(frame_scene(idx-1,n),1-a,f,a,0)
 return f

IVORY=(246,241,229,255); GOLD=(199,180,139,255)
def layer(lines):
 im=Image.new('RGBA',(W,H));d=ImageDraw.Draw(im)
 for txt,y,size,kind,color in lines:
  font=ImageFont.truetype(BRAND if kind=='brand' else SANS,size)
  bbox=d.textbbox((0,0),txt,font=font)
  assert bbox[2]-bbox[0]<=850,(txt,bbox)
  # Exact immutable raster and integer anchor. Opacity is the only animation.
  d.text((510,y),txt,font=font,fill=color,anchor='mt',stroke_width=0)
 bbox=im.getbbox();assert bbox and bbox[0]>=84 and bbox[2]<=948 and bbox[1]>=220 and bbox[3]<=1530,bbox
 return (bbox,np.array(im.crop(bbox)))

LAYERS={}
for lang in ['RU','EN']:
 ru=lang=='RU';items=[]
 def add(a,b,lines):items.append((a,b,layer(lines)))
 add(0,4.3,[('INDAH',235,180,'brand',IVORY),('ВАША ЧАСТНАЯ ВИЛЛА' if ru else 'YOUR PRIVATE VILLA',438,42,'sans',IVORY),('НА БАЛИ' if ru else 'IN BALI',502,34,'sans',GOLD)])
 add(4.4,8.7,[('Собственный бассейн' if ru else 'Your own private pool',385,49,'sans',IVORY)])
 add(8.8,19.7,[('4 спальни · До 8 гостей' if ru else '4 Bedrooms · Up to 8 Guests',385,44,'sans',IVORY)])
 add(28.6,30.75,[('Улувату · Бали' if ru else 'Uluwatu · Bali',332,52,'sans',IVORY),('Общий бассейн курорта' if ru else 'Shared resort pool',418,34,'sans',GOLD)])
 add(30.8,35.05,[('Улувату · Бали' if ru else 'Uluwatu · Bali',332,52,'sans',IVORY),('Пляж · общая зона' if ru else 'Beach · shared area',418,34,'sans',GOLD),('Доступ к пляжу включён' if ru else 'Beach access included',1395,32,'sans',IVORY),('Лежаки оплачиваются отдельно' if ru else 'Sun loungers charged separately',1445,30,'sans',IVORY)])
 add(35.2,42,[('INDAH',235,180,'brand',IVORY),('Ваш отдых на Бали начинается здесь' if ru else 'Your Bali escape starts here',439,38,'sans',IVORY),('Уточните даты в Direct' if ru else 'DM us for available dates',1390,40,'sans',IVORY),('villa-indah.com',1470,31,'sans',GOLD)])
 LAYERS[lang]=items

def opacity(t,a,b):
 # Opening is readable on the actual first frame; final card holds to the last.
 fi=1 if a==0 else smooth((t-a)/.30)
 fo=1 if b==42 else smooth((b-t)/.30)
 return float(min(fi,fo))
def caption(im,n,lang):
 out=im.copy();t=n/FPS
 for a,b,(box,png) in LAYERS[lang]:
  if a<=t<b:
   x0,y0,x1,y1=box;alpha=png[:,:,3:4].astype(np.float32)/255*opacity(t,a,b)
   area=out[y0:y1,x0:x1]
   out[y0:y1,x0:x1]=np.rint(area*(1-alpha)+png[:,:,:3]*alpha).astype(np.uint8)
 return out

def music():
 sr=48000;length=42;count=sr*length;rng=np.random.default_rng(317)
 audio=np.zeros((count,2),np.float64)
 def add(sig,start,pan=0):
  k=round(start*sr);end=min(count,k+len(sig));sig=sig[:end-k]
  if len(sig)>0:audio[k:end,0]+=sig*math.sqrt((1-pan)/2);audio[k:end,1]+=sig*math.sqrt((1+pan)/2)
 chords=[[50,57,61,64,69],[47,54,57,61,66],[43,50,54,57,62],[45,52,57,59,64],[50,57,61,64,69],[43,50,54,57,62],[50,57,61,64,69]]
 for bar,chord in enumerate(chords):
  tt=np.arange(sr*8)/sr;env=np.minimum(tt/1.4,1)*np.minimum((8-tt)/2.3,1)
  for j,note in enumerate(chord):
   hz=440*2**((note-69)/12)
   sig=(np.sin(2*np.pi*hz*tt+.1*j)+.28*np.sin(2*np.pi*hz*2*tt)+.08*np.sin(2*np.pi*hz*3*tt))*.020*env
   add(sig,bar*6,(j-2)*.24)
  # Original sparse mallet motif, never sampled from a recording.
  for j,step in enumerate([0,2,4,1,3,2]):
   tt=np.arange(sr*3)/sr;hz=440*2**((chord[step]+12-69)/12)
   sig=(np.sin(2*np.pi*hz*tt)*np.exp(-tt*2.7)+.22*np.sin(2*np.pi*hz*2.01*tt)*np.exp(-tt*7))*(1-np.exp(-tt*75))*.055
   add(sig,bar*6+j*.75+.375,(-1)**j*.28)
 for beat in np.arange(3,39,.75):
  tt=np.arange(int(sr*.25))/sr
  sig=np.sin(2*np.pi*(49*tt+2.3*(1-np.exp(-tt*21))))*np.exp(-tt*22)*.042
  add(sig,float(beat))
  tt=np.arange(int(sr*.12))/sr;noise=rng.normal(size=len(tt));noise=np.r_[0,np.diff(noise)]
  add(noise*np.exp(-tt*52)*(1-np.exp(-tt*400))*.006,float(beat+.375),.35)
 dry=audio.copy()
 for delay,gain in [(.23,.15),(.41,.11),(.67,.075),(1.07,.04)]:
  off=int(delay*sr);audio[off:]+=dry[:-off,::-1]*gain
 audio=sosfilt(butter(2,6500,fs=sr,output='sos'),audio,axis=0)
 tt=np.arange(count)/sr;audio*= (smooth(tt/1.8)*smooth((42-tt)/2.8))[:,None]
 audio*=.49/max(abs(audio).max(),1e-9)
 wavwrite(str(WORK/'original_score.wav'),sr,(audio*32767).astype(np.int16))

def metadata():
 meta={'duration':42,'fps':30,'frames':N,'resolution':[W,H],'source_commit':(subprocess.check_output(['git','-C',str(REPO),'rev-parse','HEAD'],text=True).strip() if (REPO/'.git').exists() else 'b95710b5f22de0022e97ce151caf839b89982420'),'scenes':[],'captions':{}}
 for i,s in enumerate(SCENES):
  path=REPO/'assets/photos-new'/s['name'];mats=np.array([transform(s,n) for n in range(s['start'],s['end'])])
  dm=np.diff(mats,axis=0)
  meta['scenes'].append({'index':i+1,'source':s['name'],'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'layout':s['mode'],'start':s['start']/FPS,'end':s['end']/FPS,'focal_point':[s['fx'],s['fy']],'max_translation_delta_px':float(abs(dm[:,:,2]).max()),'max_translation_acceleration_px':float(abs(np.diff(dm[:,:,2],axis=0)).max()),'zoom_range_percent':[.8,4.0]})
 for lang,items in LAYERS.items():
  meta['captions'][lang]=[{'start':a,'end':b,'fixed_bbox':box,'raster_sha256':hashlib.sha256(png.tobytes()).hexdigest()} for a,b,(box,png) in items]
 (OUT/'production_manifest.json').write_text(json.dumps(meta,indent=2,ensure_ascii=False))

if __name__=='__main__':
 metadata()
 for lang in ['RU','EN']:
  Image.fromarray(caption(base_frame(0),0,lang)).save(OUT/f'Villa_Indah_Preview_{lang}.jpg',quality=95)
 # Preview the authored compositions before expensive encoding.
 for lang in ['RU','EN']:
  sheet=Image.new('RGB',(1440,1800),(15,31,25));d=ImageDraw.Draw(sheet)
  for i in range(18):
   n=min(N-1,STARTS[i]+39);im=Image.fromarray(caption(base_frame(n),n,lang));im.thumbnail((236,420))
   x=(i%6)*240;y=(i//6)*600;sheet.paste(im,(x,y));d.text((x+8,y+433),f'{i+1:02} / {n/FPS:04.1f}s',fill='#d8c8a5')
  sheet.save(WORK/f'composition_{lang}.jpg',quality=92)
 if A.preview:raise SystemExit()
 music()
 procs={};logs={}
 for lang in ['RU','EN']:
  logs[lang]=open(WORK/f'encode_{lang}.log','w')
  cmd=['ffmpeg','-y','-v','warning','-f','rawvideo','-pixel_format','rgb24','-video_size','1080x1920','-framerate','30','-i','pipe:0','-i',str(WORK/'original_score.wav'),'-map','0:v','-map','1:a','-vf','scale=in_range=full:out_range=tv:out_color_matrix=bt709,format=yuv420p,setparams=range=limited:color_primaries=bt709:color_trc=bt709:colorspace=bt709','-c:v','libx264','-preset','fast','-crf','18','-threads','2','-r','30','-fps_mode','cfr','-color_primaries','bt709','-color_trc','bt709','-colorspace','bt709','-color_range','tv','-bsf:v','h264_metadata=colour_primaries=1:transfer_characteristics=1:matrix_coefficients=1:video_full_range_flag=0','-c:a','aac','-b:a','192k','-ar','48000','-af','loudnorm=I=-19:TP=-2:LRA=9','-t','42','-movflags','+faststart','-metadata','title=Villa Indah | '+lang,'-metadata','comment=Original Villa Indah photographs; original synthesized score; no third-party music.',str(OUT/f'Villa_Indah_Premium_{lang}.mp4')]
  procs[lang]=subprocess.Popen(cmd,stdin=subprocess.PIPE,stderr=logs[lang])
 for n in range(N):
  frame=base_frame(n)
  for lang,p in procs.items():p.stdin.write(caption(frame,n,lang).tobytes())
  if n%90==0:print(f'Rendered {n}/{N} frames ({n/FPS:.1f}s)',flush=True)
 for lang,p in procs.items():
  p.stdin.close();assert p.wait()==0,(lang,'encoding failed');logs[lang].close()
 print('Both MP4 exports completed.',flush=True)
