from PIL import Image, ImageDraw
from pathlib import Path
import random, hashlib, csv

root=Path.cwd(); out=root/'01_SOURCE'; gt=root/'02_GROUND_TRUTH'
out.mkdir(exist_ok=True); gt.mkdir(exist_ok=True)
rows=[]
formats=[('JPEG','jpg'),('PNG','png'),('BMP','bmp')]
for fmt,ext in formats:
    for i in range(1,21):
        seed=10000 + i + {'JPEG':0,'PNG':100,'BMP':200}[fmt]
        rng=random.Random(seed)
        w=320 + (i%5)*64; h=240 + (i%4)*48
        img=Image.new('RGB',(w,h),(rng.randrange(256),rng.randrange(256),rng.randrange(256)))
        d=ImageDraw.Draw(img)
        for k in range(25):
            x1=rng.randrange(w); y1=rng.randrange(h); x2=rng.randrange(x1,w); y2=rng.randrange(y1,h)
            d.rectangle((x1,y1,x2,y2),outline=(rng.randrange(256),rng.randrange(256),rng.randrange(256)))
        name=f'{fmt}_{i:02d}.{ext}'; path=out/name
        kwargs={'quality':88} if fmt=='JPEG' else {}
        img.save(path,format=fmt,**kwargs)
        hsh=hashlib.sha256(path.read_bytes()).hexdigest()
        rows.append([name,fmt,w,h,seed,path.stat().st_size,hsh])
with (gt/'source_manifest.csv').open('w',newline='',encoding='utf-8') as f:
    w=csv.writer(f); w.writerow(['filename','format','width','height','seed','size_bytes','sha256']); w.writerows(rows)
print('Selesai: 60 images')