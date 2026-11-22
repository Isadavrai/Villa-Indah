#!/usr/bin/env python3
import json, struct, subprocess, sys
from pathlib import Path
import cv2, numpy as np
from PIL import Image,ImageDraw,ImageFont
sys.path.insert(0,str(Path(__file__).parent));import build_v2 as b

OUT=b.OUT;results={}
def probe(p):return json.loads(subprocess.check_output(['ffprobe','-v','error','-show_streams','-show_format','-of','json',str(p)]))
def atoms(p):
 out=[]
 with open(p,'rb') as f:
  while True:
   pos=f.tell();h=f.read(8)
   if len(h)<8:break
   size,typ=struct.unpack('>I4s',h)
   if size==1:size=struct.unpack('>Q',f.read(8))[0]
   if not size:break
   out.append((typ.decode(),pos));f.seek(pos+size)
 return dict(out)

for lang in ('RU','EN'):
 path=OUT/f'Villa_Indah_Premium_V2_{lang}.mp4';p=probe(path);v=next(x for x in p['streams'] if x['codec_type']=='video');a=next(x for x in p['streams'] if x['codec_type']=='audio')
 assert (v['codec_name'],v['width'],v['height'],v['pix_fmt'],v['avg_frame_rate'],int(v['nb_frames']))==('h264',1080,1920,'yuv420p','30/1',b.N)
 assert v['color_space']==v['color_transfer']==v['color_primaries']=='bt709';assert a['codec_name']=='aac';assert abs(float(p['format']['duration'])-b.DURATION)<.02
 at=atoms(path);assert at['moov']<at['mdat']
 dec=subprocess.run(['ffmpeg','-v','error','-xerror','-i',str(path),'-f','null','-'],capture_output=True,text=True);assert dec.returncode==0,dec.stderr
 templates=[]
 for start,end,png in b.COPY[lang]:
  alpha=png[:,:,3];ys,xs=np.where(alpha>30);box=(max(0,xs.min()-3),max(0,ys.min()-3),min(b.W,xs.max()+4),min(b.H,ys.max()+4))
  x0,y0,x1,y1=box;mask=alpha[y0:y1,x0:x1];templates.append((start,end,box,mask))
 cap=cv2.VideoCapture(str(path));count=0;checks=[];frames={};transition_frames={};scene_mid={i*b.DUR+b.DUR//2:i for i in range(len(b.DATA))}
 while True:
  ok,f=cap.read()
  if not ok:break
  g=cv2.cvtColor(f,cv2.COLOR_BGR2GRAY);t=count/b.FPS
  if count in scene_mid:frames[scene_mid[count]]=f.copy()
  if count%b.DUR in (0,2,4,6) and count//b.DUR in b.WHIPS:transition_frames[count]=f.copy()
  if count%5==0:
   for start,end,(x0,y0,x1,y1),mask in templates:
    if start+.45<t<end-.45:
     # Locate high-contrast text edges in a six-pixel neighborhood.
     roi=g[y0-4:y1+4,x0-4:x1+4];edge=cv2.Laplacian(roi,cv2.CV_32F);templ=cv2.Laplacian(mask,cv2.CV_32F)
     _,score,_,loc=cv2.minMaxLoc(cv2.matchTemplate(edge,templ,cv2.TM_CCOEFF_NORMED));checks.append((loc[0]-4,loc[1]-4,float(score)))
  count+=1
 cap.release();assert count==b.N;assert checks and max(max(abs(x),abs(y)) for x,y,_ in checks)==0;assert min(s for _,_,s in checks)>.42
 sheet=Image.new('RGB',(1350,3200),'#101713');d=ImageDraw.Draw(sheet);font=ImageFont.truetype(b.SANS,17)
 for i,f in frames.items():
  im=Image.fromarray(cv2.cvtColor(f,cv2.COLOR_BGR2RGB));im.thumbnail((260,462));x=i%5*270;y=i//5*630;sheet.paste(im,(x,y));d.text((x+5,y+472),f'{i+1:02}  {(i*b.DUR+b.DUR//2)/b.FPS:.1f}s',font=font,fill='#d4c098')
 sheet.save(OUT/f'Villa_Indah_V2_Final_Contact_{lang}.jpg',quality=92)
 results[lang]={'file':path.name,'size_bytes':path.stat().st_size,'duration_seconds':float(p['format']['duration']),'decoded_frames':count,'decode_errors':dec.stderr,'video_codec':v['codec_name'],'audio_codec':a['codec_name'],'resolution':[v['width'],v['height']],'fps':v['avg_frame_rate'],'pixel_format':v['pix_fmt'],'rec709':True,'faststart':True,'caption_checks':len(checks),'caption_max_displacement_px':0,'caption_min_match_score':min(s for _,_,s in checks)}
(OUT/'technical_verification_v2.json').write_text(json.dumps(results,indent=2,ensure_ascii=False))
print(json.dumps(results,indent=2,ensure_ascii=False));print('All V2 checks passed.')
