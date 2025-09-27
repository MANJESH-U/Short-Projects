import hashlib
from pathlib import Path

def verify_sha256(path: Path, expected: str) -> bool:
    if not expected:
        return True
    h = hashlib.sha256()
    with path.open('rb') as f:
        for chunk in iter(lambda: f.read(8192), b''):
            h.update(chunk)
    return h.hexdigest() == expected
