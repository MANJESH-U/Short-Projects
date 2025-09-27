import argparse, os, hashlib, tarfile, zipfile, subprocess, requests, yaml
from pathlib import Path
from urllib.parse import urlparse

BASE_DIR = Path(__file__).resolve().parents[1]
DATASETS_DIR = BASE_DIR / 'datasets' / 'raw'
CHUNK_SIZE = 1024*1024

def sha256_of_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open('rb') as f:
        for chunk in iter(lambda: f.read(CHUNK_SIZE), b''):
            h.update(chunk)
    return h.hexdigest()

def download_url(url: str, dst: Path):
    dst.parent.mkdir(parents=True, exist_ok=True)
    print(f'Downloading {url} -> {dst}')
    with requests.get(url, stream=True) as r:
        r.raise_for_status()
        with dst.open('wb') as f:
            for chunk in r.iter_content(chunk_size=CHUNK_SIZE):
                if chunk:
                    f.write(chunk)

def extract_if_needed(path: Path, extract_to: Path):
    if zipfile.is_zipfile(path):
        with zipfile.ZipFile(path, 'r') as z:
            z.extractall(extract_to)
    elif tarfile.is_tarfile(path):
        with tarfile.open(path, 'r:*') as t:
            t.extractall(extract_to)

def main(config_path: Path):
    with config_path.open('r') as f:
        config = yaml.safe_load(f)
    for entry in config:
        name = entry['name']
        url = entry['url']
        filename = entry.get('filename') or os.path.basename(urlparse(url).path)
        checksum = entry.get('checksum') or None
        extract = bool(entry.get('extract'))
        target_dir = DATASETS_DIR / name
        target_dir.mkdir(parents=True, exist_ok=True)
        dst = target_dir / filename
        if dst.exists() and checksum:
            if sha256_of_file(dst) == checksum:
                print(f'Skipping {name}: checksum matches')
                continue
        if not dst.exists():
            download_url(url, dst)
        if checksum and sha256_of_file(dst) != checksum:
            raise SystemExit(f'Checksum mismatch for {dst}')
        if extract:
            extract_if_needed(dst, target_dir)

if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('--config', type=str, default=str(BASE_DIR / 'datasets' / 'datasets.yml'))
    args = p.parse_args()
    main(Path(args.config))
