"""Download a fixed official test engine, verify SHA256, extract only locally."""
import hashlib
from pathlib import Path
import sys
import urllib.request
import zipfile

ROOT = Path(__file__).resolve().parents[1]
ASSETS = {
    'win32': ('Godot_v4.5.1-stable_win64.exe.zip', 'defccc78669e644861b4247626b01ae362cd9f23975edf19c8bfd2eb1f6a1783'),
    'linux': ('Godot_v4.5.1-stable_linux.x86_64.zip', '02ec53d1cc7dbb9cc6355393c61b9ab43d1244751a124f10248a4802830788cd'),
}

def owned(path):
    path.resolve().relative_to(ROOT.resolve())
    for part in (path, *path.parents):
        if part == ROOT:
            break
        if part.is_symlink() or part.is_junction():
            raise ValueError('Linked download or extraction path')

def main():
    if sys.platform not in ASSETS:
        raise SystemExit('Automatic test-engine download supports Windows and Linux only')
    name, digest = ASSETS[sys.platform]
    directory = ROOT / '.scratch/test-engine'
    owned(directory)
    directory.mkdir(parents=True, exist_ok=True)
    url = 'https://github.com/godotengine/godot/releases/download/4.5.1-stable/' + name
    with urllib.request.urlopen(url, timeout=60) as response:  # fixed HTTPS official release
        data = response.read(100 * 1024 * 1024 + 1)
    if len(data) > 100 * 1024 * 1024 or hashlib.sha256(data).hexdigest() != digest:
        raise RuntimeError('Test engine checksum or size mismatch')
    archive = directory / 'download.zip'
    archive.write_bytes(data)
    with zipfile.ZipFile(archive) as zipped:
        for entry in zipped.infolist():
            target = directory / entry.filename
            target.resolve().relative_to(directory.resolve())
            owned(target)
        zipped.extractall(directory)
    executable = directory / name.removesuffix('.zip')
    if sys.platform == 'linux':
        executable.chmod(0o755)
    print(executable)

if __name__ == '__main__':
    main()
