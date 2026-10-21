import os
import hashlib
import csv
from PIL import Image
from pathlib import Path

ROOT_DIR = Path.cwd()
# Path mengarah langsung ke folder hasil ekstraksi Autopsy kamu
AUTOPSY_DIR = ROOT_DIR / '05_TOOL2' / 'DF05_Main_Experiment_Week4'
MANIFEST_CSV = ROOT_DIR / '02_GROUND_TRUTH' / 'source_manifest.csv'
OUTPUT_CSV = ROOT_DIR / '07_ANALYSIS' / 'main_results.csv'

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
                gt_hashes.add(row['sha256'].lower())

    results = []
    headers = ['case_id', 'container', 'condition', 'tool', 'carved_filename', 'opens_ok', 'hash_match', 'tp', 'fp']
    valid_extensions = {'.jpg', '.jpeg', '.png', '.bmp'}

    # 2. Sisir seluruh file gambar di dalam subfolder Autopsy
    carved_files = [p for p in AUTOPSY_DIR.rglob('*.*') if p.suffix.lower() in valid_extensions]

    print(f"Menganalisis {len(carved_files)} file gambar hasil ekstraksi Autopsy...")

    for i, filepath in enumerate(carved_files, start=1):
        # Mengambil nama subfolder kondisi (contiguous, split, header_damaged, truncated)
        condition_folder = filepath.parent.name
        
        file_hash = calculate_sha256(filepath)
        opens_ok = check_image_validity(filepath)
        
        # Evaluasi forensik: Hash Match jika SHA256 ada di source manifest
        hash_match = 1 if (file_hash and file_hash.lower() in gt_hashes) else 0
        tp = 1 if hash_match == 1 else 0
        fp = 1 if tp == 0 else 0

        results.append({
            'case_id': f'AUTO-{i:03d}',
            'container': f'{condition_folder}.dd',
            'condition': condition_folder,
            'tool': 'Autopsy 4.23.1',
            'carved_filename': filepath.name,
            'opens_ok': opens_ok,
            'hash_match': hash_match,
            'tp': tp,
            'fp': fp
        })

    # 3. Simpan seluruh hasil ke main_results.csv
    OUTPUT_CSV.parent.mkdir(exist_ok=True)
    with open(OUTPUT_CSV, mode='w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=headers)
        writer.writeheader()
        writer.writerows(results)

    print(f"[SUCCESS] Validasi Main Experiment Selesai! Total file dianalisis: {len(results)}. Output: {OUTPUT_CSV}")

if __name__ == "__main__":
    main()