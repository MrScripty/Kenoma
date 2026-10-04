"""Install a verified official Linux x86_64 release into a writable directory."""
from pathlib import Path
import argparse
import hashlib
import subprocess
import tempfile
import urllib.request

VERSION = '4.19.0'
URL = f'https://github.com/leanprover/lean4/releases/download/v{VERSION}/lean-{VERSION}-linux.tar.zst'
# SHA-256 of the official release bytes verified for the first milestone.
SHA256 = '6fe3ce97a58f44e2b3567d455b994eacec5bfe9ae7774f2a573444480ba813fe'
MAX_ARCHIVE_BYTES = 512 * 1024**2


def verified(path):
    if path.stat().st_size > MAX_ARCHIVE_BYTES:
        return False
    with path.open('rb') as source:
        return hashlib.file_digest(source, 'sha256').hexdigest() == SHA256


def ensure_archive(directory):
    """Keep the final cache name reserved for bytes matching the pinned digest."""
    directory.mkdir(parents=True, exist_ok=True)
    archive = directory / f'lean-{VERSION}-linux.tar.zst'
    if archive.exists():
        if verified(archive):
            return archive
        archive.unlink()  # Interrupted/corrupt old cache can be fetched again.
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(dir=directory, prefix=archive.name + '.',
                                         suffix='.part', delete=False) as output:
            temporary = Path(output.name)
            with urllib.request.urlopen(URL, timeout=120) as response:
                length = response.headers.get('Content-Length')
                if length is not None and int(length) > MAX_ARCHIVE_BYTES:
                    raise RuntimeError('Official toolchain exceeds download byte budget')
                total = 0
                while block := response.read(1024**2):
                    total += len(block)
                    if total > MAX_ARCHIVE_BYTES:
                        raise RuntimeError('Official toolchain exceeds download byte budget')
                    output.write(block)
        if not verified(temporary):
            raise RuntimeError('Official toolchain archive hash mismatch; refusing to extract or execute')
        temporary.replace(archive)  # Same-directory promotion AFTER verification.
        return archive
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)


def install(directory):
    archive = ensure_archive(directory)
    subprocess.run(['tar', '--zstd', '-xf', str(archive), '-C', str(directory)], check=True)
    binary = (directory / f'lean-{VERSION}-linux/bin/lean').resolve()
    subprocess.run([str(binary), '--version'], check=True)
    print(f'Use LEAN={binary} when building, or place its bin directory on PATH.')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--directory', type=Path, default=Path('.tools'))
    install(parser.parse_args().directory)


if __name__ == '__main__':
    main()
