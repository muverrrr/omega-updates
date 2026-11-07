#!/usr/bin/env python3
"""Check untrusted OMEGA release ZIP before GitHub publication."""
from pathlib import Path, PurePosixPath
import json, re, sys, zipfile

def verify(version, path):
    if not re.fullmatch(r'[0-9]+\.[0-9]+\.[0-9]+', version):
        raise ValueError('Invalid version')
    path = Path(path)
    if path.stat().st_size > 60 * 1024 * 1024:
        raise ValueError('Archive too large')
    with zipfile.ZipFile(path) as z:
        infos=z.infolist()
        if len(infos) > 2000 or sum(x.file_size for x in infos) > 180 * 1024 * 1024:
            raise ValueError('Too many / too large files')
        if z.testzip() is not None: raise ValueError('CRC check failed')
        meta=json.loads(z.read('OMEGA_RELEASE.json'))
        if meta.get('schema')!='omega-release-v1' or meta.get('version')!=version:
            raise ValueError('Release metadata mismatch')
        module=meta.get('module', '')
        if not re.fullmatch(r'omega_v[4-9][0-9]*',module):
            raise ValueError('Invalid module name')
        prefix='OMEGA_SIMULATION_CORE/'+module+'/'
        names=set()
        for info in infos:
            n=info.filename
            if n=='OMEGA_RELEASE.json':continue
            p=PurePosixPath(n)
            if ('\\' in n or n.startswith('/') or '..' in p.parts or
                not n.startswith(prefix) or info.flag_bits & 1):
                raise ValueError('Unsafe file path: '+n)
            if ((info.external_attr>>16)&0o170000)==0o120000:
                raise ValueError('Symlinks prohibited')
            if n in names:raise ValueError('Duplicate path')
            names.add(n)
            if '/saves/' in n or 'private' in n.lower() or 'secret' in n.lower() or n.endswith('.db'):
                raise ValueError('Private/save material prohibited: '+n)
        for required in ('start.py','service.py','install.py'):
            if prefix+required not in names:raise ValueError('Missing '+required)
    print(f'OMEGA release v{version} validated ({len(names)} files).')

if __name__=='__main__':
    if len(sys.argv)!=3:sys.exit('Usage: verify_release.py VERSION omega-update.zip')
    try:verify(sys.argv[1],sys.argv[2])
    except Exception as e:sys.exit('Rejected: '+str(e))
