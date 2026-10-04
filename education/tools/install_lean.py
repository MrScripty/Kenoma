"""Install the pinned official Linux x86_64 release into a local writable directory."""
from pathlib import Path
import argparse,hashlib,shutil,subprocess,urllib.request
VERSION='4.19.0'
URL=f'https://github.com/leanprover/lean4/releases/download/v{VERSION}/lean-{VERSION}-linux.tar.zst'
# SHA-256 of the official release bytes verified for the first milestone.
SHA256='6fe3ce97a58f44e2b3567d455b994eacec5bfe9ae7774f2a573444480ba813fe'
parser=argparse.ArgumentParser();parser.add_argument('--directory',type=Path,default=Path('.tools'))
args=parser.parse_args();args.directory.mkdir(parents=True,exist_ok=True)
archive=args.directory/f'lean-{VERSION}-linux.tar.zst'
if not archive.exists():
    print(f'Downloading official Lean {VERSION} Linux x86_64 release')
    with urllib.request.urlopen(URL,timeout=120) as response,archive.open('wb') as output:
        shutil.copyfileobj(response,output)
with archive.open('rb') as f:digest=hashlib.file_digest(f,'sha256').hexdigest()
if digest!=SHA256:raise RuntimeError('Official toolchain archive hash mismatch; refusing to execute')
subprocess.run(['tar','--zstd','-xf',str(archive),'-C',str(args.directory)],check=True)
binary=(args.directory/f'lean-{VERSION}-linux/bin/lean').resolve()
subprocess.run([str(binary),'--version'],check=True)
print(f'Use LEAN={binary} when building, or place its bin directory on PATH.')
