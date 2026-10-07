from pathlib import Path
import csv, hashlib, random
root=Path.cwd(); src=root/'01_SOURCE'; out=root/'03_CONTAINERS'; gt=root/'02_GROUND_TRUTH'
out.mkdir(exist_ok=True); rows=[]
files=sorted([p for p in src.iterdir() if p.is_file()])
SEP=b'\x00'*4096

def write_item(fh, data, fname, condition, chunk):
    start=fh.tell(); fh.write(data); end=fh.tell()-1
    rows.append([condition,fname,chunk,start,end,len(data),hashlib.sha256(data).hexdigest()])

with (out/'contiguous.dd').open('wb') as fh:
    for p in files:
        write_item(fh,p.read_bytes(),p.name,'contiguous','whole'); fh.write(SEP)

rng=random.Random(505)
with (out/'split.dd').open('wb') as fh:
    for p in files:
        b=p.read_bytes(); mid=len(b)//2
        write_item(fh,b[:mid],p.name,'split','part1')
        filler=bytes(rng.randrange(256) for _ in range(8192)); fh.write(filler)
        write_item(fh,b[mid:],p.name,'split','part2'); fh.write(SEP)

with (out/'header_damaged.dd').open('wb') as fh:
    for p in files:
        b=bytearray(p.read_bytes()); b[:4]=b'\x00'*min(4,len(b))
        write_item(fh,bytes(b),p.name,'header_damaged','whole'); fh.write(SEP)

with (out/'truncated.dd').open('wb') as fh:
    for p in files:
        b=p.read_bytes(); cut=max(1,int(len(b)*0.90))
        write_item(fh,b[:cut],p.name,'truncated','whole'); fh.write(SEP)

with (gt/'layout.csv').open('w',newline='',encoding='utf-8') as f:
    w=csv.writer(f); w.writerow(['condition','source_filename','chunk','start_offset','end_offset','chunk_size','chunk_sha256']); w.writerows(rows)
print('Containers:', ', '.join(p.name for p in out.glob('*.dd')))