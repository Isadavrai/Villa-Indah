from PIL import Image,ImageChops
from pathlib import Path
import json,hashlib
from collections import deque
sources=[('exec-b1cda203-9335-4ac0-9dae-11513f11348b.png',[0,229,458,687,916,1145]),('exec-5f2cf066-af56-4e2d-9f02-77d26df1fce9.png',[0,229,458,687,916,1145]),('exec-43ba7f65-2106-4e4f-8cec-eebf237fe7f7.png',[0,240,480,720,915,1145])]
actions=['breathing-tail','head-turn','shoulder-scratch','forearm-groom','yawn','two-hand-hang','one-hand-hang','lying-tail','dangling-feet','sleeping','arm-stretch','chest-groom','side-look','reclining','face-rub'];manifest=[]
for sheet,(filename,ys) in enumerate(sources):
 im=Image.open('/workspace/generated_images/'+filename).convert('RGBA')
 for row in range(5):
  index=sheet*5+row;ident=f'P{index+1:02}';frames=[]
  for col in range(6):
   f=im.crop((col*229,ys[row],(col+1)*229,ys[row+1]))
   # Drop near-transparent generation noise, preserving the visible fur edges.
   a=f.getchannel('A').point(lambda x:0 if x<48 else x)
   # Ignore detached fragments from neighbouring generated cells.
   w,h=f.size;pixels=a.load();seen=set();largest=[]
   for yy in range(h):
    for xx in range(w):
     if (xx,yy) in seen or not pixels[xx,yy]:continue
     q=deque([(xx,yy)]);seen.add((xx,yy));part=[]
     while q:
      x,y=q.popleft();part.append((x,y))
      for nx,ny in [(x-1,y),(x+1,y),(x,y-1),(x,y+1),(x-1,y-1),(x+1,y+1),(x-1,y+1),(x+1,y-1)]:
       if 0<=nx<w and 0<=ny<h and (nx,ny) not in seen and pixels[nx,ny]:seen.add((nx,ny));q.append((nx,ny))
     if len(part)>len(largest):largest=part
   mask=Image.new('L',(w,h));mp=mask.load()
   for x,y in largest:mp[x,y]=pixels[x,y]
   f.putalpha(mask);frames.append(f)
  boxes=[f.getbbox() for f in frames];box=(min(b[0] for b in boxes if b),min(b[1] for b in boxes if b),max(b[2] for b in boxes if b),max(b[3] for b in boxes if b));side=max(box[2]-box[0],box[3]-box[1])+12
  result=[]
  for f in frames:
   f=f.crop(box);canvas=Image.new('RGBA',(side,side));canvas.alpha_composite(f,((side-f.width)//2,side-f.height-6));canvas=canvas.resize((192,192),Image.Resampling.LANCZOS);result.append(canvas)
  path=Path('assets/monkeys/generated')/(ident+'.webp');duration=[420,190,190,330,190,300]
  result[0].save(path,save_all=True,append_images=result[1:],duration=duration,loop=0,quality=84,method=4,minimize_size=True)
  result[0].save(path.with_name(ident+'-still.png'),optimize=True)
  manifest.append(dict(id=ident,action=actions[index],frames=6,durationMs=sum(duration),source=filename,sourceSha256=hashlib.sha256(im.tobytes()).hexdigest(),bytes=path.stat().st_size))
Path('assets/monkeys/generated/manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
print('Created',len(manifest),'animations;',sum(m['bytes'] for m in manifest),'bytes')
# A contact sheet against the actual site background to inspect alpha and cell boundaries.
review=Image.new('RGB',(900,540),'#F7F3EA')
for i,m in enumerate(manifest):
 f=Image.open('assets/monkeys/generated/'+m['id']+'-still.png');f.thumbnail((170,170));review.paste(f,((i%5)*180,(i//5)*180),f)
review.save('/tmp/generated-troupe-review.png')
