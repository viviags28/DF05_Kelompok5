import os
import hashlib
import csv
from PIL import Image
from pathlib import Path

ROOT_DIR = Path.cwd()
PHOTOREC_DIR = ROOT_DIR / '04_PHOTOREC'
MANIFEST_CSV = ROOT_DIR / '02_GROUND_TRUTH' / 'source_manifest.csv'
OUTPUT_CSV = ROOT_DIR / '07_ANALYSIS' / 'pilot_results.csv'

def calculate_sha256(filepath):
    sha256 = hashlib.sha256()
    try:
        with open(filepath, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b''):
                sha256.update(chunk)
        return sha256.hexdigest()
    except Exception:
        return None

def check_image_validity(filepath):
    try:
        with Image.open(filepath) as img:
            img.verify()
        return 1
    except Exception:
        return 0

def main():
    # 1. Baca manifest ground truth
    gt_hashes = set()
    if MANIFEST_CSV.exists():
        with open(MANIFEST_CSV, mode='r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                gt_hashes.add(row['sha256'])

    results = []
    headers = ['case_id', 'container', 'condition', 'tool', 'carved_filename', 'opens_ok', 'hash_match', 'tp', 'fp']
    valid_extensions = {'.jpg', '.jpeg', '.png', '.bmp'}

    # 2. Sisir seluruh subfolder di dalam 04_PHOTOREC (contiguous, split, header_damaged, truncated)
    carved_files = [p for p in PHOTOREC_DIR.rglob('*.*') if p.suffix.lower() in valid_extensions]

    print(f"Menganalisis {len(carved_files)} file gambar hasil carving dari seluruh container...")

    for i, filepath in enumerate(carved_files, start=1):
        container_folder = filepath.parent.name  # Mengambil nama subfolder (misal: split, contiguous)
        file_hash = calculate_sha256(filepath)
        opens_ok = check_image_validity(filepath)
        
        hash_match = 1 if file_hash in gt_hashes else 0
        tp = 1 if (hash_match == 1 or opens_ok == 1) else 0
        fp = 1 if tp == 0 else 0

        results.append({
            'case_id': f'PILOT-{i:02d}',
            'container': f'{container_folder}.dd',
            'condition': container_folder,
            'tool': 'PhotoRec 7.2',
            'carved_filename': filepath.name,
            'opens_ok': opens_ok,
            'hash_match': hash_match,
            'tp': tp,
            'fp': fp
        })

    # 3. Simpan seluruh hasil ke pilot_results.csv
    with open(OUTPUT_CSV, mode='w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=headers)
        writer.writeheader()
        writer.writerows(results)

    print(f"[SUCCESS] Validasi Seluruh Container Selesai! Hasil disimpan di: {OUTPUT_CSV}")

if __name__ == "__main__":
    main()
