"""Create deterministic portable release archives and verify extracted copies."""
import argparse
from pathlib import Path
import hashlib
import os
import subprocess
import sys
import tempfile
import zipfile
from release_layout import release_files,skill_files
from release_audit import audit

ROOT=Path(__file__).resolve().parents[1]
ARCHIVE_ROOT='gamedev-workbench'

def archive(source,target,files=None):
    source=Path(source).resolve()
    files=release_files(source) if files is None else files
    with zipfile.ZipFile(target,'w',zipfile.ZIP_DEFLATED) as z:
        for path in sorted(files):
            info=zipfile.ZipInfo(ARCHIVE_ROOT+'/'+path.relative_to(source).as_posix(),date_time=(2000,1,1,0,0,0))
            info.compress_type=zipfile.ZIP_DEFLATED
            info.create_system=3; info.external_attr=0o100644<<16
            z.writestr(info,path.read_bytes())
    return hashlib.sha256(Path(target).read_bytes()).hexdigest()

def build(output_dir):
    findings=audit(ROOT)
    if findings: raise ValueError('Release audit failed: '+'; '.join(findings))
    output=Path(output_dir).resolve(); output.mkdir(parents=True,exist_ok=True)
    version=(ROOT/'skills/gamedev-workbench/VERSION').read_text(encoding='utf-8').strip()
    project_zip=output/f'gamedev-workbench-{version}.zip'
    skill_zip=output/f'gamedev-workbench-skill-{version}.zip'
    source=ROOT/'skills/gamedev-workbench'
    hashes={project_zip.name:archive(ROOT,project_zip),skill_zip.name:archive(source,skill_zip,skill_files(source))}
    sys.path.insert(0,str(source/'scripts'))
    from evidence_gallery import load_evidence,render_gallery
    report,images=load_evidence(ROOT/'docs/quality-v05')
    gallery=output/f'gamedev-workbench-gallery-{version}.html'
    gallery.write_text(render_gallery(report,images),encoding='utf-8',newline='\n')
    hashes[gallery.name]=hashlib.sha256(gallery.read_bytes()).hexdigest()
    from creative_workspace import create_workspace
    from workspace_view import render_workspace
    import json
    with tempfile.TemporaryDirectory(prefix='gdw-workspace-release-') as d:
        workspace=Path(d).resolve()/'workspace'
        create_workspace(json.loads((source/'assets/design/brief.json').read_text(encoding='utf-8')),workspace)
        page=output/f'gamedev-workbench-workspace-{version}.html'
        page.write_text(render_workspace(workspace),encoding='utf-8',newline='\n')
        hashes[page.name]=hashlib.sha256(page.read_bytes()).hexdigest()
    env=dict(os.environ,PYTHONUTF8='1')
    with tempfile.TemporaryDirectory(prefix='gdw-release-') as d:
        with zipfile.ZipFile(project_zip) as z: z.extractall(d)
        extracted=Path(d)/ARCHIVE_ROOT
        subprocess.run([sys.executable,'tools/gdw.py','validate'],cwd=extracted,env=env,check=True)
        subprocess.run([sys.executable,'-m','unittest','discover','-s','tests','-v'],cwd=extracted,env=env,check=True)
    with tempfile.TemporaryDirectory(prefix='gdw-skill-') as d:
        with zipfile.ZipFile(skill_zip) as z: z.extractall(d)
        subprocess.run([sys.executable,str(Path(d)/ARCHIVE_ROOT/'scripts/workbench.py'),'validate'],env=env,check=True)
    (output/'SHA256SUMS.txt').write_text(''.join(f'{digest}  {name}\n' for name,digest in hashes.items()),encoding='utf-8')
    return hashes

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output-dir',default=str(ROOT.parent))
    args=parser.parse_args()
    print('Archives verified:',', '.join(build(args.output_dir)))

if __name__=='__main__': main()
