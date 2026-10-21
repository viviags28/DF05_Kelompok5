import os
import hashlib
import csv
from PIL import Image
from pathlib import Path

ROOT_DIR = Path.cwd()
# Point langsung ke folder v2_main yang bersih
PHOTOREC_DIR = ROOT_DIR / '04_PHOTOREC' / 'v2_main'
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
    """Mengecek keabsahan gambar dengan verify() DAN load() untuk mendeteksi truncation"""
    try:
        # Step 1: Shallow check (Header)
        with Image.open(filepath) as img:
            img.verify()
        
        # Step 2: Deep check (Pixel decoding)
        with Image.open(filepath) as img2:
            img2.load()
            
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

    # 2. Sisir seluruh subfolder di dalam 04_PHOTOREC/v2_main
    carved_files = [p for p in PHOTOREC_DIR.rglob('*.*') if p.suffix.lower() in valid_extensions]

    print(f"Menganalisis {len(carved_files)} file gambar hasil carving v2...")

    for i, filepath in enumerate(carved_files, start=1):
        # Mengambil nama subfolder kondisi (misal: contiguous, split, header_damaged, truncated)
        condition_folder = filepath.parents[1].name if filepath.parent.name.startswith('recup_dir') else filepath.parent.name
        
        file_hash = calculate_sha256(filepath)
        opens_ok = check_image_validity(filepath)
        
        # Evaluasi forensik yang akurat:
        hash_match = 1 if file_hash in gt_hashes else 0
        
        # TP Murni = Exact hash match
        tp = 1 if hash_match == 1 else 0
        
        # FP = Gambar terekstrak tapi hash salah / corrupt / false candidate
        fp = 1 if tp == 0 else 0

        results.append({
            'case_id': f'PILOT-{i:02d}',
            'container': f'{condition_folder}.dd',
            'condition': condition_folder,
            'tool': 'PhotoRec 7.2',
            'carved_filename': filepath.name,
            'opens_ok': opens_ok,
            'hash_match': hash_match,
            'tp': tp,
            'fp': fp
        })

    # 3. Simpan seluruh hasil ke pilot_results.csv
    OUTPUT_CSV.parent.mkdir(exist_ok=True)
    with open(OUTPUT_CSV, mode='w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=headers)
        writer.writeheader()
        writer.writerows(results)

    print(f"[SUCCESS] Validasi Selesai! Total file dianalisis: {len(results)}. Output: {OUTPUT_CSV}")

if __name__ == "__main__":
    main()