"""Periksa paket hasil ekstraksi dengan runtime yang ikut di dalam ZIP."""
from pathlib import Path
import json
import hashlib
import socket
import subprocess
import tempfile
import time
import urllib.request
import zipfile

ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / 'docs/evidence'


def main():
    tools_dir = ROOT / '.tools'
    tools_dir.mkdir(exist_ok=True)
    extracted = Path(tempfile.mkdtemp(prefix='package-check-', dir=tools_dir)).resolve()
    assert extracted.is_relative_to(ROOT.resolve())
    checks = []
    with zipfile.ZipFile(ROOT / 'output/Proyek-Blessya.zip') as archive:
        assert archive.testzip() is None
        entries=archive.namelist()
        blocked=('AGENTS.md','OWNER.md','docs/STATUS-KERJA.md','docs/TUGAS-AKTIF.md',
                 'docs/HASIL-TUGAS.md','docs/RENCANA-KERJA.md','docs/REVIEW-AUDIT.md')
        for name in blocked:assert 'Proyek-Blessya/'+name not in entries,name
        assert not any('/docs/arsip/' in name for name in entries)
        manifest=json.loads(archive.read('Proyek-Blessya/MANIFEST.json'))
        for item in manifest['files']:
            payload=archive.read('Proyek-Blessya/'+item['path'])
            assert len(payload)==item['bytes']
            assert hashlib.sha256(payload).hexdigest()==item['sha256']
        assert len(entries)==len(manifest['files'])+1
        for member in archive.namelist():
            assert (extracted / member).resolve().is_relative_to(extracted)
        archive.extractall(extracted)
    checks.append('ZIP dapat diekstrak dan seluruh CRC valid')
    checks.append('Manifest cocok; dokumen kerja serta arsip tidak ikut paket akademik')
    project = extracted / 'Proyek-Blessya'
    python = project / '.tools/python/python.exe'
    assert python.is_file()
    assert (project / '.tools/python/LICENSE.txt').is_file()
    assert (project / 'output/pdf/Laporan-Simulator-Sistem-Operasi.pdf').is_file()
    assert not (project / '.tools/packages').exists()
    assert not (project / '.tools/browser').exists()
    assert 'Aplikasi dan tes dua-duanya jalan' not in (project/'tugas.md').read_text(encoding='utf-8')
    assert 'Codex' in (project/'docs/PENGGUNAAN-AI.md').read_text(encoding='utf-8')
    checks.append('Soal bersih dan pengungkapan bantuan AI tetap disertakan')
    checks.append('Runtime, lisensi, dan PDF tersedia tanpa dependency tooling')

    # Path eksplisit: cmd tidak mencari folder aktif jika NoDefaultCurrentDirectoryInExePath diset.
    tests = subprocess.run(['cmd.exe', '/d', '/c', r'.\mulai.bat test'],
                           cwd=project, capture_output=True, timeout=60)
    log = tests.stdout + b'\n--- STDERR unittest ---\n' + tests.stderr
    (EVIDENCE / 'package-tests.txt').write_bytes(log)
    assert tests.returncode == 0, f'Launcher/test gagal: {tests.returncode}'
    assert b'seluruh 3 berkas pengujian LULUS' in tests.stdout
    assert b'Ran 21 tests' in tests.stderr and b'OK' in tests.stderr
    checks.append('mulai.bat test dari folder ekstraksi: seluruh tiga berkas lulus')

    with socket.socket() as probe:
        probe.bind(('127.0.0.1', 0))
        port = probe.getsockname()[1]
    server = subprocess.Popen(
        [str(python), 'run.py', '--no-browser', '--port', str(port)],
        cwd=project, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        creationflags=subprocess.CREATE_NO_WINDOW)
    base_url = f'http://127.0.0.1:{port}'
    try:
        for _ in range(100):
            try:
                with urllib.request.urlopen(base_url, timeout=1) as response:
                    html = response.read().decode('utf-8')
                break
            except OSError:
                if server.poll() is not None:
                    raise RuntimeError('Server paket berhenti sebelum siap')
                time.sleep(0.1)
        else:
            raise RuntimeError('Server paket tidak siap dalam 10 detik')
        assert 'Penjadwalan CPU' in html and 'Producer' in html
        for asset in ('css/belajar.css', 'js/belajar.js', 'lanjutan.html'):
            with urllib.request.urlopen(base_url + '/' + asset, timeout=3) as response:
                assert response.status == 200 and len(response.read()) > 0
        checks.append('Halaman utama, CSS, JavaScript dan halaman tambahan dapat dimuat')

        def post(path, data):
            request = urllib.request.Request(base_url + path,
                data=json.dumps(data).encode('utf-8'),
                headers={'Content-Type': 'application/json'})
            with urllib.request.urlopen(request, timeout=10) as response:
                return json.loads(response.read())

        result = post('/api/scheduling', {'algorithm': 'fcfs', 'processes': [
            {'pid': 'P1', 'arrival': 0, 'burst': 5},
            {'pid': 'P2', 'arrival': 1, 'burst': 3},
            {'pid': 'P3', 'arrival': 2, 'burst': 1}]})
        assert [m['waiting'] for m in result['results'][0]['metrics']] == [0, 4, 6]
        checks.append('API FCFS paket cocok dengan contoh manual')
        result = post('/api/ipc/producer-consumer', {
            'capacity': 5, 'items': 8, 'producers': 1, 'consumers': 1,
            'produce_ms': 10, 'consume_ms': 80})
        assert result['completed'] and not result['stuck_threads']
        assert result['produced'] == result['consumed'] == 8
        assert result['leftover_in_buffer'] == 0
        checks.append('API Producer-Consumer paket selesai, delapan barang dan buffer akhir kosong')
    finally:
        server.terminate()
        server.communicate(timeout=5)

    result = {'checks': checks, 'passed': len(checks), 'extracted_to': str(project),
              'archive_sha256':hashlib.sha256((ROOT/'output/Proyek-Blessya.zip').read_bytes()).hexdigest(),
              'launcher_exit_code': tests.returncode,
              'server_stopped': server.poll() is not None}
    (EVIDENCE / 'package-check.json').write_text(
        json.dumps(result, indent=2, ensure_ascii=False), encoding='utf-8')
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == '__main__':
    main()
