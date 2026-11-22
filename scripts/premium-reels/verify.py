#!/usr/bin/env python3
"""Verify decoded final files, typography anchors, motion and every transition."""
import json, subprocess, sys, struct
from pathlib import Path
import numpy as np
import cv2
from PIL import Image, ImageDraw, ImageFont
import build as b

OUT=b.OUT
def probe(path):
 return json.loads(subprocess.check_output(['ffprobe','-v','error','-show_streams','-show_format','-of','json',str(path)]))
def boxes(path):
 out=[]
 with open(path,'rb') as f:
  while True:
   p=f.tell();head=f.read(8)
   if len(head)<8:break
   size,typ=struct.unpack('>I4s',head)
   if size==1:size=struct.unpack('>Q',f.read(8))[0]
   if size==0:break
   out.append((typ.decode(),p));f.seek(p+size)
 return out

results={}
for lang in ['RU','EN']:
 path=OUT/f'Villa_Indah_Premium_{lang}.mp4';p=probe(path)
 v=next(x for x in p['streams'] if x['codec_type']=='video');a=next(x for x in p['streams'] if x['codec_type']=='audio')
 assert (v['codec_name'],v['width'],v['height'],v['pix_fmt'],v['r_frame_rate'])==('h264',1080,1920,'yuv420p','30/1')
 assert v['avg_frame_rate']=='30/1' and int(v['nb_frames'])==1260
 assert v['color_space']==v['color_transfer']==v['color_primaries']=='bt709'
 assert a['codec_name']=='aac' and float(p['format']['duration'])==42
 atoms=dict(boxes(path));assert atoms['moov']<atoms['mdat']
 decode=subprocess.run(['ffmpeg','-v','error','-xerror','-i',str(path),'-f','null','-'],capture_output=True,text=True)
 assert decode.returncode==0,decode.stderr
 # Check every packet timestamp for a continuous 1/30 second timeline.
 packets=json.loads(subprocess.check_output(['ffprobe','-v','error','-select_streams','v:0','-show_entries','frame=best_effort_timestamp_time','-of','json',str(path)]))['frames']
 timestamps=np.array([float(x['best_effort_timestamp_time']) for x in packets]);assert np.max(abs(np.diff(timestamps)-1/30))<1e-6
 cap=cv2.VideoCapture(str(path));means=[];differences=[];shifts=[];motion=[];midframes={};boundary={};previous=None
 # Immutable text patches, with transparent background replaced by neutral dark.
 templates=[]
 for start,end,(box,png) in b.LAYERS[lang]:
  x0,y0,x1,y1=box;alpha=png[:,:,3:4]/255
  rgb=(png[:,:,:3]*alpha+28*(1-alpha)).astype(np.uint8)
  gray=cv2.cvtColor(rgb,cv2.COLOR_RGB2GRAY)
  # First line only; enough strokes for a precise integer-pixel anchor.
  height=min(100,gray.shape[0]);width=min(450,gray.shape[1])
  patch=gray[:height,:width]
  templates.append((start,end,x0,y0,width,height,cv2.Laplacian(patch,cv2.CV_32F)))
 mid={min(1259,s+39):i for i,s in enumerate(b.STARTS)}
 edgeframes={n for s in b.STARTS[1:] for n in [s-1,s,s+6,s+11,s+12]}
 count=0
 while True:
  ok,frame=cap.read()
  if not ok:break
  gray=cv2.cvtColor(frame,cv2.COLOR_BGR2GRAY);small=cv2.resize(gray,(270,480),interpolation=cv2.INTER_AREA)
  means.append(float(small.mean()))
  if previous is not None:differences.append(float(np.abs(small.astype(float)-prevsmall.astype(float)).mean()))
  t=count/30
  for start,end,x,y,w,h,temp in templates:
   if start+.4<=t<=end-.4:
    patch=gray[y-2:y+h+2,x-2:x+w+2]
    hp=cv2.Laplacian(patch,cv2.CV_32F)
    match=cv2.matchTemplate(hp,temp,cv2.TM_CCOEFF_NORMED)
    _,score,_,loc=cv2.minMaxLoc(match)
    shifts.append([count,loc[0]-2,loc[1]-2,float(score)])
  idx=min(count//66,17);s=b.SCENES[idx];local=count-s['start']
  # Track 30 consecutive pairs within each scene, excluding dissolves and text.
  if lang=='RU' and 23<=local<=52 and previous is not None:
   y0=max(s['vy']+20,600);y1=min(s['vy']+s['vh']-20,1300)
   prev=previous[y0:y1,60:1020];cur=gray[y0:y1,60:1020]
   prev=cv2.resize(prev,None,fx=.5,fy=.5);cur=cv2.resize(cur,None,fx=.5,fy=.5)
   pts=cv2.goodFeaturesToTrack(prev,80,.03,12)
   if pts is not None:
    nxt,st,err=cv2.calcOpticalFlowPyrLK(prev,cur,pts,None,winSize=(21,21),maxLevel=2)
    good=(st[:,0]==1)&(err[:,0]<15)
    p0=pts[good,0,:]*2+np.array([60,y0-s['vy']]);p1=nxt[good,0,:]*2+np.array([60,y0-s['vy']])
    m0=b.transform(s,count-1);m1=b.transform(s,count)
    src=(p0-m0[:,2])/m0[0,0];pred=src*m1[0,0]+m1[:,2]
    if len(p0):motion.append({'scene':idx+1,'frame':count,'median_residual_px':float(np.median(np.linalg.norm(p1-pred,axis=1))),'tracked_points':len(p0)})
  if count in mid:midframes[mid[count]]=frame.copy()
  if count in edgeframes:boundary[count]=frame.copy()
  if count==0:cv2.imwrite(str(OUT/f'Villa_Indah_Preview_{lang}.jpg'),frame,[cv2.IMWRITE_JPEG_QUALITY,95])
  previous=gray;prevsmall=small;count+=1
 cap.release();assert count==1260 and min(means)>12
 assert all(x[1:3]==[0,0] for x in shifts),[x for x in shifts if x[1:3]!=[0,0]][:10]
 if motion:assert max(x['median_residual_px'] for x in motion)<.35
 # Final decoded scene contact sheet (not pre-encoding renders).
 sheet=Image.new('RGB',(1440,1410),'#102019');d=ImageDraw.Draw(sheet);font=ImageFont.truetype(b.SANS,18)
 for i,f in midframes.items():
  im=Image.fromarray(cv2.cvtColor(f,cv2.COLOR_BGR2RGB));im.thumbnail((236,420));x=i%6*240;y=i//6*470;sheet.paste(im,(x,y));d.text((x+7,y+428),f'{i+1:02}  ·  {(b.STARTS[i]+39)/30:.1f}s',font=font,fill='#d5c5a4')
 sheet.save(OUT/f'Villa_Indah_Contact_{lang}.jpg',quality=94)
 # Five frames across each of the 17 transitions for visual inspection.
 sheet=Image.new('RGB',(900,17*345),'#102019');d=ImageDraw.Draw(sheet)
 for i,start in enumerate(b.STARTS[1:]):
  for j,n in enumerate([start-1,start,start+6,start+11,start+12]):
   im=Image.fromarray(cv2.cvtColor(boundary[n],cv2.COLOR_BGR2RGB));im.thumbnail((176,313));sheet.paste(im,(j*180,i*345));d.text((j*180+4,i*345+316),f'{n/30:.3f}s',fill='white')
 sheet.save(b.WORK/f'transitions_{lang}.jpg',quality=90)
 result={'file':path.name,'size_bytes':path.stat().st_size,'video':v,'audio':a,'duration_seconds':42,'decoded_frames':count,'decode_errors':decode.stderr,'faststart':True,'max_timestamp_error_seconds':float(np.max(abs(np.diff(timestamps)-1/30))),'min_frame_luma':min(means),'max_adjacent_frame_mean_difference':max(differences),'caption_frames_checked':len(shifts),'caption_max_integer_displacement_px':max(max(abs(x[1]),abs(x[2])) for x in shifts),'caption_min_match_score':min(x[3] for x in shifts),'motion_pairs_checked':len(motion),'motion_max_median_residual_px':max([x['median_residual_px'] for x in motion],default=0)}
 results[lang]=result
 (OUT/'technical_verification.json').write_text(json.dumps(results,indent=2))
 print(lang,json.dumps({k:v for k,v in result.items() if k not in ['video','audio']}),flush=True)
print('All automated checks passed.',flush=True)
