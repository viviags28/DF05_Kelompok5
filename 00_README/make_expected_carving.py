from pathlib import Path
import csv

root = Path.cwd()
gt = root / '02_GROUND_TRUTH'
manifest = gt / 'source_manifest.csv'
out_file = gt / 'expected_carving.csv'

# Kriteria outcome (disepakati kelompok SEBELUM tool dijalankan)
# expected_exact_hash : 1 jika ada run byte kontigu di container yang identik dengan source
# expected_openable   : 1 jika data di container, apa adanya, diharapkan lolos Pillow verify
RULES = {
    'contiguous':     (1, 1, 'File utuh dan kontigu; byte identik dengan source.'),
    'split':          (0, 0, 'Dipecah dua bagian, 8192 byte filler di antaranya; tidak ada run kontigu identik source.'),
    'header_damaged': (0, 0, '4 byte pertama diganti 0x00; signature header hilang.'),
    'truncated':      (0, 0, '10% bagian akhir dibuang; file tidak lengkap.'),
}

with manifest.open(newline='', encoding='utf-8') as f:
    sources = list(csv.DictReader(f))

rows = []
for cond, (exact, openable, note) in RULES.items():
    for s in sources:
        rows.append([cond, s['filename'], s['format'], s['sha256'], exact, openable, note])

with out_file.open('w', newline='', encoding='utf-8') as f:
    w = csv.writer(f)
    w.writerow(['condition', 'source_filename', 'format', 'source_sha256',
                'expected_exact_hash', 'expected_openable', 'notes'])
    w.writerows(rows)

print(f'Selesai: {len(rows)} baris -> {out_file}')