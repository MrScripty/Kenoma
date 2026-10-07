"""Copy the explicit reader/test data closure, without exporting execution archives."""
from pathlib import Path, PurePosixPath
import json, shutil


def publication_sources(education, manifest=None):
    education = Path(education).resolve()
    manifest = Path(manifest) if manifest else education/'tools/anatomy-publication-files.json'
    policy = json.loads(manifest.read_text())
    source = education/policy['sourceRoot']
    if policy['sourceRoot'] != 'data/anatomical-arm-v1' or source.is_symlink():
        raise ValueError('Unexpected publication source root')
    names = policy['files']
    if len(names) != len(set(names)):
        raise ValueError('Duplicate publication path')
    files = []
    for name in names:
        relative = PurePosixPath(name)
        path = source/name
        if relative.is_absolute() or '..' in relative.parts or str(relative) != name:
            raise ValueError('Unsafe publication path: '+name)
        if any(parent.is_symlink() for parent in [path, *path.parents] if parent != education):
            raise ValueError('Symlink publication input: '+name)
        if not path.is_file() or not path.resolve().is_relative_to(source.resolve()):
            raise ValueError('Missing publication input: '+name)
        files.append((name, path))
    return files


def copy_publication_data(education, output):
    files = publication_sources(education)  # Validate before touching generated output.
    output = Path(output).resolve()
    target = output/'data/anatomical-arm-v1'
    source = Path(education).resolve()/'data/anatomical-arm-v1'
    if target == source or target.is_relative_to(source) or source.is_relative_to(target):
        raise ValueError('Publication destination overlaps the preserved source dataset')
    if target.is_symlink() or (output/'data').is_symlink():
        raise ValueError('Symlink publication destination')
    if target.exists():
        shutil.rmtree(target)  # Scoped generated destination; never the source dataset.
    for name, source in files:
        destination = target/name
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, destination)
    return len(files)
