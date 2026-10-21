from pathlib import Path
import csv, sys

val = Path(sys.argv[1])
cond = sys.argv[2]
out = Path(sys.argv[3])
root = Path.cwd()

with (root / '02_GROUND_TRUTH' / 'source_manifest.csv').open(newline='', encoding='utf-8') as f:
    sources = list(csv.DictReader(f))
with val.open(newline='', encoding='utf-8') as f:
    recovered = list(csv.DictReader(f))

# report.xml dibuat otomatis oleh PhotoRec di tiap folder hasil; bukan hasil carving.
n_all = len(recovered)
recovered = [r for r in recovered if Path(r['path']).name.lower() != 'report.xml']
print(f'File dikecualikan (report.xml): {n_all - len(recovered)}')

by_hash = {}
for r in recovered:
    by_hash.setdefault(r['sha256'].lower(), []).append(r)

source_hashes = {s['sha256'].lower() for s in sources}

rows = []
exact = 0
for s in sources:
    hit = by_hash.get(s['sha256'].lower())
    if hit:
        r = hit[0]
        exact += 1
        rows.append([cond, s['filename'], s['format'], 1, int(r['valid_image']),
                     r['size_bytes'], s['size_bytes'], r['path']])
    else:
        rows.append([cond, s['filename'], s['format'], 0, '', '', s['size_bytes'], ''])

with out.open('w', newline='', encoding='utf-8') as f:
    w = csv.writer(f)
    w.writerow(['condition', 'source_filename', 'format', 'hash_match', 'opens_ok',
                'recovered_size', 'expected_size', 'recovered_path'])
    w.writerows(rows)

unmatched = [r for r in recovered if r['sha256'].lower() not in source_hashes]
unmatched_valid = sum(int(r['valid_image']) for r in unmatched)

print(f'Kondisi              : {cond}')
print(f'Total file recovered : {len(recovered)}')
print(f'Exact match (hash)   : {exact} dari {len(sources)} source')
print(f'Recovered tanpa match: {len(unmatched)} (lolos Pillow verify: {unmatched_valid})')
print('-> File "tanpa match" perlu ditinjau manual: partial atau false positive.')
print(f'Hasil ditulis ke     : {out}')
