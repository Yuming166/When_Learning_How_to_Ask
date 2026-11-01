"""Complete local source closure, read-only history, and explicit runtime fingerprints."""
import hashlib
import json
import sys
from pathlib import Path
from .bootstrap import ROOT


def digest(p):
    h = hashlib.sha256()
    with Path(p).open('rb') as f:
        for b in iter(lambda: f.read(1048576), b''): h.update(b)
    return h.hexdigest()


def local_sources():
    return {str(p.relative_to(ROOT)): digest(p) for p in sorted(ROOT.rglob('*.py')) if '__pycache__' not in p.parts and 'artifacts' not in p.relative_to(ROOT).parts}


def history_check():
    d = json.loads((ROOT/'HISTORICAL_INPUTS.json').read_text())
    for receipt in d['public_receipts'].values():
        for rel, h in receipt['files'].items():
            if digest(Path(receipt['root'])/rel) != h: raise RuntimeError('Historical public bytes changed: '+rel)
    for p, h in d['additional_readonly_files'].items():
        if digest(p) != h: raise RuntimeError('Historical input changed: '+p)
    return {k: len(v['files']) for k, v in d['public_receipts'].items()}


def freeze():
    if (ROOT/'SOURCE_MANIFEST.json').exists() or (ROOT/'artifacts').exists(): raise RuntimeError('No reseal or scientific retry')
    import numpy, scipy, platform, sysconfig, os
    runtime = {'python': sys.version, 'platform': platform.platform(), 'numpy': numpy.__version__, 'scipy': scipy.__version__, 'files': {}}
    paths = {Path(sys.executable).resolve()}
    stdlib = Path(sysconfig.get_path('stdlib'))
    for folder, dirs, names in os.walk(stdlib):
        dirs[:] = [d for d in dirs if d not in ['site-packages','__pycache__']]
        for n in names:
            p = Path(folder)/n
            if p.suffix in ['.py','.so']: paths.add(p.resolve())
    paths.update(p.resolve() for p in (Path(sys.prefix)/'lib').glob('libpython*.so*') if p.is_file())
    for mod in [numpy, scipy]:
        base = Path(mod.__file__).parent
        for p in base.rglob('*'):
            if p.is_file() and '__pycache__' not in p.parts and p.suffix in ['.py', '.so', '.pyi', '.pxd']:
                paths.add(p.resolve())
        for folder in [base.parent/(base.name+'.libs'), base.parent/(base.name+'_libs')]:
            if folder.exists(): paths.update(p.resolve() for p in folder.rglob('*') if p.is_file())
    runtime['files'] = {str(p): digest(p) for p in sorted(paths)}
    (ROOT/'RUNTIME_DEPENDENCIES.json').write_text(json.dumps(runtime, indent=2)+'\n')
    bound = ['config.json', 'T1D_PROTOCOL.md', 'SIMPLE_SCHEDULE_ABLATION_PLAN.md',
             'POLICY_SEMANTICS_AND_SOURCE_AUDIT.md', 'HISTORICAL_INPUTS.json',
             'PREFLIGHT.json', 'LITERATURE_SOURCES.json', 'RUNTIME_DEPENDENCIES.json']
    bound += [str(p.relative_to(ROOT)) for p in sorted((ROOT/'audit').glob('*.txt'))]
    bound += ['audit/ANALYSIS_PREFLIGHT.json','audit/PREFLIGHT_INITIAL_12.json','PREFLIGHT_GATES.json']
    manifest = {'sources': local_sources(), 'documents': {n: digest(ROOT/n) for n in bound},
                'historical_public_files_verified': history_check(),
                'scope': 'all local Python including wrappers, runner, analysis, tests and vendored dependency sources; Python executable and NumPy/SciPy Python/native binaries fingerprinted; not a complete OS attestation'}
    (ROOT/'SOURCE_MANIFEST.json').write_text(json.dumps(manifest, indent=2)+'\n')
    return verify()


def verify():
    d = json.loads((ROOT/'SOURCE_MANIFEST.json').read_text())
    if local_sources() != d['sources']: raise RuntimeError('Source set or source bytes changed')
    for n, h in d['documents'].items():
        if digest(ROOT/n) != h: raise RuntimeError('Frozen document changed: '+n)
    runtime = json.loads((ROOT/'RUNTIME_DEPENDENCIES.json').read_text())
    for p, h in runtime['files'].items():
        if digest(p) != h: raise RuntimeError('Numerical runtime changed: '+p)
    history_check()
    return {'all_local_python_files': len(d['sources']), 'documents': len(d['documents']),
            'runtime_files': len(runtime['files']), 'source_manifest_sha256': digest(ROOT/'SOURCE_MANIFEST.json'), 'passed': True}
