"""Buat paket demo Windows; dependency tooling tidak ikut dikemas."""
from pathlib import Path
import hashlib
import json
import zipfile

ROOT = Path(__file__).resolve().parents[1]
DEST = ROOT / 'output/Proyek-Blessya.zip'
PREFIX = 'Proyek-Blessya'


def package():
    # Paket akademik berbeda dari workspace. Tidak menyapu seluruh docs/.
    public_files=(
        'run.py','mulai.bat','README.md','tugas.md',
        'docs/LAPORAN.md','docs/IDENTITAS.json','docs/PERHITUNGAN-MANUAL.md',
        'docs/PANDUAN-PENGGUNA.md','docs/PENGGUNAAN-AI.md','docs/SUMBER-TEORI.md',
        'output/pdf/Laporan-Simulator-Sistem-Operasi.pdf',
        'scripts/build_report.py','scripts/report_content.py','scripts/collect_evidence.py',
        'scripts/analyze_timing.py','scripts/check_browser.cjs','scripts/report_screenshots.cjs',
        'scripts/package_project.py','scripts/check_package.py',
        'docs/evidence/experiments.json','docs/evidence/timing-analysis.json',
        'docs/evidence/tests-audit.txt','docs/evidence/browser-results.json',
        'docs/evidence/browser-audit.txt','docs/evidence/report-check.json',
        'docs/evidence/json-before-fix.txt','docs/evidence/json-partial-fix.txt',
        'docs/evidence/json-after-fix.txt',
        'docs/evidence/detail-fcfs.png','docs/evidence/detail-rr.png','docs/evidence/detail-buffer.png',
        'docs/evidence/ui-awal.png','docs/evidence/ui-fcfs.png','docs/evidence/ui-perbandingan.png',
        'docs/evidence/ui-rr.png','docs/evidence/ui-validasi.png','docs/evidence/ui-buffer.png',
        'docs/evidence/ui-konsumen.png','docs/evidence/ui-mobile.png',
    )
    files=[ROOT/name for name in public_files]
    for path in files:
        if not path.is_file():raise FileNotFoundError(path)
    for directory in ('src', 'web', 'tests', '.tools/python'):
        for path in (ROOT / directory).rglob('*'):
            relative = path.relative_to(ROOT)
            if not path.is_file() or '__pycache__' in relative.parts or path.suffix=='.pyc':
                continue
            files.append(path)
    files = sorted(set(files))
    manifest = []
    DEST.parent.mkdir(exist_ok=True)
    with zipfile.ZipFile(DEST, 'w', zipfile.ZIP_DEFLATED) as archive:
        for path in files:
            relative = path.relative_to(ROOT).as_posix()
            archive.write(path, f'{PREFIX}/{relative}')
            manifest.append({'path': relative, 'bytes': path.stat().st_size,
                             'sha256': hashlib.sha256(path.read_bytes()).hexdigest()})
        archive.writestr(f'{PREFIX}/MANIFEST.json',json.dumps(
            {'purpose':'Paket penyerahan akademik','files':manifest},indent=2,ensure_ascii=False))
    with zipfile.ZipFile(DEST) as archive:
        assert archive.testzip() is None, 'Isi ZIP gagal pemeriksaan CRC'
    result = {'archive': str(DEST.relative_to(ROOT)), 'file_count': len(files)+1,
              'bytes': DEST.stat().st_size,
              'sha256': hashlib.sha256(DEST.read_bytes()).hexdigest(),
              'files': manifest}
    (ROOT / 'output/package-manifest.json').write_text(
        json.dumps(result, indent=2, ensure_ascii=False), encoding='utf-8')
    print(json.dumps({k: v for k, v in result.items() if k != 'files'}, indent=2))


if __name__ == '__main__':
    package()
