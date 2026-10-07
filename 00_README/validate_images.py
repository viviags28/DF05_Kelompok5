from PIL import Image
from pathlib import Path
import hashlib, csv, sys
root=Path(sys.argv[1]); out=Path(sys.argv[2])
rows=[]
for p in root.rglob('*'):
    if not p.is_file(): continue
    h=hashlib.sha256(p.read_bytes()).hexdigest()
    ok=False; fmt='UNKNOWN'; err=''
    try:
        with Image.open(p) as im:
            fmt=im.format or 'UNKNOWN'; im.verify(); ok=True
    except Exception as e: err=str(e)
    rows.append([str(p),p.stat().st_size,h,fmt,int(ok),err])
with out.open('w',newline='',encoding='utf-8') as f:
    w=csv.writer(f); w.writerow(['path','size_bytes','sha256','pillow_format','valid_image','error']); w.writerows(rows)
print('validated',len(rows))