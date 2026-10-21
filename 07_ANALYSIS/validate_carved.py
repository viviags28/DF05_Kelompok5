import os
import hashlib
import csv
from PIL import Image
from pathlib import Path

ROOT_DIR = Path.cwd()
# Path Folder Hasil Kedua Alat
PHOTOREC_DIR = ROOT_DIR / '04_PHOTOREC' / 'v2_main'
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
    try:
        with Image.open(filepath) as img:
            img.verify()
        with Image.open(filepath) as img2:
            img2.load()
        return 1
    except Exception:
        return 0

def scan_tool_results(base_dir, tool_name, gt_hashes):
    results = []
    valid_extensions = {'.jpg', '.jpeg', '.png', '.bmp'}
    
    if not base_dir.exists():
        print(f"[WARN] Folder {base_dir} tidak ditemukan, melewatinya...")
        return results

    carved_files = [p for p in base_dir.rglob('.') if p.suffix.lower() in valid_extensions]
    print(f"Menganalisis {len(carved_files)} file dari {tool_name}...")

    for filepath in carved_files:
        condition_folder = filepath.parents[1].name if filepath.parent.name.startswith('recup_dir') else filepath.parent.name
        
        file_hash = calculate_sha256(filepath)
        opens_ok = check_image_validity(filepath)
        
        hash_match = 1 if (file_hash and file_hash.lower() in gt_hashes) else 0
        tp = 1 if hash_match == 1 else 0
        fp = 1 if tp == 0 else 0

        results.append({
            'container': f'{condition_folder}.dd',
            'condition': condition_folder,
            'tool': tool_name,
            'carved_filename': filepath.name,
            'opens_ok': opens_ok,
            'hash_match': hash_match,
            'tp': tp,
            'fp': fp
        })
    return results

def main():
    gt_hashes = set()
    if MANIFEST_CSV.exists():
        with open(MANIFEST_CSV, mode='r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                gt_hashes.add(row['sha256'].lower())

    all_results = []
    
    # 1. Pindai Hasil PhotoRec
    all_results.extend(scan_tool_results(PHOTOREC_DIR, 'PhotoRec 7.2', gt_hashes))
    
    # 2. Pindai Hasil Autopsy
    all_results.extend(scan_tool_results(AUTOPSY_DIR, 'Autopsy 4.23.1', gt_hashes))

    # Beri nomor case_id otomatis
    for i, row in enumerate(all_results, start=1):
        row['case_id'] = f'MAIN-{i:04d}'

    headers = ['case_id', 'container', 'condition', 'tool', 'carved_filename', 'opens_ok', 'hash_match', 'tp', 'fp']
    
    OUTPUT_CSV.parent.mkdir(exist_ok=True)
    with open(OUTPUT_CSV, mode='w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=headers)
        writer.writeheader()
        writer.writerows(all_results)

    print(f"[SUCCESS] Validasi Gabungan Selesai! Total file dianalisis: {len(all_results)}. Saved to: {OUTPUT_CSV}")

if __name__ == "__main__":
    main()